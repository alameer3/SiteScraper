"""
مستخرج رئيسي شامل - Master Website Extractor
يدمج جميع أدوات الاستخراج في نظام واحد متطور ومرن
"""

import os
import re
import json
import requests
import time
import hashlib
import mimetypes
import threading
import shutil
import zipfile
import base64
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# تكوين المسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtractionMode(Enum):
    """أنماط الاستخراج المختلفة"""
    BASIC = "basic"           # استخراج أساسي للمحتوى
    STANDARD = "standard"     # استخراج عادي مع الأصول الرئيسية
    ADVANCED = "advanced"     # استخراج متقدم مع جميع الملفات
    ULTRA = "ultra"          # استخراج فائق مع ذكاء اصطناعي
    SECURE = "secure"        # استخراج آمن مع ضوابط صارمة

class PermissionLevel(Enum):
    """مستويات الأذونات"""
    READ_ONLY = "read_only"
    DOWNLOAD_ASSETS = "download_assets"
    MODIFY_CONTENT = "modify_content"
    FULL_ACCESS = "full_access"

@dataclass
class ExtractionConfig:
    """إعدادات الاستخراج الشاملة"""
    url: str
    mode: ExtractionMode = ExtractionMode.STANDARD
    permission_level: PermissionLevel = PermissionLevel.DOWNLOAD_ASSETS
    max_pages: int = 50
    max_depth: int = 3
    max_threads: int = 5
    timeout: int = 30
    delay_between_requests: float = 1.0
    extract_images: bool = True
    extract_css: bool = True
    extract_js: bool = True
    extract_fonts: bool = True
    extract_videos: bool = False
    extract_documents: bool = False
    remove_ads: bool = True
    respect_robots_txt: bool = True
    output_directory: str = "extracted_websites"
    compress_output: bool = False
    generate_preview: bool = True
    user_agent: str = "Mozilla/5.0 (Website-Analyzer-Tool) Respectful-Crawler/1.0"

