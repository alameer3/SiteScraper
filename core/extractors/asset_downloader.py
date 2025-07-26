"""
Asset Downloader - تحميل جميع الملفات والموارد
المرحلة الأولى: محرك الاستخراج العميق

هذا المحرك يوفر:
1. تحميل جميع أنواع الأصول (صور، CSS، JS، خطوط، ملفات)
2. تنظيم الملفات حسب النوع والمجلد
3. تحسين وضغط الملفات
4. إنشاء خريطة للأصول المحملة
"""

import asyncio
import aiohttp
import hashlib
import mimetypes
import os
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json
import re
import base64

from bs4 import BeautifulSoup, Tag
from PIL import Image, ImageOptim
import cssutils

@dataclass
class DownloadConfig:
    """تكوين تحميل الأصول"""
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_concurrent_downloads: int = 10
    timeout: int = 30
    output_directory: str = "downloaded_assets"
    organize_by_type: bool = True
    optimize_images: bool = True
    minify_css: bool = True
    minify_js: bool = True
    download_external_assets: bool = False
    allowed_extensions: List[str] = None
    blocked_extensions: List[str] = None
    preserve_directory_structure: bool = True
    create_asset_map: bool = True
    user_agent: str = "Mozilla/5.0 (compatible; AssetDownloader/1.0)"

