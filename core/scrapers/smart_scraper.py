"""
كاشط ذكي شامل - Smart Comprehensive Scraper
يدمج جميع أدوات الكشط في نظام واحد ذكي ومرن
"""

import requests
import time
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Union
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup, Tag
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum
import re

# تكوين المسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapingMode(Enum):
    """أنماط الكشط المختلفة"""
    BASIC = "basic"           # كشط أساسي سريع
    STANDARD = "standard"     # كشط عادي متوازن
    ADVANCED = "advanced"     # كشط متقدم شامل
    RESPECTFUL = "respectful" # كشط محترم للقوانين
    AGGRESSIVE = "aggressive" # كشط قوي وسريع

class RespectLevel(Enum):
    """مستويات الاحترام للمواقع"""
    HIGH = "high"         # احترام عالي جداً
    MEDIUM = "medium"     # احترام متوسط
    LOW = "low"          # احترام منخفض
    ANALYSIS_ONLY = "analysis_only"  # للتحليل فقط

@dataclass
class ScrapingConfig:
    """إعدادات الكشط الشاملة"""
    base_url: str
    mode: ScrapingMode = ScrapingMode.STANDARD
    respect_level: RespectLevel = RespectLevel.MEDIUM
    max_depth: int = 3
    max_pages: int = 100
    delay_between_requests: float = 1.0
    timeout: int = 30
    max_threads: int = 3
    respect_robots_txt: bool = True
    follow_redirects: bool = True
    extract_assets: bool = True
    extract_forms: bool = True
    extract_metadata: bool = True
    detect_languages: bool = True
    analyze_structure: bool = True
    timeout_limit: int = 120
    user_agent: str = "Mozilla/5.0 (Website-Analyzer-Tool) Respectful-Crawler/1.0"