class MasterExtractor:
    """مستخرج رئيسي يدمج جميع قدرات الاستخراج"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.base_url = config.url
        self.domain = urlparse(config.url).netloc
        
        # إعداد المجلدات
        self.output_dir = Path(config.output_directory)
        self.site_id = self._generate_site_id()
        self.site_dir = self.output_dir / self.site_id
        self._setup_directories()
        
        # إعداد الجلسة
        self.session = requests.Session()
        self._setup_session()
        
        # إحصائيات شاملة
        self.stats = self._init_stats()
        
        # مجموعات البيانات
        self.visited_urls = set()
        self.failed_urls = set()
        self.external_urls = set()
        self.downloaded_files = set()
        self.page_metadata = {}
        
        # أنواع الملفات
        self.file_extensions = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico'},
            'videos': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'},
            'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'},
            'documents': {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'},
            'fonts': {'.woff', '.woff2', '.ttf', '.otf', '.eot'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'}
        }
        
        # تهيئة نظام حجب الإعلانات إذا كان مطلوباً
        if config.remove_ads:
            self._init_ad_blocker()

    def _generate_site_id(self) -> str:
        """إنشاء معرف فريد للموقع"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_hash = hashlib.md5(f"{self.base_url}_{time.time()}".encode()).hexdigest()[:8]
        domain_clean = re.sub(r'[^\w\-_]', '_', self.domain)
        return f"{domain_clean}_{timestamp}_{site_hash}"

    def _setup_directories(self):
        """إعداد هيكل المجلدات"""
        directories = [
            self.site_dir,
            self.site_dir / 'pages',
            self.site_dir / 'assets' / 'images',
            self.site_dir / 'assets' / 'css',
            self.site_dir / 'assets' / 'js',
            self.site_dir / 'assets' / 'fonts',
            self.site_dir / 'assets' / 'videos',
            self.site_dir / 'assets' / 'audio',
            self.site_dir / 'assets' / 'documents',
            self.site_dir / 'content',
            self.site_dir / 'data',
            self.site_dir / 'metadata',
            self.site_dir / 'reports'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"تم إنشاء مجلدات الإخراج في: {self.site_dir}")

    def _setup_session(self):
        """إعداد جلسة HTTP متقدمة"""
        headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(headers)
        
        # إعداد إعادة المحاولة
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _init_stats(self) -> Dict[str, Any]:
        """تهيئة الإحصائيات"""
        return {
            'extraction_start': datetime.now().isoformat(),
            'extraction_end': None,
            'mode': self.config.mode.value,
            'permission_level': self.config.permission_level.value,
            'pages_discovered': 0,
            'pages_extracted': 0,
            'pages_failed': 0,
            'assets_downloaded': {
                'images': 0,
                'css': 0,
                'js': 0,
                'fonts': 0,
                'videos': 0,
                'audio': 0,
                'documents': 0,
                'other': 0
            },
            'total_size_bytes': 0,
            'total_size_mb': 0,
            'processing_time_seconds': 0,
            'errors': [],
            'warnings': [],
            'technologies_detected': [],
            'security_issues': [],
            'performance_metrics': {},
            'ads_removed': 0,
            'tracking_removed': 0
        }

    def _init_ad_blocker(self):
        """تهيئة نظام حجب الإعلانات"""
        self.ad_selectors = [
            '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
            '[class*="banner"]', '[class*="popup"]', '[class*="modal"]',
            '.google-ads', '.adsense', '[class*="promo"]',
            '[data-ad]', '[data-google-ad]', '[class*="sponsor"]',
            '[class*="sidebar-ad"]', '[class*="header-ad"]'
        ]
        
        self.tracking_domains = {
            'google-analytics.com', 'googletagmanager.com', 'facebook.com',
            'doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com',
            'adsystem.amazon.com', 'googleadservices.com', 'hotjar.com',
            'mixpanel.com', 'segment.com', 'amplitude.com'
        }

    def extract_website(self) -> Dict[str, Any]:
        """نقطة الدخول الرئيسية للاستخراج"""
        start_time = time.time()
        self.stats['extraction_start'] = datetime.now().isoformat()
        
        try:
            logger.info(f"بدء استخراج الموقع: {self.base_url}")
            logger.info(f"نمط الاستخراج: {self.config.mode.value}")
            
            # اختيار طريقة الاستخراج حسب النمط
            if self.config.mode == ExtractionMode.BASIC:
                result = self._extract_basic()
            elif self.config.mode == ExtractionMode.STANDARD:
                result = self._extract_standard()
            elif self.config.mode == ExtractionMode.ADVANCED:
                result = self._extract_advanced()
            elif self.config.mode == ExtractionMode.ULTRA:
                result = self._extract_ultra()
            elif self.config.mode == ExtractionMode.SECURE:
                result = self._extract_secure()
            else:
                result = self._extract_standard()
            
            # إنهاء المعالجة
            end_time = time.time()
            self.stats['processing_time_seconds'] = round(end_time - start_time, 2)
            self.stats['extraction_end'] = datetime.now().isoformat()
            self.stats['total_size_mb'] = round(self.stats['total_size_bytes'] / (1024 * 1024), 2)
            
            # حفظ التقارير
            self._save_extraction_report()
            
            # ضغط الملفات إذا كان مطلوباً
            if self.config.compress_output:
                self._compress_output()
            
            result.update({
                'success': True,
                'site_id': self.site_id,
                'output_directory': str(self.site_dir),
                'stats': self.stats
            })
            
            logger.info(f"اكتمل الاستخراج بنجاح في {self.stats['processing_time_seconds']} ثانية")
            return result
            
        except Exception as e:
            logger.error(f"خطأ في الاستخراج: {e}")
            self.stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }

    # ================ ExtractionEngine المدمج ================
    
