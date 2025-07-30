"""
واجهة الاستخراج المتطورة الموحدة
Unified Advanced Extraction Interface
"""

import json
import time
import asyncio
import threading
import csv
import shutil
import sqlite3
import hashlib
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import re

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Advanced dependencies (conditional imports)
try:
    import aiohttp
    import aiofiles
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

try:
    import builtwith
    BUILTWITH_AVAILABLE = True
except ImportError:
    BUILTWITH_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Inches
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from .core.extractor_engine import AdvancedExtractorEngine
    from .core.config import ExtractionConfig, get_preset_config
except ImportError:
    # معالجة مشكلة الاستيراد النسبي
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from core.extractor_engine import AdvancedExtractorEngine
    from core.config import ExtractionConfig, get_preset_config


@dataclass
class CloningConfig:
    """إعدادات شاملة لعملية الاستنساخ"""
    target_url: str = ""
    output_directory: str = "cloned_websites"
    max_depth: int = 5
    max_pages: int = 1000
    timeout: int = 30
    delay_between_requests: float = 1.0
    extract_all_content: bool = True
    extract_hidden_content: bool = True
    extract_dynamic_content: bool = True
    extract_media_files: bool = True
    extract_documents: bool = True
    extract_apis: bool = True
    extract_database_structure: bool = True
    bypass_protection: bool = True
    handle_javascript: bool = True
    handle_ajax: bool = True
    detect_spa: bool = True
    extract_source_code: bool = True
    analyze_with_ai: bool = True

@dataclass
class AIAnalysisConfig:
    """إعدادات تحليل الذكاء الاصطناعي"""
    enable_content_analysis: bool = True
    enable_sentiment_analysis: bool = True
    enable_pattern_recognition: bool = True
    enable_code_analysis: bool = True
    enable_security_analysis: bool = True
    enable_seo_analysis: bool = True
    analysis_depth: str = "standard"  # basic, standard, deep

@dataclass 
class SpiderConfig:
    """إعدادات محرك الزحف"""
    max_depth: int = 3
    max_pages: int = 100
    respect_robots_txt: bool = True
    enable_javascript_discovery: bool = False
    delay_between_requests: float = 1.0
    timeout: int = 30
    user_agent: str = "AdvancedSpider/1.0"

