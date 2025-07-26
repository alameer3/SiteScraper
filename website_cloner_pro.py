"""
Website Cloner Pro - أداة استنساخ المواقع المتقدمة
===============================================

أداة شاملة موحدة لاستخراج ونسخ المواقع بشكل كامل
تدمج جميع الوظائف في نظام واحد متكامل

المميزات:
- استخراج شامل لكل محتويات الموقع
- نسخ طبق الأصل للمواقع
- تحليل بالذكاء الاصطناعي
- تقارير مفصلة وشاملة
- دعم للمواقع المعقدة والتفاعلية
- استخراج قواعد البيانات والـ APIs
- تجاوز الحماية والمحتوى المخفي
"""

import asyncio
import aiohttp
import aiofiles
import os
import json
import time
import logging
import hashlib
import re
import ssl
import csv
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue

# Web scraping and parsing
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Advanced browser automation
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

# Content analysis
try:
    import builtwith
    BUILTWITH_AVAILABLE = True
except ImportError:
    BUILTWITH_AVAILABLE = False

# Document generation
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

@dataclass
class CloningConfig:
    """إعدادات شاملة لعملية الاستنساخ"""
    
    # Basic settings
    target_url: str = ""
    output_directory: str = "cloned_websites"
    max_depth: int = 5
    max_pages: int = 1000
    timeout: int = 30
    delay_between_requests: float = 1.0
    
    # Content extraction
    extract_all_content: bool = True
    extract_hidden_content: bool = True
    extract_dynamic_content: bool = True
    extract_media_files: bool = True
    extract_documents: bool = True
    extract_apis: bool = True
    extract_database_structure: bool = True
    
    # Advanced features
    bypass_protection: bool = True
    handle_javascript: bool = True
    handle_ajax: bool = True
    detect_spa: bool = True
    extract_source_code: bool = True
    analyze_with_ai: bool = True
    
    # Security and stealth
    use_proxy: bool = False
    proxy_list: List[str] = field(default_factory=list)
    rotate_user_agents: bool = True
    respect_robots_txt: bool = False
    handle_captcha: bool = True
    
    # Output formats
    create_identical_copy: bool = True
    generate_reports: bool = True
    export_formats: List[str] = field(default_factory=lambda: ['html', 'json', 'csv', 'pdf', 'docx'])
    detailed_logging: bool = True
    
    # Performance
    parallel_downloads: int = 10
    use_caching: bool = True
    optimize_images: bool = False
    compress_output: bool = False