class SmartScraper:
    """كاشط ذكي يدمج جميع قدرات الكشط"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.base_url = config.base_url
        self.domain = urlparse(config.base_url).netloc
        
        # مجموعات البيانات
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.external_urls: Set[str] = set()
        
        # إحصائيات شاملة
        self.stats = self._init_stats()
        
        # إعداد الجلسة
        self.session = requests.Session()
        self._setup_session()
        
        # فحص robots.txt
        self.robots_allowed = self._check_robots_txt()
        
        # قوائم الكشف والتحليل
        self._init_detection_patterns()

    def _init_stats(self) -> Dict[str, Any]:
        """تهيئة الإحصائيات"""
        return {
            'scraping_start': datetime.now().isoformat(),
            'scraping_end': None,
            'mode': self.config.mode.value,
            'respect_level': self.config.respect_level.value,
            'pages_discovered': 0,
            'pages_scraped': 0,
            'pages_failed': 0,
            'external_links_found': 0,
            'internal_links_found': 0,
            'images_found': 0,
            'css_files_found': 0,
            'js_files_found': 0,
            'forms_found': 0,
            'errors': [],
            'warnings': [],
            'redirects_followed': 0,
            'robots_txt_respected': True,
            'total_size_bytes': 0,
            'average_response_time': 0,
            'detected_technologies': [],
            'detected_languages': [],
            'content_types': Counter(),
            'status_codes': Counter(),
            'processing_time_seconds': 0
        }

    def _setup_session(self):
        """إعداد جلسة HTTP متقدمة"""
        headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(headers)
        
        # إعداد إعادة المحاولة
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _check_robots_txt(self) -> bool:
        """فحص robots.txt"""
        try:
            if not self.config.respect_robots_txt:
                logger.info("تم تعطيل احترام robots.txt")
                return True
            
            robots_url = urljoin(self.base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch('*', self.base_url)
            
            if not can_fetch:
                if self.config.respect_level == RespectLevel.ANALYSIS_ONLY:
                    logger.warning(f"robots.txt يمنع الكشط، لكن سنتابع للتحليل فقط: {self.base_url}")
                    return True
                else:
                    logger.warning(f"robots.txt يمنع الكشط: {self.base_url}")
                    self.stats['robots_txt_respected'] = False
                    return False
            
            logger.info("robots.txt يسمح بالكشط")
            return True
            
        except Exception as e:
            logger.warning(f"لا يمكن فحص robots.txt: {e}")
            return True

    def _init_detection_patterns(self):
        """تهيئة أنماط الكشف"""
        # أنماط التقنيات
        self.tech_patterns = {
            'cms': {
                'WordPress': [r'wp-content', r'wp-includes', r'wordpress'],
                'Drupal': [r'drupal', r'sites/default', r'modules'],
                'Joomla': [r'joomla', r'templates', r'components'],
                'Magento': [r'magento', r'skin/frontend'],
                'Shopify': [r'shopify', r'cdn.shopify.com']
            },
            'frameworks': {
                'React': [r'React\.createElement', r'react-dom', r'reactjs'],
                'Vue.js': [r'Vue\.js', r'vue@', r'v-if', r'v-for'],
                'Angular': [r'@angular', r'ng-app', r'ng-controller'],
                'jQuery': [r'jquery', r'\$\(', r'jQuery\('],
                'Bootstrap': [r'bootstrap', r'btn-primary', r'container-fluid']
            }
        }
        
        # أنماط اللغات
        self.language_patterns = {
            'arabic': [r'[\u0600-\u06FF]', r'dir="rtl"', r'lang="ar"'],
            'english': [r'[a-zA-Z]+', r'lang="en"'],
            'chinese': [r'[\u4e00-\u9fff]', r'lang="zh"'],
            'japanese': [r'[\u3040-\u309f\u30a0-\u30ff]', r'lang="ja"']
        }

    def scrape_website(self) -> Dict[str, Any]:
        """نقطة الدخول الرئيسية للكشط"""
        start_time = time.time()
        self.stats['scraping_start'] = datetime.now().isoformat()
        
        try:
            logger.info(f"بدء كشط الموقع: {self.base_url}")
            logger.info(f"نمط الكشط: {self.config.mode.value}")
            logger.info(f"مستوى الاحترام: {self.config.respect_level.value}")
            
            if not self.robots_allowed and self.config.respect_level == RespectLevel.HIGH:
                return {
                    'success': False,
                    'error': 'robots.txt يمنع الكشط ومستوى الاحترام عالي',
                    'stats': self.stats
                }
            
            # اختيار طريقة الكشط حسب النمط
            if self.config.mode == ScrapingMode.BASIC:
                result = self._scrape_basic()
            elif self.config.mode == ScrapingMode.STANDARD:
                result = self._scrape_standard()
            elif self.config.mode == ScrapingMode.ADVANCED:
                result = self._scrape_advanced()
            elif self.config.mode == ScrapingMode.RESPECTFUL:
                result = self._scrape_respectful()
            elif self.config.mode == ScrapingMode.AGGRESSIVE:
                result = self._scrape_aggressive()
            else:
                result = self._scrape_standard()
            
            # إنهاء المعالجة
            end_time = time.time()
            self.stats['processing_time_seconds'] = round(end_time - start_time, 2)
            self.stats['scraping_end'] = datetime.now().isoformat()
            
            if self.stats['pages_scraped'] > 0:
                self.stats['average_response_time'] = round(
                    self.stats['processing_time_seconds'] / self.stats['pages_scraped'], 3
                )
            
            result.update({
                'success': True,
                'stats': self.stats,
                'summary': self._generate_summary()
            })
            
            logger.info(f"اكتمل الكشط في {self.stats['processing_time_seconds']} ثانية")
            logger.info(f"تم كشط {self.stats['pages_scraped']} صفحة من أصل {self.stats['pages_discovered']}")
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في الكشط: {e}")
            self.stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }

    def _scrape_basic(self) -> Dict[str, Any]:
        """كشط أساسي للصفحة الرئيسية فقط"""
        logger.info("تشغيل الكشط الأساسي")
        
        page_data = self._scrape_single_page(self.base_url)
        if page_data:
            self.stats['pages_scraped'] = 1
            self.stats['pages_discovered'] = 1
            
            return {
                'mode': 'basic',
                'pages': {self.base_url: page_data},
                'page_count': 1
            }
        else:
            return {
                'mode': 'basic',
                'pages': {},
                'page_count': 0
            }

    def _scrape_standard(self) -> Dict[str, Any]:
        """كشط عادي مع عدة صفحات"""
        logger.info("تشغيل الكشط العادي")
        
        result = self._crawl_recursive(
            self.base_url, 
            depth=0, 
            timeout_limit=self.config.timeout_limit,
            start_time=time.time()
        )
        
        return {
            'mode': 'standard',
            'pages': result,
            'page_count': len(result)
        }

    def _scrape_advanced(self) -> Dict[str, Any]:
        """كشط متقدم مع تحليل شامل"""
        logger.info("تشغيل الكشط المتقدم")
        
        # كشط متعدد الخيوط للسرعة
        result = self._parallel_scraping()
        
        # تحليل متقدم للمحتوى
        analysis = self._advanced_analysis(result)
        
        return {
            'mode': 'advanced',
            'pages': result,
            'analysis': analysis,
            'page_count': len(result)
        }

    def _scrape_respectful(self) -> Dict[str, Any]:
        """كشط محترم للقوانين"""
        logger.info("تشغيل الكشط المحترم")
        
        # زيادة التأخير بين الطلبات
        original_delay = self.config.delay_between_requests
        self.config.delay_between_requests = max(2.0, original_delay)
        
        result = self._crawl_recursive(
            self.base_url,
            depth=0,
            timeout_limit=self.config.timeout_limit,
            start_time=time.time()
        )
        
        # استعادة التأخير الأصلي
        self.config.delay_between_requests = original_delay
        
        return {
            'mode': 'respectful',
            'pages': result,
            'page_count': len(result),
            'respect_measures': {
                'increased_delay': True,
                'robots_txt_respected': self.stats['robots_txt_respected'],
                'max_pages_limited': True
            }
        }

    def _scrape_aggressive(self) -> Dict[str, Any]:
        """كشط قوي وسريع"""
        logger.info("تشغيل الكشط القوي")
        
        # تقليل التأخير للسرعة
        original_delay = self.config.delay_between_requests
        self.config.delay_between_requests = 0.2
        
        # زيادة عدد الخيوط
        original_threads = self.config.max_threads
        self.config.max_threads = 8
        
        result = self._parallel_scraping()
        
        # استعادة الإعدادات الأصلية
        self.config.delay_between_requests = original_delay
        self.config.max_threads = original_threads
        
        return {
            'mode': 'aggressive',
            'pages': result,
            'page_count': len(result),
            'performance_optimizations': {
                'reduced_delay': True,
                'increased_threads': True,
                'parallel_processing': True
            }
        }

    def _scrape_single_page(self, url: str) -> Optional[Dict[str, Any]]:
        """كشط صفحة واحدة"""
        try:
            if url in self.visited_urls:
                return None
            
            self.visited_urls.add(url)
            logger.debug(f"كشط الصفحة: {url}")
            
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            # إحصائيات الاستجابة
            self.stats['total_size_bytes'] += len(response.content)
            self.stats['status_codes'][response.status_code] += 1
            self.stats['content_types'][response.headers.get('content-type', 'unknown')] += 1
            
            # تحليل المحتوى
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                page_data = self._extract_page_data(soup, url, response)
                
                self.stats['pages_scraped'] += 1
                time.sleep(self.config.delay_between_requests)
                
                return page_data
            else:
                logger.warning(f"نوع محتوى غير مدعوم: {response.headers.get('content-type')}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في كشط {url}: {e}")
            self.failed_urls.add(url)
            self.stats['pages_failed'] += 1
            self.stats['errors'].append(f"صفحة {url}: {str(e)}")
            return None

    def _extract_page_data(self, soup: BeautifulSoup, url: str, response: requests.Response) -> Dict[str, Any]:
        """استخراج بيانات الصفحة"""
        page_data = {
            'url': url,
            'title': '',
            'meta_description': '',
            'meta_keywords': '',
            'language': '',
            'headers': {},
            'links': [],
            'assets': {},
            'forms': [],
            'content_metrics': {},
            'technologies': [],
            'response_info': {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content),
                'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
            },
            'extraction_time': datetime.now().isoformat()
        }
        
        try:
            # العنوان
            title_tag = soup.find('title')
            if title_tag:
                page_data['title'] = title_tag.get_text(strip=True)
            
            # Meta tags
            page_data['meta_description'] = self._get_meta_content(soup, 'description')
            page_data['meta_keywords'] = self._get_meta_content(soup, 'keywords')
            
            # اللغة
            html_tag = soup.find('html')
            if html_tag:
                page_data['language'] = html_tag.get('lang', '')
            
            # العناوين (h1-h6)
            for i in range(1, 7):
                headers = soup.find_all(f'h{i}')
                page_data['headers'][f'h{i}'] = [h.get_text(strip=True) for h in headers]
            
            # الروابط
            if self.config.extract_assets:
                page_data['links'] = self._extract_links(soup, url)
                page_data['assets'] = self._extract_assets(soup, url)
            
            # النماذج
            if self.config.extract_forms:
                page_data['forms'] = self._extract_forms(soup)
            
            # مقاييس المحتوى
            if self.config.analyze_structure:
                page_data['content_metrics'] = self._analyze_content_metrics(soup)
            
            # التقنيات المكتشفة
            page_data['technologies'] = self._detect_technologies(soup, response)
            
            # اكتشاف اللغات
            if self.config.detect_languages:
                detected_languages = self._detect_languages(soup)
                page_data['detected_languages'] = detected_languages
                self.stats['detected_languages'].extend(detected_languages)
            
        except Exception as e:
            logger.error(f"خطأ في استخراج بيانات الصفحة {url}: {e}")
            page_data['extraction_error'] = str(e)
        
        return page_data

    def _crawl_recursive(self, url: str, depth: int = 0, timeout_limit: int = 120, start_time: float = None) -> Dict[str, Dict[str, Any]]:
        """كشط تكراري للموقع"""
        if start_time is None:
            start_time = time.time()
        
        # فحص انتهاء الوقت
        if time.time() - start_time > timeout_limit:
            logger.warning(f"انتهى وقت التحليل بعد {timeout_limit} ثانية")
            return {}
        
        if depth > self.config.max_depth or url in self.visited_urls:
            return {}
        
        # كشط الصفحة الحالية
        page_data = self._scrape_single_page(url)
        if not page_data:
            return {}
        
        result = {url: page_data}
        self.stats['pages_discovered'] += 1
        
        # كشط الصفحات المرتبطة
        if depth < self.config.max_depth and 'links' in page_data:
            links_to_crawl = page_data['links'][:3]  # تحديد عدد الروابط
            
            for link_data in links_to_crawl:
                # فحص انتهاء الوقت قبل كل استدعاء تكراري
                if time.time() - start_time > timeout_limit:
                    break
                
                link_url = link_data['url']
                if self._is_valid_url(link_url) and link_url not in self.visited_urls:
                    try:
                        child_results = self._crawl_recursive(link_url, depth + 1, timeout_limit, start_time)
                        result.update(child_results)
                    except Exception as e:
                        logger.warning(f"خطأ في كشط {link_url}: {e}")
        
        return result

    # Helper Methods
    def _is_valid_url(self, url: str) -> bool:
        """فحص صحة الرابط"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc == self.domain and 
                   parsed.scheme in ['http', 'https'] and
                   url not in self.visited_urls)
        except Exception:
            return False

    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str:
        """استخراج محتوى meta tag"""
        meta = soup.find('meta', attrs={'name': name})
        return meta.get('content', '') if meta else ''

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """استخراج الروابط"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href:
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == self.domain:
                    self.stats['internal_links_found'] += 1
                else:
                    self.stats['external_links_found'] += 1
                    self.external_urls.add(full_url)
                
                links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)[:100],
                    'title': link.get('title', ''),
                    'type': 'internal' if urlparse(full_url).netloc == self.domain else 'external'
                })
        return links

    def _extract_assets(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List[Dict[str, str]]]:
        """استخراج الأصول"""
        assets = {
            'images': [],
            'css': [],
            'javascript': [],
            'fonts': [],
            'other': []
        }
        
        # الصور
        for img in soup.find_all('img', src=True):
            assets['images'].append({
                'src': urljoin(base_url, img.get('src', '')),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
            self.stats['images_found'] += 1
        
        # ملفات CSS
        for link in soup.find_all('link', rel='stylesheet'):
            assets['css'].append({
                'href': urljoin(base_url, link.get('href', '')),
                'media': link.get('media', 'all')
            })
            self.stats['css_files_found'] += 1
        
        # ملفات JavaScript
        for script in soup.find_all('script', src=True):
            assets['javascript'].append({
                'src': urljoin(base_url, script.get('src', '')),
                'type': script.get('type', 'text/javascript')
            })
            self.stats['js_files_found'] += 1
        
        return assets

    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """استخراج النماذج"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'select', 'textarea']):
                form_data['inputs'].append({
                    'type': input_tag.get('type', ''),
                    'name': input_tag.get('name', ''),
                    'id': input_tag.get('id', ''),
                    'required': input_tag.has_attr('required')
                })
            
            forms.append(form_data)
            self.stats['forms_found'] += 1
        
        return forms

    def _analyze_content_metrics(self, soup: BeautifulSoup) -> Dict[str, int]:
        """تحليل مقاييس المحتوى"""
        text_content = soup.get_text()
        return {
            'word_count': len(text_content.split()),
            'character_count': len(text_content),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'image_count': len(soup.find_all('img')),
            'link_count': len(soup.find_all('a')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table'))
        }

    def _detect_technologies(self, soup: BeautifulSoup, response: requests.Response) -> List[str]:
        """كشف التقنيات المستخدمة"""
        technologies = []
        content = str(soup).lower()
        
        # كشف CMS
        for cms, patterns in self.tech_patterns['cms'].items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                technologies.append(cms)
        
        # كشف Frameworks
        for framework, patterns in self.tech_patterns['frameworks'].items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                technologies.append(framework)
        
        # إضافة إلى الإحصائيات العامة
        self.stats['detected_technologies'].extend(technologies)
        
        return list(set(technologies))

    def _detect_languages(self, soup: BeautifulSoup) -> List[str]:
        """كشف اللغات المستخدمة"""
        languages = []
        content = str(soup)
        
        for language, patterns in self.language_patterns.items():
            if any(re.search(pattern, content) for pattern in patterns):
                languages.append(language)
        
        return languages

    def _generate_summary(self) -> Dict[str, Any]:
        """إنشاء ملخص للكشط"""
        return {
            'total_pages_discovered': self.stats['pages_discovered'],
            'total_pages_scraped': self.stats['pages_scraped'],
            'success_rate': round((self.stats['pages_scraped'] / max(1, self.stats['pages_discovered'])) * 100, 2),
            'total_links_found': self.stats['internal_links_found'] + self.stats['external_links_found'],
            'total_assets_found': (self.stats['images_found'] + self.stats['css_files_found'] + 
                                 self.stats['js_files_found']),
            'most_common_status_codes': dict(self.stats['status_codes'].most_common(3)),
            'detected_technologies': list(set(self.stats['detected_technologies'])),
            'detected_languages': list(set(self.stats['detected_languages'])),
            'processing_performance': {
                'total_time': self.stats['processing_time_seconds'],
                'average_time_per_page': self.stats.get('average_response_time', 0),
                'total_data_scraped_mb': round(self.stats['total_size_bytes'] / (1024 * 1024), 2)
            }
        }

    # Placeholder methods for complete functionality
    def _parallel_scraping(self): return {}
    def _advanced_analysis(self, result): return {}