class ExtractionEngine:
    """محرك الاستخراج الشامل المدمج"""
    
    def __init__(self, output_directory: str = "extractions"):
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(exist_ok=True)
        
        # قائمة الوظائف والحالات
        self.jobs: Dict[str, Any] = {}
        self.active_jobs: Dict[str, threading.Thread] = {}
        self.job_counter = 0
        
        # إحصائيات النظام
        self.system_stats = {
            'total_jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'jobs_running': 0,
            'jobs_pending': 0,
            'average_completion_time': 0.0,
        }
        
        logger.info("تم تهيئة محرك الاستخراج الشامل")

    def create_extraction_job(self, url: str, extraction_type: str = "content", 
                            priority: int = 2, config: Dict[str, Any] = None) -> str:
        """إنشاء وظيفة استخراج جديدة"""
        self.job_counter += 1
        job_id = f"job_{self.job_counter}_{int(time.time())}"
        
        job = {
            'job_id': job_id,
            'url': url,
            'extraction_type': extraction_type,
            'priority': priority,
            'config': config or {},
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'progress': 0.0,
            'result': None,
            'error': None
        }
        
        self.jobs[job_id] = job
        self.system_stats['total_jobs_created'] += 1
        self.system_stats['jobs_pending'] += 1
        
        logger.info(f"تم إنشاء وظيفة استخراج: {job_id} للرابط: {url}")
        return job_id
    
    def start_extraction_job(self, job_id: str) -> bool:
        """بدء تنفيذ وظيفة الاستخراج"""
        if job_id not in self.jobs:
            logger.error(f"الوظيفة غير موجودة: {job_id}")
            return False
        
        job = self.jobs[job_id]
        if job['status'] != 'pending':
            logger.warning(f"الوظيفة {job_id} ليست في حالة انتظار")
            return False
        
        # بدء الوظيفة في خيط منفصل
        thread = threading.Thread(target=self._execute_job, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        self.active_jobs[job_id] = thread
        job['status'] = 'running'
        job['started_at'] = datetime.now().isoformat()
        
        self.system_stats['jobs_pending'] -= 1
        self.system_stats['jobs_running'] += 1
        
        logger.info(f"تم بدء تنفيذ الوظيفة: {job_id}")
        return True
    
    def _execute_job(self, job_id: str):
        """تنفيذ وظيفة الاستخراج"""
        job = self.jobs[job_id]
        
        try:
            # إنشاء مستخرج للوظيفة
            config = ExtractionConfig()
            extractor = MasterExtractor(job['url'], config)
            
            # تحديث التقدم
            job['progress'] = 0.25
            
            # تنفيذ الاستخراج
            result = extractor.extract_website()
            
            # تحديث النتائج
            job['result'] = result
            job['status'] = 'completed'
            job['progress'] = 1.0
            job['completed_at'] = datetime.now().isoformat()
            
            self.system_stats['jobs_running'] -= 1
            self.system_stats['jobs_completed'] += 1
            
            logger.info(f"اكتملت الوظيفة بنجاح: {job_id}")
            
        except Exception as e:
            job['error'] = str(e)
            job['status'] = 'failed'
            job['completed_at'] = datetime.now().isoformat()
            
            self.system_stats['jobs_running'] -= 1
            self.system_stats['jobs_failed'] += 1
            
            logger.error(f"فشلت الوظيفة {job_id}: {e}")
        
        finally:
            # إزالة من الوظائف النشطة
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """الحصول على حالة الوظيفة"""
        if job_id not in self.jobs:
            return {'error': 'الوظيفة غير موجودة'}
        
        return self.jobs[job_id]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        return self.system_stats.copy()

    # Placeholder methods for complete functionality  
    def _extract_basic(self): return {'mode': 'basic', 'extracted_files': []}
    def _extract_standard(self): return {'mode': 'standard', 'extracted_files': []}
    def _extract_advanced(self): return {'mode': 'advanced', 'extracted_files': []}
    def _extract_ultra(self): return {'mode': 'ultra', 'extracted_files': []}
    def _extract_secure(self): return {'mode': 'secure', 'extracted_files': []}
    def _save_extraction_report(self): pass
    def _compress_output(self): pass

    def _extract_basic(self) -> Dict[str, Any]:
        """استخراج أساسي للمحتوى النصي فقط"""
        logger.info("تشغيل الاستخراج الأساسي")
        
        try:
            response = self.session.get(self.base_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج المحتوى النصي
            content = {
                'title': soup.find('title').get_text().strip() if soup.find('title') else '',
                'meta_description': self._get_meta_content(soup, 'description'),
                'headings': self._extract_headings(soup),
                'paragraphs': [p.get_text().strip() for p in soup.find_all('p')],
                'links': self._extract_links(soup),
                'text_content': soup.get_text()
            }
            
            # حفظ المحتوى
            self._save_content_data(content)
            self.stats['pages_extracted'] = 1
            
            return {
                'mode': 'basic',
                'content': content,
                'pages_processed': 1
            }
            
        except Exception as e:
            logger.error(f"خطأ في الاستخراج الأساسي: {e}")
            raise

    def _extract_standard(self) -> Dict[str, Any]:
        """استخراج عادي مع الأصول الرئيسية"""
        logger.info("تشغيل الاستخراج العادي")
        
        extracted_pages = []
        
        try:
            # استخراج الصفحة الرئيسية
            main_page = self._extract_single_page(self.base_url)
            if main_page:
                extracted_pages.append(main_page)
                self.stats['pages_extracted'] += 1
            
            # العثور على الروابط الداخلية
            internal_links = self._find_internal_links(self.base_url)
            logger.info(f"تم العثور على {len(internal_links)} رابط داخلي")
            
            # استخراج صفحات إضافية
            max_pages = min(self.config.max_pages - 1, len(internal_links))
            for i, link in enumerate(internal_links[:max_pages]):
                try:
                    logger.info(f"استخراج الصفحة {i+2}/{max_pages+1}: {link}")
                    page_data = self._extract_single_page(link)
                    if page_data:
                        extracted_pages.append(page_data)
                        self.stats['pages_extracted'] += 1
                    
                    time.sleep(self.config.delay_between_requests)
                    
                except Exception as e:
                    logger.error(f"خطأ في استخراج {link}: {e}")
                    self.stats['errors'].append(f"صفحة {link}: {str(e)}")
                    self.stats['pages_failed'] += 1
            
            return {
                'mode': 'standard',
                'pages': extracted_pages,
                'pages_processed': len(extracted_pages)
            }
            
        except Exception as e:
            logger.error(f"خطأ في الاستخراج العادي: {e}")
            raise

    def _extract_advanced(self) -> Dict[str, Any]:
        """استخراج متقدم مع جميع الملفات"""
        logger.info("تشغيل الاستخراج المتقدم")
        
        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            # استخراج متوازي للصفحات
            return self._parallel_extraction(executor)

    def _extract_ultra(self) -> Dict[str, Any]:
        """استخراج فائق مع ذكاء اصطناعي"""
        logger.info("تشغيل الاستخراج الفائق")
        
        # تحليل ذكي للموقع
        site_analysis = self._analyze_site_structure()
        
        # استخراج مُحسَّن بناءً على التحليل
        optimized_extraction = self._smart_extraction(site_analysis)
        
        return {
            'mode': 'ultra',
            'site_analysis': site_analysis,
            'extraction_result': optimized_extraction,
            'ai_insights': self._generate_ai_insights()
        }

    def _extract_secure(self) -> Dict[str, Any]:
        """استخراج آمن مع ضوابط صارمة"""
        logger.info("تشغيل الاستخراج الآمن")
        
        # فحص أمان أولي
        security_check = self._perform_security_check()
        
        if not security_check['safe']:
            logger.warning("تحذير أمني: قد يحتوي الموقع على محتوى غير آمن")
            return {
                'mode': 'secure',
                'security_warning': security_check['issues'],
                'extraction_aborted': True
            }
        
        # استخراج آمن
        return self._secure_extraction()

    def _extract_single_page(self, url: str) -> Optional[Dict[str, Any]]:
        """استخراج صفحة واحدة"""
        try:
            if url in self.visited_urls:
                return None
            
            self.visited_urls.add(url)
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # إزالة الإعلانات إذا كان مطلوباً
            if self.config.remove_ads:
                soup = self._remove_ads(soup)
            
            # استخراج الأصول
            assets = self._extract_page_assets(soup, url)
            
            # حفظ الصفحة
            page_filename = self._get_safe_filename(url)
            page_path = self.site_dir / 'pages' / page_filename
            
            # تحديث الروابط في HTML
            updated_html = self._update_html_links(soup, url)
            
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(str(updated_html))
            
            page_data = {
                'url': url,
                'filename': page_filename,
                'title': soup.find('title').get_text().strip() if soup.find('title') else '',
                'meta_description': self._get_meta_content(soup, 'description'),
                'assets': assets,
                'size_bytes': len(str(updated_html)),
                'extraction_time': datetime.now().isoformat()
            }
            
            self.page_metadata[url] = page_data
            return page_data
            
        except Exception as e:
            logger.error(f"خطأ في استخراج الصفحة {url}: {e}")
            self.failed_urls.add(url)
            return None

    # Helper Methods
    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str:
        """استخراج محتوى meta tag"""
        meta = soup.find('meta', attrs={'name': name})
        return meta.get('content', '') if meta else ''

    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """استخراج العناوين"""
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = [h.get_text().strip() for h in soup.find_all(f'h{i}')]
        return headings

    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """استخراج الروابط"""
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'url': link['href'],
                'text': link.get_text().strip(),
                'title': link.get('title', '')
            })
        return links

    def _find_internal_links(self, url: str) -> List[str]:
        """العثور على الروابط الداخلية"""
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            internal_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                if urlparse(full_url).netloc == self.domain:
                    if full_url not in internal_links and full_url != url:
                        internal_links.append(full_url)
            
            return internal_links
            
        except Exception as e:
            logger.error(f"خطأ في العثور على الروابط: {e}")
            return []

    def _get_safe_filename(self, url: str) -> str:
        """إنشاء اسم ملف آمن"""
        parsed = urlparse(url)
        path = parsed.path
        
        if not path or path == '/':
            return 'index.html'
        
        filename = unquote(path.split('/')[-1])
        if not filename:
            return 'index.html'
        
        if not '.' in filename:
            filename += '.html'
        
        # تنظيف الأحرف غير الآمنة
        safe_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        filename = ''.join(c for c in filename if c in safe_chars)
        
        return filename[:100]

    def _save_extraction_report(self):
        """حفظ تقرير الاستخراج"""
        report_path = self.site_dir / 'reports' / 'extraction_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    def _compress_output(self):
        """ضغط مجلد الإخراج"""
        zip_path = self.output_dir / f"{self.site_id}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.site_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.site_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"تم ضغط الملفات في: {zip_path}")

    # Placeholder methods for complete functionality
    def _extract_page_assets(self, soup, url): return {}
    def _remove_ads(self, soup): return soup
    def _update_html_links(self, soup, url): return soup
    def _save_content_data(self, content): pass
    def _parallel_extraction(self, executor): return {}
    def _analyze_site_structure(self): return {}
    def _smart_extraction(self, analysis): return {}
    def _generate_ai_insights(self): return {}
    def _perform_security_check(self): return {'safe': True, 'issues': []}
    def _secure_extraction(self): return {}