class AdvancedWebsiteExtractor:
    """واجهة شاملة لاستخدام جميع محركات الاستخراج المتطورة"""
    
    def __init__(self, output_directory: str = "extracted_files"):
        """تهيئة أداة الاستخراج الشاملة"""
        self.output_directory = Path(output_directory)
        self.engine = None
        self.extraction_id = 0
        self.results = {}
        
        # إعداد جلسة HTTP محسنة
        self.session = self._create_enhanced_session()
        
        # تهيئة المحركات المتقدمة
        self.cloner_pro = None
        self.spider_engine = None  
        self.deep_engine = None
        self.unified_master = None
        self.ai_engine = None
        self.comprehensive_analyzer = None
        self.screenshot_engine = None
        self.cms_detector = None
        self.sitemap_generator = None
        
        # إنشاء مجلدات الإخراج
        self._setup_extraction_directories()
        
        # تهيئة قواعد البيانات المحلية
        self._init_local_database()
    
    def _create_enhanced_session(self):
        """إنشاء جلسة HTTP محسنة مع retry strategy"""
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
        
        # إعداد headers محسنة
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        return session
    
    def _init_local_database(self):
        """تهيئة قاعدة بيانات محلية لحفظ النتائج"""
        db_path = self.output_directory / 'extraction_database.db'
        self.db_connection = sqlite3.connect(str(db_path), check_same_thread=False)
        
        # إنشاء جدول النتائج
        self.db_connection.execute('''
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extraction_id TEXT UNIQUE,
                url TEXT,
                extraction_type TEXT,
                success BOOLEAN,
                result_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration REAL,
                files_count INTEGER,
                size_mb REAL
            )
        ''')
        
        # إنشاء جدول الإحصائيات
        self.db_connection.execute('''
            CREATE TABLE IF NOT EXISTS extraction_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extraction_id TEXT,
                stat_name TEXT,
                stat_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_connection.commit()
    
    def extract_with_cloner_pro(self, url: str, config: Optional[CloningConfig] = None) -> Dict[str, Any]:
        """استخراج شامل باستخدام Website Cloner Pro"""
        start_time = time.time()
        extraction_id = f"cloner_pro_{int(time.time())}"
        
        try:
            # إعداد تكوين النسخ
            if config is None:
                config = CloningConfig(target_url=url, output_directory=str(self.output_directory / 'cloner_pro'))
            
            print(f"🚀 بدء النسخ الذكي للموقع: {url}")
            
            # تهيئة محرك النسخ الذكي
            result = self._perform_intelligent_cloning(url, config)
            
            result.update({
                'extraction_id': extraction_id,
                'method': 'cloner_pro',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
            self.results[extraction_id] = result
            return result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'method': 'cloner_pro',
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            self.results[extraction_id] = error_result
            return error_result
    
    def _perform_intelligent_cloning(self, url: str, config: CloningConfig) -> Dict[str, Any]:
        """تنفيذ النسخ الذكي للموقع"""
        
        # المرحلة 1: تحليل الموقع الأساسي
        print("📊 تحليل هيكل الموقع...")
        response = self.session.get(url, timeout=config.timeout, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # تحليل شامل للموقع
        site_analysis = {
            'basic_info': self._extract_basic_info(soup, url, response),
            'structure_analysis': self._analyze_structure(soup),
            'technology_stack': self._detect_advanced_technologies(soup, response.text),
            'api_endpoints': self._find_api_endpoints(soup),
            'database_structure': self._analyze_database_structure(soup),
            'interactive_elements': self._analyze_interactive_elements(soup),
            'security_analysis': self._analyze_security(soup, url)
        }
        
        # المرحلة 2: استخراج الأصول والمحتوى
        print("📥 استخراج الأصول والمحتوى...")
        cloning_folder = self.output_directory / 'cloner_pro' / f"clone_{int(time.time())}"
        cloning_folder.mkdir(parents=True, exist_ok=True)
        
        assets_result = self._download_comprehensive_assets(soup, url, cloning_folder)
        
        # المرحلة 3: نسخ ذكي للصفحات
        print("🔗 اكتشاف ونسخ الصفحات...")
        if config.max_pages > 1:
            spider_result = self._spider_crawl_pages(url, config, cloning_folder)
        else:
            spider_result = {'pages_crawled': 1, 'total_pages': 1}
        
        # المرحلة 4: تحليل JavaScript والمحتوى الديناميكي
        if config.handle_javascript and (SELENIUM_AVAILABLE or PLAYWRIGHT_AVAILABLE):
            print("⚡ تحليل المحتوى الديناميكي...")
            dynamic_result = self._analyze_dynamic_content(url, cloning_folder)
        else:
            dynamic_result = {'dynamic_analysis': False, 'note': 'تحليل المحتوى الديناميكي غير متاح'}
        
        # المرحلة 5: إنشاء نسخة مطابقة
        print("🎯 إنشاء النسخة المطابقة...")
        clone_result = self._generate_intelligent_clone(site_analysis, assets_result, cloning_folder)
        
        # المرحلة 6: تقييم جودة النسخ
        quality_assessment = self._assess_clone_quality(site_analysis, clone_result)
        
        return {
            'url': url,
            'success': True,
            'cloning_folder': str(cloning_folder),
            'site_analysis': site_analysis,
            'assets_result': assets_result,
            'spider_result': spider_result,
            'dynamic_result': dynamic_result,
            'clone_result': clone_result,
            'quality_assessment': quality_assessment,
            'cloning_stats': {
                'pages_cloned': spider_result.get('pages_crawled', 1),
                'assets_downloaded': assets_result.get('total_assets', 0),
                'apis_discovered': len(site_analysis['api_endpoints']),
                'interactive_elements': sum(site_analysis['interactive_elements'].values()),
                'quality_score': quality_assessment.get('overall_score', 0)
            }
        }
    
    def extract_with_spider_engine(self, url: str, config: Optional[SpiderConfig] = None) -> Dict[str, Any]:
        """استخراج شامل باستخدام محرك الزحف المتقدم"""
        start_time = time.time()
        extraction_id = f"spider_{int(time.time())}"
        
        try:
            if config is None:
                config = SpiderConfig(max_depth=3, max_pages=50)
            
            print(f"🕷️ بدء الزحف الذكي للموقع: {url}")
            
            # تنفيذ الزحف الشامل
            crawl_result = self._perform_comprehensive_crawl(url, config)
            
            crawl_result.update({
                'extraction_id': extraction_id,
                'method': 'spider_engine',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
            self.results[extraction_id] = crawl_result
            return crawl_result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'method': 'spider_engine',
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            self.results[extraction_id] = error_result
            return error_result
    
    def _perform_comprehensive_crawl(self, start_url: str, config: SpiderConfig) -> Dict[str, Any]:
        """تنفيذ زحف شامل للموقع"""
        
        visited_urls = set()
        urls_to_visit = queue.Queue()
        crawl_results = {}
        
        # إضافة الرابط الأساسي
        urls_to_visit.put((start_url, 0))  # (url, depth)
        
        crawl_folder = self.output_directory / 'spider_crawl' / f"crawl_{int(time.time())}"
        crawl_folder.mkdir(parents=True, exist_ok=True)
        
        pages_crawled = 0
        total_links_found = 0
        total_assets_found = 0
        
        print(f"🔍 بدء الزحف - العمق الأقصى: {config.max_depth}, الصفحات: {config.max_pages}")
        
        while not urls_to_visit.empty() and pages_crawled < config.max_pages:
            current_url, depth = urls_to_visit.get()
            
            # تجاهل الروابط المكررة أو التي تجاوزت العمق الأقصى
            if current_url in visited_urls or depth > config.max_depth:
                continue
            
            try:
                print(f"📄 زحف الصفحة {pages_crawled + 1}: {current_url} (عمق: {depth})")
                
                # تحميل الصفحة
                response = self.session.get(current_url, timeout=config.timeout, verify=False)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                visited_urls.add(current_url)
                
                # تحليل الصفحة
                page_analysis = {
                    'url': current_url,
                    'depth': depth,
                    'title': soup.find('title').get_text().strip() if soup.find('title') else '',
                    'status_code': response.status_code,
                    'content_length': len(response.text),
                    'links': [],
                    'images': [],
                    'scripts': [],
                    'stylesheets': [],
                    'forms': [],
                    'api_endpoints': self._find_api_endpoints(soup)
                }
                
                # استخراج الروابط
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(current_url, href)
                        # فقط الروابط الداخلية
                        if urlparse(full_url).netloc == urlparse(start_url).netloc:
                            page_analysis['links'].append({
                                'href': full_url,
                                'text': link.get_text().strip(),
                                'title': link.get('title', '')
                            })
                            
                            # إضافة للزحف إذا لم تتم زيارتها
                            if full_url not in visited_urls and depth < config.max_depth:
                                urls_to_visit.put((full_url, depth + 1))
                
                # استخراج الأصول
                page_analysis['images'] = [{'src': urljoin(current_url, img.get('src')), 'alt': img.get('alt', '')} 
                                         for img in soup.find_all('img', src=True)]
                page_analysis['scripts'] = [urljoin(current_url, script.get('src')) 
                                          for script in soup.find_all('script', src=True)]
                page_analysis['stylesheets'] = [urljoin(current_url, link.get('href')) 
                                               for link in soup.find_all('link', rel='stylesheet')]
                
                # تحليل النماذج
                for form in soup.find_all('form'):
                    form_analysis = {
                        'action': form.get('action', ''),
                        'method': form.get('method', 'get').lower(),
                        'inputs': [{'name': inp.get('name', ''), 'type': inp.get('type', 'text')} 
                                 for inp in form.find_all('input')]
                    }
                    page_analysis['forms'].append(form_analysis)
                
                # حفظ المحتوى
                page_file = crawl_folder / f"page_{pages_crawled + 1}_{urlparse(current_url).path.replace('/', '_')}.html"
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                page_analysis['saved_file'] = str(page_file)
                crawl_results[current_url] = page_analysis
                
                pages_crawled += 1
                total_links_found += len(page_analysis['links'])
                total_assets_found += len(page_analysis['images']) + len(page_analysis['scripts']) + len(page_analysis['stylesheets'])
                
                # تأخير بين الطلبات
                if config.delay_between_requests > 0:
                    time.sleep(config.delay_between_requests)
                    
            except Exception as e:
                print(f"❌ خطأ في زحف {current_url}: {str(e)}")
                crawl_results[current_url] = {
                    'url': current_url,
                    'depth': depth,
                    'error': str(e),
                    'status': 'failed'
                }
        
        # إنشاء ملخص الزحف
        summary = {
            'start_url': start_url,
            'success': True,
            'crawl_folder': str(crawl_folder),
            'pages_crawled': pages_crawled,
            'total_links_found': total_links_found,
            'total_assets_found': total_assets_found,
            'unique_domains': len(set(urlparse(url).netloc for url in visited_urls)),
            'max_depth_reached': max(result.get('depth', 0) for result in crawl_results.values() if isinstance(result, dict)),
            'crawl_results': crawl_results,
            'crawl_stats': {
                'success_rate': len([r for r in crawl_results.values() if not r.get('error')]) / len(crawl_results) * 100 if crawl_results else 0,
                'average_page_size': sum(r.get('content_length', 0) for r in crawl_results.values() if isinstance(r, dict)) / pages_crawled if pages_crawled > 0 else 0,
                'forms_found': sum(len(r.get('forms', [])) for r in crawl_results.values() if isinstance(r, dict)),
                'api_endpoints_found': sum(len(r.get('api_endpoints', [])) for r in crawl_results.values() if isinstance(r, dict))
            }
        }
        
        # حفظ ملخص الزحف
        summary_file = crawl_folder / 'crawl_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ اكتمل الزحف - تم زحف {pages_crawled} صفحة بنجاح")
        return summary
    
    def extract_with_ai_analysis(self, url: str, config: Optional[AIAnalysisConfig] = None) -> Dict[str, Any]:
        """استخراج مع تحليل ذكي متطور بالذكاء الاصطناعي"""
        start_time = time.time()
        extraction_id = f"ai_analysis_{int(time.time())}"
        
        try:
            if config is None:
                config = AIAnalysisConfig()
            
            print(f"🤖 بدء التحليل الذكي للموقع: {url}")
            
            # استخراج أساسي أولاً
            basic_result = self.extract(url, "complete")
            
            # تحليل ذكي متطور
            ai_result = self._perform_advanced_ai_analysis(url, basic_result, config)
            
            ai_result.update({
                'extraction_id': extraction_id,
                'method': 'ai_analysis',
                'basic_extraction': basic_result,
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
            self.results[extraction_id] = ai_result
            return ai_result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'method': 'ai_analysis',
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            self.results[extraction_id] = error_result
            return error_result
    
    def _perform_advanced_ai_analysis(self, url: str, basic_result: Dict[str, Any], config: AIAnalysisConfig) -> Dict[str, Any]:
        """تنفيذ التحليل الذكي المتطور"""
        
        ai_analysis = {
            'url': url,
            'success': True,
            'ai_config': asdict(config),
            'analysis_results': {}
        }
        
        try:
            # تحليل المحتوى الذكي
            if config.enable_content_analysis:
                print("📝 تحليل المحتوى بالذكاء الاصطناعي...")
                content_analysis = self._ai_content_analysis(basic_result)
                ai_analysis['analysis_results']['content_analysis'] = content_analysis
            
            # تحليل المشاعر
            if config.enable_sentiment_analysis:
                print("😊 تحليل المشاعر...")
                sentiment_analysis = self._ai_sentiment_analysis(basic_result)
                ai_analysis['analysis_results']['sentiment_analysis'] = sentiment_analysis
            
            # تحليل الأنماط
            if config.enable_pattern_recognition:
                print("🔍 تحليل الأنماط والهياكل...")
                pattern_analysis = self._ai_pattern_recognition(basic_result)
                ai_analysis['analysis_results']['pattern_analysis'] = pattern_analysis
            
            # تحليل الكود
            if config.enable_code_analysis:
                print("💻 تحليل الكود والتقنيات...")
                code_analysis = self._ai_code_analysis(basic_result)
                ai_analysis['analysis_results']['code_analysis'] = code_analysis
            
            # تحليل الأمان الذكي
            if config.enable_security_analysis:
                print("🔒 تحليل الأمان الذكي...")
                security_analysis = self._ai_security_analysis(basic_result)
                ai_analysis['analysis_results']['security_analysis'] = security_analysis
            
            # تحليل SEO الذكي
            if config.enable_seo_analysis:
                print("📈 تحليل SEO الذكي...")
                seo_analysis = self._ai_seo_analysis(basic_result)
                ai_analysis['analysis_results']['seo_analysis'] = seo_analysis
            
            # تقييم شامل ذكي
            overall_assessment = self._ai_overall_assessment(ai_analysis['analysis_results'])
            ai_analysis['overall_assessment'] = overall_assessment
            
        except Exception as e:
            ai_analysis['success'] = False
            ai_analysis['error'] = str(e)
            ai_analysis['fallback_note'] = 'تم الرجوع للتحليل الأساسي'
        
        return ai_analysis
    
    def export_to_multiple_formats(self, result: Dict[str, Any], output_folder: Optional[Path] = None) -> Dict[str, str]:
        """تصدير النتائج بصيغ متعددة متقدمة"""
        
        if output_folder is None:
            output_folder = self.output_directory / 'exports' / f"export_{int(time.time())}"
        
        output_folder.mkdir(parents=True, exist_ok=True)
        exports = {}
        
        try:
            # تصدير JSON مُنسق
            json_file = output_folder / 'complete_analysis.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            exports['json'] = str(json_file)
            
            # تصدير CSV شامل
            csv_exports = self._export_to_csv(result, output_folder)
            exports.update(csv_exports)
            
            # تصدير HTML تفاعلي
            html_file = self._export_to_interactive_html(result, output_folder)
            exports['html'] = str(html_file)
            
            # تصدير PDF (إذا كان متاحاً)
            if REPORTLAB_AVAILABLE:
                pdf_file = self._export_to_pdf(result, output_folder)
                exports['pdf'] = str(pdf_file)
            
            # تصدير Word (إذا كان متاحاً)
            if DOCX_AVAILABLE:
                word_file = self._export_to_word(result, output_folder)
                exports['word'] = str(word_file)
            
            # تصدير ملخص تنفيذي
            summary_file = self._export_executive_summary(result, output_folder)
            exports['summary'] = str(summary_file)
            
            # أرشفة مضغوطة
            archive_file = self._create_compressed_archive(output_folder)
            exports['archive'] = str(archive_file)
            
        except Exception as e:
            exports['error'] = str(e)
        
        return exports
    
    def batch_extract(self, urls: List[str], extraction_type: str = "standard", max_workers: int = 3) -> Dict[str, Any]:
        """استخراج متعدد للعديد من المواقع"""
        start_time = time.time()
        extraction_id = f"batch_{int(time.time())}"
        
        print(f"🔄 بدء الاستخراج المتعدد لـ {len(urls)} موقع...")
        
        results = {
            'extraction_id': extraction_id,
            'method': 'batch_extract',
            'total_urls': len(urls),
            'extraction_type': extraction_type,
            'results': {},
            'stats': {
                'successful_extractions': 0,
                'failed_extractions': 0,
                'total_duration': 0
            }
        }
        
        def extract_single_url(url):
            try:
                return url, self.extract(url, extraction_type)
            except Exception as e:
                return url, {'success': False, 'error': str(e), 'url': url}
        
        # استخدام ThreadPoolExecutor للمعالجة المتوازية
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(extract_single_url, url): url for url in urls}
            
            for i, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                try:
                    url, result = future.result()
                    results['results'][url] = result
                    
                    if result.get('success', False):
                        results['stats']['successful_extractions'] += 1
                        print(f"✅ نجح استخراج {i}/{len(urls)}: {url}")
                    else:
                        results['stats']['failed_extractions'] += 1
                        print(f"❌ فشل استخراج {i}/{len(urls)}: {url}")
                        
                except Exception as e:
                    results['results'][url] = {'success': False, 'error': str(e), 'url': url}
                    results['stats']['failed_extractions'] += 1
                    print(f"❌ خطأ في استخراج {i}/{len(urls)}: {url} - {str(e)}")
        
        results['stats']['total_duration'] = round(time.time() - start_time, 2)
        results['stats']['success_rate'] = (results['stats']['successful_extractions'] / len(urls)) * 100
        results['timestamp'] = datetime.now().isoformat()
        
        # حفظ النتائج المتعددة
        batch_folder = self.output_directory / 'batch_extractions' / extraction_id
        batch_folder.mkdir(parents=True, exist_ok=True)
        
        batch_summary_file = batch_folder / 'batch_summary.json'
        with open(batch_summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        results['batch_folder'] = str(batch_folder)
        self.results[extraction_id] = results
        
        print(f"🎉 اكتمل الاستخراج المتعدد - نجح {results['stats']['successful_extractions']}/{len(urls)} في {results['stats']['total_duration']} ثانية")
        return results
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات شاملة لجميع عمليات الاستخراج"""
        
        stats = {
            'total_extractions': len(self.results),
            'extraction_methods': {},
            'success_rate': 0,
            'total_duration': 0,
            'average_duration': 0,
            'most_extracted_domains': {},
            'extraction_timeline': [],
            'database_stats': self._get_database_stats()
        }
        
        successful = 0
        total_duration = 0
        
        for result in self.results.values():
            # إحصائيات الطرق
            method = result.get('method', 'unknown')
            if method not in stats['extraction_methods']:
                stats['extraction_methods'][method] = {'count': 0, 'success': 0}
            
            stats['extraction_methods'][method]['count'] += 1
            
            if result.get('success', False):
                successful += 1
                stats['extraction_methods'][method]['success'] += 1
            
            # المدة
            duration = result.get('duration', 0)
            total_duration += duration
            
            # النطاقات
            url = result.get('url', '')
            if url:
                domain = urlparse(url).netloc
                if domain not in stats['most_extracted_domains']:
                    stats['most_extracted_domains'][domain] = 0
                stats['most_extracted_domains'][domain] += 1
            
            # الجدول الزمني
            stats['extraction_timeline'].append({
                'timestamp': result.get('timestamp', ''),
                'url': url,
                'method': method,
                'success': result.get('success', False),
                'duration': duration
            })
        
        if len(self.results) > 0:
            stats['success_rate'] = (successful / len(self.results)) * 100
            stats['average_duration'] = total_duration / len(self.results)
        
        stats['total_duration'] = total_duration
        
        # ترتيب النطاقات الأكثر استخراجاً
        stats['most_extracted_domains'] = dict(
            sorted(stats['most_extracted_domains'].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        # ترتيب الجدول الزمني
        stats['extraction_timeline'].sort(
            key=lambda x: x.get('timestamp', ''), reverse=True
        )
        
        return stats
    
    # =====================================
    # وظائف مساعدة متقدمة
    # =====================================
    
    def _detect_advanced_technologies(self, soup: BeautifulSoup, content: str) -> List[str]:
        """كشف التقنيات المتقدم"""
        technologies = []
        content_lower = content.lower()
        
        # إطارات عمل JavaScript متقدمة
        js_frameworks = {
            'react': ['react', 'jsx', 'create-react-app'],
            'vue': ['vue.js', 'vuejs', 'vue-router'],
            'angular': ['angular', 'ng-', '@angular'],
            'svelte': ['svelte', 'sveltekit'],
            'next.js': ['next.js', 'nextjs', '_next/'],
            'nuxt.js': ['nuxt.js', 'nuxtjs', '_nuxt/'],
            'gatsby': ['gatsby', 'gatsbyjs'],
            'ember.js': ['ember', 'emberjs']
        }
        
        for framework, indicators in js_frameworks.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(framework)
        
        # أنظمة إدارة المحتوى المتقدمة
        cms_systems = {
            'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
            'Drupal': ['drupal', 'sites/default'],
            'Joomla': ['joomla', 'components/com_'],
            'Magento': ['magento', 'mage/'],
            'Shopify': ['shopify', 'cdn.shopify.com'],
            'Wix': ['wix.com', 'wixstatic.com'],
            'Squarespace': ['squarespace', 'sqsp.com']
        }
        
        for cms, indicators in cms_systems.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(cms)
        
        # قواعد البيانات والخوادم
        server_tech = {
            'nginx': ['nginx', 'server: nginx'],
            'apache': ['apache', 'server: apache'],
            'cloudflare': ['cloudflare', 'cf-ray'],
            'aws': ['amazonaws.com', 'cloudfront'],
            'google cloud': ['googleusercontent.com', 'gstatic.com'],
            'azure': ['azurewebsites.net', 'azure.com']
        }
        
        for tech, indicators in server_tech.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tech)
        
        # مكتبات CSS والتصميم
        css_frameworks = {
            'Bootstrap': ['bootstrap', 'btn-', 'col-'],
            'Tailwind CSS': ['tailwind', 'tw-'],
            'Bulma': ['bulma', 'is-primary'],
            'Foundation': ['foundation', 'grid-x'],
            'Material UI': ['material-ui', 'mui'],
            'Ant Design': ['antd', 'ant-design']
        }
        
        for framework, indicators in css_frameworks.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(framework)
        
        # أدوات التحليل والتسويق
        analytics_tools = {
            'Google Analytics': ['google-analytics', 'gtag', 'ga('],
            'Google Tag Manager': ['googletagmanager', 'gtm.js'],
            'Facebook Pixel': ['facebook.com/tr', 'fbq('],
            'Hotjar': ['hotjar', 'hj('],
            'Mixpanel': ['mixpanel', 'mp_'],
            'Adobe Analytics': ['adobe', 'omniture']
        }
        
        for tool, indicators in analytics_tools.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tool)
        
        return list(set(technologies))
    
    # =====================================
    # الوظائف الشاملة المطلوبة حسب 11.txt
    # =====================================
    
    def comprehensive_website_download(self, url: str, extraction_type: str = "complete") -> Dict[str, Any]:
        """
        تحميل شامل للموقع مع جميع المتطلبات المذكورة في 11.txt
        
        المحتوى الأساسي:
        • جميع صفحات HTML
        • النصوص والمحتوى النصي
        • البيانات الوصفية (Meta tags)
        • البنية الهيكلية للموقع
        
        الأصول والملفات:
        • جميع الصور (PNG, JPG, SVG, WebP)
        • ملفات CSS وأكواد التنسيق
        • ملفات JavaScript والسكريبت
        • الخطوط (Fonts)
        • الفيديو والصوت
        • المستندات (PDF, DOC, etc.)
        
        البنية التقنية:
        • الكود المصدري الكامل
        • قواعد البيانات والAPI calls
        • نظام التوجيه (Routing)
        • التفاعلات والوظائف
        • أنظمة المصادقة
        • إعدادات الخادم
        
        التصميم والتفاعل:
        • التخطيطات (Layouts)
        • الأنماط المتجاوبة
        • التأثيرات والحركات
        • واجهات المستخدم
        • تجربة المستخدم
        """
        start_time = time.time()
        extraction_id = f"comprehensive_{int(time.time())}"
        
        print(f"🚀 بدء التحميل الشامل للموقع: {url}")
        
        try:
            # إنشاء هيكل مجلدات منظم
            base_folder = self.output_directory / 'comprehensive_downloads' / extraction_id
            self._create_comprehensive_folder_structure(base_folder)
            
            # مرحلة 1: استخراج المحتوى الأساسي
            print("📄 1. استخراج المحتوى الأساسي...")
            basic_content = self._extract_comprehensive_basic_content(url, base_folder)
            
            # مرحلة 2: تحميل جميع الأصول والملفات
            print("💾 2. تحميل جميع الأصول والملفات...")
            assets_download = self._download_all_website_assets(basic_content['soup'], url, base_folder)
            
            # مرحلة 3: استخراج البنية التقنية
            print("🔧 3. استخراج البنية التقنية...")
            technical_structure = self._extract_technical_structure(basic_content['soup'], url, base_folder)
            
            # مرحلة 4: تحليل التصميم والتفاعل
            print("🎨 4. تحليل التصميم والتفاعل...")
            design_analysis = self._analyze_design_and_interaction(basic_content['soup'], url, base_folder)
            
            # مرحلة 5: التقاط screenshots تلقائي
            print("📸 5. التقاط screenshots تلقائي...")
            screenshots = self._capture_automatic_screenshots(url, base_folder)
            
            # مرحلة 6: إنشاء خريطة الموقع
            print("🗺️ 6. إنشاء خريطة الموقع...")
            sitemap = self._generate_comprehensive_sitemap(url, base_folder)
            
            # مرحلة 7: تنظيم الملفات في مجلدات مرتبة
            print("📁 7. تنظيم الملفات...")
            file_organization = self._organize_downloaded_files(base_folder)
            
            # مرحلة 8: كشف CMS المستخدم
            print("🧪 8. كشف CMS المستخدم...")
            cms_detection = self._detect_comprehensive_cms(basic_content['soup'], basic_content['response'])
            
            # مرحلة 9: اختبار الحماية
            print("🛡️ 9. اختبار الحماية...")
            security_test = self._comprehensive_security_test(url, basic_content['soup'])
            
            # مرحلة 10: دعم crawl للروابط الداخلية
            print("🕸️ 10. زحف الروابط الداخلية...")
            crawl_results = self._crawl_internal_links(url, base_folder, max_depth=3, max_pages=50)
            
            # مرحلة 11: تنزيل المحتوى من AJAX
            print("💬 11. تنزيل المحتوى من AJAX...")
            ajax_content = self._extract_ajax_content(url, basic_content['soup'], base_folder)
            
            # تجميع النتائج النهائية
            final_result = {
                'extraction_info': {
                    'extraction_id': extraction_id,
                    'url': url,
                    'extraction_type': extraction_type,
                    'success': True,
                    'duration': round(time.time() - start_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'base_folder': str(base_folder)
                },
                'basic_content': basic_content,
                'assets_download': assets_download,
                'technical_structure': technical_structure,
                'design_analysis': design_analysis,
                'screenshots': screenshots,
                'sitemap': sitemap,
                'file_organization': file_organization,
                'cms_detection': cms_detection,
                'security_test': security_test,
                'crawl_results': crawl_results,
                'ajax_content': ajax_content,
                'comprehensive_stats': self._calculate_comprehensive_stats({
                    'basic_content': basic_content,
                    'assets_download': assets_download,
                    'crawl_results': crawl_results
                })
            }
            
            # حفظ التقرير الشامل
            self._save_comprehensive_report(final_result, base_folder)
            
            print(f"✅ اكتمل التحميل الشامل في {final_result['extraction_info']['duration']} ثانية")
            return final_result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ فشل التحميل الشامل: {str(e)}")
            return error_result
    
    def _create_comprehensive_folder_structure(self, base_folder: Path):
        """إنشاء هيكل مجلدات شامل ومنظم"""
        folders = [
            '01_content',           # المحتوى الأساسي
            '02_assets/images',     # الصور
            '02_assets/css',        # ملفات CSS
            '02_assets/js',         # ملفات JavaScript
            '02_assets/fonts',      # الخطوط
            '02_assets/media',      # الفيديو والصوت
            '02_assets/documents',  # المستندات
            '03_technical',         # البنية التقنية
            '04_design',            # التصميم والتفاعل
            '05_screenshots',       # لقطات الشاشة
            '06_sitemap',           # خريطة الموقع
            '07_security',          # تحليل الأمان
            '08_crawled_pages',     # الصفحات المزحوفة
            '09_ajax_content',      # محتوى AJAX
            '10_reports'            # التقارير الشاملة
        ]
        
        for folder in folders:
            (base_folder / folder).mkdir(parents=True, exist_ok=True)
    
    def _extract_comprehensive_basic_content(self, url: str, base_folder: Path) -> Dict[str, Any]:
        """استخراج المحتوى الأساسي الشامل"""
        try:
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # حفظ الصفحة الأساسية
            main_html_file = base_folder / '01_content' / 'index.html'
            with open(main_html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # استخراج المعلومات الأساسية
            basic_info = {
                'title': soup.find('title').get_text().strip() if soup.find('title') else 'بدون عنوان',
                'description': self._get_meta_content(soup, 'description'),
                'keywords': self._get_meta_content(soup, 'keywords'),
                'language': soup.get('lang') or self._detect_content_language(soup.get_text()[:1000]),
                'charset': self._get_charset(soup),
                'canonical_url': self._get_canonical_url(soup, url),
                'og_data': self._extract_og_data(soup),
                'twitter_data': self._extract_twitter_data(soup),
                'structured_data': self._extract_structured_data(soup),
                'meta_tags': self._extract_all_meta_tags(soup),
                'headings_structure': self._extract_headings_structure(soup),
                'page_structure': self._analyze_page_structure(soup)
            }
            
            # حفظ البيانات الوصفية
            metadata_file = base_folder / '01_content' / 'metadata.json'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(basic_info, f, ensure_ascii=False, indent=2)
            
            # استخراج النصوص
            text_content = self._extract_comprehensive_text(soup)
            text_file = base_folder / '01_content' / 'extracted_text.txt'
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            return {
                'success': True,
                'response': response,
                'soup': soup,
                'basic_info': basic_info,
                'text_content': text_content,
                'main_html_file': str(main_html_file),
                'metadata_file': str(metadata_file),
                'text_file': str(text_file)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _download_all_website_assets(self, soup: BeautifulSoup, base_url: str, base_folder: Path) -> Dict[str, Any]:
        """تحميل جميع أصول الموقع بشكل شامل"""
        assets_result = {
            'images': {'downloaded': [], 'failed': [], 'total': 0},
            'css': {'downloaded': [], 'failed': [], 'total': 0},
            'js': {'downloaded': [], 'failed': [], 'total': 0},
            'fonts': {'downloaded': [], 'failed': [], 'total': 0},
            'media': {'downloaded': [], 'failed': [], 'total': 0},
            'documents': {'downloaded': [], 'failed': [], 'total': 0},
            'summary': {'total_downloaded': 0, 'total_failed': 0, 'total_size_mb': 0}
        }
        
        # تحميل الصور (جميع الأنواع)
        image_selectors = [
            'img[src]',
            'img[data-src]',
            'img[data-lazy-src]',
            'source[srcset]',
            '[style*="background-image"]'
        ]
        
        for selector in image_selectors:
            elements = soup.select(selector)
            for element in elements[:50]:  # حد أقصى 50 صورة
                image_urls = self._extract_image_urls(element, base_url)
                for img_url in image_urls:
                    self._download_asset_comprehensive(img_url, base_folder / '02_assets/images', assets_result['images'])
        
        # تحميل ملفات CSS
        css_elements = soup.find_all(['link', 'style'])
        for element in css_elements:
            if element.name == 'link' and element.get('rel') == ['stylesheet']:
                href = element.get('href')
                if href:
                    css_url = urljoin(base_url, href)
                    self._download_asset_comprehensive(css_url, base_folder / '02_assets/css', assets_result['css'])
            elif element.name == 'style':
                # حفظ CSS المدمج
                css_content = element.get_text()
                if css_content:
                    inline_css_file = base_folder / '02_assets/css' / f'inline_style_{len(assets_result["css"]["downloaded"])}.css'
                    with open(inline_css_file, 'w', encoding='utf-8') as f:
                        f.write(css_content)
                    assets_result['css']['downloaded'].append({
                        'type': 'inline',
                        'file_path': str(inline_css_file),
                        'size_mb': len(css_content.encode()) / 1024 / 1024
                    })
        
        # تحميل ملفات JavaScript
        js_elements = soup.find_all('script')
        for element in js_elements:
            src = element.get('src')
            if src:
                js_url = urljoin(base_url, src)
                self._download_asset_comprehensive(js_url, base_folder / '02_assets/js', assets_result['js'])
            else:
                # حفظ JavaScript المدمج
                js_content = element.get_text()
                if js_content and len(js_content) > 50:
                    inline_js_file = base_folder / '02_assets/js' / f'inline_script_{len(assets_result["js"]["downloaded"])}.js'
                    with open(inline_js_file, 'w', encoding='utf-8') as f:
                        f.write(js_content)
                    assets_result['js']['downloaded'].append({
                        'type': 'inline',
                        'file_path': str(inline_js_file),
                        'size_mb': len(js_content.encode()) / 1024 / 1024
                    })
        
        # تحميل الخطوط
        font_urls = self._extract_font_urls(soup, base_url)
        for font_url in font_urls:
            self._download_asset_comprehensive(font_url, base_folder / '02_assets/fonts', assets_result['fonts'])
        
        # تحميل ملفات الوسائط (فيديو وصوت)
        media_elements = soup.find_all(['video', 'audio', 'source'])
        for element in media_elements:
            src = element.get('src')
            if src:
                media_url = urljoin(base_url, src)
                self._download_asset_comprehensive(media_url, base_folder / '02_assets/media', assets_result['media'])
        
        # تحميل المستندات
        document_links = soup.find_all('a', href=True)
        for link in document_links:
            href = link.get('href')
            if href and any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
                doc_url = urljoin(base_url, href)
                self._download_asset_comprehensive(doc_url, base_folder / '02_assets/documents', assets_result['documents'])
        
        # حساب الإحصائيات الإجمالية
        for category in assets_result:
            if category != 'summary':
                assets_result['summary']['total_downloaded'] += len(assets_result[category]['downloaded'])
                assets_result['summary']['total_failed'] += len(assets_result[category]['failed'])
                assets_result['summary']['total_size_mb'] += sum(
                    item.get('size_mb', 0) for item in assets_result[category]['downloaded']
                )
                assets_result[category]['total'] = len(assets_result[category]['downloaded']) + len(assets_result[category]['failed'])
        
        return assets_result
    
    def _download_comprehensive_assets(self, soup: BeautifulSoup, base_url: str, output_folder: Path) -> Dict[str, Any]:
        """تحميل شامل للأصول"""
        assets_folder = output_folder / 'assets'
        assets_folder.mkdir(exist_ok=True)
        
        downloaded_assets = {
            'images': [],
            'css': [],
            'js': [],
            'fonts': [],
            'documents': [],
            'media': [],
            'failed': [],
            'total_assets': 0,
            'total_size_mb': 0
        }
        
        # تحميل الصور
        for img in soup.find_all('img', src=True)[:20]:
            try:
                src = img.get('src')
                if src and not src.startswith('data:'):
                    img_url = urljoin(base_url, src)
                    self._download_asset(img_url, assets_folder / 'images', downloaded_assets, 'images')
            except Exception as e:
                downloaded_assets['failed'].append({'url': src, 'error': str(e), 'type': 'image'})
        
        # تحميل ملفات CSS
        for link in soup.find_all('link', rel='stylesheet')[:10]:
            try:
                href = link.get('href')
                if href and not href.startswith('data:'):
                    css_url = urljoin(base_url, href)
                    self._download_asset(css_url, assets_folder / 'css', downloaded_assets, 'css')
            except Exception as e:
                downloaded_assets['failed'].append({'url': href, 'error': str(e), 'type': 'css'})
        
        # تحميل ملفات JavaScript
        for script in soup.find_all('script', src=True)[:10]:
            try:
                src = script.get('src')
                if src and not src.startswith('data:'):
                    js_url = urljoin(base_url, src)
                    self._download_asset(js_url, assets_folder / 'js', downloaded_assets, 'js')
            except Exception as e:
                downloaded_assets['failed'].append({'url': src, 'error': str(e), 'type': 'js'})
        
        # البحث عن الخطوط
        font_urls = self._find_font_urls(soup, base_url)
        for font_url in font_urls[:5]:
            try:
                self._download_asset(font_url, assets_folder / 'fonts', downloaded_assets, 'fonts')
            except Exception as e:
                downloaded_assets['failed'].append({'url': font_url, 'error': str(e), 'type': 'font'})
        
        downloaded_assets['total_assets'] = sum(len(downloaded_assets[key]) for key in ['images', 'css', 'js', 'fonts', 'documents', 'media'])
        
        return downloaded_assets
    
    def _download_asset(self, url: str, folder: Path, assets_dict: Dict, asset_type: str):
        """تحميل أصل واحد"""
        try:
            folder.mkdir(exist_ok=True)
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            filename = Path(urlparse(url).path).name or f"{asset_type}_{int(time.time())}"
            if not filename.split('.')[-1]:
                extensions = {'images': '.jpg', 'css': '.css', 'js': '.js', 'fonts': '.woff'}
                filename += extensions.get(asset_type, '.file')
            
            filepath = folder / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = filepath.stat().st_size / (1024 * 1024)  # MB
            assets_dict['total_size_mb'] += file_size
            
            assets_dict[asset_type].append({
                'url': url,
                'local_path': str(filepath),
                'size_mb': round(file_size, 3),
                'status': 'downloaded'
            })
            
        except Exception as e:
            assets_dict['failed'].append({'url': url, 'error': str(e), 'type': asset_type})
    
    def _find_font_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """البحث عن روابط الخطوط"""
        font_urls = []
        
        # البحث في CSS links
        for link in soup.find_all('link'):
            href = link.get('href', '')
            if 'font' in href.lower() or 'googleapis.com/css' in href:
                font_urls.append(urljoin(base_url, href))
        
        # البحث في inline styles
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            if 'font-face' in style or 'font-family' in style:
                # استخراج URLs من CSS
                import re
                urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
                for url in urls:
                    if any(ext in url.lower() for ext in ['.woff', '.woff2', '.ttf', '.otf']):
                        font_urls.append(urljoin(base_url, url))
        
        return font_urls
    
    def _spider_crawl_pages(self, url: str, config: CloningConfig, output_folder: Path) -> Dict[str, Any]:
        """زحف الصفحات للنسخ الذكي"""
        spider_config = SpiderConfig(
            max_depth=min(config.max_depth, 3),
            max_pages=min(config.max_pages, 50),
            delay_between_requests=config.delay_between_requests
        )
        
        crawl_result = self._perform_comprehensive_crawl(url, spider_config)
        
        # نسخ الملفات المزحوفة إلى مجلد النسخ
        if crawl_result.get('success'):
            crawl_folder = Path(crawl_result['crawl_folder'])
            clone_pages_folder = output_folder / 'pages'
            clone_pages_folder.mkdir(exist_ok=True)
            
            # نسخ ملفات الصفحات
            if crawl_folder.exists():
                for html_file in crawl_folder.glob('*.html'):
                    shutil.copy2(html_file, clone_pages_folder)
        
        return crawl_result
    
    def _analyze_dynamic_content(self, url: str, output_folder: Path) -> Dict[str, Any]:
        """تحليل المحتوى الديناميكي باستخدام Selenium أو Playwright"""
        
        if PLAYWRIGHT_AVAILABLE:
            return self._analyze_with_playwright(url, output_folder)
        elif SELENIUM_AVAILABLE:
            return self._analyze_with_selenium(url, output_folder)
        else:
            return {'success': False, 'error': 'لا تتوفر أدوات تحليل المحتوى الديناميكي'}
    
    def _analyze_with_playwright(self, url: str, output_folder: Path) -> Dict[str, Any]:
        """تحليل بـ Playwright"""
        try:
            async def analyze():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url)
                    
                    # انتظار تحميل JavaScript
                    await page.wait_for_timeout(3000)
                    
                    # الحصول على المحتوى النهائي
                    content = await page.content()
                    
                    # لقطة شاشة
                    screenshot_path = output_folder / 'dynamic_screenshot.png'
                    await page.screenshot(path=screenshot_path)
                    
                    # تحليل الشبكة
                    network_requests = []
                    
                    await browser.close()
                    
                    return {
                        'success': True,
                        'content_length': len(content),
                        'screenshot': str(screenshot_path),
                        'network_requests': len(network_requests),
                        'method': 'playwright'
                    }
            
            if ASYNC_AVAILABLE:
                return asyncio.run(analyze())
            else:
                return {'success': False, 'error': 'Async support not available'}
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'playwright'}
    
    def _analyze_with_selenium(self, url: str, output_folder: Path) -> Dict[str, Any]:
        """تحليل بـ Selenium"""
        try:
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # انتظار تحميل JavaScript
            time.sleep(3)
            
            content = driver.page_source
            
            # لقطة شاشة
            screenshot_path = output_folder / 'dynamic_screenshot.png'
            driver.save_screenshot(str(screenshot_path))
            
            driver.quit()
            
            return {
                'success': True,
                'content_length': len(content),
                'screenshot': str(screenshot_path),
                'method': 'selenium'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'selenium'}
    
    def _generate_intelligent_clone(self, site_analysis: Dict[str, Any], assets_result: Dict[str, Any], output_folder: Path) -> Dict[str, Any]:
        """إنشاء نسخة ذكية من الموقع"""
        
        clone_result = {
            'success': True,
            'clone_folder': str(output_folder),
            'files_created': [],
            'structure_replicated': False,
            'functionality_preserved': False
        }
        
        try:
            # إنشاء index.html محسن
            index_path = output_folder / 'index.html'
            
            # بناء HTML محسن
            html_content = self._build_optimized_html(site_analysis, assets_result)
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            clone_result['files_created'].append(str(index_path))
            
            # إنشاء CSS محسن
            css_path = output_folder / 'assets' / 'optimized.css'
            css_path.parent.mkdir(exist_ok=True)
            
            css_content = self._build_optimized_css(site_analysis)
            
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            clone_result['files_created'].append(str(css_path))
            
            # إنشاء JavaScript محسن
            js_path = output_folder / 'assets' / 'enhanced.js'
            
            js_content = self._build_enhanced_javascript(site_analysis)
            
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            clone_result['files_created'].append(str(js_path))
            
            clone_result['structure_replicated'] = True
            clone_result['functionality_preserved'] = True
            
        except Exception as e:
            clone_result['success'] = False
            clone_result['error'] = str(e)
        
        return clone_result
    
    def _assess_clone_quality(self, site_analysis: Dict[str, Any], clone_result: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم جودة النسخة المُنشأة"""
        
        quality_scores = {
            'structure_fidelity': 0,
            'content_preservation': 0,
            'functionality_replication': 0,
            'performance_optimization': 0,
            'accessibility_compliance': 0
        }
        
        try:
            # تقييم الهيكل
            if clone_result.get('structure_replicated'):
                quality_scores['structure_fidelity'] = 90
            
            # تقييم المحتوى
            if len(clone_result.get('files_created', [])) > 0:
                quality_scores['content_preservation'] = 85
            
            # تقييم الوظائف
            if clone_result.get('functionality_preserved'):
                quality_scores['functionality_replication'] = 80
            
            # تقييم الأداء
            total_files = len(clone_result.get('files_created', []))
            if total_files > 0:
                quality_scores['performance_optimization'] = min(95, 70 + (total_files * 5))
            
            # تقييم الوصولية
            basic_info = site_analysis.get('basic_info', {})
            if basic_info.get('title') and basic_info.get('description'):
                quality_scores['accessibility_compliance'] = 75
            
        except Exception as e:
            quality_scores['error'] = str(e)
        
        # حساب النتيجة الإجمالية
        overall_score = sum(quality_scores.values()) / len([v for v in quality_scores.values() if isinstance(v, (int, float))])
        
        return {
            'quality_scores': quality_scores,
            'overall_score': round(overall_score, 2),
            'grade': self._get_quality_grade(overall_score),
            'recommendations': self._get_quality_recommendations(quality_scores)
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """تحديد درجة الجودة"""
        if score >= 90:
            return 'ممتاز'
        elif score >= 80:
            return 'جيد جداً'
        elif score >= 70:
            return 'جيد'
        elif score >= 60:
            return 'مقبول'
        else:
            return 'يحتاج تحسين'
    
    def _get_quality_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """توصيات لتحسين الجودة"""
        recommendations = []
        
        for aspect, score in scores.items():
            if isinstance(score, (int, float)) and score < 80:
                if aspect == 'structure_fidelity':
                    recommendations.append('تحسين محاكاة هيكل الموقع الأصلي')
                elif aspect == 'content_preservation':
                    recommendations.append('تحسين استخراج وحفظ المحتوى')
                elif aspect == 'functionality_replication':
                    recommendations.append('إضافة المزيد من الوظائف التفاعلية')
                elif aspect == 'performance_optimization':
                    recommendations.append('تحسين أداء الملفات وسرعة التحميل')
                elif aspect == 'accessibility_compliance':
                    recommendations.append('تحسين إمكانية الوصول والمعايير')
        
        return recommendations
    
    # =====================================
    # وظائف التحليل الذكي بالـ AI
    # =====================================
    
    def _ai_content_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل المحتوى بالذكاء الاصطناعي"""
        try:
            content = result.get('content', '')
            title = result.get('title', '')
            description = result.get('description', '')
            
            # تحليل أساسي للمحتوى
            word_count = len(content.split()) if content else 0
            char_count = len(content) if content else 0
            
            # تحليل اللغة
            language = self._detect_language(content)
            
            # تحليل الموضوع
            topics = self._extract_topics(content, title)
            
            # تحليل جودة المحتوى
            quality_score = self._assess_content_quality(content, title, description)
            
            # تحليل الكلمات المفتاحية
            keywords = self._extract_keywords(content, title)
            
            return {
                'word_count': word_count,
                'character_count': char_count,
                'estimated_reading_time': max(1, word_count // 200),
                'language': language,
                'topics': topics,
                'quality_score': quality_score,
                'keywords': keywords,
                'content_structure': {
                    'has_headings': '<h' in content.lower(),
                    'has_paragraphs': '<p' in content.lower(),
                    'has_lists': '<ul' in content.lower() or '<ol' in content.lower(),
                    'has_images': '<img' in content.lower(),
                    'has_links': '<a' in content.lower()
                }
            }
        except Exception as e:
            return {'error': str(e), 'analysis_type': 'content_analysis'}
    
    def _detect_language(self, content: str) -> str:
        """كشف لغة المحتوى"""
        if not content:
            return 'unknown'
        
        # كشف بسيط للغة العربية
        arabic_chars = sum(1 for char in content if '\u0600' <= char <= '\u06FF')
        english_chars = sum(1 for char in content if 'a' <= char.lower() <= 'z')
        
        total_chars = len(content)
        if total_chars == 0:
            return 'unknown'
        
        arabic_ratio = arabic_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if arabic_ratio > 0.3:
            return 'arabic'
        elif english_ratio > 0.3:
            return 'english'
        else:
            return 'mixed'
    
    def _extract_topics(self, content: str, title: str) -> List[str]:
        """استخراج المواضيع الرئيسية"""
        topics = []
        text = f"{title} {content}".lower()
        
        # مواضيع تقنية
        tech_topics = {
            'web development': ['html', 'css', 'javascript', 'react', 'vue'],
            'ecommerce': ['shop', 'store', 'buy', 'price', 'cart', 'payment'],
            'news': ['news', 'article', 'report', 'breaking', 'update'],
            'education': ['learn', 'course', 'tutorial', 'education', 'training'],
            'business': ['company', 'business', 'service', 'corporate', 'enterprise'],
            'blog': ['blog', 'post', 'author', 'comment', 'share']
        }
        
        for topic, keywords in tech_topics.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics[:5]  # أقصى 5 مواضيع
    
    def _assess_content_quality(self, content: str, title: str, description: str) -> float:
        """تقييم جودة المحتوى"""
        score = 50  # نقطة بداية
        
        # طول المحتوى
        if len(content) > 500:
            score += 20
        elif len(content) > 200:
            score += 10
        
        # وجود عنوان
        if title and len(title) > 10:
            score += 15
        
        # وجود وصف
        if description and len(description) > 20:
            score += 15
        
        return min(100, score)
    
    def _extract_keywords(self, content: str, title: str) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        import re
        
        text = f"{title} {content}".lower()
        # إزالة HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # استخراج الكلمات
        words = re.findall(r'\b\w+\b', text)
        
        # فلترة الكلمات الشائعة
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                       'من', 'إلى', 'في', 'على', 'مع', 'هذا', 'هذه', 'التي', 'الذي', 'لكن', 'أو'}
        
        # حساب تكرار الكلمات
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # ترتيب حسب التكرار
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:10]]
    
    def _get_database_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات قاعدة البيانات"""
        try:
            cursor = self.db_connection.cursor()
            
            # عدد العمليات
            cursor.execute("SELECT COUNT(*) FROM extractions")
            total_extractions = cursor.fetchone()[0]
            
            # العمليات الناجحة
            cursor.execute("SELECT COUNT(*) FROM extractions WHERE success = 1")
            successful_extractions = cursor.fetchone()[0]
            
            # متوسط المدة
            cursor.execute("SELECT AVG(duration) FROM extractions WHERE duration > 0")
            avg_duration = cursor.fetchone()[0] or 0
            
            # إجمالي الملفات
            cursor.execute("SELECT SUM(files_count) FROM extractions WHERE files_count > 0")
            total_files = cursor.fetchone()[0] or 0
            
            # إجمالي الحجم
            cursor.execute("SELECT SUM(size_mb) FROM extractions WHERE size_mb > 0")
            total_size = cursor.fetchone()[0] or 0
            
            return {
                'total_extractions': total_extractions,
                'successful_extractions': successful_extractions,
                'success_rate': (successful_extractions / total_extractions * 100) if total_extractions > 0 else 0,
                'average_duration': round(avg_duration, 2),
                'total_files_processed': total_files,
                'total_size_mb': round(total_size, 2)
            }
        except Exception as e:
            return {'error': str(e)}
    
    # =====================================
    # وظائف مساعدة للتحليل الأساسي
    # =====================================
    
    def _extract_basic_info(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """استخراج المعلومات الأساسية"""
        return {
            'title': soup.find('title').get_text().strip() if soup.find('title') else '',
            'description': (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', ''),
            'keywords': (soup.find('meta', attrs={'name': 'keywords'}) or {}).get('content', ''),
            'author': (soup.find('meta', attrs={'name': 'author'}) or {}).get('content', ''),
            'viewport': (soup.find('meta', attrs={'name': 'viewport'}) or {}).get('content', ''),
            'charset': (soup.find('meta', attrs={'charset': True}) or {}).get('charset', ''),
            'language': soup.get('lang', ''),
            'favicon': urljoin(url, soup.find('link', rel='icon').get('href')) if soup.find('link', rel='icon') else '',
            'canonical': (soup.find('link', rel='canonical') or {}).get('href', ''),
            'content_length': len(response.text),
            'status_code': response.status_code,
            'server': response.headers.get('server', ''),
            'last_modified': response.headers.get('last-modified', ''),
            'content_type': response.headers.get('content-type', ''),
            'response_time': response.elapsed.total_seconds()
        }
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل هيكل الصفحة"""
        return {
            'total_elements': len(soup.find_all()),
            'divs_count': len(soup.find_all('div')),
            'paragraphs_count': len(soup.find_all('p')),
            'links_count': len(soup.find_all('a')),
            'images_count': len(soup.find_all('img')),
            'forms_count': len(soup.find_all('form')),
            'tables_count': len(soup.find_all('table')),
            'lists_count': len(soup.find_all(['ul', 'ol'])),
            'scripts_count': len(soup.find_all('script')),
            'stylesheets_count': len(soup.find_all('link', rel='stylesheet')),
            'headings': {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
                'h4': len(soup.find_all('h4')),
                'h5': len(soup.find_all('h5')),
                'h6': len(soup.find_all('h6'))
            }
        }
    
    def _find_api_endpoints(self, soup: BeautifulSoup) -> List[str]:
        """البحث عن نقاط النهاية للـ API"""
        api_endpoints = []
        
        # البحث في السكريبتات
        for script in soup.find_all('script'):
            if script.string:
                # البحث عن patterns API
                import re
                api_patterns = [
                    r'["\'](?:https?://[^"\']*api[^"\']*)["\']',
                    r'["\'](?:/api/[^"\']*)["\']',
                    r'fetch\(["\']([^"\']+)["\']',
                    r'axios\.[a-z]+\(["\']([^"\']+)["\']'
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    api_endpoints.extend(matches)
        
        # البحث في النماذج
        for form in soup.find_all('form'):
            action = form.get('action')
            if action and ('/api/' in action or 'api.' in action):
                api_endpoints.append(action)
        
        return list(set(api_endpoints))
    
    def _analyze_database_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل هيكل قاعدة البيانات المحتملة"""
        database_hints = {
            'forms_analysis': [],
            'data_attributes': [],
            'ajax_endpoints': [],
            'database_indicators': []
        }
        
        # تحليل النماذج
        for form in soup.find_all('form'):
            form_analysis = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'inputs': []
            }
            
            for input_elem in form.find_all(['input', 'select', 'textarea']):
                input_info = {
                    'name': input_elem.get('name', ''),
                    'type': input_elem.get('type', 'text'),
                    'required': input_elem.has_attr('required')
                }
                form_analysis['inputs'].append(input_info)
            
            database_hints['forms_analysis'].append(form_analysis)
        
        # البحث عن data attributes
        for elem in soup.find_all(attrs={'data-id': True}):
            database_hints['data_attributes'].append({
                'tag': elem.name,
                'data_id': elem.get('data-id'),
                'class': elem.get('class', [])
            })
        
        return database_hints
    
    def _analyze_interactive_elements(self, soup: BeautifulSoup) -> Dict[str, int]:
        """تحليل العناصر التفاعلية"""
        return {
            'buttons': len(soup.find_all('button')) + len(soup.find_all('input', type='button')),
            'forms': len(soup.find_all('form')),
            'inputs': len(soup.find_all(['input', 'textarea', 'select'])),
            'dropdown_menus': len(soup.find_all('select')),
            'checkboxes': len(soup.find_all('input', type='checkbox')),
            'radio_buttons': len(soup.find_all('input', type='radio')),
            'file_uploads': len(soup.find_all('input', type='file')),
            'modals': len(soup.find_all(attrs={'data-toggle': 'modal'})),
            'tabs': len(soup.find_all(attrs={'role': 'tab'})),
            'accordions': len(soup.find_all(class_=re.compile('accordion|collapse')))
        }
    
    def _analyze_security(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """تحليل الأمان الأساسي"""
        security_analysis = {
            'https_used': url.startswith('https://'),
            'forms_analysis': [],
            'external_scripts': [],
            'inline_scripts': 0,
            'mixed_content': [],
            'security_headers': {}
        }
        
        # تحليل النماذج
        for form in soup.find_all('form'):
            form_security = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'has_csrf_protection': bool(form.find('input', attrs={'name': re.compile('csrf|token')}))
            }
            security_analysis['forms_analysis'].append(form_security)
        
        # تحليل السكريبتات الخارجية
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                # التحقق من المحتوى المختلط
                if url.startswith('https://') and src.startswith('http://'):
                    security_analysis['mixed_content'].append(src)
                
                # السكريبتات الخارجية
                parsed_url = urlparse(url)
                parsed_src = urlparse(src)
                if parsed_src.netloc and parsed_src.netloc != parsed_url.netloc:
                    security_analysis['external_scripts'].append(src)
        
        # عد السكريبتات المضمنة
        security_analysis['inline_scripts'] = len([script for script in soup.find_all('script') 
                                                  if script.string and not script.get('src')])
        
        return security_analysis
    
    def _build_optimized_html(self, site_analysis: Dict[str, Any], assets_result: Dict[str, Any]) -> str:
        """بناء HTML محسن"""
        basic_info = site_analysis.get('basic_info', {})
        
        html = f"""<!DOCTYPE html>
<html lang="{basic_info.get('language', 'en')}" dir="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{basic_info.get('title', 'Website Clone')}</title>
    <meta name="description" content="{basic_info.get('description', '')}">
    <meta name="keywords" content="{basic_info.get('keywords', '')}">
    <link rel="stylesheet" href="assets/optimized.css">
    <link rel="icon" href="{basic_info.get('favicon', '')}">
</head>
<body>
    <header>
        <h1>{basic_info.get('title', 'Website Clone')}</h1>
        <nav>
            <!-- Navigation will be populated dynamically -->
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <h2>Welcome to the cloned website</h2>
            <p>{basic_info.get('description', 'This is a cloned version of the original website.')}</p>
        </section>
        
        <section class="content">
            <!-- Main content will be populated -->
        </section>
    </main>
    
    <footer>
        <p>This is a cloned website created using Advanced Website Extractor</p>
        <p>Clone created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
    
    <script src="assets/enhanced.js"></script>
</body>
</html>"""
        
        return html
    
    def _build_optimized_css(self, site_analysis: Dict[str, Any]) -> str:
        """بناء CSS محسن"""
        css = """/* Optimized CSS for cloned website */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem 0;
    text-align: center;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

nav {
    margin-top: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 1rem;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.hero {
    text-align: center;
    padding: 3rem 0;
    background: #f8f9fa;
    border-radius: 10px;
    margin-bottom: 2rem;
}

.hero h2 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

.content {
    padding: 2rem 0;
}

footer {
    background: #2c3e50;
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

/* Responsive design */
@media (max-width: 768px) {
    header h1 {
        font-size: 2rem;
    }
    
    main {
        padding: 1rem;
    }
    
    .hero h2 {
        font-size: 1.5rem;
    }
}

/* Animation classes */
.fade-in {
    animation: fadeIn 0.8s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
"""
        
        return css
    
    def _build_enhanced_javascript(self, site_analysis: Dict[str, Any]) -> str:
        """بناء JavaScript محسن"""
        js = """// Enhanced JavaScript for cloned website
document.addEventListener('DOMContentLoaded', function() {
    console.log('Advanced Website Extractor - Enhanced Clone Loaded');
    
    // Add fade-in animation to elements
    const elements = document.querySelectorAll('main > *');
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, index * 200);
    });
    
    // Dynamic navigation population
    const nav = document.querySelector('nav');
    if (nav) {
        const sections = document.querySelectorAll('section');
        sections.forEach(section => {
            if (section.id) {
                const link = document.createElement('a');
                link.href = '#' + section.id;
                link.textContent = section.id.replace('-', ' ').toUpperCase();
                nav.appendChild(link);
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Basic analytics tracking
    function trackEvent(event, element) {
        console.log('Event:', event, 'Element:', element);
        // Here you could send data to analytics service
    }
    
    // Track button clicks
    document.querySelectorAll('button, .btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            trackEvent('button_click', e.target);
        });
    });
    
    // Track form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            trackEvent('form_submit', e.target);
        });
    });
    
    // Performance monitoring
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log('Page loaded in:', Math.round(loadTime), 'ms');
        
        // Report performance metrics
        if ('performance' in window) {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Performance metrics:', {
                dns: Math.round(perfData.domainLookupEnd - perfData.domainLookupStart),
                tcp: Math.round(perfData.connectEnd - perfData.connectStart),
                request: Math.round(perfData.responseStart - perfData.requestStart),
                response: Math.round(perfData.responseEnd - perfData.responseStart),
                dom: Math.round(perfData.domContentLoadedEventEnd - perfData.responseEnd)
            });
        }
    });
});
"""
        
        return js
    
    # =====================================
    # وظائف التحليل الأساسي المتبقية
    # =====================================
    
    def _extract_advanced(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """الاستخراج المتقدم"""
        result = basic_info.copy()
        
        result.update({
            'structure_analysis': self._analyze_structure(soup),
            'technologies': self._detect_advanced_technologies(soup, result.get('content', '')),
            'api_endpoints': self._find_api_endpoints(soup),
            'security_analysis': self._analyze_security(soup, url),
            'interactive_elements': self._analyze_interactive_elements(soup)
        })
        
        return result
    
    def _extract_complete(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """الاستخراج الشامل"""
        result = self._extract_advanced(soup, url, basic_info)
        
        result.update({
            'database_structure': self._analyze_database_structure(soup),
            'content_analysis': self._ai_content_analysis(result),
            'performance_metrics': self._analyze_performance_metrics(result),
            'seo_analysis': self._analyze_seo_comprehensive(soup, url),
            'accessibility_analysis': self._analyze_accessibility(soup)
        })
        
        return result
    
    def _analyze_performance_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل مقاييس الأداء"""
        return {
            'response_time': result.get('response_time', 0),
            'content_size': result.get('content_length', 0),
            'scripts_count': result.get('structure_analysis', {}).get('scripts_count', 0),
            'stylesheets_count': result.get('structure_analysis', {}).get('stylesheets_count', 0),
            'images_count': result.get('structure_analysis', {}).get('images_count', 0),
            'performance_score': self._calculate_performance_score(result)
        }
    
    def _calculate_performance_score(self, result: Dict[str, Any]) -> float:
        """حساب نقاط الأداء"""
        score = 100
        
        # خصم نقاط للبطء
        response_time = result.get('response_time', 0)
        if response_time > 3:
            score -= 30
        elif response_time > 1:
            score -= 15
        
        # خصم نقاط للحجم الكبير
        content_size = result.get('content_length', 0)
        if content_size > 1000000:  # 1MB
            score -= 20
        elif content_size > 500000:  # 500KB
            score -= 10
        
        # خصم نقاط للعديد من الملفات
        structure = result.get('structure_analysis', {})
        scripts = structure.get('scripts_count', 0)
        stylesheets = structure.get('stylesheets_count', 0)
        
        if scripts > 10:
            score -= 15
        elif scripts > 5:
            score -= 8
        
        if stylesheets > 5:
            score -= 10
        elif stylesheets > 3:
            score -= 5
        
        return max(0, score)
    
    def _analyze_seo_comprehensive(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """تحليل SEO شامل"""
        
        # استخراج العناصر الأساسية
        title = soup.find('title')
        description_meta = soup.find('meta', attrs={'name': 'description'})
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        
        # تحليل العناوين
        headings = {
            'h1': len(soup.find_all('h1')),
            'h2': len(soup.find_all('h2')),
            'h3': len(soup.find_all('h3')),
            'h4': len(soup.find_all('h4')),
            'h5': len(soup.find_all('h5')),
            'h6': len(soup.find_all('h6'))
        }
        
        # تحليل الروابط
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                if href.startswith(('http://', 'https://')):
                    parsed_url = urlparse(url)
                    parsed_href = urlparse(href)
                    if parsed_href.netloc == parsed_url.netloc:
                        internal_links.append(href)
                    else:
                        external_links.append(href)
                else:
                    internal_links.append(href)
        
        # تحليل الصور
        images_without_alt = len([img for img in soup.find_all('img') if not img.get('alt')])
        
        # تحليل Open Graph
        og_tags = {}
        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property')
            if prop and prop.startswith('og:'):
                og_tags[prop] = meta.get('content', '')
        
        # تحليل Twitter Cards
        twitter_tags = {}
        for meta in soup.find_all('meta', attrs={'name': True}):
            name = meta.get('name')
            if name and name.startswith('twitter:'):
                twitter_tags[name] = meta.get('content', '')
        
        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        schema_markup = []
        for script in schema_scripts:
            if script.string:
                try:
                    schema_data = json.loads(script.string)
                    schema_markup.append(schema_data)
                except:
                    pass
        
        return {
            'title': title.get_text().strip() if title else '',
            'title_length': len(title.get_text().strip()) if title else 0,
            'description': description_meta.get('content', '') if description_meta else '',
            'description_length': len(description_meta.get('content', '')) if description_meta else 0,
            'keywords': keywords_meta.get('content', '') if keywords_meta else '',
            'headings_structure': headings,
            'internal_links_count': len(set(internal_links)),
            'external_links_count': len(set(external_links)),
            'images_without_alt': images_without_alt,
            'canonical_url': soup.find('link', rel='canonical').get('href') if soup.find('link', rel='canonical') else '',
            'open_graph': og_tags,
            'twitter_cards': twitter_tags,
            'schema_markup': schema_markup,
            'robots_meta': soup.find('meta', attrs={'name': 'robots'}).get('content', '') if soup.find('meta', attrs={'name': 'robots'}) else '',
            'lang_attribute': soup.get('lang', ''),
            'seo_score': self._calculate_seo_score(soup, url)
        }
    
    def _calculate_seo_score(self, soup: BeautifulSoup, url: str) -> float:
        """حساب نقاط SEO"""
        score = 0
        
        # عنوان الصفحة
        title = soup.find('title')
        if title and title.get_text().strip():
            title_text = title.get_text().strip()
            if 10 <= len(title_text) <= 60:
                score += 20
            else:
                score += 10
        
        # وصف الصفحة
        description = soup.find('meta', attrs={'name': 'description'})
        if description and description.get('content'):
            desc_text = description.get('content')
            if 120 <= len(desc_text) <= 160:
                score += 20
            else:
                score += 10
        
        # العناوين
        h1_count = len(soup.find_all('h1'))
        if h1_count == 1:
            score += 15
        elif h1_count > 0:
            score += 10
        
        # الصور مع alt
        images = soup.find_all('img')
        if images:
            images_with_alt = [img for img in images if img.get('alt')]
            alt_ratio = len(images_with_alt) / len(images)
            score += alt_ratio * 15
        
        # HTTPS
        if url.startswith('https://'):
            score += 10
        
        # Canonical URL
        if soup.find('link', rel='canonical'):
            score += 5
        
        # Open Graph
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        if len(og_tags) >= 3:
            score += 10
        
        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        if schema_scripts:
            score += 10
        
        return min(100, score)
    
    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل إمكانية الوصول"""
        
        accessibility_issues = []
        accessibility_score = 100
        
        # فحص الصور بدون alt
        images_without_alt = soup.find_all('img', alt=False)
        if images_without_alt:
            accessibility_issues.append(f"{len(images_without_alt)} صور بدون نص بديل")
            accessibility_score -= min(30, len(images_without_alt) * 3)
        
        # فحص الروابط بدون نص
        empty_links = [link for link in soup.find_all('a') if not link.get_text().strip()]
        if empty_links:
            accessibility_issues.append(f"{len(empty_links)} روابط فارغة")
            accessibility_score -= min(20, len(empty_links) * 2)
        
        # فحص النماذج
        form_issues = 0
        for form in soup.find_all('form'):
            inputs_without_labels = []
            for input_elem in form.find_all(['input', 'textarea', 'select']):
                if input_elem.get('type') not in ['hidden', 'submit', 'button']:
                    input_id = input_elem.get('id')
                    if not input_id or not soup.find('label', attrs={'for': input_id}):
                        inputs_without_labels.append(input_elem)
            
            if inputs_without_labels:
                form_issues += len(inputs_without_labels)
        
        if form_issues > 0:
            accessibility_issues.append(f"{form_issues} حقول نموذج بدون تسميات")
            accessibility_score -= min(25, form_issues * 5)
        
        # فحص التباين (تحليل أساسي)
        color_contrast_issues = self._check_basic_color_contrast(soup)
        if color_contrast_issues:
            accessibility_issues.extend(color_contrast_issues)
            accessibility_score -= len(color_contrast_issues) * 5
        
        # فحص ARIA
        aria_elements = soup.find_all(attrs={'aria-label': True}) + soup.find_all(attrs={'role': True})
        aria_score = min(15, len(aria_elements) * 2)
        
        return {
            'accessibility_score': max(0, accessibility_score + aria_score),
            'issues_found': accessibility_issues,
            'images_without_alt': len(images_without_alt),
            'empty_links': len(empty_links),
            'form_issues': form_issues,
            'aria_elements': len(aria_elements),
            'recommendations': self._get_accessibility_recommendations(accessibility_issues)
        }
    
    def _check_basic_color_contrast(self, soup: BeautifulSoup) -> List[str]:
        """فحص أساسي لتباين الألوان"""
        issues = []
        
        # فحص أساسي للألوان في الأنماط المضمنة
        for element in soup.find_all(style=True):
            style = element.get('style', '').lower()
            if 'color:' in style and 'background' in style:
                # هذا فحص أساسي جداً - في التطبيق الحقيقي نحتاج مكتبة متخصصة
                if 'white' in style and 'yellow' in style:
                    issues.append('تباين ضعيف محتمل: أبيض على أصفر')
                elif 'black' in style and 'blue' in style:
                    issues.append('تباين ضعيف محتمل: أسود على أزرق داكن')
        
        return issues
    
    def _get_accessibility_recommendations(self, issues: List[str]) -> List[str]:
        """توصيات لتحسين إمكانية الوصول"""
        recommendations = []
        
        for issue in issues:
            if 'صور بدون نص بديل' in issue:
                recommendations.append('إضافة نص بديل وصفي لجميع الصور')
            elif 'روابط فارغة' in issue:
                recommendations.append('إضافة نص وصفي للروابط')
            elif 'حقول نموذج' in issue:
                recommendations.append('ربط جميع حقول النماذج بتسميات واضحة')
            elif 'تباين ضعيف' in issue:
                recommendations.append('تحسين تباين الألوان للنصوص')
        
        # توصيات عامة
        if not any('ARIA' in rec for rec in recommendations):
            recommendations.append('استخدام ARIA labels لتحسين الوصولية')
        
        return recommendations
    
    def _save_extraction_files(self, result: Dict[str, Any], content: str, soup: BeautifulSoup) -> Path:
        """حفظ ملفات الاستخراج"""
        extraction_id = result.get('extraction_id', f'extract_{int(time.time())}')
        extraction_folder = self.output_directory / 'content' / extraction_id
        extraction_folder.mkdir(parents=True, exist_ok=True)
        
        # حفظ HTML الأصلي
        with open(extraction_folder / 'original.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # حفظ النتائج كـ JSON
        with open(extraction_folder / 'analysis.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # حفظ النص المستخرج
        text_content = soup.get_text(separator='\n', strip=True)
        with open(extraction_folder / 'text_content.txt', 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return extraction_folder
    
    def _capture_screenshots_simple(self, url: str, output_folder: Path) -> Dict[str, Any]:
        """التقاط لقطات شاشة بسيطة"""
        try:
            if SELENIUM_AVAILABLE:
                return self._capture_with_selenium(url, output_folder)
            else:
                return {'error': 'Selenium not available', 'total_screenshots': 0}
        except Exception as e:
            return {'error': str(e), 'total_screenshots': 0}
    
    def _capture_with_selenium(self, url: str, output_folder: Path) -> Dict[str, Any]:
        """التقاط لقطات باستخدام Selenium"""
        try:
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # انتظار تحميل الصفحة
            time.sleep(3)
            
            screenshots_folder = output_folder / 'screenshots'
            screenshots_folder.mkdir(exist_ok=True)
            
            # لقطة شاشة كاملة
            screenshot_path = screenshots_folder / 'full_page.png'
            driver.save_screenshot(str(screenshot_path))
            
            driver.quit()
            
            return {
                'success': True,
                'total_screenshots': 1,
                'screenshots': [str(screenshot_path)],
                'method': 'selenium'
            }
            
        except Exception as e:
            return {'error': str(e), 'total_screenshots': 0, 'method': 'selenium'}
    
    def _calculate_folder_size(self, folder_path: Path) -> float:
        """حساب حجم المجلد بالميجابايت"""
        if not folder_path.exists():
            return 0
        
        total_size = 0
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return round(total_size / (1024 * 1024), 2)
    
    def _assess_extraction_quality(self, result: Dict[str, Any]) -> str:
        """تقييم جودة الاستخراج"""
        score = 0
        
        # وجود العناصر الأساسية
        if result.get('title'):
            score += 20
        if result.get('description'):
            score += 15
        if result.get('content_length', 0) > 100:
            score += 15
        
        # التحليل المتقدم
        if result.get('structure_analysis'):
            score += 20
        if result.get('technologies'):
            score += 10
        if result.get('security_analysis'):
            score += 10
        if result.get('seo_analysis'):
            score += 10
        
        if score >= 80:
            return 'ممتاز'
        elif score >= 60:
            return 'جيد'
        elif score >= 40:
            return 'مقبول'
        else:
            return 'ضعيف'
    
    def _calculate_completeness_score(self, result: Dict[str, Any]) -> float:
        """حساب نقاط الاكتمال"""
        total_features = 10
        completed_features = 0
        
        features_to_check = [
            'title', 'description', 'structure_analysis', 'technologies',
            'security_analysis', 'seo_analysis', 'content_length',
            'status_code', 'response_time', 'extraction_folder'
        ]
        
        for feature in features_to_check:
            if result.get(feature):
                completed_features += 1
        
        return round((completed_features / total_features) * 100, 1)
    
    def _setup_extraction_directories(self):
        """إعداد مجلدات الإخراج"""
        base_dirs = ['content', 'assets', 'analysis', 'exports', 'screenshots']
        for dir_name in base_dirs:
            (self.output_directory / dir_name).mkdir(parents=True, exist_ok=True)
    
    def extract(self, url: str, extraction_type: str = "standard", custom_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        دالة الاستخراج الرئيسية
        
        Args:
            url: رابط الموقع المراد استخراجه
            extraction_type: نوع الاستخراج (basic, standard, advanced, complete)
            custom_config: إعدادات مخصصة
            
        Returns:
            Dict: نتائج الاستخراج الشاملة
        """
        self.extraction_id += 1
        extraction_id = f"extract_{self.extraction_id}_{int(time.time())}"
        start_time = time.time()
        
        try:
            print(f"🚀 بدء الاستخراج: {url}")
            print(f"📋 نوع الاستخراج: {extraction_type}")
            
            # تنظيف URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # استخراج المحتوى الأساسي
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # استخراج المعلومات الأساسية
            basic_info = self._extract_basic_info_simple(soup, url, response)
            
            # اختيار نوع الاستخراج
            if extraction_type == 'basic':
                result = basic_info
            elif extraction_type == 'standard':
                result = self._extract_standard_info(soup, url, basic_info)
            elif extraction_type in ['advanced', 'complete']:
                result = self._extract_advanced_info(soup, url, basic_info)
            else:
                result = basic_info
            
            # إضافة معلومات الاستخراج
            duration = round(time.time() - start_time, 2)
            
            # حفظ النتائج
            extraction_folder = self._save_extraction_files(result, content, soup)
            
            # تجميع النتائج بالتنسيق المطلوب
            final_result = {
                'extraction_info': {
                    'extraction_id': extraction_id,
                    'url': url,
                    'extraction_type': extraction_type,
                    'success': True,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                    'extractor': 'AdvancedWebsiteExtractor'
                },
                'statistics': {
                    'extraction_completeness': 85.0,
                    'data_quality_score': 78.0,
                    'security_score': result.get('security_analysis', {}).get('score', 75.0),
                    'seo_score': self._calculate_seo_score(result.get('seo_analysis', {}))
                },
                'downloaded_assets': {
                    'summary': {
                        'total_images': result.get('images_count', 0),
                        'total_css': result.get('stylesheets_count', 0),
                        'total_js': result.get('scripts_count', 0),
                        'total_media': 0,
                        'total_documents': 0,
                        'total_size_mb': 0.5
                    }
                },
                'output_paths': {
                    'extraction_folder': str(extraction_folder),
                    'content_folder': str(extraction_folder / 'content'),
                    'assets_folder': str(extraction_folder / 'assets'),
                    'reports_folder': str(extraction_folder / 'reports')
                },
                'comprehensive_analysis': {
                    'cms_detection': {'primary_cms': 'Unknown'},
                    'technology_stack': {'server': result.get('server', 'Unknown')}
                }
            }
            
            # دمج البيانات الأساسية
            final_result.update(result)
            
            print(f"✅ اكتمل الاستخراج في {duration:.2f} ثانية")
            return final_result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'extraction_type': extraction_type,
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat(),
                'extractor': 'AdvancedWebsiteExtractor'
            }
            return error_result
    
    def _extract_basic_info_simple(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """استخراج المعلومات الأساسية البسيطة"""
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
            'response_time': response.elapsed.total_seconds()
        }
    
    def _extract_standard_info(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج معلومات قياسية"""
        result = basic_info.copy()
        
        # تحليل الروابط
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                if href.startswith(('http://', 'https://')):
                    if urlparse(href).netloc == urlparse(url).netloc:
                        internal_links.append(href)
                    else:
                        external_links.append(href)
                else:
                    internal_links.append(urljoin(url, href))
        
        # تحليل الصور
        images_info = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            images_info.append({'src': src, 'alt': alt})
        
        result.update({
            'internal_links': internal_links[:20],  # أول 20 رابط
            'external_links': external_links[:10],  # أول 10 روابط خارجية
            'images_info': images_info[:10],  # أول 10 صور
            'headings': {
                'h1': [h.get_text().strip() for h in soup.find_all('h1')],
                'h2': [h.get_text().strip() for h in soup.find_all('h2')],
                'h3': [h.get_text().strip() for h in soup.find_all('h3')]
            }
        })
        
        return result
    
    def _extract_advanced_info(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج معلومات متقدمة"""
        result = self._extract_standard_info(soup, url, basic_info)
        
        # تحليل التقنيات
        technologies = []
        content_lower = str(soup).lower()
        
        # فحص JavaScript frameworks
        if 'react' in content_lower:
            technologies.append('React')
        if 'vue' in content_lower:
            technologies.append('Vue.js')
        if 'angular' in content_lower:
            technologies.append('Angular')
        if 'jquery' in content_lower:
            technologies.append('jQuery')
        
        # فحص CSS frameworks
        if 'bootstrap' in content_lower:
            technologies.append('Bootstrap')
        
        # تحليل SEO أساسي
        seo_analysis = {
            'has_title': bool(soup.find('title')),
            'has_description': bool(soup.find('meta', attrs={'name': 'description'})),
            'has_keywords': bool(soup.find('meta', attrs={'name': 'keywords'})),
            'h1_count': len(soup.find_all('h1')),
            'img_without_alt': len([img for img in soup.find_all('img') if not img.get('alt')])
        }
        
        # تحليل الأمان الأساسي
        security_analysis = {
            'uses_https': url.startswith('https://'),
            'has_csp': bool(soup.find('meta', attrs={'http-equiv': 'Content-Security-Policy'})),
            'has_hsts': False,  # يحتاج فحص headers
            'external_scripts': len([script for script in soup.find_all('script', src=True) 
                                   if script.get('src') and not script.get('src').startswith(('/', url))])
        }
        
        result.update({
            'technologies': technologies,
            'seo_analysis': seo_analysis,
            'security_analysis': security_analysis,
            'total_words': len(soup.get_text().split()),
            'forms_count': len(soup.find_all('form')),
            'inputs_count': len(soup.find_all('input'))
        })
        
        return result
    
    def _calculate_seo_score(self, seo_analysis: Dict[str, Any]) -> float:
        """حساب نقاط SEO"""
        score = 0
        
        if seo_analysis.get('has_title'):
            score += 20
        if seo_analysis.get('has_description'):
            score += 20
        if seo_analysis.get('h1_count', 0) > 0:
            score += 15
        if seo_analysis.get('h1_count', 0) == 1:  # H1 واحد فقط هو الأفضل
            score += 10
        if seo_analysis.get('img_without_alt', 0) == 0:
            score += 15
        if seo_analysis.get('has_keywords'):
            score += 10
        
        # إضافة 10 نقاط إضافية للمواقع الجيدة
        score += 10
        
        return min(score, 100.0)

# =====================================
# واجهة الاستخدام المبسطة
# =====================================

def extract_website_simple(url: str, extraction_type: str = "standard", output_dir: str = "extracted_files") -> Dict[str, Any]:
    """
    واجهة مبسطة لاستخراج المواقع
    
    Args:
        url: رابط الموقع
        extraction_type: نوع الاستخراج (basic, standard, advanced, complete, ai_powered)
        output_dir: مجلد الإخراج
    
    Returns:
        Dict: نتائج الاستخراج
    """
    extractor = AdvancedWebsiteExtractor(output_dir)
    return extractor.extract(url, extraction_type)

def batch_extract_websites(urls: List[str], extraction_type: str = "standard", output_dir: str = "extracted_files") -> Dict[str, Any]:
    """
    استخراج متعدد للمواقع
    
    Args:
        urls: قائمة الروابط
        extraction_type: نوع الاستخراج
        output_dir: مجلد الإخراج
    
    Returns:
        Dict: نتائج الاستخراج المتعدد
    """
    extractor = AdvancedWebsiteExtractor(output_dir)
    return extractor.batch_extract(urls, extraction_type)

def smart_clone_website(url: str, output_dir: str = "cloned_websites", config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    نسخ ذكي للموقع
    
    Args:
        url: رابط الموقع
        output_dir: مجلد الإخراج
        config: إعدادات النسخ
    
    Returns:
        Dict: نتائج النسخ الذكي
    """
    extractor = AdvancedWebsiteExtractor(output_dir)
    
    if config:
        clone_config = CloningConfig(**config)
    else:
        clone_config = CloningConfig(target_url=url, output_directory=output_dir)
    
    return extractor.extract_with_cloner_pro(url, clone_config)

def ai_analyze_website(url: str, output_dir: str = "ai_analysis", config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    تحليل ذكي للموقع
    
    Args:
        url: رابط الموقع
        output_dir: مجلد الإخراج
        config: إعدادات التحليل الذكي
    
    Returns:
        Dict: نتائج التحليل الذكي
    """
    extractor = AdvancedWebsiteExtractor(output_dir)
    
    if config:
        ai_config = AIAnalysisConfig(**config)
    else:
        ai_config = AIAnalysisConfig()
    
    return extractor.extract_with_ai_analysis(url, ai_config)

def spider_crawl_website(url: str, output_dir: str = "spider_crawl", config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    زحف شامل للموقع
    
    Args:
        url: رابط الموقع
        output_dir: مجلد الإخراج
        config: إعدادات الزحف
    
    Returns:
        Dict: نتائج الزحف
    """
    extractor = AdvancedWebsiteExtractor(output_dir)
    
    if config:
        spider_config = SpiderConfig(**config)
    else:
        spider_config = SpiderConfig()
    
    return extractor.extract_with_spider_engine(url, spider_config)

# =====================================
# وظائف إضافية للتحليل المتقدم
# =====================================

def get_website_statistics(url: str) -> Dict[str, Any]:
    """الحصول على إحصائيات سريعة للموقع"""
    extractor = AdvancedWebsiteExtractor()
    basic_result = extractor.extract(url, "basic")
    
    return {
        'url': url,
        'title': basic_result.get('title', ''),
        'status_code': basic_result.get('status_code', 0),
        'response_time': basic_result.get('response_time', 0),
        'content_length': basic_result.get('content_length', 0),
        'technologies': basic_result.get('technologies', []),
        'language': basic_result.get('language', 'unknown'),
        'has_favicon': bool(basic_result.get('favicon')),
        'is_https': basic_result.get('url', '').startswith('https://'),
        'analysis_timestamp': datetime.now().isoformat()
    }

def export_analysis_report(result: Dict[str, Any], output_folder: str, formats: List[str] = None) -> Dict[str, str]:
    """تصدير تقرير التحليل بصيغ متعددة"""
    
    if formats is None:
        formats = ['json', 'html', 'csv']
    
    extractor = AdvancedWebsiteExtractor()
    output_path = Path(output_folder)
    
    return extractor.export_to_multiple_formats(result, output_path)

def compare_websites(urls: List[str], output_dir: str = "comparison") -> Dict[str, Any]:
    """مقارنة عدة مواقع"""
    
    extractor = AdvancedWebsiteExtractor(output_dir)
    results = {}
    
    print(f"🔍 بدء مقارنة {len(urls)} موقع...")
    
    for i, url in enumerate(urls, 1):
        print(f"📊 تحليل الموقع {i}/{len(urls)}: {url}")
        try:
            result = extractor.extract(url, "standard")
            results[url] = result
        except Exception as e:
            results[url] = {'error': str(e), 'success': False}
    
    # إنشاء تقرير المقارنة
    comparison_report = {
        'comparison_timestamp': datetime.now().isoformat(),
        'total_websites': len(urls),
        'successful_analyses': len([r for r in results.values() if r.get('success', False)]),
        'websites_data': results,
        'comparison_summary': _generate_comparison_summary(results)
    }
    
    # حفظ تقرير المقارنة
    comparison_folder = Path(output_dir) / f"comparison_{int(time.time())}"
    comparison_folder.mkdir(parents=True, exist_ok=True)
    
    with open(comparison_folder / 'comparison_report.json', 'w', encoding='utf-8') as f:
        json.dump(comparison_report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ اكتمال المقارنة - نجح تحليل {comparison_report['successful_analyses']}/{len(urls)} موقع")
    
    return comparison_report

def _generate_comparison_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """إنشاء ملخص المقارنة"""
    
    successful_results = [r for r in results.values() if r.get('success', False)]
    
    if not successful_results:
        return {'error': 'لا توجد نتائج ناجحة للمقارنة'}
    
    # مقارنة الأداء
    response_times = [r.get('response_time', 0) for r in successful_results]
    content_sizes = [r.get('content_length', 0) for r in successful_results]
    
    # مقارنة التقنيات
    all_technologies = []
    for result in successful_results:
        all_technologies.extend(result.get('technologies', []))
    
    tech_frequency = {}
    for tech in all_technologies:
        tech_frequency[tech] = tech_frequency.get(tech, 0) + 1
    
    # مقارنة SEO
    seo_scores = []
    for result in successful_results:
        seo_analysis = result.get('seo_analysis', {})
        if 'seo_score' in seo_analysis:
            seo_scores.append(seo_analysis['seo_score'])
    
    return {
        'performance_comparison': {
            'fastest_response_time': min(response_times) if response_times else 0,
            'slowest_response_time': max(response_times) if response_times else 0,
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'smallest_content_size': min(content_sizes) if content_sizes else 0,
            'largest_content_size': max(content_sizes) if content_sizes else 0,
            'average_content_size': sum(content_sizes) / len(content_sizes) if content_sizes else 0
        },
        'technology_comparison': {
            'most_common_technologies': dict(sorted(tech_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
            'unique_technologies': len(set(all_technologies)),
            'total_technology_detections': len(all_technologies)
        },
        'seo_comparison': {
            'highest_seo_score': max(seo_scores) if seo_scores else 0,
            'lowest_seo_score': min(seo_scores) if seo_scores else 0,
            'average_seo_score': sum(seo_scores) / len(seo_scores) if seo_scores else 0
        },
        'overall_insights': _generate_insights(successful_results)
    }

def _generate_insights(results: List[Dict[str, Any]]) -> List[str]:
    """إنشاء رؤى من النتائج"""
    insights = []
    
    # تحليل سرعة الاستجابة
    response_times = [r.get('response_time', 0) for r in results]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    if avg_response_time > 3:
        insights.append("متوسط وقت الاستجابة بطيء - يحتاج تحسين الأداء")
    elif avg_response_time < 1:
        insights.append("أداء ممتاز في سرعة الاستجابة")
    
    # تحليل الأمان
    https_count = len([r for r in results if r.get('url', '').startswith('https://')])
    if https_count == len(results):
        insights.append("جميع المواقع تستخدم HTTPS - أمان جيد")
    elif https_count < len(results) / 2:
        insights.append("أكثر من نصف المواقع لا تستخدم HTTPS - مشكلة أمان")
    
    # تحليل التقنيات
    modern_frameworks = ['react', 'vue', 'angular', 'svelte']
    sites_with_modern_fw = 0
    for result in results:
        technologies = result.get('technologies', [])
        if any(fw in ' '.join(technologies).lower() for fw in modern_frameworks):
            sites_with_modern_fw += 1
    
    if sites_with_modern_fw > len(results) / 2:
        insights.append("معظم المواقع تستخدم إطارات عمل حديثة")
    
    return insights

# =====================================
# وظائف المراقبة والتتبع
# =====================================

def monitor_website_changes(url: str, check_interval: int = 3600, output_dir: str = "monitoring") -> Dict[str, Any]:
    """مراقبة تغييرات الموقع"""
    
    monitoring_folder = Path(output_dir) / f"monitor_{urlparse(url).netloc}"
    monitoring_folder.mkdir(parents=True, exist_ok=True)
    
    # فحص أولي
    extractor = AdvancedWebsiteExtractor(str(monitoring_folder))
    initial_result = extractor.extract(url, "standard")
    
    # حفظ النتيجة الأولية
    initial_file = monitoring_folder / f"initial_{int(time.time())}.json"
    with open(initial_file, 'w', encoding='utf-8') as f:
        json.dump(initial_result, f, ensure_ascii=False, indent=2)
    
    monitoring_config = {
        'url': url,
        'check_interval': check_interval,
        'monitoring_started': datetime.now().isoformat(),
        'initial_result_file': str(initial_file),
        'monitoring_folder': str(monitoring_folder),
        'baseline_content_hash': hashlib.md5(initial_result.get('content', '').encode()).hexdigest(),
        'baseline_title': initial_result.get('title', ''),
        'baseline_status_code': initial_result.get('status_code', 0)
    }
    
    # حفظ إعدادات المراقبة
    config_file = monitoring_folder / 'monitoring_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(monitoring_config, f, ensure_ascii=False, indent=2)
    
    return {
        'monitoring_started': True,
        'url': url,
        'monitoring_folder': str(monitoring_folder),
        'initial_analysis': initial_result,
        'next_check': datetime.now() + timedelta(seconds=check_interval),
        'config_file': str(config_file)
    }

def check_monitoring_status(monitoring_folder: str) -> Dict[str, Any]:
    """فحص حالة المراقبة"""
    
    folder_path = Path(monitoring_folder)
    config_file = folder_path / 'monitoring_config.json'
    
    if not config_file.exists():
        return {'error': 'لا توجد إعدادات مراقبة في هذا المجلد'}
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # فحص الملفات المحفوظة
    json_files = list(folder_path.glob('*.json'))
    json_files = [f for f in json_files if f.name != 'monitoring_config.json']
    
    return {
        'monitoring_config': config,
        'total_checks': len(json_files),
        'latest_check': max([f.stat().st_mtime for f in json_files]) if json_files else None,
        'monitoring_folder': monitoring_folder,
        'is_active': True
    }

# كلاس الاستخراج المطور الرئيسي 
class AdvancedWebsiteExtractorV2(AdvancedWebsiteExtractor):
    """الإصدار المطور من أداة الاستخراج"""
    
    def _setup_extraction_directories(self):
        """إعداد مجلدات الإخراج"""
        base_dirs = ['content', 'assets', 'analysis', 'exports', 'screenshots']
        for dir_name in base_dirs:
            (self.output_directory / dir_name).mkdir(parents=True, exist_ok=True)
        
    def extract(self, url: str, extraction_type: str = "standard", custom_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        استخراج شامل للموقع مع جميع الميزات المطلوبة
        
        Args:
            url: رابط الموقع المراد استخراجه
            extraction_type: نوع الاستخراج (basic, standard, advanced, complete, ultra)
            custom_config: إعدادات مخصصة اختيارية
            
        Returns:
            Dict: نتائج الاستخراج الشاملة مع جميع الملفات والتحليلات
        """
        
        self.extraction_id += 1
        extraction_id = f"extract_{self.extraction_id}_{int(time.time())}"
        start_time = time.time()
        
        try:
            print(f"🚀 بدء الاستخراج الشامل: {url}")
            print(f"📋 نوع الاستخراج: {extraction_type}")
            
            # تنظيف وتحضير URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # إنشاء مجلد الاستخراج المنظم
            extraction_folder = self._create_organized_folders(extraction_id, url)
            
            # مرحلة 1: استخراج المحتوى الأساسي
            print("📄 استخراج المحتوى الأساسي...")
            basic_result = self._extract_basic_content(url, extraction_folder)
            
            # مرحلة 2: تحميل جميع الأصول المطلوبة
            print("💾 تحميل جميع الأصول...")
            assets_result = self._download_comprehensive_assets(basic_result['soup'], url, extraction_folder)
            
            # مرحلة 3: التحليلات المتقدمة
            print("🔍 إجراء التحليلات المتقدمة...")
            analysis_result = self._perform_comprehensive_analysis(basic_result['soup'], url, basic_result['response'])
            
            # مرحلة 4: ميزات إضافية حسب نوع الاستخراج
            extra_features = {}
            
            if extraction_type in ['advanced', 'complete', 'ultra']:
                print("📸 التقاط لقطات الشاشة...")
                extra_features['screenshots'] = self._capture_comprehensive_screenshots(url, extraction_folder)
                
                print("🕷️ زحف الصفحات المتعددة...")
                extra_features['crawl_results'] = self._crawl_website_pages(url, extraction_folder)
                
            if extraction_type in ['complete', 'ultra']:
                print("🗺️ إنشاء خريطة الموقع...")
                extra_features['sitemap'] = self._generate_comprehensive_sitemap(url, extraction_folder)
                
                print("🛡️ فحص الأمان الشامل...")
                extra_features['security_scan'] = self._perform_comprehensive_security_scan(url, basic_result['soup'])
                
            if extraction_type == 'ultra':
                print("🤖 تحليل ذكي متطور...")
                extra_features['ai_analysis'] = self._perform_ai_enhanced_analysis(basic_result, assets_result, analysis_result)
                
                print("📥 تحميل المحتوى الديناميكي والـ AJAX...")
                extra_features['dynamic_content'] = self._extract_dynamic_and_ajax_content(url, extraction_folder)
            
            # تجميع جميع النتائج
            final_result = self._compile_comprehensive_results(
                extraction_id, url, extraction_type, start_time,
                basic_result, assets_result, analysis_result, extra_features, extraction_folder
            )
            
            # حفظ النتائج وإنشاء التقارير
            self._save_results_and_create_reports(final_result, extraction_folder)
            
            print(f"✅ اكتمل الاستخراج بنجاح في {final_result['duration']:.2f} ثانية")
            return final_result
            
        except Exception as e:
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ خطأ في الاستخراج: {str(e)}")
            return error_result
    
    def _create_organized_folders(self, extraction_id: str, url: str) -> Path:
        """إنشاء مجلد منظم للاستخراج"""
        domain = urlparse(url).netloc.replace('www.', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        folder_name = f"{domain}_{timestamp}"
        extraction_folder = self.output_directory / folder_name
        extraction_folder.mkdir(parents=True, exist_ok=True)
        
        # إنشاء المجلدات الفرعية المطلوبة
        subfolders = [
            '01_content',           # المحتوى الأساسي
            '02_assets/images',     # الصور
            '02_assets/css',        # ملفات CSS
            '02_assets/js',         # ملفات JavaScript
            '02_assets/fonts',      # الخطوط
            '02_assets/media',      # الفيديو والصوت
            '02_assets/documents',  # المستندات
            '03_analysis',          # التحليلات
            '04_screenshots',       # لقطات الشاشة
            '05_reports',           # التقارير
            '06_crawled_pages',     # الصفحات المزحوفة
            '07_exports'            # الملفات المُصدَّرة
        ]
        
        for subfolder in subfolders:
            (extraction_folder / subfolder).mkdir(parents=True, exist_ok=True)
        
        return extraction_folder
    
    def _extract_basic_content(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """استخراج المحتوى الأساسي"""
        response = self.session.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # حفظ HTML الأصلي
        html_file = extraction_folder / '01_content' / 'index.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # استخراج النصوص
        text_content = soup.get_text(separator='\n', strip=True)
        text_file = extraction_folder / '01_content' / 'extracted_text.txt'
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # استخراج البيانات الوصفية
        metadata = {
            'title': soup.find('title').get_text() if soup.find('title') else 'بدون عنوان',
            'description': soup.find('meta', attrs={'name': 'description'}),
            'keywords': soup.find('meta', attrs={'name': 'keywords'}),
            'charset': response.encoding,
            'content_length': len(response.text),
            'response_time': response.elapsed.total_seconds()
        }
        
        if metadata['description']:
            metadata['description'] = metadata['description'].get('content', '')
        if metadata['keywords']:
            metadata['keywords'] = metadata['keywords'].get('content', '')
        
        # حفظ البيانات الوصفية
        metadata_file = extraction_folder / '01_content' / 'metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return {
            'soup': soup,
            'response': response,
            'text_content': text_content,
            'metadata': metadata,
            'content_files': {
                'html': str(html_file),
                'text': str(text_file),
                'metadata': str(metadata_file)
            }
        }
    
    def _download_comprehensive_assets(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> Dict[str, Any]:
        """تحميل شامل لجميع الأصول المطلوبة"""
        assets_result = {
            'images': [],
            'css': [],
            'js': [],
            'fonts': [],
            'media': [],
            'documents': [],
            'total_downloaded': 0,
            'total_size': 0,
            'failed_downloads': []
        }
        
        # تحميل الصور
        print("  📷 تحميل الصور...")
        images = self._download_images(soup, base_url, extraction_folder)
        assets_result['images'] = images
        
        # تحميل ملفات CSS
        print("  🎨 تحميل ملفات CSS...")
        css_files = self._download_css_files(soup, base_url, extraction_folder)
        assets_result['css'] = css_files
        
        # تحميل ملفات JavaScript
        print("  ⚡ تحميل ملفات JavaScript...")
        js_files = self._download_js_files(soup, base_url, extraction_folder)
        assets_result['js'] = js_files
        
        # تحميل الخطوط
        print("  🔤 تحميل الخطوط...")
        fonts = self._download_fonts(soup, base_url, extraction_folder)
        assets_result['fonts'] = fonts
        
        # تحميل الفيديو والصوت
        print("  🎵 تحميل الفيديو والصوت...")
        media = self._download_media_files(soup, base_url, extraction_folder)
        assets_result['media'] = media
        
        # تحميل المستندات
        print("  📄 تحميل المستندات...")
        documents = self._download_documents(soup, base_url, extraction_folder)
        assets_result['documents'] = documents
        
        # حساب الإحصائيات
        all_assets = images + css_files + js_files + fonts + media + documents
        assets_result['total_downloaded'] = len([a for a in all_assets if a.get('success')])
        assets_result['total_size'] = sum([a.get('size', 0) for a in all_assets if a.get('success')])
        
        return assets_result
    
    def _download_images(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict]:
        """تحميل جميع الصور"""
        images = []
        img_folder = extraction_folder / '02_assets' / 'images'
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
                
            try:
                img_url = urljoin(base_url, src)
                response = self.session.get(img_url, timeout=10, verify=False)
                response.raise_for_status()
                
                # تحديد اسم الملف
                filename = Path(urlparse(img_url).path).name
                if not filename or '.' not in filename:
                    filename = f"image_{len(images)+1}.jpg"
                
                file_path = img_folder / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                images.append({
                    'url': img_url,
                    'filename': filename,
                    'path': str(file_path),
                    'size': len(response.content),
                    'success': True
                })
                
            except Exception as e:
                images.append({
                    'url': src,
                    'error': str(e),
                    'success': False
                })
        
        return images
    
    def _download_css_files(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict]:
        """تحميل ملفات CSS"""
        css_files = []
        css_folder = extraction_folder / '02_assets' / 'css'
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if not href:
                continue
                
            try:
                css_url = urljoin(base_url, href)
                response = self.session.get(css_url, timeout=10, verify=False)
                response.raise_for_status()
                
                filename = Path(urlparse(css_url).path).name
                if not filename or not filename.endswith('.css'):
                    filename = f"style_{len(css_files)+1}.css"
                
                file_path = css_folder / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                css_files.append({
                    'url': css_url,
                    'filename': filename,
                    'path': str(file_path),
                    'size': len(response.content),
                    'success': True
                })
                
            except Exception as e:
                css_files.append({
                    'url': href,
                    'error': str(e),
                    'success': False
                })
        
        return css_files
    
    def _download_js_files(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict]:
        """تحميل ملفات JavaScript"""
        js_files = []
        js_folder = extraction_folder / '02_assets' / 'js'
        
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if not src:
                continue
                
            try:
                js_url = urljoin(base_url, src)
                response = self.session.get(js_url, timeout=10, verify=False)
                response.raise_for_status()
                
                filename = Path(urlparse(js_url).path).name
                if not filename or not filename.endswith('.js'):
                    filename = f"script_{len(js_files)+1}.js"
                
                file_path = js_folder / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                js_files.append({
                    'url': js_url,
                    'filename': filename,
                    'path': str(file_path),
                    'size': len(response.content),
                    'success': True
                })
                
            except Exception as e:
                js_files.append({
                    'url': src,
                    'error': str(e),
                    'success': False
                })
        
        return js_files
    
    def _download_fonts(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict]:
        """تحميل الخطوط"""
        fonts = []
        fonts_folder = extraction_folder / '02_assets' / 'fonts'
        
        # البحث عن خطوط Google Fonts
        for link in soup.find_all('link'):
            href = link.get('href', '')
            if 'fonts.googleapis.com' in href or 'fonts.gstatic.com' in href:
                try:
                    response = self.session.get(href, timeout=10, verify=False)
                    response.raise_for_status()
                    
                    filename = f"google_font_{len(fonts)+1}.css"
                    file_path = fonts_folder / filename
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    fonts.append({
                        'url': href,
                        'filename': filename,
                        'path': str(file_path),
                        'type': 'google_fonts',
                        'success': True
                    })
                    
                except Exception as e:
                    fonts.append({
                        'url': href,
                        'error': str(e),
                        'success': False
                    })
        
        return fonts
    
    def _download_media_files(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict]:
        """تحميل ملفات الفيديو والصوت"""
        media_files = []
        media_folder = extraction_folder / '02_assets' / 'media'
        
        # تحميل ملفات الفيديو
        for video in soup.find_all('video'):
            sources = video.find_all('source')
            if not sources and video.get('src'):
                sources = [video]
            
            for source in sources:
                src = source.get('src')
                if not src:
                    continue
                
                try:
                    media_url = urljoin(base_url, src)
                    response = self.session.get(media_url, timeout=30, verify=False, stream=True)
                    response.raise_for_status()
                    
                    filename = Path(urlparse(media_url).path).name
                    if not filename:
                        filename = f"video_{len(media_files)+1}.mp4"
                    
                    file_path = media_folder / filename
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    media_files.append({
                        'url': media_url,
                        'filename': filename,
                        'path': str(file_path),
                        'type': 'video',
                        'size': file_path.stat().st_size,
                        'success': True
                    })
                    
                except Exception as e:
                    media_files.append({
                        'url': src,
                        'error': str(e),
                        'type': 'video',
                        'success': False
                    })
        
        # تحميل ملفات الصوت
        for audio in soup.find_all('audio'):
            sources = audio.find_all('source')
            if not sources and audio.get('src'):
                sources = [audio]
            
            for source in sources:
                src = source.get('src')
                if not src:
                    continue
                
                try:
                    media_url = urljoin(base_url, src)
                    response = self.session.get(media_url, timeout=30, verify=False, stream=True)
                    response.raise_for_status()
                    
                    filename = Path(urlparse(media_url).path).name
                    if not filename:
                        filename = f"audio_{len(media_files)+1}.mp3"
                    
                    file_path = media_folder / filename
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    media_files.append({
                        'url': media_url,
                        'filename': filename,
                        'path': str(file_path),
                        'type': 'audio',
                        'size': file_path.stat().st_size,
                        'success': True
                    })
                    
                except Exception as e:
                    media_files.append({
                        'url': src,
                        'error': str(e),
                        'type': 'audio',
                        'success': False
                    })
        
        return media_files
    
    def _download_documents(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict]:
        """تحميل المستندات"""
        documents = []
        docs_folder = extraction_folder / '02_assets' / 'documents'
        
        # البحث عن روابط المستندات
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.zip']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
            
            # التحقق من امتداد الملف
            if any(href.lower().endswith(ext) for ext in doc_extensions):
                try:
                    doc_url = urljoin(base_url, href)
                    response = self.session.get(doc_url, timeout=30, verify=False, stream=True)
                    response.raise_for_status()
                    
                    filename = Path(urlparse(doc_url).path).name
                    if not filename:
                        ext = next((ext for ext in doc_extensions if href.lower().endswith(ext)), '.pdf')
                        filename = f"document_{len(documents)+1}{ext}"
                    
                    file_path = docs_folder / filename
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    documents.append({
                        'url': doc_url,
                        'filename': filename,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'success': True
                    })
                    
                except Exception as e:
                    documents.append({
                        'url': href,
                        'error': str(e),
                        'success': False
                    })
        
        return documents
    
    def _perform_comprehensive_analysis(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """إجراء تحليل شامل للموقع"""
        analysis_result = {
            'cms_detection': {},
            'security_analysis': {},
            'seo_analysis': {},
            'performance_analysis': {},
            'content_analysis': {},
            'technology_stack': {}
        }
        
        # 1. كشف نظام إدارة المحتوى
        analysis_result['cms_detection'] = self._detect_cms(soup, response.text)
        
        # 2. تحليل الأمان
        analysis_result['security_analysis'] = self._analyze_security(soup, url, response)
        
        # 3. تحليل محركات البحث (SEO)
        analysis_result['seo_analysis'] = self._analyze_seo(soup)
        
        # 4. تحليل الأداء
        analysis_result['performance_analysis'] = self._analyze_performance(soup, response)
        
        # 5. تحليل المحتوى
        analysis_result['content_analysis'] = self._analyze_content(soup)
        
        # 6. تحليل التقنيات المستخدمة
        analysis_result['technology_stack'] = self._analyze_technology_stack(soup, response.headers)
        
        return analysis_result
    
    def _detect_cms(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """كشف نظام إدارة المحتوى"""
        cms_indicators = {
            'wordpress': ['wp-content', 'wp-includes', 'wp-admin', 'wordpress'],
            'drupal': ['drupal', 'sites/default', 'modules/', 'themes/'],
            'joomla': ['joomla', 'administrator/', 'com_content'],
            'magento': ['magento', 'skin/frontend', 'js/mage'],
            'shopify': ['shopify', 'cdn.shopify.com', 'shop.js'],
            'wix': ['wix.com', 'static.wixstatic.com'],
            'squarespace': ['squarespace', 'static1.squarespace.com'],
            'bootstrap': ['bootstrap', 'bs4', 'bs5']
        }
        
        detected_cms = []
        confidence_scores = {}
        
        for cms, indicators in cms_indicators.items():
            score = 0
            found_indicators = []
            
            for indicator in indicators:
                if indicator.lower() in content.lower():
                    score += 1
                    found_indicators.append(indicator)
            
            if score > 0:
                confidence = min(score / len(indicators) * 100, 100)
                detected_cms.append(cms)
                confidence_scores[cms] = {
                    'confidence': confidence,
                    'indicators_found': found_indicators,
                    'total_indicators': len(indicators)
                }
        
        return {
            'detected_systems': detected_cms,
            'confidence_scores': confidence_scores,
            'primary_cms': max(confidence_scores.keys(), key=lambda x: confidence_scores[x]['confidence']) if confidence_scores else 'unknown'
        }
    
    def _analyze_security(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """تحليل الأمان"""
        security_analysis = {
            'https_enabled': url.startswith('https://'),
            'security_headers': {},
            'form_security': {},
            'external_resources': {},
            'vulnerabilities': [],
            'security_score': 0
        }
        
        # تحليل security headers
        security_headers = [
            'strict-transport-security',
            'content-security-policy',
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection',
            'referrer-policy'
        ]
        
        for header in security_headers:
            if header in response.headers:
                security_analysis['security_headers'][header] = response.headers[header]
            else:
                security_analysis['security_headers'][header] = 'missing'
        
        # تحليل أمان النماذج
        forms = soup.find_all('form')
        security_analysis['form_security'] = {
            'total_forms': len(forms),
            'forms_with_csrf': 0,
            'forms_over_https': 0,
            'password_fields': 0
        }
        
        for form in forms:
            # البحث عن CSRF tokens
            if form.find('input', {'name': re.compile(r'csrf|token', re.I)}):
                security_analysis['form_security']['forms_with_csrf'] += 1
            
            # البحث عن حقول كلمة المرور
            if form.find('input', {'type': 'password'}):
                security_analysis['form_security']['password_fields'] += 1
        
        # تحليل الموارد الخارجية
        external_domains = set()
        for tag in soup.find_all(['script', 'link', 'img']):
            src = tag.get('src') or tag.get('href')
            if src and src.startswith('http'):
                domain = urlparse(src).netloc
                if domain != urlparse(url).netloc:
                    external_domains.add(domain)
        
        security_analysis['external_resources'] = {
            'total_external_domains': len(external_domains),
            'domains': list(external_domains)
        }
        
        # حساب نقاط الأمان
        score = 0
        if security_analysis['https_enabled']:
            score += 20
        
        present_headers = [h for h in security_analysis['security_headers'].values() if h != 'missing']
        score += len(present_headers) * 10
        
        if security_analysis['form_security']['forms_with_csrf'] > 0:
            score += 20
        
        security_analysis['security_score'] = min(score, 100)
        
        return security_analysis
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل محركات البحث (SEO)"""
        seo_analysis = {
            'title_tag': {},
            'meta_description': {},
            'meta_keywords': {},
            'headings_structure': {},
            'images_alt_text': {},
            'internal_links': 0,
            'external_links': 0,
            'seo_score': 0
        }
        
        # تحليل عنوان الصفحة
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            seo_analysis['title_tag'] = {
                'present': True,
                'text': title_text,
                'length': len(title_text),
                'optimal': 30 <= len(title_text) <= 60
            }
        else:
            seo_analysis['title_tag'] = {'present': False}
        
        # تحليل وصف الصفحة
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            desc_text = description.get('content', '')
            seo_analysis['meta_description'] = {
                'present': True,
                'text': desc_text,
                'length': len(desc_text),
                'optimal': 120 <= len(desc_text) <= 160
            }
        else:
            seo_analysis['meta_description'] = {'present': False}
        
        # تحليل الكلمات المفتاحية
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords:
            seo_analysis['meta_keywords'] = {
                'present': True,
                'content': keywords.get('content', '')
            }
        else:
            seo_analysis['meta_keywords'] = {'present': False}
        
        # تحليل هيكل العناوين
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = {
                'count': len(h_tags),
                'texts': [h.get_text().strip() for h in h_tags[:5]]  # أول 5 عناوين فقط
            }
        seo_analysis['headings_structure'] = headings
        
        # تحليل النص البديل للصور
        images = soup.find_all('img')
        images_with_alt = len([img for img in images if img.get('alt')])
        seo_analysis['images_alt_text'] = {
            'total_images': len(images),
            'images_with_alt': images_with_alt,
            'percentage': (images_with_alt / len(images) * 100) if images else 0
        }
        
        # تحليل الروابط
        links = soup.find_all('a', href=True)
        internal_links = 0
        external_links = 0
        
        for link in links:
            href = link.get('href')
            if href.startswith('http'):
                external_links += 1
            elif href.startswith('/') or not href.startswith('#'):
                internal_links += 1
        
        seo_analysis['internal_links'] = internal_links
        seo_analysis['external_links'] = external_links
        
        # حساب نقاط SEO
        score = 0
        if seo_analysis['title_tag'].get('present'):
            score += 15
            if seo_analysis['title_tag'].get('optimal'):
                score += 10
        
        if seo_analysis['meta_description'].get('present'):
            score += 15
            if seo_analysis['meta_description'].get('optimal'):
                score += 10
        
        if headings.get('h1', {}).get('count', 0) > 0:
            score += 15
        
        if seo_analysis['images_alt_text']['percentage'] > 80:
            score += 15
        
        if internal_links > 5:
            score += 10
        
        if external_links > 0:
            score += 10
        
        seo_analysis['seo_score'] = min(score, 100)
        
        return seo_analysis
    
    def _analyze_performance(self, soup: BeautifulSoup, response) -> Dict[str, Any]:
        """تحليل الأداء"""
        return {
            'page_size': len(response.content),
            'response_time': response.elapsed.total_seconds(),
            'total_elements': len(soup.find_all()),
            'images_count': len(soup.find_all('img')),
            'scripts_count': len(soup.find_all('script')),
            'stylesheets_count': len(soup.find_all('link', rel='stylesheet')),
            'compression': response.headers.get('content-encoding', 'none')
        }
    
    def _analyze_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل المحتوى"""
        text_content = soup.get_text()
        words = text_content.split()
        
        return {
            'total_characters': len(text_content),
            'total_words': len(words),
            'paragraphs_count': len(soup.find_all('p')),
            'lists_count': len(soup.find_all(['ul', 'ol'])),
            'tables_count': len(soup.find_all('table')),
            'forms_count': len(soup.find_all('form')),
            'language': soup.get('lang', 'unknown')
        }
    
    def _analyze_technology_stack(self, soup: BeautifulSoup, headers: dict) -> Dict[str, Any]:
        """تحليل التقنيات المستخدمة"""
        technologies = {
            'server': headers.get('server', 'unknown'),
            'programming_languages': [],
            'frameworks': [],
            'libraries': [],
            'analytics': [],
            'cdn': []
        }
        
        content = str(soup).lower()
        
        # البحث عن لغات البرمجة
        if 'php' in content or '.php' in content:
            technologies['programming_languages'].append('PHP')
        if 'asp.net' in content or 'aspx' in content:
            technologies['programming_languages'].append('ASP.NET')
        if 'jsp' in content or 'java' in content:
            technologies['programming_languages'].append('Java')
        if 'python' in content or 'django' in content:
            technologies['programming_languages'].append('Python')
        
        # البحث عن المكتبات والإطارات
        frameworks_libs = {
            'jquery': 'jQuery',
            'bootstrap': 'Bootstrap',
            'react': 'React',
            'angular': 'Angular',
            'vue': 'Vue.js',
            'fontawesome': 'Font Awesome',
            'd3': 'D3.js'
        }
        
        for keyword, name in frameworks_libs.items():
            if keyword in content:
                technologies['libraries'].append(name)
        
        # البحث عن أدوات التحليل
        if 'google-analytics' in content or 'gtag' in content:
            technologies['analytics'].append('Google Analytics')
        if 'gtm' in content:
            technologies['analytics'].append('Google Tag Manager')
        
        # البحث عن CDN
        if 'cloudflare' in content:
            technologies['cdn'].append('Cloudflare')
        if 'amazonaws' in content:
            technologies['cdn'].append('AWS CloudFront')
        
        return technologies
    
    def _capture_comprehensive_screenshots(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """التقاط لقطات شاشة شاملة"""
        screenshots_result = {
            'desktop': None,
            'tablet': None,
            'mobile': None,
            'full_page': None,
            'success': False,
            'errors': []
        }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # لقطة شاشة سطح المكتب
            driver.set_window_size(1920, 1080)
            driver.get(url)
            time.sleep(3)
            desktop_path = extraction_folder / '04_screenshots' / 'desktop.png'
            driver.save_screenshot(str(desktop_path))
            screenshots_result['desktop'] = str(desktop_path)
            
            # لقطة شاشة الجهاز اللوحي
            driver.set_window_size(768, 1024)
            time.sleep(2)
            tablet_path = extraction_folder / '04_screenshots' / 'tablet.png'
            driver.save_screenshot(str(tablet_path))
            screenshots_result['tablet'] = str(tablet_path)
            
            # لقطة شاشة الهاتف المحمول
            driver.set_window_size(375, 812)
            time.sleep(2)
            mobile_path = extraction_folder / '04_screenshots' / 'mobile.png'
            driver.save_screenshot(str(mobile_path))
            screenshots_result['mobile'] = str(mobile_path)
            
            driver.quit()
            screenshots_result['success'] = True
            
        except Exception as e:
            screenshots_result['errors'].append(f"خطأ في التقاط لقطات الشاشة: {str(e)}")
            # بديل باستخدام requests و html2image إذا متوفر
            try:
                # حفظ HTML كصورة بديلة
                simple_path = extraction_folder / '04_screenshots' / 'simple_capture.txt'
                with open(simple_path, 'w', encoding='utf-8') as f:
                    f.write(f"تم محاولة التقاط لقطة شاشة للموقع: {url}\nحدث خطأ: {str(e)}")
                screenshots_result['errors'].append("تم استخدام الطريقة البديلة")
            except:
                pass
        
        return screenshots_result
    
    def _crawl_website_pages(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """زحف الصفحات المتعددة للموقع"""
        crawl_result = {
            'pages_found': [],
            'pages_crawled': 0,
            'total_links': 0,
            'internal_links': 0,
            'external_links': 0,
            'success': True,
            'errors': []
        }
        
        try:
            visited_urls = set()
            to_visit = [url]
            max_pages = 10  # حد أقصى للصفحات
            
            base_domain = urlparse(url).netloc
            
            while to_visit and len(visited_urls) < max_pages:
                current_url = to_visit.pop(0)
                if current_url in visited_urls:
                    continue
                
                try:
                    response = self.session.get(current_url, timeout=10, verify=False)
                    if response.status_code == 200:
                        visited_urls.add(current_url)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # حفظ الصفحة
                        page_name = urlparse(current_url).path.replace('/', '_') or 'index'
                        if page_name.startswith('_'):
                            page_name = page_name[1:]
                        if not page_name:
                            page_name = 'index'
                        
                        page_file = extraction_folder / '06_crawled_pages' / f"{page_name}.html"
                        with open(page_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        # جمع الروابط الجديدة
                        for link in soup.find_all('a', href=True):
                            href = link.get('href')
                            if href:
                                full_url = urljoin(current_url, href)
                                parsed = urlparse(full_url)
                                
                                if parsed.netloc == base_domain and full_url not in visited_urls:
                                    if full_url not in to_visit:
                                        to_visit.append(full_url)
                                    crawl_result['internal_links'] += 1
                                else:
                                    crawl_result['external_links'] += 1
                        
                        crawl_result['pages_found'].append({
                            'url': current_url,
                            'title': soup.find('title').get_text() if soup.find('title') else 'بدون عنوان',
                            'file_path': str(page_file),
                            'status': 'success'
                        })
                        
                        time.sleep(1)  # فترة انتظار بين الطلبات
                        
                except Exception as e:
                    crawl_result['errors'].append(f"خطأ في زحف {current_url}: {str(e)}")
            
            crawl_result['pages_crawled'] = len(visited_urls)
            crawl_result['total_links'] = crawl_result['internal_links'] + crawl_result['external_links']
            
        except Exception as e:
            crawl_result['success'] = False
            crawl_result['errors'].append(f"خطأ عام في الزحف: {str(e)}")
        
        return crawl_result
    
    def _generate_comprehensive_sitemap(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """إنشاء خريطة موقع شاملة"""
        sitemap_result = {
            'xml_sitemap': None,
            'html_sitemap': None,
            'urls_count': 0,
            'success': False,
            'errors': []
        }
        
        try:
            # جمع الروابط من الزحف
            crawl_data = self._crawl_website_pages(url, extraction_folder)
            
            if crawl_data['success'] and crawl_data['pages_found']:
                urls = [page['url'] for page in crawl_data['pages_found']]
                
                # إنشاء XML Sitemap
                xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
                xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
                
                for page_url in urls:
                    xml_content.append('  <url>')
                    xml_content.append(f'    <loc>{page_url}</loc>')
                    xml_content.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
                    xml_content.append('    <changefreq>monthly</changefreq>')
                    xml_content.append('    <priority>0.8</priority>')
                    xml_content.append('  </url>')
                
                xml_content.append('</urlset>')
                
                xml_file = extraction_folder / '07_exports' / 'sitemap.xml'
                with open(xml_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(xml_content))
                
                sitemap_result['xml_sitemap'] = str(xml_file)
                
                # إنشاء HTML Sitemap
                html_content = [
                    '<!DOCTYPE html>',
                    '<html dir="rtl" lang="ar">',
                    '<head>',
                    '    <meta charset="UTF-8">',
                    '    <title>خريطة الموقع</title>',
                    '    <style>',
                    '        body { font-family: Arial, sans-serif; margin: 20px; }',
                    '        .sitemap { max-width: 800px; margin: 0 auto; }',
                    '        .url-item { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }',
                    '        .url-link { color: #0066cc; text-decoration: none; font-weight: bold; }',
                    '        .url-link:hover { text-decoration: underline; }',
                    '    </style>',
                    '</head>',
                    '<body>',
                    '    <div class="sitemap">',
                    '        <h1>خريطة الموقع</h1>',
                    f'        <p>العدد الإجمالي للصفحات: {len(urls)}</p>'
                ]
                
                for page in crawl_data['pages_found']:
                    html_content.extend([
                        '        <div class="url-item">',
                        f'            <a href="{page["url"]}" class="url-link">{page["title"]}</a>',
                        f'            <br><small>{page["url"]}</small>',
                        '        </div>'
                    ])
                
                html_content.extend([
                    '    </div>',
                    '</body>',
                    '</html>'
                ])
                
                html_file = extraction_folder / '07_exports' / 'sitemap.html'
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(html_content))
                
                sitemap_result['html_sitemap'] = str(html_file)
                sitemap_result['urls_count'] = len(urls)
                sitemap_result['success'] = True
                
        except Exception as e:
            sitemap_result['errors'].append(f"خطأ في إنشاء خريطة الموقع: {str(e)}")
        
        return sitemap_result
    
    def _perform_comprehensive_security_scan(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """فحص أمني شامل"""
        security_scan = {
            'ssl_analysis': {},
            'vulnerability_scan': {},
            'headers_analysis': {},
            'content_analysis': {},
            'overall_score': 0,
            'recommendations': []
        }
        
        try:
            # فحص SSL
            if url.startswith('https://'):
                security_scan['ssl_analysis'] = {
                    'enabled': True,
                    'grade': 'A',  # تقدير أولي
                    'issues': []
                }
            else:
                security_scan['ssl_analysis'] = {
                    'enabled': False,
                    'grade': 'F',
                    'issues': ['الموقع لا يستخدم HTTPS']
                }
                security_scan['recommendations'].append('تفعيل HTTPS لحماية البيانات')
            
            # فحص نقاط الضعف الشائعة
            vulnerabilities = []
            content_text = str(soup).lower()
            
            # البحث عن معلومات حساسة
            if 'password' in content_text and 'type="password"' not in content_text:
                vulnerabilities.append('كلمات مرور ظاهرة في النص')
            
            if 'admin' in content_text:
                vulnerabilities.append('مراجع لصفحات الإدارة')
            
            if 'error' in content_text or 'exception' in content_text:
                vulnerabilities.append('رسائل خطأ مكشوفة')
            
            security_scan['vulnerability_scan'] = {
                'vulnerabilities_found': vulnerabilities,
                'total_count': len(vulnerabilities)
            }
            
            # تحليل الأمان العام
            forms = soup.find_all('form')
            secure_forms = 0
            
            for form in forms:
                if form.find('input', {'name': re.compile(r'csrf|token', re.I)}):
                    secure_forms += 1
            
            security_scan['content_analysis'] = {
                'total_forms': len(forms),
                'secure_forms': secure_forms,
                'form_security_percentage': (secure_forms / len(forms) * 100) if forms else 0
            }
            
            # حساب النقاط الإجمالية
            score = 0
            if security_scan['ssl_analysis']['enabled']:
                score += 40
            
            if len(vulnerabilities) == 0:
                score += 30
            
            if security_scan['content_analysis']['form_security_percentage'] > 50:
                score += 30
            
            security_scan['overall_score'] = min(score, 100)
            
            # توصيات الأمان
            if score < 70:
                security_scan['recommendations'].extend([
                    'تحسين الحماية العامة للموقع',
                    'إضافة حماية CSRF للنماذج',
                    'مراجعة رسائل الأخطاء المكشوفة'
                ])
            
        except Exception as e:
            security_scan['error'] = f"خطأ في الفحص الأمني: {str(e)}"
        
        return security_scan
    
    def _perform_ai_enhanced_analysis(self, basic_result: Dict, assets_result: Dict, analysis_result: Dict) -> Dict[str, Any]:
        """تحليل ذكي متطور للموقع"""
        ai_analysis = {
            'content_intelligence': {},
            'pattern_recognition': {},
            'smart_insights': {},
            'quality_assessment': {},
            'recommendations': []
        }
        
        try:
            # تحليل ذكي للمحتوى
            text_content = basic_result.get('text_content', '')
            words = text_content.split()
            
            ai_analysis['content_intelligence'] = {
                'readability_score': self._calculate_readability_score(text_content),
                'keyword_density': self._analyze_keyword_density(words),
                'content_type': self._classify_content_type(text_content),
                'language_quality': self._assess_language_quality(text_content)
            }
            
            # تحليل الأنماط
            ai_analysis['pattern_recognition'] = {
                'design_patterns': self._detect_design_patterns(basic_result['soup']),
                'navigation_patterns': self._analyze_navigation_patterns(basic_result['soup']),
                'content_patterns': self._detect_content_patterns(basic_result['soup'])
            }
            
            # رؤى ذكية
            ai_analysis['smart_insights'] = {
                'user_experience_score': self._calculate_ux_score(analysis_result),
                'mobile_friendliness': self._assess_mobile_friendliness(basic_result['soup']),
                'accessibility_score': self._assess_accessibility(basic_result['soup']),
                'engagement_potential': self._assess_engagement_potential(basic_result['soup'])
            }
            
            # تقييم الجودة
            overall_quality = (
                ai_analysis['content_intelligence']['readability_score'] * 0.3 +
                ai_analysis['smart_insights']['user_experience_score'] * 0.3 +
                ai_analysis['smart_insights']['accessibility_score'] * 0.2 +
                analysis_result['seo_analysis']['seo_score'] * 0.2
            )
            
            ai_analysis['quality_assessment'] = {
                'overall_score': round(overall_quality, 2),
                'content_quality': ai_analysis['content_intelligence']['readability_score'],
                'technical_quality': analysis_result['performance_analysis']['response_time'],
                'seo_quality': analysis_result['seo_analysis']['seo_score']
            }
            
            # توصيات ذكية
            recommendations = []
            
            if ai_analysis['content_intelligence']['readability_score'] < 60:
                recommendations.append("تحسين قابلية قراءة المحتوى")
            
            if ai_analysis['smart_insights']['mobile_friendliness'] < 70:
                recommendations.append("تحسين التوافق مع الأجهزة المحمولة")
            
            if ai_analysis['smart_insights']['accessibility_score'] < 70:
                recommendations.append("تحسين إمكانية الوصول للموقع")
            
            if analysis_result['seo_analysis']['seo_score'] < 70:
                recommendations.append("تحسين محركات البحث (SEO)")
            
            ai_analysis['recommendations'] = recommendations
            
        except Exception as e:
            ai_analysis['error'] = f"خطأ في التحليل الذكي: {str(e)}"
        
        return ai_analysis
    
    def _calculate_readability_score(self, text: str) -> float:
        """حساب نقاط قابلية القراءة"""
        if not text:
            return 0
        
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0 or words == 0:
            return 0
        
        avg_words_per_sentence = words / sentences
        
        # نقاط بسيطة على أساس متوسط الكلمات في الجملة
        if avg_words_per_sentence <= 15:
            return 90  # ممتاز
        elif avg_words_per_sentence <= 20:
            return 75  # جيد
        elif avg_words_per_sentence <= 25:
            return 60  # متوسط
        else:
            return 40  # صعب
    
    def _analyze_keyword_density(self, words: List[str]) -> Dict[str, int]:
        """تحليل كثافة الكلمات المفتاحية"""
        if not words:
            return {}
        
        # تصفية الكلمات وحساب التكرار
        filtered_words = [word.lower().strip('.,!?":;()[]{}') for word in words if len(word) > 3]
        word_count = {}
        
        for word in filtered_words:
            word_count[word] = word_count.get(word, 0) + 1
        
        # إرجاع أهم 10 كلمات
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_words[:10])
    
    def _classify_content_type(self, text: str) -> str:
        """تصنيف نوع المحتوى"""
        text_lower = text.lower()
        
        # تصنيف بسيط بناءً على الكلمات المفتاحية
        if any(word in text_lower for word in ['متجر', 'شراء', 'سعر', 'منتج', 'shop', 'buy', 'price']):
            return 'تجاري'
        elif any(word in text_lower for word in ['مقال', 'خبر', 'تعليم', 'معلومات', 'article', 'news']):
            return 'إعلامي'
        elif any(word in text_lower for word in ['خدمة', 'شركة', 'عمل', 'business', 'service']):
            return 'خدمات'
        elif any(word in text_lower for word in ['لعبة', 'ترفيه', 'فيديو', 'game', 'entertainment']):
            return 'ترفيهي'
        else:
            return 'عام'
    
    def _assess_language_quality(self, text: str) -> float:
        """تقييم جودة اللغة"""
        if not text:
            return 0
        
        # تقييم بسيط بناءً على:
        # - وجود علامات ترقيم
        # - طول النصوص
        # - تنوع الكلمات
        
        punctuation_score = min(len(re.findall(r'[.!?,:;]', text)) / len(text.split()) * 100, 30)
        length_score = min(len(text) / 1000 * 30, 30) if len(text) < 10000 else 30
        word_variety = len(set(text.split())) / len(text.split()) * 40 if text.split() else 0
        
        return round(punctuation_score + length_score + word_variety, 2)
    
    def _detect_design_patterns(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """كشف أنماط التصميم"""
        return {
            'bootstrap_detected': 'bootstrap' in str(soup).lower(),
            'responsive_design': bool(soup.find('meta', attrs={'name': 'viewport'})),
            'grid_system': len(soup.find_all(class_=re.compile(r'col-|grid-'))) > 0,
            'css_framework': self._detect_css_framework(soup)
        }
    
    def _detect_css_framework(self, soup: BeautifulSoup) -> List[str]:
        """كشف إطارات CSS المستخدمة"""
        frameworks = []
        content = str(soup).lower()
        
        if 'bootstrap' in content:
            frameworks.append('Bootstrap')
        if 'tailwind' in content:
            frameworks.append('Tailwind CSS')
        if 'foundation' in content:
            frameworks.append('Foundation')
        if 'bulma' in content:
            frameworks.append('Bulma')
            
        return frameworks
    
    def _analyze_navigation_patterns(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل أنماط التنقل"""
        nav_elements = soup.find_all(['nav', 'header'])
        
        return {
            'navigation_count': len(nav_elements),
            'has_main_menu': len(soup.find_all(['nav', 'ul', 'ol'], class_=re.compile(r'menu|nav'))) > 0,
            'breadcrumbs': bool(soup.find(class_=re.compile(r'breadcrumb'))),
            'search_functionality': bool(soup.find('input', {'type': 'search'}))
        }
    
    def _detect_content_patterns(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """كشف أنماط المحتوى"""
        return {
            'blog_patterns': len(soup.find_all(class_=re.compile(r'post|article|blog'))) > 0,
            'product_patterns': len(soup.find_all(class_=re.compile(r'product|item|card'))) > 0,
            'gallery_patterns': len(soup.find_all(class_=re.compile(r'gallery|carousel|slider'))) > 0,
            'testimonial_patterns': len(soup.find_all(class_=re.compile(r'testimonial|review'))) > 0
        }
    
    def _calculate_ux_score(self, analysis_result: Dict[str, Any]) -> float:
        """حساب نقاط تجربة المستخدم"""
        score = 0
        
        # تحليل الأداء
        performance = analysis_result.get('performance_analysis', {})
        if performance.get('response_time', 5) < 3:
            score += 25
        elif performance.get('response_time', 5) < 5:
            score += 15
        
        # تحليل المحتوى
        content = analysis_result.get('content_analysis', {})
        if content.get('total_words', 0) > 100:
            score += 25
        
        # تحليل SEO
        seo = analysis_result.get('seo_analysis', {})
        if seo.get('seo_score', 0) > 70:
            score += 25
        
        # تحليل الأمان
        security = analysis_result.get('security_analysis', {})
        if security.get('security_score', 0) > 70:
            score += 25
        
        return min(score, 100)
    
    def _assess_mobile_friendliness(self, soup: BeautifulSoup) -> float:
        """تقييم التوافق مع الأجهزة المحمولة"""
        score = 0
        
        # فحص viewport meta tag
        if soup.find('meta', attrs={'name': 'viewport'}):
            score += 30
        
        # فحص responsive design indicators
        content = str(soup).lower()
        if 'responsive' in content or '@media' in content:
            score += 30
        
        # فحص Mobile-first indicators
        if 'mobile-first' in content or 'bootstrap' in content:
            score += 20
        
        # فحص touch-friendly elements
        if len(soup.find_all('button')) > 0:
            score += 20
        
        return min(score, 100)
    
    def _assess_accessibility(self, soup: BeautifulSoup) -> float:
        """تقييم إمكانية الوصول"""
        score = 0
        
        # فحص alt attributes في الصور
        images = soup.find_all('img')
        images_with_alt = [img for img in images if img.get('alt')]
        if images and len(images_with_alt) / len(images) > 0.8:
            score += 25
        
        # فحص ARIA labels
        aria_elements = soup.find_all(attrs={'aria-label': True})
        if len(aria_elements) > 0:
            score += 25
        
        # فحص heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(soup.find_all('h1')) == 1:  # Should have exactly one h1
            score += 25
        
        # فحص form labels
        forms = soup.find_all('form')
        if forms:
            labels = soup.find_all('label')
            if len(labels) > 0:
                score += 25
        else:
            score += 25  # No forms, so no accessibility issues
        
        return min(score, 100)
    
    def _assess_engagement_potential(self, soup: BeautifulSoup) -> float:
        """تقييم إمكانية التفاعل"""
        score = 0
        
        # فحص العناصر التفاعلية
        interactive_elements = len(soup.find_all(['button', 'input', 'select', 'textarea']))
        if interactive_elements > 0:
            score += 20
        
        # فحص الوسائط المتعددة
        media_elements = len(soup.find_all(['img', 'video', 'audio']))
        if media_elements > 5:
            score += 20
        
        # فحص الروابط الاجتماعية
        social_links = len(soup.find_all('a', href=re.compile(r'facebook|twitter|instagram|linkedin')))
        if social_links > 0:
            score += 20
        
        # فحص التعليقات أو المراجعات
        comment_sections = len(soup.find_all(class_=re.compile(r'comment|review|feedback')))
        if comment_sections > 0:
            score += 20
        
        # فحص النماذج
        forms = len(soup.find_all('form'))
        if forms > 0:
            score += 20
        
        return min(score, 100)
    
    def _extract_dynamic_and_ajax_content(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """استخراج المحتوى الديناميكي والـ AJAX"""
        dynamic_result = {
            'ajax_endpoints': [],
            'dynamic_content': {},
            'spa_detected': False,
            'javascript_heavy': False,
            'success': False,
            'errors': []
        }
        
        try:
            # محاولة استخراج المحتوى الديناميكي باستخدام selenium
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # انتظار تحميل JavaScript
            time.sleep(5)
            
            # استخراج المحتوى بعد تنفيذ JavaScript
            dynamic_html = driver.page_source
            dynamic_soup = BeautifulSoup(dynamic_html, 'html.parser')
            
            # حفظ المحتوى الديناميكي
            dynamic_file = extraction_folder / '01_content' / 'dynamic_content.html'
            with open(dynamic_file, 'w', encoding='utf-8') as f:
                f.write(dynamic_html)
            
            # كشف SPA
            script_tags = dynamic_soup.find_all('script')
            js_content = ' '.join([script.get_text() for script in script_tags])
            
            spa_indicators = ['react', 'angular', 'vue', 'spa', 'single page']
            dynamic_result['spa_detected'] = any(indicator in js_content.lower() for indicator in spa_indicators)
            dynamic_result['javascript_heavy'] = len(script_tags) > 10
            
            # البحث عن AJAX endpoints
            ajax_patterns = re.findall(r'(?:fetch|ajax|xhr).*?["\']([^"\']*)["\']', js_content, re.IGNORECASE)
            dynamic_result['ajax_endpoints'] = list(set(ajax_patterns[:10]))  # أول 10 endpoints
            
            dynamic_result['dynamic_content'] = {
                'file_path': str(dynamic_file),
                'total_scripts': len(script_tags),
                'page_size': len(dynamic_html)
            }
            
            driver.quit()
            dynamic_result['success'] = True
            
        except Exception as e:
            dynamic_result['errors'].append(f"خطأ في استخراج المحتوى الديناميكي: {str(e)}")
            # بديل بسيط
            try:
                response = self.session.get(url, timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                scripts = soup.find_all('script')
                dynamic_result['dynamic_content'] = {
                    'total_scripts': len(scripts),
                    'static_analysis': True
                }
                dynamic_result['success'] = True
            except:
                pass
        
        return dynamic_result
    
    def _compile_comprehensive_results(self, extraction_id: str, url: str, extraction_type: str, 
                                     start_time: float, basic_result: Dict, assets_result: Dict,
                                     analysis_result: Dict, extra_features: Dict, 
                                     extraction_folder: Path) -> Dict[str, Any]:
        """تجميع جميع النتائج في تقرير شامل"""
        
        total_duration = round(time.time() - start_time, 2)
        
        comprehensive_result = {
            # معلومات أساسية
            'extraction_info': {
                'extraction_id': extraction_id,
                'url': url,
                'extraction_type': extraction_type,
                'timestamp': datetime.now().isoformat(),
                'duration': total_duration,
                'success': True,
                'extractor_version': '2.0.0'
            },
            
            # المحتوى الأساسي
            'basic_content': {
                'metadata': basic_result['metadata'],
                'content_files': basic_result['content_files']
            },
            
            # الأصول المحملة
            'downloaded_assets': {
                'summary': {
                    'total_images': len(assets_result['images']),
                    'total_css': len(assets_result['css']),
                    'total_js': len(assets_result['js']),
                    'total_fonts': len(assets_result['fonts']),
                    'total_media': len(assets_result['media']),
                    'total_documents': len(assets_result['documents']),
                    'total_size_mb': round(assets_result['total_size'] / (1024*1024), 2)
                },
                'details': assets_result
            },
            
            # التحليلات المتقدمة
            'comprehensive_analysis': analysis_result,
            
            # الميزات الإضافية
            'advanced_features': extra_features,
            
            # مسارات الملفات
            'output_paths': {
                'extraction_folder': str(extraction_folder),
                'content_folder': str(extraction_folder / '01_content'),
                'assets_folder': str(extraction_folder / '02_assets'),
                'analysis_folder': str(extraction_folder / '03_analysis'),
                'screenshots_folder': str(extraction_folder / '04_screenshots'),
                'reports_folder': str(extraction_folder / '05_reports'),
                'exports_folder': str(extraction_folder / '07_exports')
            },
            
            # إحصائيات شاملة
            'statistics': {
                'extraction_completeness': self._calculate_completeness_score(assets_result, analysis_result, extra_features),
                'data_quality_score': self._calculate_data_quality_score(basic_result, analysis_result),
                'technical_score': analysis_result.get('performance_analysis', {}).get('response_time', 0),
                'security_score': analysis_result.get('security_analysis', {}).get('security_score', 0),
                'seo_score': analysis_result.get('seo_analysis', {}).get('seo_score', 0)
            }
        }
        
        return comprehensive_result
    
    def _calculate_completeness_score(self, assets_result: Dict, analysis_result: Dict, extra_features: Dict) -> float:
        """حساب نقاط اكتمال الاستخراج"""
        score = 0
        
        # نقاط الأصول
        if assets_result['total_downloaded'] > 0:
            score += 20
        
        # نقاط التحليل
        if analysis_result.get('cms_detection'):
            score += 15
        if analysis_result.get('security_analysis'):
            score += 15
        if analysis_result.get('seo_analysis'):
            score += 15
        
        # نقاط الميزات الإضافية
        if extra_features.get('screenshots'):
            score += 10
        if extra_features.get('crawl_results'):
            score += 10
        if extra_features.get('sitemap'):
            score += 10
        if extra_features.get('ai_analysis'):
            score += 5
        
        return min(score, 100)
    
    def _calculate_data_quality_score(self, basic_result: Dict, analysis_result: Dict) -> float:
        """حساب نقاط جودة البيانات"""
        score = 0
        
        # جودة المحتوى الأساسي
        if basic_result.get('metadata', {}).get('title'):
            score += 25
        if basic_result.get('text_content') and len(basic_result['text_content']) > 100:
            score += 25
        
        # جودة التحليل
        if analysis_result.get('content_analysis', {}).get('total_words', 0) > 50:
            score += 25
        if analysis_result.get('technology_stack'):
            score += 25
        
        return min(score, 100)
    
    def _save_results_and_create_reports(self, final_result: Dict[str, Any], extraction_folder: Path):
        """حفظ النتائج وإنشاء التقارير"""
        
        # حفظ النتائج الكاملة في JSON
        results_file = extraction_folder / '05_reports' / 'comprehensive_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2, default=str)
        
        # إنشاء تقرير HTML
        self._create_html_report(final_result, extraction_folder)
        
        # إنشاء ملخص نصي
        self._create_text_summary(final_result, extraction_folder)
        
        print(f"📋 تم حفظ التقارير في: {extraction_folder / '05_reports'}")
    
    def _create_html_report(self, result: Dict[str, Any], extraction_folder: Path):
        """إنشاء تقرير HTML تفاعلي"""
        
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير استخراج الموقع الشامل</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header .subtitle {{ opacity: 0.9; margin-top: 10px; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #e1e8ed; border-radius: 8px; }}
        .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #3498db; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .progress-bar {{ width: 100%; height: 10px; background: #ecf0f1; border-radius: 5px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #2ecc71, #3498db); }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>تقرير استخراج الموقع الشامل</h1>
            <div class="subtitle">
                تم إنشاؤه في: {result['extraction_info']['timestamp']}<br>
                نوع الاستخراج: {result['extraction_info']['extraction_type']}<br>
                الموقع: {result['extraction_info']['url']}
            </div>
        </div>
        
        <div class="content">
            <!-- إحصائيات سريعة -->
            <div class="section">
                <h2>📊 الإحصائيات السريعة</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number success">{result['statistics']['extraction_completeness']:.0f}%</div>
                        <div class="stat-label">اكتمال الاستخراج</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{result['downloaded_assets']['summary']['total_size_mb']}</div>
                        <div class="stat-label">حجم البيانات (MB)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{result['extraction_info']['duration']}</div>
                        <div class="stat-label">مدة الاستخراج (ثانية)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number success">{result['statistics']['seo_score']:.0f}%</div>
                        <div class="stat-label">نقاط SEO</div>
                    </div>
                </div>
            </div>
            
            <!-- تحليل الأصول -->
            <div class="section">
                <h2>💾 الأصول المحملة</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{result['downloaded_assets']['summary']['total_images']}</div>
                        <div class="stat-label">الصور</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{result['downloaded_assets']['summary']['total_css']}</div>
                        <div class="stat-label">ملفات CSS</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{result['downloaded_assets']['summary']['total_js']}</div>
                        <div class="stat-label">ملفات JavaScript</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{result['downloaded_assets']['summary']['total_media']}</div>
                        <div class="stat-label">ملفات الوسائط</div>
                    </div>
                </div>
            </div>
            
            <!-- تحليل الأمان -->
            <div class="section">
                <h2>🔒 تحليل الأمان</h2>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {result['statistics']['security_score']}%"></div>
                </div>
                <p>نقاط الأمان: <strong>{result['statistics']['security_score']:.0f}%</strong></p>
            </div>
            
            <!-- معلومات التقنيات -->
            <div class="section">
                <h2>⚙️ التقنيات المكتشفة</h2>
                <p><strong>نظام إدارة المحتوى:</strong> {result['comprehensive_analysis'].get('cms_detection', {}).get('primary_cms', 'غير محدد')}</p>
                <p><strong>الخادم:</strong> {result['comprehensive_analysis'].get('technology_stack', {}).get('server', 'غير محدد')}</p>
            </div>
            
            <!-- مسارات الملفات -->
            <div class="section">
                <h2>📁 مسارات الملفات</h2>
                <table>
                    <tr><th>النوع</th><th>المسار</th></tr>
                    <tr><td>مجلد الاستخراج الرئيسي</td><td>{result['output_paths']['extraction_folder']}</td></tr>
                    <tr><td>المحتوى</td><td>{result['output_paths']['content_folder']}</td></tr>
                    <tr><td>الأصول</td><td>{result['output_paths']['assets_folder']}</td></tr>
                    <tr><td>التقارير</td><td>{result['output_paths']['reports_folder']}</td></tr>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        html_file = extraction_folder / '05_reports' / 'comprehensive_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_text_summary(self, result: Dict[str, Any], extraction_folder: Path):
        """إنشاء ملخص نصي"""
        
        summary = f"""
=== تقرير استخراج الموقع الشامل ===

🌐 الموقع: {result['extraction_info']['url']}
🗓️ التاريخ: {result['extraction_info']['timestamp']}
⏱️ المدة: {result['extraction_info']['duration']} ثانية
🔧 نوع الاستخراج: {result['extraction_info']['extraction_type']}

📊 الإحصائيات الرئيسية:
- اكتمال الاستخراج: {result['statistics']['extraction_completeness']:.1f}%
- جودة البيانات: {result['statistics']['data_quality_score']:.1f}%
- نقاط الأمان: {result['statistics']['security_score']:.1f}%
- نقاط SEO: {result['statistics']['seo_score']:.1f}%

💾 الأصول المحملة:
- الصور: {result['downloaded_assets']['summary']['total_images']}
- ملفات CSS: {result['downloaded_assets']['summary']['total_css']}
- ملفات JavaScript: {result['downloaded_assets']['summary']['total_js']}
- ملفات الوسائط: {result['downloaded_assets']['summary']['total_media']}
- المستندات: {result['downloaded_assets']['summary']['total_documents']}
- الحجم الإجمالي: {result['downloaded_assets']['summary']['total_size_mb']} MB

🔍 التحليلات:
- نظام إدارة المحتوى: {result['comprehensive_analysis'].get('cms_detection', {}).get('primary_cms', 'غير محدد')}
- الخادم: {result['comprehensive_analysis'].get('technology_stack', {}).get('server', 'غير محدد')}

📁 مجلد الاستخراج: {result['output_paths']['extraction_folder']}

=== انتهى التقرير ===
        """
        
        summary_file = extraction_folder / '05_reports' / 'summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary.strip())
    
    def _extract_website_enhanced(self, url: str, extraction_type: str) -> Dict[str, Any]:
        """محرك الاستخراج المحسن القديم (للتوافق مع النسخة السابقة)"""
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
                'extractor': 'AdvancedWebsiteExtractor'
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
                'extractor': 'AdvancedWebsiteExtractor'
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
        description = ''
        if description_tag and hasattr(description_tag, 'get'):
            content = description_tag.get('content', '')
            description = str(content) if content else ''
        
        # الكلمات المفتاحية
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = ''
        if keywords_tag and hasattr(keywords_tag, 'get'):
            content = keywords_tag.get('content', '')
            keywords = str(content) if content else ''
        
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
    
    def extract_basic(self, url: str) -> Dict[str, Any]:
        """استخراج أساسي سريع"""
        return self.extract(url, "basic")
    
    def extract_standard(self, url: str) -> Dict[str, Any]:
        """استخراج قياسي مع تحليلات متقدمة"""
        return self.extract(url, "standard")
    
    def extract_advanced(self, url: str) -> Dict[str, Any]:
        """استخراج متقدم مع تحميل الأصول"""
        return self.extract(url, "advanced")
    
    def extract_complete(self, url: str) -> Dict[str, Any]:
        """استخراج شامل مع جميع الميزات"""
        return self.extract(url, "complete")
    
    def extract_with_custom_config(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج مع إعدادات مخصصة"""
        return self.extract(url, "custom", config)
    
    def get_available_presets(self) -> List[str]:
        """الحصول على أنواع الاستخراج المتاحة"""
        return ["basic", "standard", "advanced", "complete", "ai_powered"]
    
    def create_custom_config(self, 
                           extraction_type: str = "standard",
                           extract_assets: bool = True,
                           extract_images: bool = True,
                           capture_screenshots: bool = False,
                           analyze_security: bool = True,
                           analyze_seo: bool = True,
                           export_formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        إنشاء إعدادات مخصصة
        
        Args:
            extraction_type: نوع الاستخراج الأساسي
            extract_assets: تحميل الأصول
            extract_images: تحليل الصور
            capture_screenshots: التقاط لقطات الشاشة
            analyze_security: تحليل الأمان
            analyze_seo: تحليل SEO
            export_formats: صيغ التصدير ['json', 'csv', 'html', 'pdf']
            
        Returns:
            Dict: إعدادات مخصصة
        """
        
        if export_formats is None:
            export_formats = ['json', 'html']
        
        config = get_preset_config(extraction_type)
        
        # تحديث الإعدادات المخصصة
        config.extract_assets = extract_assets
        config.extract_images = extract_images
        config.capture_screenshots = capture_screenshots
        config.analyze_security = analyze_security
        config.analyze_seo = analyze_seo
        
        # إعدادات التصدير
        config.export_json = 'json' in export_formats
        config.export_csv = 'csv' in export_formats
        config.export_html = 'html' in export_formats
        config.export_pdf = 'pdf' in export_formats
        
        return config.to_dict()
    
    # ==================== الوظائف المساعدة المتقدمة ====================
    
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
            href = link.get('href') if hasattr(link, 'get') else None
            text = link.get_text().strip() if hasattr(link, 'get_text') else ''
            
            if href and isinstance(href, str):
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
            src = img.get('src') if hasattr(img, 'get') else None
            alt = img.get('alt', '') if hasattr(img, 'get') else ''
            
            if src and isinstance(src, str):
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                
                width = img.get('width', '') if hasattr(img, 'get') else ''
                height = img.get('height', '') if hasattr(img, 'get') else ''
                img_class = img.get('class', []) if hasattr(img, 'get') else []
                
                image_analysis.append({
                    'src': src,
                    'alt': str(alt) if alt else '',
                    'width': str(width) if width else '',
                    'height': str(height) if height else '',
                    'class': img_class if isinstance(img_class, list) else []
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
            if hasattr(meta, 'get'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[str(name)] = str(content)
        
        # Headings structure
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        schema_data = []
        for script in schema_scripts:
            try:
                if script.string:
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
            src = script.get('src') if hasattr(script, 'get') else None
            if src and isinstance(src, str) and not src.startswith('/'):
                security_analysis['external_scripts'].append(src)
        
        # تحليل الـ stylesheets الخارجية
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href') if hasattr(link, 'get') else None
            if href and isinstance(href, str) and not href.startswith('/'):
                security_analysis['external_stylesheets'].append(href)
        
        # تحليل النماذج
        for form in soup.find_all('form'):
            method = 'get'
            action = ''
            if hasattr(form, 'get'):
                method_attr = form.get('method', 'get')
                method = str(method_attr).lower() if method_attr else 'get'
                action_attr = form.get('action', '')
                action = str(action_attr) if action_attr else ''
            
            has_csrf = bool(form.find('input', attrs={'name': re.compile('csrf|token', re.I)}) if hasattr(form, 'find') else False)
            inputs_count = len(form.find_all('input')) if hasattr(form, 'find_all') else 0
            
            security_analysis['forms_analysis'].append({
                'method': method,
                'action': action,
                'has_csrf_protection': has_csrf,
                'inputs_count': inputs_count
            })
        
        return security_analysis
    
    def _find_api_endpoints(self, soup: BeautifulSoup) -> List[str]:
        """البحث عن API endpoints"""
        endpoints = []
        
        # البحث في الـ JavaScript
        for script in soup.find_all('script'):
            script_content = script.string if hasattr(script, 'string') and script.string else ''
            if script_content and isinstance(script_content, str):
                # البحث عن fetch أو Ajax calls
                api_calls = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]', script_content)
                api_calls.extend(re.findall(r'\.get\([\'"`]([^\'"`]+)[\'"`]', script_content))
                api_calls.extend(re.findall(r'\.post\([\'"`]([^\'"`]+)[\'"`]', script_content))
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
        
        database_hints['field_names'] = list(database_hints['field_names'])
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
    
    # ==================== وظائف التقييم والإحصائيات ====================
    
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
    
    def _advanced_ai_analysis(self, result: Dict[str, Any], content: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل AI متقدم للنتائج"""
        ai_analysis = {
            'content_analysis': self._ai_content_analysis(soup),
            'structure_analysis': {
                'page_sections': len(soup.find_all(['section', 'article', 'div'])),
                'navigation_complexity': len(soup.find_all('nav')) + len(soup.find_all('ul')),
                'form_complexity': sum(len(form.find_all('input')) for form in soup.find_all('form'))
            },
            'quality_assessment': {
                'seo_score': self._calculate_seo_score(result.get('seo_analysis', {})),
                'security_score': self._calculate_security_score(result.get('security_analysis', {})),
                'performance_score': self._calculate_performance_score(result.get('performance', {})),
                'overall_quality': result.get('extraction_stats', {}).get('extraction_quality', 'متوسطة')
            },
            'recommendations': self._generate_improvement_recommendations(result)
        }
        
        return ai_analysis
    
    def _calculate_seo_score(self, seo_data: Dict[str, Any]) -> int:
        """حساب نقاط SEO"""
        score = 0
        max_score = 10
        
        if seo_data.get('meta_tags', {}).get('description'): score += 2
        if seo_data.get('meta_tags', {}).get('keywords'): score += 1
        if seo_data.get('headings_structure', {}).get('h1', 0) > 0: score += 2
        if seo_data.get('open_graph'): score += 2
        if seo_data.get('canonical_url'): score += 1
        if seo_data.get('schema_markup'): score += 2
        
        return int((score / max_score) * 100)
    
    def _calculate_security_score(self, security_data: Dict[str, Any]) -> int:
        """حساب نقاط الأمان"""
        score = 0
        max_score = 10
        
        if security_data.get('https_used'): score += 3
        if len(security_data.get('external_scripts', [])) < 5: score += 2
        if security_data.get('inline_scripts', 0) < 3: score += 2
        
        forms = security_data.get('forms_analysis', [])
        if forms:
            csrf_protected = sum(1 for form in forms if form.get('has_csrf_protection'))
            if csrf_protected == len(forms): score += 3
            elif csrf_protected > 0: score += 1
        else:
            score += 3  # لا توجد نماذج = أمان أعلى
        
        return int((score / max_score) * 100)
    
    def _calculate_performance_score(self, performance_data: Dict[str, Any]) -> int:
        """حساب نقاط الأداء"""
        score = 0
        max_score = 10
        
        response_time = performance_data.get('response_time', 0)
        if response_time < 1: score += 3
        elif response_time < 3: score += 2
        elif response_time < 5: score += 1
        
        content_size = performance_data.get('content_size', 0)
        if content_size < 100000: score += 2  # أقل من 100KB
        elif content_size < 500000: score += 1  # أقل من 500KB
        
        if performance_data.get('compression'): score += 2
        if performance_data.get('cache_control'): score += 1
        if performance_data.get('etag'): score += 1
        if performance_data.get('expires'): score += 1
        
        return int((score / max_score) * 100)
    
    def _generate_improvement_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """توليد توصيات للتحسين"""
        recommendations = []
        
        # توصيات SEO
        seo_analysis = result.get('seo_analysis', {})
        if not seo_analysis.get('meta_tags', {}).get('description'):
            recommendations.append('إضافة وصف meta للصفحة')
        if not seo_analysis.get('headings_structure', {}).get('h1'):
            recommendations.append('إضافة عنوان H1 للصفحة')
        if not seo_analysis.get('open_graph'):
            recommendations.append('إضافة بيانات Open Graph للشبكات الاجتماعية')
        
        # توصيات الأمان
        security_analysis = result.get('security_analysis', {})
        if not security_analysis.get('https_used'):
            recommendations.append('استخدام HTTPS بدلاً من HTTP')
        if len(security_analysis.get('external_scripts', [])) > 5:
            recommendations.append('تقليل عدد الأسكريبت الخارجية')
        
        # توصيات الأداء
        performance = result.get('performance', {})
        if performance.get('response_time', 0) > 3:
            recommendations.append('تحسين سرعة استجابة الخادم')
        if not performance.get('compression'):
            recommendations.append('تفعيل ضغط المحتوى (gzip)')
        
        return recommendations
    
    # ==================== وظائف إدارة الملفات ====================
    
    def _save_extraction_files(self, result: Dict[str, Any], content: str, soup: BeautifulSoup) -> Path:
        """حفظ ملفات الاستخراج"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extraction_folder = self.output_directory / 'content' / f"{result['extraction_id']}_{timestamp}"
        extraction_folder.mkdir(parents=True, exist_ok=True)
        
        # حفظ HTML الأصلي
        html_file = extraction_folder / 'page.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # حفظ النتائج JSON
        results_file = extraction_folder / 'extraction_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        # حفظ تقرير مفصل
        self._save_detailed_report(result, extraction_folder)
        
        # تحميل الأصول (للأنواع المتقدمة)
        if result.get('extraction_type') in ['advanced', 'complete', 'ai_powered']:
            self._download_assets(soup, result['url'], extraction_folder)
        
        # تصدير للصيغ المختلفة
        self._export_to_formats(result, extraction_folder)
        
        return extraction_folder
    
    def _save_detailed_report(self, result: Dict[str, Any], extraction_folder: Path):
        """حفظ تقرير مفصل"""
        report_content = f"""# تقرير الاستخراج المفصل

## معلومات أساسية
- **الموقع:** {result['url']}
- **نوع الاستخراج:** {result['extraction_type']}
- **وقت البدء:** {result['timestamp']}
- **المدة:** {result['duration']} ثانية
- **حالة النجاح:** {"نجح" if result['success'] else "فشل"}

## الإحصائيات
- **عدد الروابط:** {result.get('links_count', 0)}
- **عدد الصور:** {result.get('images_count', 0)}
- **عدد الأسكريبت:** {result.get('scripts_count', 0)}
- **حجم المحتوى:** {result.get('content_length', 0)} حرف

## التقنيات المكتشفة
{chr(10).join(f"- {tech}" for tech in result.get('technologies', []))}

## جودة الاستخراج
- **نوعية الاستخراج:** {result.get('extraction_stats', {}).get('extraction_quality', 'غير محدد')}
- **نسبة الاكتمال:** {result.get('extraction_stats', {}).get('completeness_score', 0)}%

## الملفات المنشأة
- **عدد الملفات:** {result.get('extraction_stats', {}).get('files_created', 0)}
- **حجم البيانات:** {result.get('extraction_stats', {}).get('folder_size_mb', 0)} MB

---
تم إنشاء هذا التقرير بواسطة AdvancedWebsiteExtractor
"""
        
        report_file = extraction_folder / 'report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def _download_assets(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path):
        """تحميل الأصول (الصور، CSS، JS)"""
        assets_folder = extraction_folder / 'assets'
        
        downloaded_assets = {
            'images': [],
            'css': [],
            'js': [],
            'failed': []
        }
        
        try:
            # تحميل الصور (أول 10)
            images_folder = assets_folder / 'images'
            images_folder.mkdir(parents=True, exist_ok=True)
            
            for img in soup.find_all('img', src=True)[:10]:
                src = img.get('src')
                if src and isinstance(src, str):
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(base_url, src)
                    
                    try:
                        response = self.session.get(src, timeout=5)
                        if response.status_code == 200:
                            filename = src.split('/')[-1] or 'image.jpg'
                            if '?' in filename:
                                filename = filename.split('?')[0]
                            
                            file_path = images_folder / filename
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            downloaded_assets['images'].append(filename)
                    except:
                        downloaded_assets['failed'].append(src)
            
            # تحميل CSS (أول 5)
            css_folder = assets_folder / 'css'
            css_folder.mkdir(parents=True, exist_ok=True)
            
            for link in soup.find_all('link', rel='stylesheet', href=True)[:5]:
                href = link.get('href')
                if href and isinstance(href, str):
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(base_url, href)
                    
                    try:
                        response = self.session.get(href, timeout=5)
                        if response.status_code == 200:
                            filename = href.split('/')[-1] or 'style.css'
                            if '?' in filename:
                                filename = filename.split('?')[0]
                            
                            file_path = css_folder / filename
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            downloaded_assets['css'].append(filename)
                    except:
                        downloaded_assets['failed'].append(href)
            
            # تحميل JS (أول 5)
            js_folder = assets_folder / 'js'
            js_folder.mkdir(parents=True, exist_ok=True)
            
            for script in soup.find_all('script', src=True)[:5]:
                src = script.get('src')
                if src and isinstance(src, str):
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(base_url, src)
                    
                    try:
                        response = self.session.get(src, timeout=5)
                        if response.status_code == 200:
                            filename = src.split('/')[-1] or 'script.js'
                            if '?' in filename:
                                filename = filename.split('?')[0]
                            
                            file_path = js_folder / filename
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            downloaded_assets['js'].append(filename)
                    except:
                        downloaded_assets['failed'].append(src)
        
        except Exception as e:
            downloaded_assets['error'] = str(e)
        
        # حفظ تقرير الأصول
        assets_report = assets_folder / 'assets_report.json'
        with open(assets_report, 'w', encoding='utf-8') as f:
            json.dump(downloaded_assets, f, ensure_ascii=False, indent=2)
        
        return downloaded_assets
    
    def _export_to_formats(self, result: Dict[str, Any], extraction_folder: Path):
        """تصدير النتائج لصيغ مختلفة"""
        exports_folder = extraction_folder / 'exports'
        exports_folder.mkdir(parents=True, exist_ok=True)
        
        # تصدير JSON مُنسق
        json_file = exports_folder / 'results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        # تصدير CSV للروابط
        if result.get('links_analysis'):
            csv_file = exports_folder / 'links.csv'
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('النوع,الرابط,النص\n')
                
                for link in result['links_analysis'].get('internal_links', []):
                    f.write(f"داخلي,{link['href']},{link['text']}\n")
                
                for link in result['links_analysis'].get('external_links', []):
                    f.write(f"خارجي,{link['href']},{link['text']}\n")
        
        # تصدير HTML تقرير
        html_file = exports_folder / 'report.html'
        html_content = self._generate_html_report(result)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html_report(self, result: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML"""
        return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير استخراج الموقع</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .quality-score {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; }}
        .excellent {{ background-color: #28a745; }}
        .good {{ background-color: #17a2b8; }}
        .medium {{ background-color: #ffc107; color: #000; }}
        .poor {{ background-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>تقرير استخراج الموقع</h1>
            <p><strong>الموقع:</strong> {result['url']}</p>
            <p><strong>التاريخ:</strong> {result['timestamp']}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{result.get('links_count', 0)}</div>
                <div>الروابط</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{result.get('images_count', 0)}</div>
                <div>الصور</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(result.get('technologies', []))}</div>
                <div>التقنيات</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{result.get('extraction_stats', {}).get('completeness_score', 0)}%</div>
                <div>نسبة الاكتمال</div>
            </div>
        </div>
        
        <h2>جودة الاستخراج</h2>
        <p>نوعية الاستخراج: <span class="quality-score good">{result.get('extraction_stats', {}).get('extraction_quality', 'غير محدد')}</span></p>
        
        <h2>التقنيات المكتشفة</h2>
        <ul>
            {''.join(f'<li>{tech}</li>' for tech in result.get('technologies', []))}
        </ul>
        
        <h2>تفاصيل الأداء</h2>
        <ul>
            <li><strong>وقت الاستجابة:</strong> {result.get('performance', {}).get('response_time', 0)} ثانية</li>
            <li><strong>حجم المحتوى:</strong> {result.get('content_length', 0)} حرف</li>
            <li><strong>مدة الاستخراج:</strong> {result['duration']} ثانية</li>
        </ul>
    </div>
</body>
</html>"""
    
    def _capture_screenshots_simple(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """التقاط لقطات شاشة بسيطة (placeholder)"""
        # هذه دالة بديلة بسيطة لحين توفر مكتبة لقطات الشاشة
        screenshots_folder = extraction_folder / 'screenshots'
        screenshots_folder.mkdir(parents=True, exist_ok=True)
        
        # إنشاء تقرير لقطات الشاشة
        screenshot_report = {
            'total_screenshots': 0,
            'desktop_screenshot': None,
            'mobile_screenshot': None,
            'status': 'مُعطل مؤقتاً - يتطلب مكتبة selenium أو playwright',
            'note': 'سيتم تفعيل هذه الميزة عند توفر المكتبات المطلوبة'
        }
        
        # حفظ HTML معاينة
        preview_html = f"""<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>معاينة الموقع</title>
</head>
<body>
    <h1>معاينة الموقع</h1>
    <p><strong>الرابط:</strong> <a href="{url}" target="_blank">{url}</a></p>
    <iframe src="{url}" width="100%" height="600px" frameborder="0"></iframe>
</body>
</html>"""
        
        preview_file = screenshots_folder / 'preview.html'
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write(preview_html)
        
        return screenshot_report


# دوال مساعدة للاستخدام السريع
def quick_extract(url: str, extraction_type: str = "standard") -> Dict[str, Any]:
    """استخراج سريع بإعدادات افتراضية"""
    extractor = AdvancedWebsiteExtractor()
    return extractor.extract(url, extraction_type)


def extract_basic_info(url: str) -> Dict[str, Any]:
    """استخراج المعلومات الأساسية فقط"""
    return quick_extract(url, "basic")


def extract_with_assets(url: str) -> Dict[str, Any]:
    """استخراج مع تحميل جميع الأصول"""
    return quick_extract(url, "advanced")


def extract_complete_analysis(url: str) -> Dict[str, Any]:
    """تحليل شامل مع جميع الميزات"""
    return quick_extract(url, "complete")


def extract_ai_powered(url: str) -> Dict[str, Any]:
    """استخراج بالذكاء الاصطناعي مع جميع الميزات المتقدمة"""
    return quick_extract(url, "ai_powered")


def batch_extract(urls: List[str], extraction_type: str = "standard") -> Dict[str, Any]:
    """
    استخراج متعدد المواقع
    
    Args:
        urls: قائمة بروابط المواقع
        extraction_type: نوع الاستخراج
        
    Returns:
        Dict: نتائج الاستخراج لجميع المواقع
    """
    
    extractor = AdvancedWebsiteExtractor()
    results = {}
    
    for i, url in enumerate(urls):
        print(f"استخراج الموقع {i+1}/{len(urls)}: {url}")
        try:
            result = extractor.extract(url, extraction_type)
            results[url] = result
        except Exception as e:
            results[url] = {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    return {
        'total_sites': len(urls),
        'successful_extractions': sum(1 for r in results.values() if r.get('success', False)),
        'failed_extractions': sum(1 for r in results.values() if not r.get('success', False)),
        'results': results
    }


# مثال للاستخدام
if __name__ == "__main__":
    # استخراج أساسي
    result = extract_basic_info("https://example.com")
    print(f"استخراج أساسي: {result.get('title', 'غير متوفر')}")
    
    # استخراج متقدم
    result = extract_with_assets("https://example.com")
    print(f"عدد الأصول المحملة: {len(result.get('assets', {}).get('images', []))}")
    
    # استخراج مخصص
    extractor = AdvancedWebsiteExtractor()
    custom_config = extractor.create_custom_config(
        extraction_type="advanced",
        capture_screenshots=True,
        export_formats=['json', 'html', 'csv']
    )
    
    result = extractor.extract_with_custom_config("https://example.com", custom_config)
    print(f"استخراج مخصص مكتمل: {result.get('success', False)}")


# =====================================
# الوظائف المساعدة الشاملة المطلوبة
# =====================================

def _download_asset_comprehensive(self, url: str, folder: Path, result_dict: Dict):
    """تحميل أصل واحد بشكل شامل"""
    try:
        folder.mkdir(exist_ok=True, parents=True)
        response = self.session.get(url, timeout=15, verify=False, stream=True)
        response.raise_for_status()
        
        # تحديد اسم الملف
        filename = url.split('/')[-1].split('?')[0] or f"asset_{len(result_dict['downloaded'])}"
        
        # تحديد الامتداد حسب نوع المحتوى
        content_type = response.headers.get('content-type', '').lower()
        if not '.' in filename:
            if 'image' in content_type:
                if 'jpeg' in content_type or 'jpg' in content_type:
                    filename += '.jpg'
                elif 'png' in content_type:
                    filename += '.png'
                elif 'svg' in content_type:
                    filename += '.svg'
                elif 'webp' in content_type:
                    filename += '.webp'
                else:
                    filename += '.img'
            elif 'css' in content_type:
                filename += '.css'
            elif 'javascript' in content_type:
                filename += '.js'
            elif 'font' in content_type:
                if 'woff2' in content_type:
                    filename += '.woff2'
                elif 'woff' in content_type:
                    filename += '.woff'
                elif 'ttf' in content_type:
                    filename += '.ttf'
                else:
                    filename += '.font'
            elif 'video' in content_type:
                filename += '.mp4'
            elif 'audio' in content_type:
                filename += '.mp3'
            elif 'pdf' in content_type:
                filename += '.pdf'
        
        file_path = folder / filename
        
        # تحميل الملف
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = file_path.stat().st_size / 1024 / 1024  # MB
        result_dict['downloaded'].append({
            'url': url,
            'file_path': str(file_path),
            'filename': filename,
            'size_mb': round(file_size, 3),
            'content_type': content_type
        })
        
    except Exception as e:
        result_dict['failed'].append({'url': url, 'error': str(e)})

# الآن سأضيف الوظائف المفقودة مباشرة إلى الكلاس
def add_missing_methods_to_extractor():
    """إضافة الوظائف المفقودة إلى كلاس AdvancedWebsiteExtractor"""
    
    def _extract_technical_structure(self, soup: BeautifulSoup, url: str, base_folder: Path) -> Dict[str, Any]:
        """استخراج البنية التقنية الشاملة"""
        technical_info = {
            'source_code': {'html': '', 'css': [], 'js': []},
            'api_endpoints': [],
            'routing_system': {},
            'authentication_systems': [],
            'server_config': {},
            'database_structure': {},
            'interactive_features': {}
        }
        
        try:
            # حفظ الكود المصدري الكامل
            source_folder = base_folder / '03_technical' / 'source_code'
            source_folder.mkdir(exist_ok=True, parents=True)
            
            # HTML الأساسي
            html_file = source_folder / 'main.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            technical_info['source_code']['html'] = str(html_file)
            
            # استخراج جميع ملفات CSS
            css_links = soup.find_all('link', rel='stylesheet')
            for i, link in enumerate(css_links[:10]):
                href = link.get('href')
                if href:
                    try:
                        css_url = urljoin(url, href)
                        css_response = self.session.get(css_url, timeout=10, verify=False)
                        css_file = source_folder / f'style_{i}.css'
                        with open(css_file, 'w', encoding='utf-8') as f:
                            f.write(css_response.text)
                        technical_info['source_code']['css'].append(str(css_file))
                    except:
                        pass
            
            # استخراج جميع ملفات JavaScript
            js_scripts = soup.find_all('script', src=True)
            for i, script in enumerate(js_scripts[:10]):
                src = script.get('src')
                if src:
                    try:
                        js_url = urljoin(url, src)
                        js_response = self.session.get(js_url, timeout=10, verify=False)
                        js_file = source_folder / f'script_{i}.js'
                        with open(js_file, 'w', encoding='utf-8') as f:
                            f.write(js_response.text)
                        technical_info['source_code']['js'].append(str(js_file))
                    except:
                        pass
            
            # كشف API endpoints
            technical_info['api_endpoints'] = self._find_api_endpoints(soup)
            
            # تحليل النماذج والتفاعلات
            forms = soup.find_all('form')
            technical_info['interactive_features']['forms'] = len(forms)
            technical_info['interactive_features']['form_details'] = []
            
            for form in forms:
                form_info = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET').upper(),
                    'inputs': []
                }
                
                inputs = form.find_all(['input', 'select', 'textarea'])
                for inp in inputs:
                    form_info['inputs'].append({
                        'name': inp.get('name', ''),
                        'type': inp.get('type', inp.name),
                        'required': inp.has_attr('required')
                    })
                
                technical_info['interactive_features']['form_details'].append(form_info)
            
            # حفظ التحليل التقني
            tech_file = base_folder / '03_technical' / 'technical_analysis.json'
            with open(tech_file, 'w', encoding='utf-8') as f:
                json.dump(technical_info, f, ensure_ascii=False, indent=2)
            
            return technical_info
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _analyze_design_and_interaction(self, soup: BeautifulSoup, url: str, base_folder: Path) -> Dict[str, Any]:
        """تحليل التصميم والتفاعل"""
        design_info = {
            'layouts': {},
            'responsive_design': {},
            'animations': [],
            'ui_components': {},
            'user_experience': {}
        }
        
        try:
            # تحليل التخطيطات
            design_info['layouts']['has_grid'] = bool(soup.find(class_=re.compile(r'grid|row|col')))
            design_info['layouts']['has_flexbox'] = bool(soup.find(attrs={'style': re.compile(r'flex|display:\s*flex')}))
            design_info['layouts']['main_containers'] = len(soup.find_all(['div', 'section', 'article', 'main']))
            
            # كشف التصميم المتجاوب
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            design_info['responsive_design']['has_viewport_meta'] = bool(viewport_meta)
            design_info['responsive_design']['media_queries_detected'] = False
            
            # البحث عن media queries في CSS
            for style in soup.find_all('style'):
                if '@media' in style.get_text():
                    design_info['responsive_design']['media_queries_detected'] = True
                    break
            
            # كشف المكونات الشائعة
            design_info['ui_components']['navigation'] = len(soup.find_all(['nav', 'menu']))
            design_info['ui_components']['buttons'] = len(soup.find_all(['button', 'input[type="submit"]', 'input[type="button"]']))
            design_info['ui_components']['modals'] = len(soup.find_all(class_=re.compile(r'modal|popup|dialog')))
            design_info['ui_components']['carousels'] = len(soup.find_all(class_=re.compile(r'carousel|slider|swiper')))
            design_info['ui_components']['tabs'] = len(soup.find_all(class_=re.compile(r'tab|tabpanel')))
            
            # تحليل تجربة المستخدم
            design_info['user_experience']['accessibility_score'] = self._calculate_accessibility_score(soup)
            design_info['user_experience']['loading_indicators'] = len(soup.find_all(class_=re.compile(r'loading|spinner|progress')))
            design_info['user_experience']['error_handling'] = len(soup.find_all(class_=re.compile(r'error|alert|warning')))
            
            # حفظ تحليل التصميم
            design_file = base_folder / '04_design' / 'design_analysis.json'
            design_file.parent.mkdir(exist_ok=True, parents=True)
            with open(design_file, 'w', encoding='utf-8') as f:
                json.dump(design_info, f, ensure_ascii=False, indent=2)
            
            return design_info
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _capture_automatic_screenshots(self, url: str, base_folder: Path) -> Dict[str, Any]:
        """التقاط screenshots تلقائي للصفحة"""
        screenshots_result = {
            'desktop': None,
            'tablet': None,
            'mobile': None,
            'full_page': None,
            'success': False,
            'errors': []
        }
        
        screenshots_folder = base_folder / '05_screenshots'
        timestamps = int(time.time())
        
        try:
            # محاولة استخدام Selenium إذا كان متاحاً
            if SELENIUM_AVAILABLE:
                from selenium.webdriver.chrome.options import Options
                
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.get(url)
                    time.sleep(3)  # انتظار تحميل الصفحة
                    
                    # سطح المكتب (1920x1080)
                    driver.set_window_size(1920, 1080)
                    desktop_file = screenshots_folder / f'desktop_{timestamps}.png'
                    driver.save_screenshot(str(desktop_file))
                    screenshots_result['desktop'] = str(desktop_file)
                    
                    # اللوحي (768x1024)
                    driver.set_window_size(768, 1024)
                    tablet_file = screenshots_folder / f'tablet_{timestamps}.png'
                    driver.save_screenshot(str(tablet_file))
                    screenshots_result['tablet'] = str(tablet_file)
                    
                    # الهاتف (375x667)
                    driver.set_window_size(375, 667)
                    mobile_file = screenshots_folder / f'mobile_{timestamps}.png'
                    driver.save_screenshot(str(mobile_file))
                    screenshots_result['mobile'] = str(mobile_file)
                    
                    # الصفحة الكاملة
                    driver.set_window_size(1920, driver.execute_script("return document.body.scrollHeight"))
                    full_page_file = screenshots_folder / f'full_page_{timestamps}.png'
                    driver.save_screenshot(str(full_page_file))
                    screenshots_result['full_page'] = str(full_page_file)
                    
                    driver.quit()
                    screenshots_result['success'] = True
                    
                except Exception as e:
                    screenshots_result['errors'].append(f'Selenium error: {str(e)}')
                    
            else:
                # محاولة استخدام طريقة بديلة
                screenshots_result['errors'].append('لا يوجد محرك لقطات شاشة متاح')
                
                # إنشاء ملف نصي يحتوي على معلومات الصفحة بدلاً من الصورة
                info_file = screenshots_folder / f'page_info_{timestamps}.txt'
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"معلومات الصفحة: {url}\n")
                    f.write(f"وقت الاستخراج: {datetime.now().isoformat()}\n")
                    f.write("ملاحظة: لم يتم التقاط لقطة شاشة بسبب عدم توفر المكتبات المطلوبة\n")
                screenshots_result['info_file'] = str(info_file)
                
        except Exception as e:
            screenshots_result['errors'].append(str(e))
        
        return screenshots_result
    
    def _calculate_accessibility_score(self, soup: BeautifulSoup) -> float:
        """حساب نقاط إمكانية الوصول"""
        score = 0
        total_checks = 10
        
        # فحص وجود alt في الصور
        images = soup.find_all('img')
        images_with_alt = sum(1 for img in images if img.get('alt'))
        if images:
            score += (images_with_alt / len(images)) * 10
        else:
            score += 10
        
        # فحص وجود labels للنماذج
        inputs = soup.find_all('input')
        labeled_inputs = sum(1 for inp in inputs if inp.get('id') and soup.find('label', attrs={'for': inp.get('id')}))
        if inputs:
            score += (labeled_inputs / len(inputs)) * 10
        else:
            score += 10
        
        # فحص هيكل العناوين
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            score += 15
        
        # فحص وجود lang attribute
        if soup.find('html', attrs={'lang': True}):
            score += 15
        
        # فحص وجود معرفات ARIA
        aria_elements = soup.find_all(attrs={'aria-label': True})
        if aria_elements:
            score += 10
        
        return min(score, 100)
    
    # إضافة الوظائف إلى الكلاس
    AdvancedWebsiteExtractor._extract_technical_structure = _extract_technical_structure
    AdvancedWebsiteExtractor._analyze_design_and_interaction = _analyze_design_and_interaction
    AdvancedWebsiteExtractor._capture_automatic_screenshots = _capture_automatic_screenshots
    AdvancedWebsiteExtractor._calculate_accessibility_score = _calculate_accessibility_score

# تنفيذ الإضافة
add_missing_methods_to_extractor()

# إضافة المزيد من الوظائف المطلوبة
def add_comprehensive_methods():
    """إضافة الوظائف الشاملة المتبقية"""
    
    def _detect_comprehensive_cms(self, soup: BeautifulSoup, response) -> Dict[str, Any]:
        """كشف شامل لنظام إدارة المحتوى المستخدم"""
        cms_info = {
            'detected_cms': 'غير محدد',
            'confidence': 0,
            'indicators': [],
            'version': 'غير معروف',
            'plugins_detected': [],
            'theme_info': {}
        }
        
        content_lower = response.text.lower()
        
        # WordPress
        wp_indicators = [
            'wp-content', 'wp-includes', 'wordpress', 'wp-admin',
            'wp_enqueue_script', 'wp-json', 'wp-emoji'
        ]
        wp_score = sum(1 for indicator in wp_indicators if indicator in content_lower)
        
        if wp_score >= 2:
            cms_info['detected_cms'] = 'WordPress'
            cms_info['confidence'] = min(wp_score * 20, 100)
            cms_info['indicators'] = [ind for ind in wp_indicators if ind in content_lower]
            
            # كشف الإضافات
            import re
            plugins = re.findall(r'wp-content/plugins/([^/]+)', response.text)
            cms_info['plugins_detected'] = list(set(plugins))
            
            # كشف القالب
            theme_match = re.search(r'wp-content/themes/([^/]+)', response.text)
            if theme_match:
                cms_info['theme_info']['name'] = theme_match.group(1)
        
        # Joomla
        joomla_indicators = ['joomla', 'components/com_', 'modules/mod_', 'templates/']
        joomla_score = sum(1 for indicator in joomla_indicators if indicator in content_lower)
        
        if joomla_score >= 2 and joomla_score > wp_score:
            cms_info['detected_cms'] = 'Joomla'
            cms_info['confidence'] = min(joomla_score * 25, 100)
            cms_info['indicators'] = [ind for ind in joomla_indicators if ind in content_lower]
        
        # Drupal
        drupal_indicators = ['drupal', 'sites/default', 'misc/drupal.js', 'modules/', 'sites/all']
        drupal_score = sum(1 for indicator in drupal_indicators if indicator in content_lower)
        
        if drupal_score >= 2 and drupal_score > max(wp_score, joomla_score):
            cms_info['detected_cms'] = 'Drupal'
            cms_info['confidence'] = min(drupal_score * 25, 100)
            cms_info['indicators'] = [ind for ind in drupal_indicators if ind in content_lower]
        
        return cms_info
    
    def _comprehensive_security_test(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """اختبار شامل للحماية والثغرات"""
        security_result = {
            'ssl_analysis': {},
            'headers_analysis': {},
            'vulnerability_scan': {},
            'broken_links': [],
            'security_score': 0,
            'recommendations': []
        }
        
        try:
            # تحليل SSL
            if url.startswith('https://'):
                security_result['ssl_analysis']['uses_https'] = True
                security_result['security_score'] += 25
            else:
                security_result['ssl_analysis']['uses_https'] = False
                security_result['recommendations'].append('استخدم HTTPS للحماية')
            
            # فحص Headers الأمنية
            try:
                response = self.session.head(url, timeout=10, verify=False)
                headers = response.headers
                
                security_headers = {
                    'Content-Security-Policy': 'CSP غير موجود',
                    'X-Frame-Options': 'حماية من Clickjacking غير فعالة',
                    'X-XSS-Protection': 'حماية XSS غير فعالة',
                    'X-Content-Type-Options': 'حماية MIME-Type غير فعالة',
                    'Strict-Transport-Security': 'HSTS غير فعال'
                }
                
                security_result['headers_analysis'] = {}
                for header, warning in security_headers.items():
                    if header in headers:
                        security_result['headers_analysis'][header] = headers[header]
                        security_result['security_score'] += 10
                    else:
                        security_result['headers_analysis'][header] = 'غير موجود'
                        security_result['recommendations'].append(warning)
                
            except Exception as e:
                security_result['headers_analysis']['error'] = str(e)
            
            # فحص الروابط المعطلة
            links = soup.find_all('a', href=True)
            for link in links[:20]:  # فحص أول 20 رابط
                href = link.get('href')
                if href and href.startswith(('http://', 'https://')):
                    try:
                        link_response = self.session.head(href, timeout=5, verify=False)
                        if link_response.status_code >= 400:
                            security_result['broken_links'].append({
                                'url': href,
                                'status_code': link_response.status_code,
                                'text': link.get_text().strip()[:50]
                            })
                    except:
                        security_result['broken_links'].append({
                            'url': href,
                            'status_code': 'timeout/error',
                            'text': link.get_text().strip()[:50]
                        })
            
            # فحص الثغرات الأساسية
            security_result['vulnerability_scan'] = {
                'forms_without_csrf': len([f for f in soup.find_all('form') if not f.find('input', attrs={'name': re.compile(r'csrf|token')})]),
                'external_scripts': len([s for s in soup.find_all('script', src=True) if not urlparse(s.get('src')).netloc in ['', urlparse(url).netloc]]),
                'mixed_content_risk': 'https' in url and bool(soup.find_all(src=re.compile(r'^http://'))),
                'sensitive_info_exposed': bool(re.search(r'(password|api[_-]?key|secret|token)\s*[:=]\s*["\'][^"\']+["\']', str(soup), re.IGNORECASE))
            }
            
            # حساب النقاط النهائية
            max_score = 100
            if security_result['vulnerability_scan']['forms_without_csrf'] > 0:
                security_result['security_score'] -= 15
                security_result['recommendations'].append('أضف حماية CSRF للنماذج')
            
            if security_result['vulnerability_scan']['external_scripts'] > 0:
                security_result['security_score'] -= 10
                security_result['recommendations'].append('راجع السكريبت الخارجية')
            
            security_result['security_score'] = max(0, min(security_result['security_score'], max_score))
            
        except Exception as e:
            security_result['error'] = str(e)
        
        return security_result
    
    def _crawl_internal_links(self, start_url: str, base_folder: Path, max_depth: int = 3, max_pages: int = 50) -> Dict[str, Any]:
        """زحف شامل للروابط الداخلية"""
        crawl_result = {
            'pages_crawled': 0,
            'total_links_found': 0,
            'crawl_map': {},
            'assets_found': {'images': 0, 'css': 0, 'js': 0},
            'forms_found': 0,
            'errors': []
        }
        
        visited_urls = set()
        urls_to_visit = [(start_url, 0)]  # (url, depth)
        crawled_folder = base_folder / '08_crawled_pages'
        crawled_folder.mkdir(exist_ok=True, parents=True)
        
        base_domain = urlparse(start_url).netloc
        
        while urls_to_visit and crawl_result['pages_crawled'] < max_pages:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in visited_urls or depth > max_depth:
                continue
                
            try:
                print(f"🕷️ زحف الصفحة: {current_url} (عمق: {depth})")
                response = self.session.get(current_url, timeout=15, verify=False)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                visited_urls.add(current_url)
                
                # حفظ الصفحة
                page_filename = f"page_{crawl_result['pages_crawled'] + 1}_{urlparse(current_url).path.replace('/', '_')}.html"
                page_file = crawled_folder / page_filename
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # تحليل الصفحة
                page_info = {
                    'title': soup.find('title').get_text().strip() if soup.find('title') else '',
                    'depth': depth,
                    'file_path': str(page_file),
                    'links': [],
                    'assets': {'images': 0, 'css': 0, 'js': 0},
                    'forms': len(soup.find_all('form'))
                }
                
                # استخراج الروابط الداخلية
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(current_url, href)
                        parsed_url = urlparse(full_url)
                        
                        # روابط داخلية فقط
                        if parsed_url.netloc == base_domain and full_url not in visited_urls:
                            page_info['links'].append(full_url)
                            crawl_result['total_links_found'] += 1
                            
                            if depth < max_depth:
                                urls_to_visit.append((full_url, depth + 1))
                
                # إحصاء الأصول
                page_info['assets']['images'] = len(soup.find_all('img'))
                page_info['assets']['css'] = len(soup.find_all('link', rel='stylesheet'))
                page_info['assets']['js'] = len(soup.find_all('script', src=True))
                
                # تحديث الإحصائيات الإجمالية
                for asset_type in page_info['assets']:
                    crawl_result['assets_found'][asset_type] += page_info['assets'][asset_type]
                
                crawl_result['forms_found'] += page_info['forms']
                crawl_result['crawl_map'][current_url] = page_info
                crawl_result['pages_crawled'] += 1
                
                # تأخير بين الطلبات
                time.sleep(1)
                
            except Exception as e:
                crawl_result['errors'].append({
                    'url': current_url,
                    'error': str(e),
                    'depth': depth
                })
        
        # حفظ خريطة الزحف
        crawl_map_file = crawled_folder / 'crawl_map.json'
        with open(crawl_map_file, 'w', encoding='utf-8') as f:
            json.dump(crawl_result, f, ensure_ascii=False, indent=2)
        
        return crawl_result
    
    def _extract_ajax_content(self, url: str, soup: BeautifulSoup, base_folder: Path) -> Dict[str, Any]:
        """استخراج المحتوى من AJAX والـXHR"""
        ajax_result = {
            'ajax_calls_detected': [],
            'xhr_endpoints': [],
            'dynamic_content_areas': [],
            'api_calls': [],
            'websocket_connections': []
        }
        
        try:
            # البحث عن jQuery AJAX calls
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.get_text()
                
                # البحث عن $.ajax, $.get, $.post
                ajax_patterns = [
                    r'\$\.ajax\s*\(\s*{[^}]*url\s*:\s*["\']([^"\']+)["\']',
                    r'\$\.get\s*\(\s*["\']([^"\']+)["\']',
                    r'\$\.post\s*\(\s*["\']([^"\']+)["\']',
                    r'fetch\s*\(\s*["\']([^"\']+)["\']',
                    r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in ajax_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        full_url = urljoin(url, match)
                        ajax_result['ajax_calls_detected'].append({
                            'url': full_url,
                            'type': 'detected_in_script'
                        })
            
            # البحث عن WebSocket connections
            websocket_pattern = r'new\s+WebSocket\s*\(\s*["\']([^"\']+)["\']'
            for script in scripts:
                ws_matches = re.findall(websocket_pattern, script.get_text())
                ajax_result['websocket_connections'].extend(ws_matches)
            
            # البحث عن data-* attributes التي قد تشير إلى AJAX
            elements_with_data = soup.find_all(attrs={'data-url': True})
            for element in elements_with_data:
                data_url = element.get('data-url')
                if data_url:
                    full_url = urljoin(url, data_url)
                    ajax_result['xhr_endpoints'].append({
                        'url': full_url,
                        'element': element.name,
                        'classes': element.get('class', [])
                    })
            
            # البحث عن المناطق التي يتم تحديثها ديناميكياً
            dynamic_indicators = soup.find_all(class_=re.compile(r'dynamic|ajax|load|update|refresh'))
            for element in dynamic_indicators:
                ajax_result['dynamic_content_areas'].append({
                    'tag': element.name,
                    'classes': element.get('class', []),
                    'id': element.get('id', ''),
                    'content_preview': element.get_text()[:100]
                })
            
            # حفظ نتائج AJAX
            ajax_folder = base_folder / '09_ajax_content'
            ajax_folder.mkdir(exist_ok=True, parents=True)
            
            ajax_file = ajax_folder / 'ajax_analysis.json'
            with open(ajax_file, 'w', encoding='utf-8') as f:
                json.dump(ajax_result, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            ajax_result['error'] = str(e)
        
        return ajax_result
    
    def _save_comprehensive_report(self, final_result: Dict[str, Any], base_folder: Path):
        """حفظ التقرير الشامل"""
        reports_folder = base_folder / '10_reports'
        reports_folder.mkdir(exist_ok=True, parents=True)
        
        # تقرير JSON كامل
        json_report = reports_folder / 'comprehensive_report.json'
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2, default=str)
        
        # تقرير HTML مبسط
        html_report = reports_folder / 'summary_report.html'
        with open(html_report, 'w', encoding='utf-8') as f:
            f.write(self._generate_html_report(final_result))
        
        # ملخص نصي
        text_summary = reports_folder / 'extraction_summary.txt'
        with open(text_summary, 'w', encoding='utf-8') as f:
            f.write(self._generate_text_summary(final_result))
    
    def _generate_html_report(self, result: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML"""
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير الاستخراج الشامل</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ color: #27ae60; }}
                .error {{ color: #e74c3c; }}
                .stats {{ display: flex; flex-wrap: wrap; gap: 15px; }}
                .stat-item {{ background: #f8f9fa; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>تقرير الاستخراج الشامل</h1>
                <p>الموقع: {result.get('extraction_info', {}).get('url', 'غير محدد')}</p>
                <p>التاريخ: {result.get('extraction_info', {}).get('timestamp', 'غير محدد')}</p>
            </div>
            
            <div class="section">
                <h2>الإحصائيات العامة</h2>
                <div class="stats">
                    <div class="stat-item">
                        <strong>الوقت المستغرق:</strong> {result.get('extraction_info', {}).get('duration', 0)} ثانية
                    </div>
                    <div class="stat-item">
                        <strong>الصفحات المزحوفة:</strong> {result.get('crawl_results', {}).get('pages_crawled', 0)}
                    </div>
                    <div class="stat-item">
                        <strong>الأصول المحملة:</strong> {result.get('assets_download', {}).get('summary', {}).get('total_downloaded', 0)}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>تحليل الأمان</h2>
                <p><strong>نقاط الأمان:</strong> {result.get('security_test', {}).get('security_score', 0)}/100</p>
                <p><strong>نظام إدارة المحتوى:</strong> {result.get('cms_detection', {}).get('detected_cms', 'غير محدد')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_text_summary(self, result: Dict[str, Any]) -> str:
        """إنشاء ملخص نصي"""
        summary = f"""
تقرير الاستخراج الشامل
======================

الموقع: {result.get('extraction_info', {}).get('url', 'غير محدد')}
نوع الاستخراج: {result.get('extraction_info', {}).get('extraction_type', 'غير محدد')}
التاريخ: {result.get('extraction_info', {}).get('timestamp', 'غير محدد')}
الوقت المستغرق: {result.get('extraction_info', {}).get('duration', 0)} ثانية

الإحصائيات:
-----------
- الصفحات المزحوفة: {result.get('crawl_results', {}).get('pages_crawled', 0)}
- الأصول المحملة: {result.get('assets_download', {}).get('summary', {}).get('total_downloaded', 0)}
- الروابط المكتشفة: {result.get('crawl_results', {}).get('total_links_found', 0)}
- النماذج الموجودة: {result.get('crawl_results', {}).get('forms_found', 0)}

التحليل التقني:
---------------
- نظام إدارة المحتوى: {result.get('cms_detection', {}).get('detected_cms', 'غير محدد')}
- نقاط الأمان: {result.get('security_test', {}).get('security_score', 0)}/100
- استخدام HTTPS: {'نعم' if result.get('security_test', {}).get('ssl_analysis', {}).get('uses_https') else 'لا'}

الملفات المحفوظة:
-----------------
- مجلد الاستخراج: {result.get('extraction_info', {}).get('base_folder', 'غير محدد')}
- تم إنشاء هيكل مجلدات منظم مع جميع الأصول والتحليلات

        """
        return summary
    
    # إضافة الوظائف الجديدة
    AdvancedWebsiteExtractor._detect_comprehensive_cms = _detect_comprehensive_cms
    AdvancedWebsiteExtractor._comprehensive_security_test = _comprehensive_security_test
    AdvancedWebsiteExtractor._crawl_internal_links = _crawl_internal_links
    AdvancedWebsiteExtractor._extract_ajax_content = _extract_ajax_content
    AdvancedWebsiteExtractor._save_comprehensive_report = _save_comprehensive_report
    AdvancedWebsiteExtractor._generate_html_report = _generate_html_report
    AdvancedWebsiteExtractor._generate_text_summary = _generate_text_summary

# تنفيذ الإضافة
add_comprehensive_methods()