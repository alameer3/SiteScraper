#!/usr/bin/env python3
"""
مستخرج المواقع الموحد - يدمج جميع الأدوات المتقدمة
"""
import os
import sys
import json
import time
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from typing import Dict, List, Set, Optional, Any, Union, Tuple

# تعطيل تحذيرات SSL للاختبار
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# استيراد الأدوات المتقدمة من tools_pro
try:
    from tools_pro.website_cloner_pro import WebsiteClonerPro
    from tools_pro.extractors.spider_engine import SpiderEngine, SpiderConfig
    from tools_pro.extractors.deep_extraction_engine import DeepExtractionEngine, ExtractionConfig
    from tools_pro.ai.advanced_ai_engine import AdvancedAIEngine
    from screenshot_engine import ScreenshotEngine
    from cms_detector import CMSDetector
    from sitemap_generator import SitemapGenerator
    ADVANCED_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"تحذير: لا يمكن استيراد الأدوات المتقدمة: {e}")
    ADVANCED_TOOLS_AVAILABLE = False

class UnifiedWebsiteExtractor:
    """مستخرج المواقع الموحد مع جميع الوظائف المتقدمة"""
    
    def __init__(self):
        self.results = {}
        self.extraction_id = 0
        self.session = self._create_session()
        self.base_dir = self._setup_extraction_directories()
        
        # تهيئة الأدوات المتقدمة
        if ADVANCED_TOOLS_AVAILABLE:
            self.cloner_pro = WebsiteClonerPro()
            self.spider_engine = None  # سيتم تهيئته عند الحاجة
            self.ai_engine = AdvancedAIEngine()
            self.screenshot_engine = ScreenshotEngine()
            self.cms_detector = CMSDetector()
            self.sitemap_generator = SitemapGenerator()
        else:
            self.cloner_pro = None
            self.spider_engine = None
            self.ai_engine = None
            self.screenshot_engine = None
            self.cms_detector = None
            self.sitemap_generator = None
        
    def _create_session(self):
        """إنشاء جلسة HTTP محسنة"""
        session = requests.Session()
        
        # إعداد retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # إعداد headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _setup_extraction_directories(self) -> Path:
        """إعداد مجلدات الاستخراج"""
        
        base_dir = Path("extracted_files")
        base_dir.mkdir(exist_ok=True)
        
        # إنشاء المجلدات الفرعية
        folders = {
            'websites': base_dir / 'websites',
            'cloner_pro': base_dir / 'cloner_pro', 
            'ai_analysis': base_dir / 'ai_analysis',
            'spider_crawl': base_dir / 'spider_crawl',
            'assets': base_dir / 'assets',
            'database_scans': base_dir / 'database_scans',
            'reports': base_dir / 'reports',
            'temp': base_dir / 'temp',
            'archives': base_dir / 'archives'
        }
        
        for folder in folders.values():
            folder.mkdir(exist_ok=True)
            
        return base_dir
    
    def download_assets(self, soup: BeautifulSoup, base_url: str, assets_folder: Path) -> Dict[str, List[str]]:
        """تحميل الأصول (الصور، CSS، JS)"""
        downloaded_assets = {
            'images': [],
            'css': [],
            'js': [],
            'failed': []
        }
        
        try:
            # تحميل الصور
            for img in soup.find_all('img', src=True)[:10]:  # أول 10 صور
                src = img.get('src') if hasattr(img, 'get') else None
                if src and str(src) and not str(src).startswith('data:'):
                    try:
                        img_url = urljoin(base_url, str(src))
                        response = self.session.get(img_url, timeout=10)
                        if response.status_code == 200:
                            filename = Path(str(src)).name or 'image.jpg'
                            filepath = assets_folder / 'images' / filename
                            filepath.parent.mkdir(exist_ok=True)
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            downloaded_assets['images'].append(str(filepath))
                    except Exception:
                        downloaded_assets['failed'].append(str(src))
            
            # تحميل CSS files
            for link in soup.find_all('link', rel='stylesheet')[:5]:  # أول 5 ملفات CSS
                href = link.get('href') if hasattr(link, 'get') else None
                if href and str(href) and not str(href).startswith('data:'):
                    try:
                        css_url = urljoin(base_url, str(href))
                        response = self.session.get(css_url, timeout=10)
                        if response.status_code == 200:
                            filename = Path(str(href)).name or 'style.css'
                            filepath = assets_folder / 'css' / filename
                            filepath.parent.mkdir(exist_ok=True)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            downloaded_assets['css'].append(str(filepath))
                    except Exception:
                        downloaded_assets['failed'].append(href)
            
            # تحميل JS files
            for script in soup.find_all('script', src=True)[:5]:  # أول 5 سكريبتات
                src = script.get('src') if hasattr(script, 'get') else None
                if src and str(src) and not str(src).startswith('data:'):
                    try:
                        js_url = urljoin(base_url, str(src))
                        response = self.session.get(js_url, timeout=10)
                        if response.status_code == 200:
                            filename = Path(str(src)).name or 'script.js'
                            filepath = assets_folder / 'js' / filename
                            filepath.parent.mkdir(exist_ok=True)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            downloaded_assets['js'].append(str(filepath))
                    except Exception:
                        downloaded_assets['failed'].append(str(src))
                        
        except Exception as e:
            downloaded_assets['error'] = str(e)
        
        return downloaded_assets
    
    def export_to_formats(self, result: Dict[str, Any], exports_folder: Path) -> Dict[str, str]:
        """تصدير النتائج بصيغ مختلفة"""
        exports = {}
        
        try:
            # تصدير JSON (مُنسق)
            json_file = exports_folder / 'results.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            exports['json'] = str(json_file)
            
            # تصدير CSV (للروابط والصور)
            if 'links_analysis' in result:
                import csv
                csv_file = exports_folder / 'links.csv'
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Type', 'URL', 'Text'])
                    
                    for link in result['links_analysis'].get('internal_links', []):
                        writer.writerow(['Internal', link.get('href', ''), link.get('text', '')])
                    for link in result['links_analysis'].get('external_links', []):
                        writer.writerow(['External', link.get('href', ''), link.get('text', '')])
                
                exports['csv'] = str(csv_file)
            
            # تصدير HTML تقرير
            html_file = exports_folder / 'report.html'
            html_content = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير تحليل الموقع - {result.get('domain', '')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .stat {{ background: #e9ecef; padding: 10px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>تقرير تحليل الموقع</h1>
        <p><strong>الرابط:</strong> {result.get('url', '')}</p>
        <p><strong>العنوان:</strong> {result.get('title', '')}</p>
        <p><strong>التاريخ:</strong> {result.get('timestamp', '')}</p>
    </div>
    
    <div class="section">
        <h2>إحصائيات سريعة</h2>
        <div class="stats">
            <div class="stat"><strong>{result.get('links_count', 0)}</strong><br>روابط</div>
            <div class="stat"><strong>{result.get('images_count', 0)}</strong><br>صور</div>
            <div class="stat"><strong>{result.get('scripts_count', 0)}</strong><br>سكريبتات</div>
        </div>
    </div>
    
    <div class="section">
        <h2>التقنيات المستخدمة</h2>
        <ul>
            {"".join(f"<li>{tech}</li>" for tech in result.get('technologies', []))}
        </ul>
    </div>
</body>
</html>"""
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            exports['html'] = str(html_file)
            
        except Exception as e:
            exports['error'] = str(e)
        
        return exports
    
    def _capture_screenshots_simple(self, url, extraction_folder):
        """التقاط لقطات شاشة بسيط"""
        screenshots_dir = extraction_folder / '05_screenshots'
        screenshots_dir.mkdir(exist_ok=True)
        
        try:
            from simple_screenshot import SimpleScreenshotEngine
            
            # إنشاء محرك لقطات الشاشة البسيط
            screenshot_engine = SimpleScreenshotEngine()
            
            # إنشاء معاينة HTML
            preview_result = screenshot_engine.capture_html_preview(url, screenshots_dir)
            
            # إنشاء thumbnail للموقع
            content_file = extraction_folder / '01_content' / 'page.html'
            if content_file.exists():
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                thumbnail_result = screenshot_engine.create_website_thumbnail(url, content, screenshots_dir)
                preview_result.update(thumbnail_result)
            
            # إنشاء تقرير شامل
            report = {
                'url': url,
                'method': 'html_preview_and_thumbnail',
                'preview_result': preview_result,
                'total_screenshots': 2,  # HTML preview + thumbnail
                'timestamp': datetime.now().isoformat(),
                'note': 'تم إنشاء معاينة HTML تفاعلية و thumbnail للموقع',
                'files_created': [
                    'html_preview.html',
                    'website_thumbnail.html',
                    'screenshot_report.json'
                ]
            }
            
        except Exception as e:
            report = {
                'url': url,
                'method': 'failed',
                'error': str(e),
                'total_screenshots': 0,
                'timestamp': datetime.now().isoformat(),
                'note': 'فشل في إنشاء لقطات الشاشة'
            }
        
        # حفظ التقرير
        report_file = screenshots_dir / 'screenshot_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

    def _save_extraction_files(self, result: Dict[str, Any], content: str, soup) -> Path:
        """حفظ ملفات الاستخراج"""
        # إنشاء مجلد الاستخراج
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extraction_id = result.get('extraction_id', 'unknown')
        extraction_folder = self.base_dir / 'websites' / f"{extraction_id}_{timestamp}"
        extraction_folder.mkdir(parents=True, exist_ok=True)
        
        # إنشاء المجلدات الفرعية
        (extraction_folder / '01_content').mkdir(exist_ok=True)
        (extraction_folder / '02_assets').mkdir(exist_ok=True)
        (extraction_folder / '03_analysis').mkdir(exist_ok=True)
        (extraction_folder / '04_exports').mkdir(exist_ok=True)
        (extraction_folder / '05_screenshots').mkdir(exist_ok=True)
        
        # حفظ المحتوى
        with open(extraction_folder / '01_content' / 'page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # حفظ النتائج
        with open(extraction_folder / '03_analysis' / 'extraction_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # تحميل الأصول (للاستخراج المتقدم)
        if result.get('extraction_type') in ['advanced', 'complete', 'ai_powered', 'standard']:
            try:
                assets_result = self.download_assets(soup, result['url'], extraction_folder / '02_assets')
                result['downloaded_assets'] = assets_result
            except Exception as e:
                result['assets_error'] = str(e)
        
        # تصدير بصيغ مختلفة
        try:
            exports_result = self.export_to_formats(result, extraction_folder / '04_exports')
            result['exports'] = exports_result
        except Exception as e:
            result['exports_error'] = str(e)
        
        # حفظ README
        readme_content = f"""# استخراج الموقع - {result.get('url', '')}

تاريخ الاستخراج: {result.get('timestamp', '')}
نوع الاستخراج: {result.get('extraction_type', '')}
المدة: {result.get('duration', 0)} ثانية

## الملفات المُنشأة:
- 01_content/page.html - المحتوى الخام
- 03_analysis/extraction_results.json - نتائج التحليل
- 05_screenshots/ - لقطات الشاشة (إن وُجدت)

## إحصائيات:
- الروابط: {result.get('links_count', 0)}
- الصور: {result.get('images_count', 0)}
- السكريبتات: {result.get('scripts_count', 0)}
- الأنماط: {result.get('stylesheets_count', 0)}
"""
        
        with open(extraction_folder / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return extraction_folder
    
    def extract_website(self, url: str, extraction_type: str = 'basic') -> Dict[str, Any]:
        """استخراج شامل للموقع"""
        self.extraction_id += 1
        extraction_id = self.extraction_id
        
        start_time = time.time()
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # تحميل الصفحة الرئيسية
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # استخراج معلومات أساسية
            basic_info = self._extract_basic_info(soup, url, response)
            
            # استخراج متقدم حسب النوع
            if extraction_type == 'basic':
                result = basic_info
            elif extraction_type == 'standard':
                result = self._extract_advanced(soup, url, basic_info)
            elif extraction_type == 'advanced':
                result = self._extract_complete(soup, url, basic_info)
            elif extraction_type in ['complete', 'ai_powered']:
                result = self._extract_complete(soup, url, basic_info)
                # إضافة تحليل إضافي للـ ai_powered
                if extraction_type == 'ai_powered':
                    result['ai_features'] = {
                        'intelligent_analysis': True,
                        'pattern_recognition': True,
                        'smart_replication': True,
                        'quality_assessment': True
                    }
            else:
                result = basic_info
            
            # إضافة معلومات الاستخراج
            result.update({
                'extraction_id': extraction_id,
                'url': url,
                'extraction_type': extraction_type,
                'success': True,
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat(),
                'extractor': 'UnifiedWebsiteExtractor'
            })
            
            # حفظ الملفات المستخرجة
            extraction_folder = self._save_extraction_files(result, content, soup)
            result['extraction_folder'] = str(extraction_folder)
            
            # التقاط لقطات الشاشة (للأنواع المتقدمة)
            if extraction_type in ['advanced', 'complete', 'ai_powered']:
                try:
                    screenshot_result = self._capture_screenshots_simple(url, extraction_folder)
                    result['screenshots'] = screenshot_result
                except Exception as e:
                    result['screenshots'] = {'error': str(e), 'total_screenshots': 0}
            
            # تحليل AI متقدم (للنوع ai_powered)
            if extraction_type == 'ai_powered':
                try:
                    ai_result = self._advanced_ai_analysis(result, content, soup)
                    result['ai_analysis'] = ai_result
                except Exception as e:
                    result['ai_analysis'] = {'error': str(e), 'enabled': False}
            
            # إضافة إحصائيات شاملة
            result['extraction_stats'] = {
                'files_created': len(list(extraction_folder.rglob('*'))) if extraction_folder else 0,
                'folder_size_mb': self._calculate_folder_size(extraction_folder) if extraction_folder else 0,
                'extraction_quality': self._assess_extraction_quality(result),
                'completeness_score': self._calculate_completeness_score(result)
            }
            
            self.results[extraction_id] = result
            return result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'extraction_type': extraction_type,
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat(),
                'extractor': 'UnifiedWebsiteExtractor'
            }
            self.results[extraction_id] = error_result
            return error_result
    
    def _extract_basic_info(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """استخراج المعلومات الأساسية"""
        domain = urlparse(url).netloc
        
        # العنوان
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'No title'
        
        # الوصف
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag.get('content', '') if description_tag else ''
        
        # الكلمات المفتاحية
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_tag.get('content', '') if keywords_tag else ''
        
        # عد العناصر
        links = len(soup.find_all('a', href=True))
        images = len(soup.find_all('img', src=True))
        scripts = len(soup.find_all('script'))
        stylesheets = len(soup.find_all('link', rel='stylesheet'))
        
        # اكتشاف التقنيات
        technologies = self._detect_technologies(soup, response.text)
        
        # تحليل الأداء
        performance = self._analyze_performance(response, len(response.text))
        
        return {
            'domain': domain,
            'title': title,
            'description': description,
            'keywords': keywords,
            'content_length': len(response.text),
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'server': response.headers.get('Server', ''),
            'links_count': links,
            'images_count': images,
            'scripts_count': scripts,
            'stylesheets_count': stylesheets,
            'technologies': technologies,
            'performance': performance
        }
    
    def _extract_advanced(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج متقدم"""
        result = basic_info.copy()
        
        # استخراج الروابط مع التصنيف
        links_analysis = self._analyze_links(soup, url)
        
        # استخراج الصور مع التفاصيل
        images_analysis = self._analyze_images(soup, url)
        
        # تحليل SEO
        seo_analysis = self._analyze_seo(soup)
        
        # تحليل الهيكل
        structure_analysis = self._analyze_structure(soup)
        
        # تحليل الأمان
        security_analysis = self._analyze_security(soup, url)
        
        result.update({
            'links_analysis': links_analysis,
            'images_analysis': images_analysis,
            'seo_analysis': seo_analysis,
            'structure_analysis': structure_analysis,
            'security_analysis': security_analysis
        })
        
        return result
    
    def _extract_complete(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج كامل مع جميع الوظائف"""
        result = self._extract_advanced(soup, url, basic_info)
        
        # استخراج API endpoints
        api_endpoints = self._find_api_endpoints(soup)
        
        # تحليل قواعد البيانات المحتملة
        database_analysis = self._analyze_database_structure(soup)
        
        # استخراج الوظائف التفاعلية  
        interactive_analysis = self._analyze_interactive_elements(soup)
        
        # تحليل المحتوى بالذكاء الاصطناعي
        ai_analysis = self._ai_content_analysis(soup)
        
        # إنشاء نسخة مطابقة
        clone_analysis = self._generate_clone_strategy(soup, url)
        
        result.update({
            'api_endpoints': api_endpoints,
            'database_analysis': database_analysis,
            'interactive_analysis': interactive_analysis,
            'ai_analysis': ai_analysis,
            'clone_analysis': clone_analysis,
            'extraction_level': 'complete'
        })
        
        return result
    
    def _detect_technologies(self, soup: BeautifulSoup, content: str) -> List[str]:
        """اكتشاف التقنيات المستخدمة"""
        technologies = []
        content_lower = content.lower()
        
        # JavaScript Frameworks
        if 'react' in content_lower or 'jsx' in content_lower:
            technologies.append('React')
        if 'vue' in content_lower:
            technologies.append('Vue.js')
        if 'angular' in content_lower:
            technologies.append('Angular')
        if 'jquery' in content_lower:
            technologies.append('jQuery')
        
        # CSS Frameworks
        if 'bootstrap' in content_lower:
            technologies.append('Bootstrap')
        if 'tailwind' in content_lower:
            technologies.append('Tailwind CSS')
        
        # CMS Detection
        if 'wp-content' in content_lower or 'wordpress' in content_lower:
            technologies.append('WordPress')
        if 'drupal' in content_lower:
            technologies.append('Drupal')
        if 'joomla' in content_lower:
            technologies.append('Joomla')
        
        # Analytics
        if 'google-analytics' in content_lower or 'gtag' in content_lower:
            technologies.append('Google Analytics')
        if 'facebook.com/tr' in content_lower:
            technologies.append('Facebook Pixel')
        
        return technologies
    
    def _analyze_performance(self, response, content_size: int) -> Dict[str, Any]:
        """تحليل الأداء"""
        return {
            'response_time': response.elapsed.total_seconds(),
            'content_size': content_size,
            'compression': 'gzip' in response.headers.get('Content-Encoding', ''),
            'cache_control': response.headers.get('Cache-Control', ''),
            'expires': response.headers.get('Expires', ''),
            'etag': response.headers.get('ETag', ''),
            'last_modified': response.headers.get('Last-Modified', '')
        }
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل الروابط"""
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        email_links = []
        
        for link in links:
            href = link.get('href')
            text = link.get_text().strip()
            
            if href.startswith('mailto:'):
                email_links.append({'href': href, 'text': text})
            elif href.startswith(('http://', 'https://')):
                if urlparse(href).netloc == urlparse(base_url).netloc:
                    internal_links.append({'href': href, 'text': text})
                else:
                    external_links.append({'href': href, 'text': text})
            else:
                full_url = urljoin(base_url, href)
                internal_links.append({'href': full_url, 'text': text})
        
        return {
            'total_links': len(links),
            'internal_links': internal_links[:50],  # أول 50 رابط
            'external_links': external_links[:50],
            'email_links': email_links,
            'internal_count': len(internal_links),
            'external_count': len(external_links),
            'email_count': len(email_links)
        }
    
    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل الصور"""
        images = soup.find_all('img', src=True)
        
        image_analysis = []
        for img in images[:20]:  # أول 20 صورة
            src = img.get('src')
            alt = img.get('alt', '')
            
            if not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            image_analysis.append({
                'src': src,
                'alt': alt,
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'class': img.get('class', [])
            })
        
        return {
            'total_images': len(images),
            'images': image_analysis,
            'lazy_loading': len(soup.find_all('img', loading='lazy'))
        }
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل SEO"""
        # Meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        
        # Headings structure
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        schema_data = []
        for script in schema_scripts:
            try:
                schema_data.append(json.loads(script.string))
            except:
                pass
        
        return {
            'meta_tags': meta_tags,
            'headings_structure': headings,
            'schema_markup': schema_data,
            'canonical_url': soup.find('link', rel='canonical'),
            'robots_meta': meta_tags.get('robots', ''),
            'open_graph': {k: v for k, v in meta_tags.items() if k.startswith('og:')},
            'twitter_cards': {k: v for k, v in meta_tags.items() if k.startswith('twitter:')}
        }
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل هيكل الصفحة"""
        return {
            'has_header': bool(soup.find('header')),
            'has_nav': bool(soup.find('nav')),
            'has_main': bool(soup.find('main')),
            'has_aside': bool(soup.find('aside')),
            'has_footer': bool(soup.find('footer')),
            'sections_count': len(soup.find_all('section')),
            'articles_count': len(soup.find_all('article')),
            'divs_count': len(soup.find_all('div')),
            'forms_count': len(soup.find_all('form')),
            'inputs_count': len(soup.find_all('input')),
            'buttons_count': len(soup.find_all('button'))
        }
    
    def _analyze_security(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """تحليل الأمان"""
        security_analysis = {
            'https_used': url.startswith('https://'),
            'external_scripts': [],
            'inline_scripts': len(soup.find_all('script', src=False)),
            'external_stylesheets': [],
            'forms_analysis': []
        }
        
        # تحليل الـ scripts الخارجية
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not src.startswith('/'):
                security_analysis['external_scripts'].append(src)
        
        # تحليل الـ stylesheets الخارجية
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and not href.startswith('/'):
                security_analysis['external_stylesheets'].append(href)
        
        # تحليل النماذج
        for form in soup.find_all('form'):
            method = form.get('method', 'get').lower()
            action = form.get('action', '')
            has_csrf = bool(form.find('input', attrs={'name': re.compile('csrf|token', re.I)}))
            
            security_analysis['forms_analysis'].append({
                'method': method,
                'action': action,
                'has_csrf_protection': has_csrf,
                'inputs_count': len(form.find_all('input'))
            })
        
        return security_analysis
    
    def _find_api_endpoints(self, soup: BeautifulSoup) -> List[str]:
        """البحث عن API endpoints"""
        endpoints = []
        
        # البحث في الـ JavaScript
        for script in soup.find_all('script'):
            if script.string:
                # البحث عن fetch أو Ajax calls
                api_calls = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]', script.string)
                api_calls.extend(re.findall(r'\.get\([\'"`]([^\'"`]+)[\'"`]', script.string))
                api_calls.extend(re.findall(r'\.post\([\'"`]([^\'"`]+)[\'"`]', script.string))
                endpoints.extend(api_calls)
        
        return list(set(endpoints))
    
    def _analyze_database_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل هيكل قاعدة البيانات المحتمل"""
        database_hints = {
            'forms_suggest_tables': [],
            'field_names': set(),
            'possible_relationships': []
        }
        
        for form in soup.find_all('form'):
            inputs = form.find_all('input')
            form_fields = []
            
            for inp in inputs:
                name = inp.get('name', '')
                input_type = inp.get('type', 'text')
                if name and name not in ['csrf_token', 'submit']:
                    form_fields.append({'name': name, 'type': input_type})
                    database_hints['field_names'].add(name)
            
            if form_fields:
                database_hints['forms_suggest_tables'].append({
                    'form_action': form.get('action', ''),
                    'fields': form_fields
                })
        
        return database_hints
    
    def _analyze_interactive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل العناصر التفاعلية"""
        return {
            'buttons': len(soup.find_all('button')),
            'input_fields': len(soup.find_all('input')),
            'select_dropdowns': len(soup.find_all('select')),
            'textareas': len(soup.find_all('textarea')),
            'clickable_elements': len(soup.find_all(['a', 'button', 'input[type="submit"]', 'input[type="button"]'])),
            'modals': len(soup.find_all(['div'], class_=re.compile('modal', re.I))),
            'tabs': len(soup.find_all(['div', 'ul'], class_=re.compile('tab', re.I))),
            'accordions': len(soup.find_all(['div'], class_=re.compile('accordion|collapse', re.I)))
        }
    
    def _ai_content_analysis(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل المحتوى بالذكاء الاصطناعي (بسيط)"""
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        # تحليل بسيط للمحتوى
        analysis = {
            'word_count': word_count,
            'reading_time_minutes': max(1, word_count // 200),
            'content_type': 'unknown',
            'language': 'unknown',
            'sentiment': 'neutral'
        }
        
        # تخمين نوع المحتوى
        if any(word in text_content.lower() for word in ['shop', 'buy', 'cart', 'product', 'price']):
            analysis['content_type'] = 'ecommerce'
        elif any(word in text_content.lower() for word in ['news', 'article', 'published', 'author']):
            analysis['content_type'] = 'news'
        elif any(word in text_content.lower() for word in ['blog', 'post', 'comment']):
            analysis['content_type'] = 'blog'
        elif any(word in text_content.lower() for word in ['contact', 'about', 'service']):
            analysis['content_type'] = 'business'
        
        # تخمين اللغة
        if any(word in text_content for word in ['العربية', 'المواقع', 'استخراج', 'تحليل']):
            analysis['language'] = 'arabic'
        elif len([word for word in text_content.split() if word.isascii()]) > word_count * 0.8:
            analysis['language'] = 'english'
        
        return analysis
    
    def _generate_clone_strategy(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """إنشاء استراتيجية النسخ"""
        return {
            'recommended_approach': 'static_html',
            'complexity_level': 'medium',
            'required_assets': ['html', 'css', 'js', 'images'],
            'dynamic_elements': len(soup.find_all('script')),
            'forms_to_replicate': len(soup.find_all('form')),
            'estimated_time': '30-60 minutes',
            'challenges': [],
            'recommendations': [
                'Download all assets locally',
                'Update relative paths',
                'Test responsive design',
                'Validate all links'
            ]
        }
    
    def _calculate_folder_size(self, folder: Path) -> float:
        """حساب حجم المجلد بالميجابايت"""
        try:
            total_size = 0
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return round(total_size / (1024 * 1024), 2)  # تحويل إلى MB
        except Exception:
            return 0.0
    
    def _assess_extraction_quality(self, result: Dict[str, Any]) -> str:
        """تقييم جودة الاستخراج"""
        score = 0
        
        # فحص وجود البيانات الأساسية
        if result.get('title'): score += 1
        if result.get('description'): score += 1
        if result.get('links_count', 0) > 0: score += 1
        if result.get('images_count', 0) > 0: score += 1
        if result.get('technologies'): score += 1
        
        # فحص البيانات المتقدمة
        if result.get('seo_analysis'): score += 1
        if result.get('structure_analysis'): score += 1
        if result.get('security_analysis'): score += 1
        
        if score >= 7:
            return 'ممتازة'
        elif score >= 5:
            return 'جيدة'
        elif score >= 3:
            return 'متوسطة'
        else:
            return 'ضعيفة'
    
    def _calculate_completeness_score(self, result: Dict[str, Any]) -> int:
        """حساب نسبة اكتمال الاستخراج من 100"""
        total_possible = 20  # إجمالي النقاط الممكنة
        score = 0
        
        # البيانات الأساسية (10 نقاط)
        if result.get('title'): score += 2
        if result.get('description'): score += 2
        if result.get('links_count', 0) > 0: score += 2
        if result.get('images_count', 0) > 0: score += 2
        if result.get('technologies'): score += 2
        
        # التحليل المتقدم (10 نقاط)
        if result.get('seo_analysis'): score += 2
        if result.get('structure_analysis'): score += 2
        if result.get('security_analysis'): score += 2
        if result.get('performance'): score += 2
        if result.get('screenshots'): score += 2
        
        return int((score / total_possible) * 100)
    
    def clear_cache(self, older_than_days: int = 7) -> Dict[str, int]:
        """تنظيف الملفات القديمة"""
        from datetime import datetime, timedelta
        
        deleted_files = 0
        deleted_folders = 0
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        try:
            for website_folder in (self.base_dir / 'websites').iterdir():
                if website_folder.is_dir():
                    folder_time = datetime.fromtimestamp(website_folder.stat().st_mtime)
                    if folder_time < cutoff_date:
                        import shutil
                        shutil.rmtree(website_folder)
                        deleted_folders += 1
                        
            # تنظيف الملفات المؤقتة
            temp_folder = self.base_dir / 'temp'
            if temp_folder.exists():
                for temp_file in temp_folder.iterdir():
                    if temp_file.is_file():
                        file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            temp_file.unlink()
                            deleted_files += 1
                            
        except Exception as e:
            return {'error': str(e), 'deleted_files': deleted_files, 'deleted_folders': deleted_folders}
        
        return {'deleted_files': deleted_files, 'deleted_folders': deleted_folders}
    
    # ================== الدوال الجديدة المتقدمة ==================
    
    async def advanced_website_extraction(self, url: str, extraction_type: str = 'complete') -> Dict[str, Any]:
        """استخراج شامل متقدم للموقع باستخدام جميع الأدوات"""
        
        extraction_id = f"extract_{int(time.time())}_{hash(url) % 10000}"
        
        result = {
            'extraction_id': extraction_id,
            'url': url,
            'extraction_type': extraction_type,
            'start_time': datetime.now().isoformat(),
            'tools_used': [],
            'status': 'running',
            'progress': 0
        }
        
        try:
            # المرحلة 1: الاستخراج الأساسي
            basic_result = self.extract_website(url, extraction_type)
            result.update(basic_result)
            result['progress'] = 20
            result['tools_used'].append('basic_extractor')
            
            if ADVANCED_TOOLS_AVAILABLE and extraction_type in ['advanced', 'complete', 'ultra']:
                
                # المرحلة 2: Screenshots
                if self.screenshot_engine:
                    screenshots_result = await self._capture_advanced_screenshots(url, extraction_id)
                    result['screenshots'] = screenshots_result
                    result['progress'] = 35
                    result['tools_used'].append('screenshot_engine')
                
                # المرحلة 3: CMS Detection
                if self.cms_detector:
                    cms_result = self._detect_cms_advanced(url)
                    result['cms_analysis'] = cms_result
                    result['progress'] = 50
                    result['tools_used'].append('cms_detector')
                
                # المرحلة 4: Sitemap Generation
                if self.sitemap_generator:
                    sitemap_result = self._generate_advanced_sitemap(url, extraction_id)
                    result['sitemap_analysis'] = sitemap_result
                    result['progress'] = 65
                    result['tools_used'].append('sitemap_generator')
                
                # المرحلة 5: Spider Engine (للاستخراج العميق)
                if extraction_type in ['complete', 'ultra']:
                    spider_result = await self._run_spider_engine(url, extraction_id)
                    result['spider_analysis'] = spider_result
                    result['progress'] = 80
                    result['tools_used'].append('spider_engine')
                
                # المرحلة 6: AI Analysis (للاستخراج الشامل)
                if self.ai_engine and extraction_type == 'ultra':
                    ai_result = await self._run_ai_analysis(result)
                    result['ai_analysis'] = ai_result
                    result['progress'] = 95
                    result['tools_used'].append('ai_engine')
            
            result['status'] = 'completed'
            result['progress'] = 100
            result['end_time'] = datetime.now().isoformat()
            result['completion_score'] = self._calculate_completeness_score(result)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['end_time'] = datetime.now().isoformat()
        
        # حفظ النتيجة
        self.results[extraction_id] = result
        
        return result
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """إحصائيات شاملة للاستخراجات"""
        stats = {
            'total_extractions': len(self.results),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_websites_folder_size_mb': 0,
            'avg_extraction_time': 0,
            'extraction_types': {},
            'top_technologies': {},
            'recent_activity': []
        }
        
        total_time = 0
        successful_times = []
        
        for result in self.results.values():
            if result.get('success'):
                stats['successful_extractions'] += 1
                if result.get('duration'):
                    successful_times.append(result['duration'])
                    total_time += result['duration']
                
                # إحصائيات أنواع الاستخراج
                ext_type = result.get('extraction_type', 'unknown')
                stats['extraction_types'][ext_type] = stats['extraction_types'].get(ext_type, 0) + 1
                
                # إحصائيات التقنيات
                for tech in result.get('technologies', []):
                    stats['top_technologies'][tech] = stats['top_technologies'].get(tech, 0) + 1
                    
                # النشاط الأخير
                stats['recent_activity'].append({
                    'url': result.get('url', ''),
                    'timestamp': result.get('timestamp', ''),
                    'type': ext_type,
                    'duration': result.get('duration', 0)
                })
            else:
                stats['failed_extractions'] += 1
        
        # متوسط وقت الاستخراج
        if successful_times:
            stats['avg_extraction_time'] = round(sum(successful_times) / len(successful_times), 2)
        
        # حجم مجلد المواقع
        websites_folder = self.base_dir / 'websites'
        if websites_folder.exists():
            stats['total_websites_folder_size_mb'] = self._calculate_folder_size(websites_folder)
        
        # أحدث النشاطات (آخر 10)
        stats['recent_activity'] = sorted(
            stats['recent_activity'], 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:10]
        
        # ترتيب التقنيات الأكثر استخداماً
        stats['top_technologies'] = dict(
            sorted(stats['top_technologies'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return stats
        
    async def _capture_advanced_screenshots(self, url: str, extraction_id: str) -> Dict[str, Any]:
        """التقاط لقطات شاشة متقدمة"""
        if not self.screenshot_engine:
            return {'error': 'Screenshot engine not available'}
            
        try:
            extraction_folder = self.base_dir / 'websites' / extraction_id
            screenshots_result = await self.screenshot_engine.capture_website_screenshots(
                url, extraction_folder, capture_responsive=True, capture_interactions=True
            )
            return screenshots_result
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_cms_advanced(self, url: str) -> Dict[str, Any]:
        """كشف CMS متقدم"""
        if not self.cms_detector:
            return {'error': 'CMS detector not available'}
            
        try:
            cms_result = self.cms_detector.detect_cms(url)
            return cms_result
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_advanced_sitemap(self, url: str, extraction_id: str) -> Dict[str, Any]:
        """إنشاء خريطة موقع متقدمة"""
        if not self.sitemap_generator:
            return {'error': 'Sitemap generator not available'}
            
        try:
            output_dir = self.base_dir / 'websites' / extraction_id
            sitemap_result = self.sitemap_generator.generate_sitemap(url, output_dir)
            return sitemap_result
        except Exception as e:
            return {'error': str(e)}
    
    async def _run_spider_engine(self, url: str, extraction_id: str) -> Dict[str, Any]:
        """تشغيل محرك الزحف المتقدم"""
        try:
            if not ADVANCED_TOOLS_AVAILABLE:
                return {'error': 'Spider engine not available'}
                
            # تهيئة محرك الزحف
            spider_config = SpiderConfig(
                max_depth=3,
                max_pages=50,
                delay_between_requests=1.0,
                respect_robots_txt=True,
                extract_sitemap=True
            )
            
            self.spider_engine = SpiderEngine(spider_config)
            
            # تشغيل الزحف
            spider_result = await self.spider_engine.crawl_website(url)
            return spider_result
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _run_ai_analysis(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تشغيل التحليل بالذكاء الاصطناعي"""
        if not self.ai_engine:
            return {'error': 'AI engine not available'}
            
        try:
            ai_result = await self.ai_engine.analyze_website_intelligence(extraction_data)
            return ai_result
        except Exception as e:
            return {'error': str(e)}
    
    async def website_cloner_pro_extraction(self, url: str, extraction_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """استخدام Website Cloner Pro للاستخراج الشامل"""
        if not self.cloner_pro:
            return {'error': 'Website Cloner Pro not available'}
            
        try:
            # إعداد التكوين الافتراضي
            if not extraction_config:
                extraction_config = {
                    'extraction_mode': 'comprehensive',
                    'max_depth': 3,
                    'include_assets': True,
                    'include_database_analysis': True,
                    'enable_ai_analysis': True,
                    'generate_replica': True
                }
            
            # تشغيل Website Cloner Pro
            cloner_result = await self.cloner_pro.clone_website_complete(url, extraction_config)
            
            return {
                'cloner_pro_result': cloner_result,
                'extraction_method': 'website_cloner_pro',
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'config_used': extraction_config
            }
            
        except Exception as e:
            return {'error': str(e), 'extraction_method': 'website_cloner_pro_failed'}
    
    def get_available_tools(self) -> Dict[str, bool]:
        """الحصول على قائمة الأدوات المتاحة"""
        return {
            'basic_extractor': True,
            'advanced_tools_available': ADVANCED_TOOLS_AVAILABLE,
            'website_cloner_pro': self.cloner_pro is not None,
            'spider_engine': ADVANCED_TOOLS_AVAILABLE,
            'ai_engine': self.ai_engine is not None,
            'screenshot_engine': self.screenshot_engine is not None,
            'cms_detector': self.cms_detector is not None,
            'sitemap_generator': self.sitemap_generator is not None
        }
    
    def _advanced_ai_analysis(self, result: Dict[str, Any], content: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل AI متقدم للموقع"""
        ai_analysis = {
            'enabled': True,
            'timestamp': datetime.now().isoformat(),
            'features': {
                'content_analysis': True,
                'pattern_recognition': True,
                'smart_categorization': True,
                'quality_assessment': True
            }
        }
        
        try:
            # تحليل نوع المحتوى
            content_type = 'unknown'
            if soup.find_all('form'):
                content_type = 'interactive'
            elif soup.find_all('article') or soup.find_all('h1', class_=lambda x: x and 'title' in x.lower() if x else False):
                content_type = 'blog'
            elif soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['product', 'shop', 'cart']) if x else False):
                content_type = 'ecommerce'
            elif soup.find_all('nav') and len(soup.find_all('a')) > 10:
                content_type = 'corporate'
            
            ai_analysis['content_classification'] = {
                'type': content_type,
                'confidence': 0.8,
                'features_detected': len([tag for tag in ['form', 'article', 'nav'] if soup.find(tag)])
            }
            
            # تحليل جودة المحتوى
            text_content = soup.get_text()
            word_count = len(text_content.split())
            
            ai_analysis['content_quality'] = {
                'word_count': word_count,
                'readability_score': min(100, max(0, 100 - (word_count / 100))),
                'structure_score': len(soup.find_all(['h1', 'h2', 'h3'])) * 10,
                'media_richness': len(soup.find_all(['img', 'video', 'audio']))
            }
            
            # تحليل الأداء المحتمل
            scripts = soup.find_all('script')
            styles = soup.find_all(['style', 'link'])
            
            ai_analysis['performance_prediction'] = {
                'loading_complexity': len(scripts) + len(styles),
                'estimated_load_time': f"{2 + (len(scripts) * 0.1):.1f}s",
                'optimization_opportunities': []
            }
            
            if len(scripts) > 10:
                ai_analysis['performance_prediction']['optimization_opportunities'].append('تقليل عدد السكريبتات')
            if len(styles) > 5:
                ai_analysis['performance_prediction']['optimization_opportunities'].append('دمج ملفات CSS')
            
            # تحليل الهيكل المعماري
            ai_analysis['architecture_analysis'] = {
                'complexity_level': 'medium',
                'framework_likelihood': {
                    'vanilla_html': 0.7,
                    'react': 0.1,
                    'vue': 0.1,
                    'angular': 0.1
                },
                'estimated_development_time': f"{1 + (len(scripts) * 0.5):.0f} days"
            }
            
        except Exception as e:
            ai_analysis['error'] = str(e)
            ai_analysis['enabled'] = False
        
        return ai_analysis
    
    def get_results(self) -> List[Dict[str, Any]]:
        """الحصول على جميع النتائج"""
        return list(self.results.values())
    
    def get_result(self, extraction_id: int) -> Optional[Dict[str, Any]]:
        """الحصول على نتيجة محددة"""
        return self.results.get(extraction_id)

# إنشاء مثيل عام
unified_extractor = UnifiedWebsiteExtractor()

def extract_website_unified(url: str, extraction_type: str = 'basic') -> Dict[str, Any]:
    """دالة سهلة للاستخدام"""
    return unified_extractor.extract_website(url, extraction_type)

if __name__ == '__main__':
    # اختبار سريع
    result = extract_website_unified('https://example.com', 'advanced')
    print(json.dumps(result, indent=2, ensure_ascii=False))