class AssetDownloader:
    """محرك تحميل الأصول الذكي"""
    
    def __init__(self, config: Optional[DownloadConfig] = None):
        self.config = config or DownloadConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # مجلدات التنظيم
        self.asset_folders = {
            'images': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico', 'bmp'],
            'stylesheets': ['css'],
            'scripts': ['js', 'ts'],
            'fonts': ['woff', 'woff2', 'ttf', 'otf', 'eot'],
            'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
            'media': ['mp4', 'mp3', 'avi', 'wav', 'webm', 'ogg', 'mov'],
            'archives': ['zip', 'rar', '7z', 'tar', 'gz'],
            'data': ['json', 'xml', 'csv', 'xlsx'],
            'other': []
        }
        
        # إحصائيات التحميل
        self.download_stats = {
            'total_assets': 0,
            'downloaded_successfully': 0,
            'failed_downloads': 0,
            'total_size_bytes': 0,
            'optimized_assets': 0,
            'duplicate_assets': 0,
            'external_assets': 0,
            'start_time': None,
            'end_time': None
        }
        
        # خريطة الأصول
        self.asset_map: Dict[str, Dict[str, Any]] = {}
        self.downloaded_files: Set[str] = set()
        self.failed_downloads: Set[str] = set()
        self.duplicate_hashes: Dict[str, str] = {}
        
        # إعداد المجلدات الافتراضية
        if self.config.allowed_extensions is None:
            self.config.allowed_extensions = []
            for extensions in self.asset_folders.values():
                self.config.allowed_extensions.extend(extensions)
        
        if self.config.blocked_extensions is None:
            self.config.blocked_extensions = ['exe', 'bat', 'cmd', 'scr', 'com']
    
    async def __aenter__(self):
        """بدء جلسة التحميل"""
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_downloads)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.config.user_agent}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """إنهاء جلسة التحميل"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def download_website_assets(self, site_map: Dict[str, Dict], base_url: str) -> Dict[str, Any]:
        """تحميل جميع أصول الموقع"""
        logging.info("بدء تحميل أصول الموقع...")
        self.download_stats['start_time'] = datetime.now()
        
        # إنشاء مجلد الإخراج
        output_path = Path(self.config.output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # جمع جميع الأصول من خريطة الموقع
        all_assets = await self._collect_assets_from_sitemap(site_map, base_url)
        
        # تصفية الأصول
        filtered_assets = self._filter_assets(all_assets)
        
        # تحميل الأصول بالتوازي
        await self._download_assets_parallel(filtered_assets, base_url)
        
        # تحسين الأصول المحملة
        if self.config.optimize_images or self.config.minify_css or self.config.minify_js:
            await self._optimize_assets()
        
        # إنشاء خريطة الأصول
        if self.config.create_asset_map:
            await self._create_asset_map()
        
        self.download_stats['end_time'] = datetime.now()
        
        return self._generate_download_report()
    
    async def _collect_assets_from_sitemap(self, site_map: Dict[str, Dict], base_url: str) -> Set[str]:
        """جمع جميع الأصول من خريطة الموقع"""
        all_assets = set()
        
        for page_url, page_data in site_map.items():
            try:
                # تحميل صفحة HTML لاستخراج الأصول
                if self.session:
                    async with self.session.get(page_url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            assets = await self._extract_assets_from_html(html_content, page_url)
                            all_assets.update(assets)
            except Exception as e:
                logging.error(f"خطأ في جمع الأصول من {page_url}: {e}")
        
        return all_assets
    
    async def _extract_assets_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """استخراج جميع الأصول من HTML"""
        assets = set()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # الصور
        for img in soup.find_all('img'):
            if isinstance(img, Tag):
                # src العادي
                src = img.get('src')
                if src:
                    assets.add(urljoin(base_url, src))
                
                # data-src (lazy loading)
                data_src = img.get('data-src')
                if data_src:
                    assets.add(urljoin(base_url, data_src))
                
                # srcset
                srcset = img.get('srcset')
                if srcset:
                    for src_item in srcset.split(','):
                        src_url = src_item.strip().split()[0]
                        assets.add(urljoin(base_url, src_url))
        
        # ملفات CSS
        for link in soup.find_all('link', rel='stylesheet'):
            if isinstance(link, Tag):
                href = link.get('href')
                if href:
                    assets.add(urljoin(base_url, href))
        
        # ملفات JavaScript
        for script in soup.find_all('script', src=True):
            if isinstance(script, Tag):
                src = script.get('src')
                if src:
                    assets.add(urljoin(base_url, src))
        
        # الخطوط من CSS
        css_links = soup.find_all('link', rel='stylesheet')
        for css_link in css_links:
            if isinstance(css_link, Tag):
                href = css_link.get('href')
                if href:
                    css_url = urljoin(base_url, href)
                    font_assets = await self._extract_fonts_from_css(css_url, base_url)
                    assets.update(font_assets)
        
        # ملفات الوسائط
        for video in soup.find_all('video'):
            if isinstance(video, Tag):
                src = video.get('src')
                if src:
                    assets.add(urljoin(base_url, src))
                
                # مصادر متعددة
                for source in video.find_all('source'):
                    if isinstance(source, Tag):
                        src = source.get('src')
                        if src:
                            assets.add(urljoin(base_url, src))
        
        # ملفات الصوت
        for audio in soup.find_all('audio'):
            if isinstance(audio, Tag):
                src = audio.get('src')
                if src:
                    assets.add(urljoin(base_url, src))
        
        # الأيقونات
        for link in soup.find_all('link', rel=['icon', 'shortcut icon', 'apple-touch-icon']):
            if isinstance(link, Tag):
                href = link.get('href')
                if href:
                    assets.add(urljoin(base_url, href))
        
        # ملفات من CSS inline
        style_tags = soup.find_all('style')
        for style in style_tags:
            if isinstance(style, Tag) and style.string:
                css_assets = self._extract_assets_from_css_content(style.string, base_url)
                assets.update(css_assets)
        
        return assets
    
    async def _extract_fonts_from_css(self, css_url: str, base_url: str) -> Set[str]:
        """استخراج الخطوط من ملف CSS"""
        fonts = set()
        
        try:
            if self.session:
                async with self.session.get(css_url) as response:
                    if response.status == 200:
                        css_content = await response.text()
                        fonts = self._extract_assets_from_css_content(css_content, css_url)
        except Exception as e:
            logging.error(f"خطأ في استخراج الخطوط من {css_url}: {e}")
        
        return fonts
    
    def _extract_assets_from_css_content(self, css_content: str, base_url: str) -> Set[str]:
        """استخراج الأصول من محتوى CSS"""
        assets = set()
        
        # البحث عن url() في CSS
        url_pattern = r'url\(["\']?([^"\'()]+)["\']?\)'
        matches = re.findall(url_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            # تنظيف الرابط
            url = match.strip()
            if url.startswith('data:'):
                continue  # تخطي data URLs
            
            full_url = urljoin(base_url, url)
            assets.add(full_url)
        
        return assets
    
    def _filter_assets(self, assets: Set[str]) -> List[str]:
        """تصفية الأصول حسب الإعدادات"""
        filtered = []
        
        for asset_url in assets:
            try:
                parsed = urlparse(asset_url)
                
                # فحص الامتداد
                path_lower = parsed.path.lower()
                extension = path_lower.split('.')[-1] if '.' in path_lower else ''
                
                # فحص الامتدادات المحظورة
                if extension in self.config.blocked_extensions:
                    continue
                
                # فحص الامتدادات المسموحة
                if self.config.allowed_extensions and extension not in self.config.allowed_extensions:
                    continue
                
                # فحص الأصول الخارجية
                if not self.config.download_external_assets:
                    # التحقق من النطاق (سيتم تمريره من الدالة الرئيسية)
                    pass
                
                filtered.append(asset_url)
                
            except Exception as e:
                logging.error(f"خطأ في تصفية الأصل {asset_url}: {e}")
        
        return filtered
    
    async def _download_assets_parallel(self, assets: List[str], base_url: str):
        """تحميل الأصول بالتوازي"""
        self.download_stats['total_assets'] = len(assets)
        
        # تقسيم المهام
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        
        async def download_single_asset(asset_url: str):
            async with semaphore:
                await self._download_single_asset(asset_url, base_url)
        
        # تنفيذ التحميلات بالتوازي
        tasks = [download_single_asset(asset_url) for asset_url in assets]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _download_single_asset(self, asset_url: str, base_url: str):
        """تحميل أصل واحد"""
        try:
            if not self.session:
                return
            
            async with self.session.get(asset_url) as response:
                if response.status != 200:
                    self.failed_downloads.add(asset_url)
                    self.download_stats['failed_downloads'] += 1
                    return
                
                # فحص حجم الملف
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.config.max_file_size:
                    logging.warning(f"تم تخطي ملف كبير الحجم: {asset_url}")
                    return
                
                content = await response.read()
                content_type = response.headers.get('content-type', '')
                
                # حساب hash لتجنب التكرار
                file_hash = hashlib.md5(content).hexdigest()
                if file_hash in self.duplicate_hashes:
                    self.download_stats['duplicate_assets'] += 1
                    logging.info(f"تم تخطي ملف مكرر: {asset_url}")
                    return
                
                self.duplicate_hashes[file_hash] = asset_url
                
                # تحديد مسار الحفظ
                file_path = self._determine_file_path(asset_url, content_type)
                
                # إنشاء المجلد إذا لم يوجد
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # حفظ الملف
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # تحديث الإحصائيات
                self.downloaded_files.add(asset_url)
                self.download_stats['downloaded_successfully'] += 1
                self.download_stats['total_size_bytes'] += len(content)
                
                # إضافة إلى خريطة الأصول
                self.asset_map[asset_url] = {
                    'local_path': str(file_path),
                    'original_url': asset_url,
                    'file_size': len(content),
                    'content_type': content_type,
                    'file_hash': file_hash,
                    'download_time': datetime.now().isoformat(),
                    'asset_type': self._determine_asset_type(asset_url, content_type)
                }
                
                logging.info(f"تم تحميل: {asset_url} -> {file_path}")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل {asset_url}: {e}")
            self.failed_downloads.add(asset_url)
            self.download_stats['failed_downloads'] += 1
    
    def _determine_file_path(self, asset_url: str, content_type: str) -> Path:
        """تحديد مسار حفظ الملف"""
        parsed = urlparse(asset_url)
        base_path = Path(self.config.output_directory)
        
        # استخراج اسم الملف والامتداد
        path_parts = parsed.path.strip('/').split('/')
        filename = path_parts[-1] if path_parts else 'index.html'
        
        # إضافة امتداد إذا لم يوجد
        if '.' not in filename:
            extension = mimetypes.guess_extension(content_type)
            if extension:
                filename += extension
        
        if self.config.organize_by_type:
            # تنظيم حسب نوع الملف
            asset_type = self._determine_asset_type(asset_url, content_type)
            file_path = base_path / asset_type / filename
        elif self.config.preserve_directory_structure:
            # الحفاظ على هيكل المجلدات
            directory_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
            file_path = base_path / parsed.netloc / directory_path / filename
        else:
            # حفظ مسطح
            file_path = base_path / filename
        
        # التعامل مع الملفات المكررة
        counter = 1
        original_path = file_path
        while file_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            file_path = original_path.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        
        return file_path
    
    def _determine_asset_type(self, asset_url: str, content_type: str) -> str:
        """تحديد نوع الأصل"""
        # من الامتداد
        parsed = urlparse(asset_url)
        extension = parsed.path.lower().split('.')[-1] if '.' in parsed.path else ''
        
        for asset_type, extensions in self.asset_folders.items():
            if extension in extensions:
                return asset_type
        
        # من content-type
        if content_type:
            if content_type.startswith('image/'):
                return 'images'
            elif content_type.startswith('text/css'):
                return 'stylesheets'
            elif content_type.startswith('application/javascript') or content_type.startswith('text/javascript'):
                return 'scripts'
            elif content_type.startswith('font/') or 'font' in content_type:
                return 'fonts'
            elif content_type.startswith('video/') or content_type.startswith('audio/'):
                return 'media'
            elif content_type.startswith('application/pdf'):
                return 'documents'
        
        return 'other'
    
    async def _optimize_assets(self):
        """تحسين الأصول المحملة"""
        logging.info("بدء تحسين الأصول...")
        
        optimization_tasks = []
        
        for asset_url, asset_info in self.asset_map.items():
            asset_type = asset_info.get('asset_type', '')
            local_path = Path(asset_info.get('local_path', ''))
            
            if not local_path.exists():
                continue
            
            # تحسين الصور
            if asset_type == 'images' and self.config.optimize_images:
                task = asyncio.create_task(self._optimize_image(local_path))
                optimization_tasks.append(task)
            
            # ضغط CSS
            elif asset_type == 'stylesheets' and self.config.minify_css:
                task = asyncio.create_task(self._minify_css(local_path))
                optimization_tasks.append(task)
            
            # ضغط JavaScript
            elif asset_type == 'scripts' and self.config.minify_js:
                task = asyncio.create_task(self._minify_js(local_path))
                optimization_tasks.append(task)
        
        # تنفيذ التحسينات بالتوازي
        if optimization_tasks:
            results = await asyncio.gather(*optimization_tasks, return_exceptions=True)
            successful_optimizations = sum(1 for r in results if r is True)
            self.download_stats['optimized_assets'] = successful_optimizations
    
    async def _optimize_image(self, image_path: Path) -> bool:
        """تحسين صورة"""
        try:
            if not image_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                return False
            
            # استخدام PIL لتحسين الصورة
            with Image.open(image_path) as img:
                # تحويل إلى RGB إذا كانت PNG مع شفافية
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # حفظ مع تحسين
                img.save(image_path, optimize=True, quality=85)
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في تحسين الصورة {image_path}: {e}")
            return False
    
    async def _minify_css(self, css_path: Path) -> bool:
        """ضغط ملف CSS"""
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # إزالة التعليقات والمساحات الزائدة
            css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
            css_content = re.sub(r'\s+', ' ', css_content)
            css_content = re.sub(r';\s*}', '}', css_content)
            css_content = re.sub(r'{\s*', '{', css_content)
            css_content = re.sub(r';\s*', ';', css_content)
            css_content = css_content.strip()
            
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في ضغط CSS {css_path}: {e}")
            return False
    
    async def _minify_js(self, js_path: Path) -> bool:
        """ضغط ملف JavaScript (أساسي)"""
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # إزالة التعليقات والمساحات الزائدة (أساسي)
            js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
            js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
            js_content = re.sub(r'\s+', ' ', js_content)
            js_content = js_content.strip()
            
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في ضغط JS {js_path}: {e}")
            return False
    
    async def _create_asset_map(self):
        """إنشاء خريطة الأصول"""
        asset_map_path = Path(self.config.output_directory) / 'asset_map.json'
        
        # إضافة إحصائيات إضافية
        enhanced_map = {
            'metadata': {
                'total_assets': len(self.asset_map),
                'download_date': datetime.now().isoformat(),
                'total_size_mb': self.download_stats['total_size_bytes'] / (1024 * 1024),
                'asset_types_count': self._count_asset_types()
            },
            'assets': self.asset_map,
            'failed_downloads': list(self.failed_downloads),
            'download_stats': self.download_stats
        }
        
        with open(asset_map_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_map, f, indent=2, ensure_ascii=False)
        
        logging.info(f"تم حفظ خريطة الأصول في: {asset_map_path}")
    
    def _count_asset_types(self) -> Dict[str, int]:
        """حساب عدد كل نوع من الأصول"""
        type_counts = {}
        for asset_info in self.asset_map.values():
            asset_type = asset_info.get('asset_type', 'other')
            type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
        return type_counts
    
    def _generate_download_report(self) -> Dict[str, Any]:
        """إنشاء تقرير التحميل النهائي"""
        duration = None
        if self.download_stats['start_time'] and self.download_stats['end_time']:
            duration = (self.download_stats['end_time'] - self.download_stats['start_time']).total_seconds()
        
        success_rate = 0
        if self.download_stats['total_assets'] > 0:
            success_rate = (self.download_stats['downloaded_successfully'] / self.download_stats['total_assets']) * 100
        
        return {
            'download_summary': {
                'total_assets_found': self.download_stats['total_assets'],
                'successfully_downloaded': self.download_stats['downloaded_successfully'],
                'failed_downloads': self.download_stats['failed_downloads'],
                'duplicate_assets_skipped': self.download_stats['duplicate_assets'],
                'optimized_assets': self.download_stats['optimized_assets'],
                'success_rate_percentage': round(success_rate, 2),
                'total_size_mb': round(self.download_stats['total_size_bytes'] / (1024 * 1024), 2),
                'download_duration_seconds': duration,
                'download_speed_mbps': round((self.download_stats['total_size_bytes'] / (1024 * 1024)) / max(duration, 1), 2) if duration else 0
            },
            
            'asset_breakdown': self._count_asset_types(),
            
            'file_organization': {
                'output_directory': self.config.output_directory,
                'organized_by_type': self.config.organize_by_type,
                'preserved_directory_structure': self.config.preserve_directory_structure,
                'asset_map_created': self.config.create_asset_map
            },
            
            'optimization_results': {
                'images_optimized': self.config.optimize_images,
                'css_minified': self.config.minify_css,
                'js_minified': self.config.minify_js,
                'total_optimized': self.download_stats['optimized_assets']
            },
            
            'failed_downloads': list(self.failed_downloads),
            'asset_map_location': str(Path(self.config.output_directory) / 'asset_map.json') if self.config.create_asset_map else None
        }