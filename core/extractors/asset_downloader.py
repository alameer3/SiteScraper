"""
Asset Downloader - تحميل جميع الموارد والملفات
المرحلة الأولى: محرك الاستخراج العميق
"""

import asyncio
import aiohttp
import aiofiles
import os
import logging
import hashlib
import mimetypes
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse
from pathlib import Path
from dataclasses import dataclass
import time

@dataclass
class AssetDownloadConfig:
    """تكوين تحميل الأصول"""
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    timeout: int = 30
    max_concurrent_downloads: int = 10
    save_directory: str = "downloaded_assets"
    organize_by_type: bool = True
    verify_checksums: bool = True
    allowed_extensions: Optional[Set[str]] = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {
                '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.webp', 
                '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot',
                '.mp4', '.mp3', '.wav', '.pdf', '.zip'
            }

class AssetDownloader:
    """محمل الأصول والملفات"""
    
    def __init__(self, config: Optional[AssetDownloadConfig] = None):
        self.config = config or AssetDownloadConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.downloaded_assets: Dict[str, str] = {}
        self.failed_downloads: Set[str] = set()
        self.download_stats = {
            'total_size': 0,
            'files_downloaded': 0,
            'files_failed': 0,
            'start_time': 0,
            'end_time': 0
        }
        
        # إعداد مجلد التحميل
        self.base_path = Path(self.config.save_directory)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """دخول Context Manager"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """خروج Context Manager"""
        if self.session:
            await self.session.close()
    
    async def download_all_assets(self, asset_urls: List[str], base_url: str) -> Dict[str, Any]:
        """تحميل جميع الأصول"""
        self.download_stats['start_time'] = time.time()
        self.logger.info(f"بدء تحميل {len(asset_urls)} أصل...")
        
        # تنظيم الروابط
        organized_urls = self._organize_asset_urls(asset_urls, base_url)
        
        # تحميل متوازي
        download_tasks = []
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        
        for asset_url in organized_urls:
            task = self._download_single_asset(semaphore, asset_url, base_url)
            download_tasks.append(task)
        
        # انتظار اكتمال جميع التحميلات
        results = await asyncio.gather(*download_tasks, return_exceptions=True)
        
        self.download_stats['end_time'] = time.time()
        
        return {
            'downloaded_assets': self.downloaded_assets,
            'failed_downloads': list(self.failed_downloads),
            'statistics': self.download_stats,
            'organized_structure': self._get_organized_structure()
        }
    
    def _organize_asset_urls(self, asset_urls: List[str], base_url: str) -> List[str]:
        """تنظيم روابط الأصول"""
        organized = []
        seen = set()
        
        for url in asset_urls:
            # تحويل الروابط النسبية إلى مطلقة
            full_url = urljoin(base_url, url)
            
            if full_url not in seen:
                # التحقق من الامتداد
                parsed = urlparse(full_url)
                path_lower = parsed.path.lower()
                
                # التحقق من الامتدادات المسموحة
                if any(path_lower.endswith(ext) for ext in self.config.allowed_extensions):
                    organized.append(full_url)
                    seen.add(full_url)
        
        return organized
    
    async def _download_single_asset(self, semaphore: asyncio.Semaphore, 
                                   asset_url: str, base_url: str) -> Optional[str]:
        """تحميل أصل واحد"""
        async with semaphore:
            try:
                async with self.session.get(asset_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # التحقق من حجم الملف
                        if len(content) > self.config.max_file_size:
                            self.logger.warning(f"ملف كبير جداً: {asset_url}")
                            return None
                        
                        # حفظ الملف
                        saved_path = await self._save_asset(asset_url, content)
                        if saved_path:
                            self.downloaded_assets[asset_url] = saved_path
                            self.download_stats['files_downloaded'] += 1
                            self.download_stats['total_size'] += len(content)
                            return saved_path
                    
                    else:
                        self.logger.warning(f"فشل تحميل {asset_url}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"خطأ في تحميل {asset_url}: {e}")
                self.failed_downloads.add(asset_url)
                self.download_stats['files_failed'] += 1
            
            return None
    
    async def _save_asset(self, asset_url: str, content: bytes) -> Optional[str]:
        """حفظ الأصل في النظام"""
        try:
            # تحديد نوع الملف
            parsed = urlparse(asset_url)
            filename = os.path.basename(parsed.path) or 'index.html'
            
            # تنظيم حسب النوع
            if self.config.organize_by_type:
                file_type = self._get_file_type(filename)
                save_path = self.base_path / file_type / filename
            else:
                save_path = self.base_path / filename
            
            # إنشاء المجلدات إذا لم تكن موجودة
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # التعامل مع الأسماء المكررة
            counter = 1
            original_path = save_path
            while save_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                save_path = original_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # حفظ الملف
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(content)
            
            self.logger.debug(f"تم حفظ: {save_path}")
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"خطأ في حفظ {asset_url}: {e}")
            return None
    
    def _get_file_type(self, filename: str) -> str:
        """تحديد نوع الملف للتنظيم"""
        ext = Path(filename).suffix.lower()
        
        type_mapping = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'],
            'styles': ['.css'],
            'scripts': ['.js'],
            'fonts': ['.woff', '.woff2', '.ttf', '.eot'],
            'media': ['.mp4', '.mp3', '.wav'],
            'documents': ['.pdf', '.zip', '.txt']
        }
        
        for file_type, extensions in type_mapping.items():
            if ext in extensions:
                return file_type
        
        return 'other'
    
    def _get_organized_structure(self) -> Dict[str, Any]:
        """الحصول على بنية الملفات المنظمة"""
        structure = {}
        
        for url, path in self.downloaded_assets.items():
            file_path = Path(path)
            file_type = file_path.parent.name
            
            if file_type not in structure:
                structure[file_type] = {
                    'files': [],
                    'count': 0,
                    'total_size': 0
                }
            
            file_size = file_path.stat().st_size if file_path.exists() else 0
            structure[file_type]['files'].append({
                'name': file_path.name,
                'path': str(file_path),
                'url': url,
                'size': file_size
            })
            structure[file_type]['count'] += 1
            structure[file_type]['total_size'] += file_size
        
        return structure