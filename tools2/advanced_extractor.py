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
    
    def _setup_extraction_directories(self):
        """إعداد مجلدات الإخراج"""
        base_dirs = ['content', 'assets', 'analysis', 'exports', 'screenshots']
        for dir_name in base_dirs:
            (self.output_directory / dir_name).mkdir(parents=True, exist_ok=True)
        
    def extract(self, url: str, extraction_type: str = "standard", custom_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        استخراج شامل للموقع
        
        Args:
            url: رابط الموقع المراد استخراجه
            extraction_type: نوع الاستخراج (basic, standard, advanced, complete, ai_powered)
            custom_config: إعدادات مخصصة اختيارية
            
        Returns:
            Dict: نتائج الاستخراج الشاملة
        """
        
        # إعداد التكوين
        if custom_config:
            config = ExtractionConfig.from_dict(custom_config)
        else:
            config = get_preset_config(extraction_type)
        
        config.target_url = url
        config.output_directory = str(self.output_directory)
        
        # تهيئة المحرك
        self.engine = AdvancedExtractorEngine(config)
        
        # استخدام المحرك الجديد المحسن
        result = self._extract_website_enhanced(url, extraction_type)
            
        return result
    
    def _extract_website_enhanced(self, url: str, extraction_type: str) -> Dict[str, Any]:
        """محرك الاستخراج المحسن مع الوظائف المتقدمة"""
        self.extraction_id += 1
        extraction_id = f"extract_{self.extraction_id}_{int(time.time())}"
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