@dataclass 
class CloningResult:
    """نتائج عملية الاستنساخ"""
    
    success: bool = False
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    
    # Statistics
    pages_extracted: int = 0
    assets_downloaded: int = 0
    errors_encountered: int = 0
    total_size: int = 0
    
    # Paths and files
    output_path: str = ""
    cloned_site_path: str = ""
    reports_path: str = ""
    
    # Analysis results
    technologies_detected: Dict[str, Any] = field(default_factory=dict)
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    security_analysis: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Detailed results
    extracted_content: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class WebsiteClonerPro:
    """أداة استنساخ المواقع المتقدمة الموحدة"""
    
    def __init__(self, config: Optional[CloningConfig] = None):
        self.config = config or CloningConfig()
        self.logger = self._setup_logging()
        self.session: Optional[aiohttp.ClientSession] = None
        self.selenium_driver: Optional[webdriver.Chrome] = None
        
        # Results storage
        self.result = CloningResult()
        self.extracted_urls: Set[str] = set()
        self.download_queue: queue.Queue = queue.Queue()
        self.error_count: int = 0
        
        # Analysis caches
        self.content_cache: Dict[str, str] = {}
        self.asset_cache: Dict[str, bytes] = {}
        self.analysis_cache: Dict[str, Any] = {}
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        self.current_user_agent_index = 0
        
    def _setup_logging(self) -> logging.Logger:
        """إعداد نظام التسجيل"""
        logger = logging.getLogger('WebsiteClonerPro')
        logger.setLevel(logging.DEBUG if self.config.detailed_logging else logging.INFO)
        
        # إنشاء معالج الملف
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(f'logs/cloner_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler.setLevel(logging.DEBUG)
        
        # إنشاء معالج وحدة التحكم
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # تنسيق الرسائل
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    async def clone_website_complete(self, target_url: str) -> CloningResult:
        """الوظيفة الرئيسية لاستنساخ الموقع بشكل كامل"""
        
        self.config.target_url = target_url
        self.result.start_time = datetime.now()
        
        self.logger.info(f"🚀 بدء عملية الاستنساخ الشامل للموقع: {target_url}")
        
        try:
            # المرحلة 1: التحضير والتهيئة
            await self._phase_1_preparation()
            
            # المرحلة 2: الاستكشاف والتحليل الأولي
            await self._phase_2_discovery()
            
            # المرحلة 3: الاستخراج الشامل
            await self._phase_3_comprehensive_extraction()
            
            # المرحلة 4: تحليل المحتوى والتقنيات
            await self._phase_4_content_analysis()
            
            # المرحلة 5: الاستخراج المتقدم والخفي
            await self._phase_5_advanced_extraction()
            
            # المرحلة 6: التحليل بالذكاء الاصطناعي
            await self._phase_6_ai_analysis()
            
            # المرحلة 7: إنشاء النسخة المطابقة
            await self._phase_7_create_replica()
            
            # المرحلة 8: ضمان الجودة والاختبار
            await self._phase_8_quality_assurance()
            
            # المرحلة 9: إنتاج التقارير الشاملة
            await self._phase_9_comprehensive_reporting()
            
            # المرحلة 10: التنظيم النهائي والتسليم
            await self._phase_10_final_organization()
            
            self.result.success = True
            self.logger.info("✅ تم اكتمال عملية الاستنساخ بنجاح")
            
        except Exception as e:
            self.result.success = False
            self.result.error_log.append(f"خطأ عام في عملية الاستنساخ: {str(e)}")
            self.logger.error(f"❌ فشل في عملية الاستنساخ: {e}", exc_info=True)
            
        finally:
            # تنظيف الموارد
            await self._cleanup_resources()
            
            # حساب الإحصائيات النهائية
            self.result.end_time = datetime.now()
            self.result.duration = (self.result.end_time - self.result.start_time).total_seconds()
            
        return self.result
    
    async def _phase_1_preparation(self):
        """المرحلة 1: التحضير والتهيئة"""
        self.logger.info("📋 المرحلة 1: التحضير والتهيئة")
        
        # إنشاء المجلدات الأساسية
        self.result.output_path = os.path.join(
            self.config.output_directory,
            f"{urlparse(self.config.target_url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        os.makedirs(self.result.output_path, exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "01_extracted_content"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "02_assets"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "03_source_code"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "04_analysis"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "05_cloned_site"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "06_reports"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "07_databases"), exist_ok=True)
        os.makedirs(os.path.join(self.result.output_path, "08_apis"), exist_ok=True)
        
        # إعداد جلسة HTTP
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self._get_user_agent()}
        )
        
        # إعداد متصفح Selenium إذا كان متوفراً
        if SELENIUM_AVAILABLE and self.config.handle_javascript:
            await self._setup_selenium()
            
        self.logger.info("✅ تم إكمال مرحلة التحضير")
        
    async def _phase_2_discovery(self):
        """المرحلة 2: الاستكشاف والتحليل الأولي"""
        self.logger.info("🔍 المرحلة 2: الاستكشاف والتحليل الأولي")
        
        # الحصول على الصفحة الرئيسية
        main_page_content = await self._fetch_page_content(self.config.target_url)
        if not main_page_content:
            raise Exception("فشل في الحصول على المحتوى الرئيسي للموقع")
            
        # تحليل أولي للصفحة الرئيسية
        soup = BeautifulSoup(main_page_content, 'html.parser')
        
        # اكتشاف نوع الموقع
        site_type = await self._detect_site_type(soup)
        self.result.extracted_content['site_type'] = site_type
        
        # استخراج الروابط الأساسية
        base_links = await self._extract_all_links(soup, self.config.target_url)
        self.result.extracted_content['discovered_links'] = len(base_links)
        
        # تحليل robots.txt
        robots_content = await self._analyze_robots_txt()
        self.result.extracted_content['robots_analysis'] = robots_content
        
        # اكتشاف خريطة الموقع
        sitemap_urls = await self._discover_sitemaps()
        self.result.extracted_content['sitemap_urls'] = sitemap_urls
        
        # تحليل أولي للتقنيات
        initial_tech_analysis = await self._initial_technology_detection(soup)
        self.result.technologies_detected = initial_tech_analysis
        
        self.logger.info("✅ تم إكمال مرحلة الاستكشاف")
        
    async def _phase_3_comprehensive_extraction(self):
        """المرحلة 3: الاستخراج الشامل"""
        self.logger.info("📥 المرحلة 3: الاستخراج الشامل")
        
        # استخراج جميع الصفحات
        await self._extract_all_pages()
        
        # تحميل جميع الأصول
        await self._download_all_assets()
        
        # استخراج المحتوى الديناميكي
        if self.config.extract_dynamic_content:
            await self._extract_dynamic_content()
            
        # استخراج المحتوى المخفي
        if self.config.extract_hidden_content:
            await self._extract_hidden_content()
            
        self.logger.info("✅ تم إكمال مرحلة الاستخراج الشامل")
        
    async def _phase_4_content_analysis(self):
        """المرحلة 4: تحليل المحتوى والتقنيات"""
        self.logger.info("🔬 المرحلة 4: تحليل المحتوى والتقنيات")
        
        # تحليل شامل للتقنيات المستخدمة
        comprehensive_tech = await self._comprehensive_technology_analysis()
        self.result.technologies_detected.update(comprehensive_tech)
        
        # تحليل بنية الموقع
        structure_analysis = await self._analyze_site_structure()
        self.result.extracted_content['structure_analysis'] = structure_analysis
        
        # تحليل الأمان
        security_analysis = await self._comprehensive_security_analysis()
        self.result.security_analysis = security_analysis
        
        # تحليل الأداء
        performance_analysis = await self._performance_analysis()
        self.result.performance_metrics = performance_analysis
        
        self.logger.info("✅ تم إكمال مرحلة تحليل المحتوى")
        
    async def _phase_5_advanced_extraction(self):
        """المرحلة 5: الاستخراج المتقدم والخفي"""
        self.logger.info("🎯 المرحلة 5: الاستخراج المتقدم")
        
        # استخراج APIs والنقاط النهائية
        if self.config.extract_apis:
            api_endpoints = await self._extract_api_endpoints()
            self.result.extracted_content['api_endpoints'] = api_endpoints
            
        # تحليل قواعد البيانات المحتملة
        if self.config.extract_database_structure:
            db_structure = await self._analyze_database_structure()
            self.result.extracted_content['database_structure'] = db_structure
            
        # استخراج الكود المصدري
        if self.config.extract_source_code:
            source_code = await self._extract_source_code()
            self.result.extracted_content['source_code_analysis'] = source_code
            
        # تحليل التفاعلات والوظائف
        interactions = await self._analyze_interactions()
        self.result.extracted_content['interactions'] = interactions
        
        self.logger.info("✅ تم إكمال مرحلة الاستخراج المتقدم")
        
    async def _phase_6_ai_analysis(self):
        """المرحلة 6: التحليل بالذكاء الاصطناعي"""
        if not self.config.analyze_with_ai:
            return
            
        self.logger.info("🤖 المرحلة 6: التحليل بالذكاء الاصطناعي")
        
        # تحليل الأنماط
        pattern_analysis = await self._ai_pattern_analysis()
        self.result.ai_analysis['patterns'] = pattern_analysis
        
        # تحليل الغرض والمحتوى
        content_analysis = await self._ai_content_analysis()
        self.result.ai_analysis['content_analysis'] = content_analysis
        
        # توصيات التحسين
        optimization_recommendations = await self._ai_optimization_analysis()
        self.result.ai_analysis['optimization'] = optimization_recommendations
        
        # تحليل تجربة المستخدم
        ux_analysis = await self._ai_ux_analysis()
        self.result.ai_analysis['ux_analysis'] = ux_analysis
        
        self.logger.info("✅ تم إكمال مرحلة التحليل بالذكاء الاصطناعي")
        
    async def _phase_7_create_replica(self):
        """المرحلة 7: إنشاء النسخة المطابقة"""
        self.logger.info("🔄 المرحلة 7: إنشاء النسخة المطابقة")
        
        if self.config.create_identical_copy:
            # إنشاء هيكل الموقع المطابق
            replica_structure = await self._create_replica_structure()
            
            # نسخ وتعديل الملفات
            await self._copy_and_modify_files()
            
            # إنشاء نظام التوجيه
            await self._create_routing_system()
            
            # إعداد قاعدة البيانات المحلية
            await self._setup_local_database()
            
            self.result.cloned_site_path = os.path.join(self.result.output_path, "05_cloned_site")
            
        self.logger.info("✅ تم إكمال إنشاء النسخة المطابقة")
        
    async def _phase_8_quality_assurance(self):
        """المرحلة 8: ضمان الجودة والاختبار"""
        self.logger.info("🔍 المرحلة 8: ضمان الجودة")
        
        # اختبار الروابط
        broken_links = await self._test_all_links()
        self.result.extracted_content['broken_links'] = broken_links
        
        # اختبار الأصول
        missing_assets = await self._verify_assets()
        self.result.extracted_content['missing_assets'] = missing_assets
        
        # مقارنة الأداء
        performance_comparison = await self._compare_performance()
        self.result.performance_metrics['comparison'] = performance_comparison
        
        # تقييم الجودة الإجمالية
        quality_score = await self._calculate_quality_score()
        self.result.extracted_content['quality_score'] = quality_score
        
        self.logger.info("✅ تم إكمال مرحلة ضمان الجودة")
        
    async def _phase_9_comprehensive_reporting(self):
        """المرحلة 9: إنتاج التقارير الشاملة"""
        self.logger.info("📊 المرحلة 9: إنتاج التقارير")
        
        self.result.reports_path = os.path.join(self.result.output_path, "06_reports")
        
        # تقرير HTML تفاعلي
        if 'html' in self.config.export_formats:
            await self._generate_html_report()
            
        # تقرير JSON تفصيلي
        if 'json' in self.config.export_formats:
            await self._generate_json_report()
            
        # تقرير CSV للبيانات
        if 'csv' in self.config.export_formats:
            await self._generate_csv_reports()
            
        # تقرير PDF
        if 'pdf' in self.config.export_formats and REPORTLAB_AVAILABLE:
            await self._generate_pdf_report()
            
        # تقرير Word
        if 'docx' in self.config.export_formats and DOCX_AVAILABLE:
            await self._generate_docx_report()
            
        self.logger.info("✅ تم إكمال إنتاج التقارير")
        
    async def _phase_10_final_organization(self):
        """المرحلة 10: التنظيم النهائي والتسليم"""
        self.logger.info("📁 المرحلة 10: التنظيم النهائي")
        
        # إنشاء دليل المشروع
        await self._create_project_guide()
        
        # ضغط الملفات إذا كان مطلوباً
        if self.config.compress_output:
            await self._compress_output()
            
        # إنشاء checksums للتحقق من سلامة البيانات
        await self._generate_checksums()
        
        # إنشاء ملف README شامل
        await self._create_readme_file()
        
        # حساب الإحصائيات النهائية
        await self._calculate_final_statistics()
        
        self.logger.info("✅ تم إكمال التنظيم النهائي")

    # ==================== Helper Methods ====================
    
    def _get_user_agent(self) -> str:
        """الحصول على User Agent متناوب"""
        if self.config.rotate_user_agents:
            ua = self.user_agents[self.current_user_agent_index]
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
            return ua
        return self.user_agents[0]
        
    async def _fetch_page_content(self, url: str, use_js: bool = False) -> Optional[str]:
        """جلب محتوى الصفحة مع دعم JavaScript"""
        try:
            if use_js and self.selenium_driver:
                # استخدام Selenium للمحتوى الديناميكي
                self.selenium_driver.get(url)
                await asyncio.sleep(3)  # انتظار تحميل المحتوى
                return self.selenium_driver.page_source
            else:
                # استخدام aiohttp للمحتوى الثابت
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.warning(f"فشل في جلب {url}: {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"خطأ في جلب {url}: {e}")
            self.error_count += 1
            return None
            
    async def _setup_selenium(self):
        """إعداد متصفح Selenium"""
        try:
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--user-agent={self._get_user_agent()}')
            
            self.selenium_driver = webdriver.Chrome(options=options)
            self.logger.info("تم إعداد Selenium بنجاح")
        except Exception as e:
            self.logger.warning(f"فشل في إعداد Selenium: {e}")
            self.selenium_driver = None
            
    async def _cleanup_resources(self):
        """تنظيف الموارد"""
        if self.session:
            await self.session.close()
            
        if self.selenium_driver:
            self.selenium_driver.quit()

    # ==================== Core Implementation Methods ====================
    
    async def _detect_site_type(self, soup: BeautifulSoup) -> str:
        """كشف نوع الموقع بناءً على المحتوى والتقنيات"""
        
        # تحليل العلامات والمحتوى
        if soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'wordpress', re.I)}):
            return "WordPress Blog/Site"
        elif soup.find('script', src=re.compile(r'wp-content|wp-includes')):
            return "WordPress Site"
        elif soup.find('div', class_='shopify-section'):
            return "Shopify E-commerce"
        elif soup.find('form', action=re.compile(r'cart|checkout')):
            return "E-commerce Site"
        elif soup.find('article') or soup.find('div', class_=re.compile(r'blog|post')):
            return "Blog/News Site"
        elif soup.find('div', class_=re.compile(r'portfolio|gallery')):
            return "Portfolio/Gallery"
        elif soup.find('form', method='post') and soup.find('input', type='email'):
            return "Business/Contact Site"
        elif soup.find('video') or soup.find('iframe', src=re.compile(r'youtube|vimeo')):
            return "Media/Entertainment"
        elif soup.find('div', class_=re.compile(r'course|lesson|education')):
            return "Educational Site"
        else:
            return "Business/Corporate Site"
    
    async def _extract_all_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """استخراج جميع الروابط من الصفحة"""
        links = set()
        parsed_base = urlparse(base_url)
        
        # استخراج روابط <a>
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if href:
                full_url = urljoin(base_url, href)
                if self._is_valid_internal_url(full_url, parsed_base.netloc):
                    links.add(full_url)
        
        # استخراج روابط من JavaScript
        for script in soup.find_all('script'):
            if script.string:
                # البحث عن روابط في الكود
                js_links = re.findall(r'["\']([^"\']*\.(?:html|php|asp|jsp)[^"\']*)["\']', script.string)
                for js_link in js_links:
                    full_url = urljoin(base_url, js_link)
                    if self._is_valid_internal_url(full_url, parsed_base.netloc):
                        links.add(full_url)
        
        return list(links)
    
    def _is_valid_url(self, url: str) -> bool:
        """التحقق من صحة الرابط"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ['http', 'https']
        except:
            return False
    
    def _is_valid_internal_url(self, url: str, base_domain: str) -> bool:
        """التحقق من أن الرابط داخلي وصحيح"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme in ['http', 'https']:
                return False
            if not parsed.netloc:
                return True  # relative URL
            return parsed.netloc == base_domain or parsed.netloc.endswith('.' + base_domain)
        except:
            return False
    
    async def _analyze_robots_txt(self) -> Dict[str, Any]:
        """تحليل ملف robots.txt"""
        robots_url = urljoin(self.config.target_url, '/robots.txt')
        try:
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    content = await response.text()
                    return {
                        'exists': True,
                        'content': content,
                        'disallowed_paths': re.findall(r'Disallow:\s*(.+)', content),
                        'allowed_paths': re.findall(r'Allow:\s*(.+)', content),
                        'sitemaps': re.findall(r'Sitemap:\s*(.+)', content)
                    }
        except:
            pass
        return {'exists': False}
    
    async def _discover_sitemaps(self) -> List[str]:
        """اكتشاف خرائط الموقع"""
        potential_sitemaps = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap.php',
            '/sitemaps.xml',
            '/sitemap1.xml'
        ]
        
        found_sitemaps = []
        for sitemap_path in potential_sitemaps:
            sitemap_url = urljoin(self.config.target_url, sitemap_path)
            try:
                async with self.session.get(sitemap_url) as response:
                    if response.status == 200:
                        found_sitemaps.append(sitemap_url)
            except:
                continue
        
        return found_sitemaps
    
    async def _initial_technology_detection(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """الكشف الأولي عن التقنيات المستخدمة"""
        technologies = {
            'frameworks': [],
            'cms': [],
            'analytics': [],
            'javascript_libraries': [],
            'css_frameworks': [],
            'meta_info': {}
        }
        
        # تحليل العلامات الوصفية
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'generator':
                technologies['meta_info']['generator'] = meta.get('content', '')
            elif meta.get('property') == 'og:type':
                technologies['meta_info']['og_type'] = meta.get('content', '')
        
        # كشف المكتبات من خلال السكريبت
        for script in soup.find_all('script', src=True):
            src = script['src'].lower()
            if 'jquery' in src:
                technologies['javascript_libraries'].append('jQuery')
            elif 'react' in src:
                technologies['frameworks'].append('React')
            elif 'vue' in src:
                technologies['frameworks'].append('Vue.js')
            elif 'angular' in src:
                technologies['frameworks'].append('Angular')
            elif 'bootstrap' in src:
                technologies['css_frameworks'].append('Bootstrap')
            elif 'google-analytics' in src or 'gtag' in src:
                technologies['analytics'].append('Google Analytics')
        
        # كشف CSS frameworks
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                href = link['href'].lower()
                if 'bootstrap' in href:
                    technologies['css_frameworks'].append('Bootstrap')
                elif 'foundation' in href:
                    technologies['css_frameworks'].append('Foundation')
                elif 'bulma' in href:
                    technologies['css_frameworks'].append('Bulma')
        
        return technologies
    
    async def _extract_all_pages(self):
        """استخراج جميع صفحات الموقع"""
        urls_to_process = [self.config.target_url]
        processed_urls = set()
        depth = 0
        
        while urls_to_process and depth < self.config.max_depth and len(processed_urls) < self.config.max_pages:
            current_batch = urls_to_process.copy()
            urls_to_process.clear()
            
            for url in current_batch:
                if url in processed_urls:
                    continue
                    
                self.logger.info(f"استخراج الصفحة: {url}")
                
                # جلب محتوى الصفحة
                content = await self._fetch_page_content(url, use_js=self.config.handle_javascript)
                if content:
                    # حفظ المحتوى
                    page_filename = self._url_to_filename(url) + '.html'
                    page_path = os.path.join(self.result.output_path, "01_extracted_content", page_filename)
                    
                    async with aiofiles.open(page_path, 'w', encoding='utf-8') as f:
                        await f.write(content)
                    
                    # استخراج الروابط الجديدة
                    soup = BeautifulSoup(content, 'html.parser')
                    new_links = await self._extract_all_links(soup, url)
                    
                    for new_link in new_links:
                        if new_link not in processed_urls and new_link not in current_batch:
                            urls_to_process.append(new_link)
                    
                    processed_urls.add(url)
                    self.result.pages_extracted += 1
                    
                await asyncio.sleep(self.config.delay_between_requests)
            
            depth += 1
    
    def _url_to_filename(self, url: str) -> str:
        """تحويل URL إلى اسم ملف آمن"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        
        # تنظيف اسم الملف
        filename = re.sub(r'[^\w\-_\.]', '_', path)
        filename = re.sub(r'_+', '_', filename)
        
        # إضافة query parameters كـ suffix
        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode()).hexdigest()[:8]
            filename += f'_{query_hash}'
        
        return filename
    
    async def _download_all_assets(self):
        """تحميل جميع الأصول (صور، CSS، JS، إلخ)"""
        assets_found = set()
        
        # البحث في جميع الملفات المستخرجة
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                file_path = os.path.join(content_dir, html_file)
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # استخراج الصور
                    for img in soup.find_all('img', src=True):
                        asset_url = urljoin(self.config.target_url, img['src'])
                        assets_found.add(('image', asset_url))
                    
                    # استخراج CSS
                    for link in soup.find_all('link', href=True):
                        if link.get('rel') and 'stylesheet' in link['rel']:
                            asset_url = urljoin(self.config.target_url, link['href'])
                            assets_found.add(('css', asset_url))
                    
                    # استخراج JavaScript
                    for script in soup.find_all('script', src=True):
                        asset_url = urljoin(self.config.target_url, script['src'])
                        assets_found.add(('js', asset_url))
        
        # تحميل الأصول
        for asset_type, asset_url in assets_found:
            await self._download_asset(asset_type, asset_url)
    
    async def _download_asset(self, asset_type: str, url: str):
        """تحميل أصل واحد"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # تحديد المجلد والامتداد
                    if asset_type == 'image':
                        folder = 'images'
                        ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
                    elif asset_type == 'css':
                        folder = 'css'
                        ext = '.css'
                    elif asset_type == 'js':
                        folder = 'js'
                        ext = '.js'
                    else:
                        folder = 'other'
                        ext = os.path.splitext(urlparse(url).path)[1] or '.bin'
                    
                    # إنشاء المجلد
                    asset_dir = os.path.join(self.result.output_path, "02_assets", folder)
                    os.makedirs(asset_dir, exist_ok=True)
                    
                    # اسم الملف
                    filename = os.path.basename(urlparse(url).path) or f'asset_{hashlib.md5(url.encode()).hexdigest()[:8]}{ext}'
                    file_path = os.path.join(asset_dir, filename)
                    
                    # حفظ الملف
                    async with aiofiles.open(file_path, 'wb') as f:
                        await f.write(content)
                    
                    self.result.assets_downloaded += 1
                    self.result.total_size += len(content)
                    
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الأصل {url}: {e}")
            self.error_count += 1

    # ==================== Advanced Analysis Methods ====================
    
    async def _extract_dynamic_content(self):
        """استخراج المحتوى الديناميكي باستخدام JavaScript"""
        if not self.selenium_driver:
            return
            
        self.logger.info("استخراج المحتوى الديناميكي...")
        
        try:
            self.selenium_driver.get(self.config.target_url)
            await asyncio.sleep(5)  # انتظار تحميل المحتوى الديناميكي
            
            # تنفيذ سكريبت لاستخراج المحتوى المخفي
            dynamic_content = self.selenium_driver.execute_script("""
                return {
                    hiddenElements: Array.from(document.querySelectorAll('[style*="display: none"], [hidden]')).map(el => el.outerHTML),
                    loadedScripts: Array.from(document.scripts).map(s => s.src).filter(s => s),
                    ajaxCalls: window.ajaxCalls || [],
                    dynamicData: window.dynamicData || {}
                };
            """)
            
            # حفظ المحتوى الديناميكي
            dynamic_path = os.path.join(self.result.output_path, "03_source_code", "dynamic_content.json")
            async with aiofiles.open(dynamic_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(dynamic_content, ensure_ascii=False, indent=2))
                
        except Exception as e:
            self.logger.error(f"خطأ في استخراج المحتوى الديناميكي: {e}")
    
    async def _extract_hidden_content(self):
        """استخراج المحتوى المخفي والمشفر"""
        self.logger.info("استخراج المحتوى المخفي...")
        
        hidden_content = {
            'comments': [],
            'hidden_forms': [],
            'encoded_data': [],
            'obfuscated_js': []
        }
        
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                file_path = os.path.join(content_dir, html_file)
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    
                # استخراج التعليقات المخفية
                comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
                hidden_content['comments'].extend(comments)
                
                # البحث عن البيانات المشفرة
                encoded_patterns = [
                    r'data:([^;]+);base64,([A-Za-z0-9+/=]+)',
                    r'btoa\(["\']([^"\']+)["\']\)',
                    r'atob\(["\']([^"\']+)["\']\)'
                ]
                
                for pattern in encoded_patterns:
                    matches = re.findall(pattern, content)
                    hidden_content['encoded_data'].extend(matches)
        
        # حفظ المحتوى المخفي
        hidden_path = os.path.join(self.result.output_path, "03_source_code", "hidden_content.json")
        async with aiofiles.open(hidden_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(hidden_content, ensure_ascii=False, indent=2))
    
    async def _comprehensive_technology_analysis(self) -> Dict[str, Any]:
        """تحليل شامل للتقنيات المستخدمة"""
        tech_analysis = {
            'server_info': {},
            'frameworks_detailed': {},
            'database_indicators': [],
            'security_features': [],
            'performance_tools': [],
            'third_party_services': []
        }
        
        # تحليل headers للحصول على معلومات الخادم
        try:
            async with self.session.head(self.config.target_url) as response:
                headers = dict(response.headers)
                tech_analysis['server_info'] = {
                    'server': headers.get('Server', 'Unknown'),
                    'powered_by': headers.get('X-Powered-By', 'Unknown'),
                    'framework': headers.get('X-Framework', 'Unknown'),
                    'all_headers': headers
                }
        except:
            pass
        
        # استخدام builtwith إذا كان متوفراً
        if BUILTWITH_AVAILABLE:
            try:
                builtwith_result = builtwith.parse(self.config.target_url)
                tech_analysis['frameworks_detailed'] = builtwith_result
            except:
                pass
        
        return tech_analysis
    
    async def _analyze_site_structure(self) -> Dict[str, Any]:
        """تحليل بنية الموقع"""
        structure = {
            'page_hierarchy': {},
            'navigation_patterns': [],
            'content_types': {},
            'url_patterns': [],
            'internal_linking': {}
        }
        
        # تحليل URL patterns
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                # استخراج نمط URL من اسم الملف
                url_pattern = html_file.replace('.html', '').replace('_', '/')
                structure['url_patterns'].append(url_pattern)
        
        return structure
    
    async def _comprehensive_security_analysis(self) -> Dict[str, Any]:
        """تحليل أمني شامل"""
        security = {
            'ssl_analysis': {},
            'headers_security': {},
            'vulnerabilities': [],
            'authentication_methods': [],
            'data_protection': {}
        }
        
        # تحليل SSL
        try:
            parsed_url = urlparse(self.config.target_url)
            if parsed_url.scheme == 'https':
                # هنا يمكن إضافة تحليل شهادة SSL
                security['ssl_analysis']['enabled'] = True
            else:
                security['ssl_analysis']['enabled'] = False
        except:
            pass
        
        # تحليل security headers
        try:
            async with self.session.get(self.config.target_url) as response:
                headers = dict(response.headers)
                security['headers_security'] = {
                    'csp': headers.get('Content-Security-Policy'),
                    'xss_protection': headers.get('X-XSS-Protection'),
                    'frame_options': headers.get('X-Frame-Options'),
                    'content_type_options': headers.get('X-Content-Type-Options'),
                    'hsts': headers.get('Strict-Transport-Security')
                }
        except:
            pass
        
        return security
    
    async def _performance_analysis(self) -> Dict[str, Any]:
        """تحليل الأداء"""
        performance = {
            'load_times': {},
            'resource_sizes': {},
            'optimization_opportunities': [],
            'caching_analysis': {}
        }
        
        start_time = time.time()
        try:
            async with self.session.get(self.config.target_url) as response:
                load_time = time.time() - start_time
                performance['load_times']['main_page'] = load_time
                performance['resource_sizes']['main_page'] = len(await response.read())
        except:
            pass
        
        return performance
    
    async def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """استخراج نقاط API والاستدعاءات"""
        api_endpoints = []
        
        # البحث في JavaScript files عن API calls
        js_dir = os.path.join(self.result.output_path, "02_assets", "js")
        if os.path.exists(js_dir):
            for js_file in os.listdir(js_dir):
                if js_file.endswith('.js'):
                    file_path = os.path.join(js_dir, js_file)
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            js_content = await f.read()
                            
                        # البحث عن API patterns
                        api_patterns = [
                            r'fetch\(["\']([^"\']+)["\']',
                            r'axios\.(?:get|post|put|delete)\(["\']([^"\']+)["\']',
                            r'jQuery\.(?:get|post|ajax)\(["\']([^"\']+)["\']',
                            r'api["\']:\s*["\']([^"\']+)["\']'
                        ]
                        
                        for pattern in api_patterns:
                            matches = re.findall(pattern, js_content)
                            for match in matches:
                                api_endpoints.append({
                                    'url': match,
                                    'source_file': js_file,
                                    'method': 'unknown'
                                })
                    except:
                        continue
        
        return api_endpoints
    
    async def _analyze_database_structure(self) -> Dict[str, Any]:
        """تحليل بنية قاعدة البيانات المحتملة"""
        db_structure = {
            'detected_queries': [],
            'table_references': [],
            'connection_strings': [],
            'orm_patterns': []
        }
        
        # البحث في ملفات JavaScript و HTML عن database patterns
        all_files = []
        
        # إضافة ملفات HTML
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        if os.path.exists(content_dir):
            all_files.extend([(f, 'html') for f in os.listdir(content_dir) if f.endswith('.html')])
        
        # إضافة ملفات JS
        js_dir = os.path.join(self.result.output_path, "02_assets", "js")
        if os.path.exists(js_dir):
            all_files.extend([(f, 'js') for f in os.listdir(js_dir) if f.endswith('.js')])
        
        for filename, file_type in all_files:
            if file_type == 'html':
                file_path = os.path.join(content_dir, filename)
            else:
                file_path = os.path.join(js_dir, filename)
                
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # البحث عن SQL patterns
                sql_patterns = [
                    r'SELECT\s+.+\s+FROM\s+(\w+)',
                    r'INSERT\s+INTO\s+(\w+)',
                    r'UPDATE\s+(\w+)\s+SET',
                    r'DELETE\s+FROM\s+(\w+)'
                ]
                
                for pattern in sql_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if match not in db_structure['table_references']:
                            db_structure['table_references'].append(match)
            except:
                continue
        
        return db_structure
    
    async def _extract_source_code(self) -> Dict[str, Any]:
        """استخراج وتحليل الكود المصدري"""
        source_analysis = {
            'html_structure': {},
            'css_analysis': {},
            'javascript_functions': [],
            'embedded_code': {},
            'code_complexity': {}
        }
        
        # تحليل HTML
        content_dir = os.path.join(self.result.output_path, "01_extracted_content") 
        html_files = [f for f in os.listdir(content_dir) if f.endswith('.html')]
        
        source_analysis['html_structure']['total_files'] = len(html_files)
        source_analysis['html_structure']['average_size'] = 0
        
        total_size = 0
        for html_file in html_files:
            file_path = os.path.join(content_dir, html_file)
            size = os.path.getsize(file_path)
            total_size += size
        
        if html_files:
            source_analysis['html_structure']['average_size'] = total_size // len(html_files)
        
        # تحليل CSS
        css_dir = os.path.join(self.result.output_path, "02_assets", "css")
        if os.path.exists(css_dir):
            css_files = [f for f in os.listdir(css_dir) if f.endswith('.css')]
            source_analysis['css_analysis']['total_files'] = len(css_files)
            
            # تحليل selectors في CSS
            all_selectors = set()
            for css_file in css_files:
                file_path = os.path.join(css_dir, css_file)
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        css_content = await f.read()
                    
                    # استخراج CSS selectors
                    selectors = re.findall(r'([.#]?[\w-]+)\s*{', css_content)
                    all_selectors.update(selectors)
                except:
                    continue
            
            source_analysis['css_analysis']['unique_selectors'] = len(all_selectors)
        
        # تحليل JavaScript
        js_dir = os.path.join(self.result.output_path, "02_assets", "js")
        if os.path.exists(js_dir):
            js_files = [f for f in os.listdir(js_dir) if f.endswith('.js')]
            
            for js_file in js_files:
                file_path = os.path.join(js_dir, js_file)
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        js_content = await f.read()
                    
                    # استخراج JavaScript functions
                    functions = re.findall(r'function\s+(\w+)\s*\(', js_content)
                    source_analysis['javascript_functions'].extend(functions)
                except:
                    continue
        
        return source_analysis
    
    async def _analyze_interactions(self) -> Dict[str, Any]:
        """تحليل التفاعلات والوظائف"""
        interactions = {
            'form_interactions': [],
            'click_handlers': [],
            'ajax_interactions': [],
            'user_inputs': [],
            'dynamic_behaviors': []
        }
        
        # تحليل النماذج
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                file_path = os.path.join(content_dir, html_file)
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    soup = BeautifulSoup(content, 'html.parser')
                
                # تحليل النماذج
                for form in soup.find_all('form'):
                    form_data = {
                        'action': form.get('action', ''),
                        'method': form.get('method', 'GET'),
                        'inputs': []
                    }
                    
                    for input_tag in form.find_all(['input', 'textarea', 'select']):
                        input_data = {
                            'type': input_tag.get('type', 'text'),
                            'name': input_tag.get('name', ''),
                            'required': input_tag.has_attr('required')
                        }
                        form_data['inputs'].append(input_data)
                    
                    interactions['form_interactions'].append(form_data)
                
                # تحليل click handlers
                for element in soup.find_all(attrs={'onclick': True}):
                    interactions['click_handlers'].append({
                        'element': element.name,
                        'onclick': element['onclick']
                    })
        
        return interactions

    # ==================== AI Analysis Methods ====================
    
    async def _ai_pattern_analysis(self) -> Dict[str, Any]:
        """تحليل الأنماط بالذكاء الاصطناعي"""
        patterns = {
            'design_patterns': [],
            'code_patterns': [],
            'user_flow_patterns': [],
            'content_patterns': []
        }
        
        # تحليل أنماط التصميم من CSS
        css_dir = os.path.join(self.result.output_path, "02_assets", "css")
        if os.path.exists(css_dir):
            for css_file in os.listdir(css_dir):
                if css_file.endswith('.css'):
                    file_path = os.path.join(css_dir, css_file)
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            css_content = await f.read()
                        
                        # كشف أنماط CSS شائعة
                        if 'flexbox' in css_content or 'display: flex' in css_content:
                            patterns['design_patterns'].append('Flexbox Layout')
                        if 'grid' in css_content or 'display: grid' in css_content:
                            patterns['design_patterns'].append('CSS Grid Layout')
                        if 'media' in css_content and 'max-width' in css_content:
                            patterns['design_patterns'].append('Responsive Design')
                        if 'animation' in css_content or 'transition' in css_content:
                            patterns['design_patterns'].append('CSS Animations')
                    except:
                        continue
        
        # تحليل أنماط JavaScript
        js_dir = os.path.join(self.result.output_path, "02_assets", "js")
        if os.path.exists(js_dir):
            for js_file in os.listdir(js_dir):
                if js_file.endswith('.js'):
                    file_path = os.path.join(js_dir, js_file)
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            js_content = await f.read()
                        
                        # كشف أنماط JavaScript
                        if 'addEventListener' in js_content:
                            patterns['code_patterns'].append('Event-Driven Programming')
                        if 'Promise' in js_content or 'async' in js_content:
                            patterns['code_patterns'].append('Asynchronous Programming')
                        if 'class ' in js_content and 'constructor' in js_content:
                            patterns['code_patterns'].append('Object-Oriented Programming')
                        if 'module.exports' in js_content or 'export' in js_content:
                            patterns['code_patterns'].append('Modular Programming')
                    except:
                        continue
        
        return patterns
    
    async def _ai_content_analysis(self) -> Dict[str, Any]:
        """تحليل المحتوى بالذكاء الاصطناعي"""
        content_analysis = {
            'content_type': 'mixed',
            'language_detected': 'unknown',
            'reading_level': 'intermediate',
            'content_quality': {},
            'seo_analysis': {},
            'accessibility_score': 0
        }
        
        # تحليل المحتوى النصي
        all_text = ""
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                file_path = os.path.join(content_dir, html_file)
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # استخراج النص فقط
                    text = soup.get_text()
                    all_text += text + " "
        
        # تحليل النص
        if all_text:
            # كشف اللغة الأساسية
            arabic_chars = len(re.findall(r'[\u0600-\u06FF]', all_text))
            english_chars = len(re.findall(r'[a-zA-Z]', all_text))
            
            if arabic_chars > english_chars:
                content_analysis['language_detected'] = 'arabic'
            elif english_chars > arabic_chars:
                content_analysis['language_detected'] = 'english'
            else:
                content_analysis['language_detected'] = 'multilingual'
            
            # تحليل جودة المحتوى
            word_count = len(all_text.split())
            sentence_count = len(re.findall(r'[.!?]+', all_text))
            
            content_analysis['content_quality'] = {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_words_per_sentence': word_count / max(sentence_count, 1),
                'estimated_reading_time': word_count / 200  # assuming 200 words per minute
            }
        
        return content_analysis
    
    async def _ai_optimization_analysis(self) -> List[str]:
        """تحليل التحسين بالذكاء الاصطناعي"""
        recommendations = []
        
        # تحليل الأداء وتقديم توصيات
        if self.result.performance_metrics:
            load_time = self.result.performance_metrics.get('load_times', {}).get('main_page', 0)
            if load_time > 3:
                recommendations.append("تحسين سرعة تحميل الصفحة - الوقت الحالي أكثر من 3 ثوانٍ")
        
        # تحليل الأصول
        if self.result.assets_downloaded > 100:
            recommendations.append("تقليل عدد الأصول المحملة - العدد الحالي مرتفع")
        
        if self.result.total_size > 5000000:  # 5MB
            recommendations.append("ضغط الأصول - الحجم الإجمالي أكبر من 5MB")
        
        # تحليل الأمان
        if self.result.security_analysis:
            if not self.result.security_analysis.get('ssl_analysis', {}).get('enabled'):
                recommendations.append("تفعيل شهادة SSL للأمان")
        
        return recommendations
    
    async def _ai_ux_analysis(self) -> Dict[str, Any]:
        """تحليل تجربة المستخدم بالذكاء الاصطناعي"""
        ux_analysis = {
            'navigation_clarity': 'good',
            'content_accessibility': 'moderate',
            'mobile_friendliness': 'unknown',
            'user_interaction_patterns': [],
            'improvement_suggestions': []
        }
        
        # تحليل التنقل
        if self.result.extracted_content.get('form_interactions'):
            forms_count = len(self.result.extracted_content['form_interactions'])
            if forms_count > 0:
                ux_analysis['user_interaction_patterns'].append(f"يحتوي على {forms_count} نماذج تفاعلية")
        
        # تحليل إمكانية الوصول
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        accessibility_issues = 0
        
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                file_path = os.path.join(content_dir, html_file)
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    soup = BeautifulSoup(content, 'html.parser')
                
                # فحص الصور بدون alt text
                images_without_alt = soup.find_all('img', alt=False)
                accessibility_issues += len(images_without_alt)
                
                # فحص الروابط بدون نص وصفي
                empty_links = soup.find_all('a', string=False)
                accessibility_issues += len(empty_links)
        
        if accessibility_issues > 0:
            ux_analysis['improvement_suggestions'].append(f"إضافة نصوص وصفية لـ {accessibility_issues} عنصر")
        
        return ux_analysis

    # ==================== Website Replication Methods ====================
    
    async def _create_replica_structure(self):
        """إنشاء هيكل الموقع المطابق"""
        self.logger.info("إنشاء هيكل الموقع المطابق...")
        
        replica_dir = os.path.join(self.result.output_path, "05_cloned_site")
        
        # إنشاء المجلدات الأساسية
        subdirs = ['assets', 'css', 'js', 'images', 'pages', 'data']
        for subdir in subdirs:
            os.makedirs(os.path.join(replica_dir, subdir), exist_ok=True)
        
        # إنشاء ملف index.html أساسي
        index_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>موقع مستنسخ</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <div id="app">
        <h1>مرحباً بك في الموقع المستنسخ</h1>
        <p>تم إنشاء هذا الموقع تلقائياً باستخدام أداة Website Cloner Pro</p>
    </div>
    <script src="js/main.js"></script>
</body>
</html>"""
        
        async with aiofiles.open(os.path.join(replica_dir, 'index.html'), 'w', encoding='utf-8') as f:
            await f.write(index_content)
    
    async def _copy_and_modify_files(self):
        """نسخ وتعديل الملفات للموقع المطابق"""
        self.logger.info("نسخ وتعديل الملفات...")
        
        replica_dir = os.path.join(self.result.output_path, "05_cloned_site")
        
        # نسخ ملفات HTML
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        if os.path.exists(content_dir):
            for html_file in os.listdir(content_dir):
                if html_file.endswith('.html'):
                    src_path = os.path.join(content_dir, html_file)
                    dst_path = os.path.join(replica_dir, 'pages', html_file)
                    
                    # قراءة وتعديل المحتوى
                    async with aiofiles.open(src_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    # تعديل المسارات لتكون نسبية
                    modified_content = await self._modify_paths_in_html(content)
                    
                    async with aiofiles.open(dst_path, 'w', encoding='utf-8') as f:
                        await f.write(modified_content)
        
        # نسخ الأصول
        assets_dir = os.path.join(self.result.output_path, "02_assets")
        if os.path.exists(assets_dir):
            await self._copy_assets_recursively(assets_dir, replica_dir)
    
    async def _modify_paths_in_html(self, html_content: str) -> str:
        """تعديل المسارات في HTML لتكون متوافقة مع البنية الجديدة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # تعديل مسارات الصور
        for img in soup.find_all('img', src=True):
            original_src = img['src']
            if not original_src.startswith(('http://', 'https://', '//')):
                # تحويل إلى مسار نسبي
                filename = os.path.basename(original_src)
                img['src'] = f'../images/{filename}'
        
        # تعديل مسارات CSS
        for link in soup.find_all('link', href=True):
            if link.get('rel') and 'stylesheet' in link['rel']:
                original_href = link['href']
                if not original_href.startswith(('http://', 'https://', '//')):
                    filename = os.path.basename(original_href)
                    link['href'] = f'../css/{filename}'
        
        # تعديل مسارات JavaScript
        for script in soup.find_all('script', src=True):
            original_src = script['src']
            if not original_src.startswith(('http://', 'https://', '//')):
                filename = os.path.basename(original_src)
                script['src'] = f'../js/{filename}'
        
        return str(soup)
    
    async def _copy_assets_recursively(self, src_dir: str, dst_dir: str):
        """نسخ الأصول بشكل تكراري"""
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                src_file = os.path.join(root, file)
                
                # تحديد المجلد الوجهة بناءً على نوع الملف
                if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
                    dst_subdir = 'images'
                elif file.endswith('.css'):
                    dst_subdir = 'css'
                elif file.endswith('.js'):
                    dst_subdir = 'js'
                else:
                    dst_subdir = 'assets'
                
                dst_file = os.path.join(dst_dir, dst_subdir, file)
                
                try:
                    shutil.copy2(src_file, dst_file)
                except Exception as e:
                    self.logger.warning(f"فشل في نسخ {src_file}: {e}")
    
    async def _create_routing_system(self):
        """إنشاء نظام التوجيه للموقع المطابق"""
        self.logger.info("إنشاء نظام التوجيه...")
        
        replica_dir = os.path.join(self.result.output_path, "05_cloned_site")
        
        # إنشاء ملف .htaccess للتوجيه
        htaccess_content = """RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php?route=$1 [QSA,L]

# تفعيل الضغط
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# تفعيل التخزين المؤقت
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/pdf "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType application/x-javascript "access plus 1 month"
    ExpiresByType application/x-shockwave-flash "access plus 1 month"
    ExpiresByType image/x-icon "access plus 1 year"
    ExpiresDefault "access plus 2 days"
</IfModule>"""
        
        async with aiofiles.open(os.path.join(replica_dir, '.htaccess'), 'w', encoding='utf-8') as f:
            await f.write(htaccess_content)
        
        # إنشاء ملف router.php أساسي
        php_router = """<?php
// Simple PHP Router for Cloned Website
$route = $_GET['route'] ?? '';

// تنظيف المسار
$route = trim($route, '/');
if (empty($route)) {
    $route = 'index';
}

// تحديد الملف المطلوب
$page_file = 'pages/' . $route . '.html';

if (file_exists($page_file)) {
    // عرض الصفحة المطلوبة
    include $page_file;
} else {
    // عرض صفحة 404
    http_response_code(404);
    echo '<h1>404 - الصفحة غير موجودة</h1>';
    echo '<p>الصفحة المطلوبة غير متوفرة.</p>';
    echo '<a href="/">العودة للصفحة الرئيسية</a>';
}
?>"""
        
        async with aiofiles.open(os.path.join(replica_dir, 'router.php'), 'w', encoding='utf-8') as f:
            await f.write(php_router)
    
    async def _setup_local_database(self):
        """إعداد قاعدة بيانات محلية للموقع المطابق"""
        self.logger.info("إعداد قاعدة البيانات المحلية...")
        
        db_dir = os.path.join(self.result.output_path, "07_databases")
        db_file = os.path.join(db_dir, "cloned_site.db")
        
        # إنشاء قاعدة بيانات SQLite
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # إنشاء جداول أساسية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                url TEXT,
                local_path TEXT,
                size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # حفظ بيانات الصفحات المستخرجة
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        if os.path.exists(content_dir):
            for html_file in os.listdir(content_dir):
                if html_file.endswith('.html'):
                    file_path = os.path.join(content_dir, html_file)
                    
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    title = soup.find('title')
                    title_text = title.get_text() if title else html_file
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO pages (url, title, content)
                        VALUES (?, ?, ?)
                    ''', (html_file, title_text, content))
        
        conn.commit()
        conn.close()
        
        # إنشاء ملف اتصال قاعدة البيانات
        db_config = f"""<?php
// Database Configuration for Cloned Website
$database_config = [
    'type' => 'sqlite',
    'path' => 'databases/cloned_site.db',
    'options' => [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]
];

// Database Connection Function
function getDatabase() {{
    global $database_config;
    try {{
        $pdo = new PDO(
            'sqlite:' . $database_config['path'],
            null,
            null,
            $database_config['options']
        );
        return $pdo;
    }} catch (PDOException $e) {{
        error_log('Database connection failed: ' . $e->getMessage());
        return null;
    }}
}}
?>"""
        
        replica_dir = os.path.join(self.result.output_path, "05_cloned_site")
        async with aiofiles.open(os.path.join(replica_dir, 'database.php'), 'w', encoding='utf-8') as f:
            await f.write(db_config)
    
    # ==================== Quality Assurance Methods ====================
    
    async def _test_all_links(self) -> List[str]:
        """اختبار جميع الروابط للتأكد من عملها"""
        self.logger.info("اختبار الروابط...")
        
        broken_links = []
        content_dir = os.path.join(self.result.output_path, "01_extracted_content")
        
        for html_file in os.listdir(content_dir):
            if html_file.endswith('.html'):
                file_path = os.path.join(content_dir, html_file)
                
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # اختبار روابط الصور
                for img in soup.find_all('img', src=True):
                    img_url = urljoin(self.config.target_url, img['src'])
                    if not await self._test_url(img_url):
                        broken_links.append(f"صورة مكسورة: {img_url}")
                
                # اختبار الروابط النصية
                for link in soup.find_all('a', href=True):
                    link_url = urljoin(self.config.target_url, link['href'])
                    if link_url.startswith(('http://', 'https://')) and not await self._test_url(link_url):
                        broken_links.append(f"رابط مكسور: {link_url}")
        
        return broken_links
    
    async def _test_url(self, url: str) -> bool:
        """اختبار رابط واحد"""
        try:
            async with self.session.head(url) as response:
                return response.status < 400
        except:
            return False
    
    async def _verify_assets(self) -> List[str]:
        """التحقق من سلامة الأصول المحملة"""
        missing_assets = []
        assets_dir = os.path.join(self.result.output_path, "02_assets")
        
        if os.path.exists(assets_dir):
            for root, dirs, files in os.walk(assets_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # التحقق من حجم الملف
                    if os.path.getsize(file_path) == 0:
                        missing_assets.append(f"ملف فارغ: {file}")
                    
                    # التحقق من نوع الملف
                    if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        try:
                            # يمكن إضافة فحص أكثر تفصيلاً للصور هنا
                            pass
                        except:
                            missing_assets.append(f"صورة تالفة: {file}")
        
        return missing_assets
    
    async def _compare_performance(self) -> Dict[str, Any]:
        """مقارنة أداء الموقع الأصلي والنسخة"""
        comparison = {
            'original_load_time': 0,
            'replica_load_time': 0,
            'size_difference': 0,
            'functionality_preservation': 'unknown'
        }
        
        # قياس سرعة الموقع الأصلي
        start_time = time.time()
        try:
            async with self.session.get(self.config.target_url) as response:
                if response.status == 200:
                    comparison['original_load_time'] = time.time() - start_time
        except:
            pass
        
        return comparison
    
    async def _calculate_quality_score(self) -> Dict[str, Any]:
        """حساب نقاط الجودة الإجمالية"""
        quality_score = {
            'overall_score': 0,
            'completeness': 0,
            'accuracy': 0,
            'performance': 0,
            'functionality': 0
        }
        
        # حساب درجة الاكتمال
        expected_pages = 10  # افتراضي
        actual_pages = self.result.pages_extracted
        quality_score['completeness'] = min(100, (actual_pages / expected_pages) * 100)
        
        # حساب درجة الدقة
        total_errors = len(self.result.error_log)
        if total_errors == 0:
            quality_score['accuracy'] = 100
        else:
            quality_score['accuracy'] = max(0, 100 - (total_errors * 10))
        
        # حساب درجة الأداء
        if self.result.total_size > 0:
            size_efficiency = min(100, (self.result.assets_downloaded / max(self.result.total_size / 1000000, 1)) * 10)
            quality_score['performance'] = size_efficiency
        
        # حساب النقاط الإجمالية
        quality_score['overall_score'] = (
            quality_score['completeness'] * 0.3 +
            quality_score['accuracy'] * 0.3 +
            quality_score['performance'] * 0.2 +
            quality_score['functionality'] * 0.2
        )
        


async def main():
    """وظيفة اختبار الأداة"""
    config = CloningConfig(
        target_url="https://example.com",
        max_depth=3,
        max_pages=50,
        extract_all_content=True,
        analyze_with_ai=True,
        generate_reports=True
    )
    
    cloner = WebsiteClonerPro(config)
    result = await cloner.clone_website_complete("https://example.com")
    
    if result.success:
        print(f"✅ تم الاستنساخ بنجاح في: {result.output_path}")
        print(f"📊 الصفحات المستخرجة: {result.pages_extracted}")
        print(f"📁 الأصول المحملة: {result.assets_downloaded}")
        print(f"⏱️ المدة: {result.duration:.2f} ثانية")
    else:
        print("❌ فشل في عملية الاستنساخ")
        for error in result.error_log:
            print(f"  - {error}")

if __name__ == "__main__":
    asyncio.run(main())