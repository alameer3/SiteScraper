"""
محرك التحليل الأساسي - Core Analysis Engine
"""
import re
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Tag, NavigableString
import urllib3

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class WebsiteAnalyzer:
    """محلل المواقع الرئيسي - نسخة محسنة ومرتبة"""
    
    def __init__(self):
        self.session = self._create_session()
        self.analysis_results = {}
        
    def _create_session(self) -> requests.Session:
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
        
        # Headers واقعية
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def analyze_website(self, url: str, analysis_type: str = 'standard') -> Dict[str, Any]:
        """
        تحليل موقع ويب شامل
        
        أنواع التحليل:
        - basic: تحليل أساسي سريع
        - standard: تحليل قياسي شامل
        - advanced: تحليل متقدم مع تفاصيل إضافية
        """
        logger.info(f"بدء تحليل الموقع: {url} - نوع التحليل: {analysis_type}")
        
        start_time = time.time()
        analysis_result = {
            'url': url,
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'execution_time': 0,
            'data': {}
        }
        
        try:
            # جلب محتوى الصفحة
            response = self._fetch_page(url)
            if not response:
                raise Exception("فشل في جلب محتوى الصفحة")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # التحليل الأساسي
            basic_data = self._analyze_basic(soup, response, url)
            analysis_result['data'].update(basic_data)
            
            # التحليل حسب النوع
            if analysis_type in ['standard', 'advanced']:
                standard_data = self._analyze_standard(soup, response, url)
                analysis_result['data'].update(standard_data)
            
            if analysis_type == 'advanced':
                advanced_data = self._analyze_advanced(soup, response, url)
                analysis_result['data'].update(advanced_data)
            
            analysis_result['success'] = True
            
        except Exception as e:
            logger.error(f"خطأ في التحليل: {str(e)}")
            analysis_result['error'] = str(e)
        
        finally:
            analysis_result['execution_time'] = round(time.time() - start_time, 2)
        
        return analysis_result
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """جلب محتوى الصفحة مع معالجة محسنة للأخطاء"""
        try:
            response = self.session.get(url, timeout=15, verify=False)
            
            # معالجة خاصة لكودات الخطأ الشائعة
            if response.status_code == 403:
                logger.warning(f"وصول محظور للموقع {url} - 403 Forbidden")
                raise Exception(f"الوصول محظور للموقع {url}. قد يكون الموقع محمياً أو يحظر البرامج الآلية")
            elif response.status_code == 404:
                logger.warning(f"الصفحة غير موجودة {url} - 404 Not Found")
                raise Exception(f"الصفحة غير موجودة: {url}")
            elif response.status_code == 429:
                logger.warning(f"طلبات كثيرة جداً {url} - 429 Too Many Requests")
                raise Exception(f"طلبات كثيرة جداً من الموقع {url}. حاول مرة أخرى لاحقاً")
            elif response.status_code >= 500:
                logger.warning(f"خطأ في خادم الموقع {url} - {response.status_code}")
                raise Exception(f"خطأ في خادم الموقع {url}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.SSLError as e:
            logger.error(f"خطأ SSL في {url}: {str(e)}")
            raise Exception(f"خطأ في شهادة الأمان للموقع {url}")
        except requests.exceptions.Timeout as e:
            logger.error(f"انتهت مهلة الاتصال بـ {url}: {str(e)}")
            raise Exception(f"انتهت مهلة الاتصال بالموقع {url}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"خطأ في الاتصال بـ {url}: {str(e)}")
            raise Exception(f"فشل الاتصال بالموقع {url}")
        except Exception as e:
            logger.error(f"خطأ في جلب الصفحة {url}: {str(e)}")
            raise Exception(f"فشل في استخراج المحتوى الأساسي: {str(e)}")
    
    def _analyze_basic(self, soup: BeautifulSoup, response: requests.Response, url: str) -> Dict[str, Any]:
        """التحليل الأساسي"""
        data = {}
        
        # معلومات أساسية
        data['title'] = soup.title.string.strip() if soup.title else 'بدون عنوان'
        data['status_code'] = response.status_code
        data['content_type'] = response.headers.get('content-type', '')
        data['server'] = response.headers.get('server', 'غير محدد')
        data['content_length'] = len(response.content)
        
        # Meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                meta_tags[meta.get('name')] = meta.get('content', '')
            elif meta.get('property'):
                meta_tags[meta.get('property')] = meta.get('content', '')
        data['meta_tags'] = meta_tags
        
        # عدد العناصر
        data['element_counts'] = {
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img')),
            'scripts': len(soup.find_all('script')),
            'stylesheets': len(soup.find_all('link', rel='stylesheet')),
            'forms': len(soup.find_all('form')),
            'headings': {
                f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)
            }
        }
        
        return data
    
    def _analyze_standard(self, soup: BeautifulSoup, response: requests.Response, url: str) -> Dict[str, Any]:
        """التحليل القياسي"""
        data = {}
        
        # تحليل التقنيات المستخدمة
        data['technologies'] = self._detect_technologies(soup, response)
        
        # تحليل SEO
        data['seo_analysis'] = self._analyze_seo(soup)
        
        # تحليل الروابط
        data['links_analysis'] = self._analyze_links(soup, url)
        
        # تحليل الصور
        data['images_analysis'] = self._analyze_images(soup, url)
        
        # تحليل الأمان
        data['security_headers'] = self._analyze_security_headers(response)
        
        return data
    
    def _analyze_advanced(self, soup: BeautifulSoup, response: requests.Response, url: str) -> Dict[str, Any]:
        """التحليل المتقدم"""
        data = {}
        
        # تحليل الأداء
        data['performance_analysis'] = self._analyze_performance(soup, response)
        
        # تحليل البنية
        data['structure_analysis'] = self._analyze_structure(soup)
        
        # تحليل المحتوى
        data['content_analysis'] = self._analyze_content(soup)
        
        # تحليل JavaScript
        data['javascript_analysis'] = self._analyze_javascript(soup)
        
        return data
    
    def _detect_technologies(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """كشف التقنيات المستخدمة"""
        technologies = {
            'cms': 'غير محدد',
            'frameworks': [],
            'analytics': [],
            'server_info': response.headers.get('server', 'غير محدد')
        }
        
        # كشف CMS
        cms_indicators = {
            'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
            'Drupal': ['drupal', 'sites/default'],
            'Joomla': ['joomla', 'option=com_'],
            'Shopify': ['shopify', 'myshopify'],
            'Magento': ['magento', 'mage/'],
            'Django': ['csrfmiddlewaretoken'],
            'Laravel': ['laravel_session']
        }
        
        page_html = str(soup)
        for cms, indicators in cms_indicators.items():
            if any(indicator in page_html.lower() for indicator in indicators):
                technologies['cms'] = cms
                break
        
        # كشف JavaScript frameworks
        js_frameworks = {
            'React': ['react', 'reactdom'],
            'Vue': ['vue.js', '__vue__'],
            'Angular': ['angular', 'ng-app'],
            'jQuery': ['jquery', '$'],
            'Bootstrap': ['bootstrap']
        }
        
        for framework, indicators in js_frameworks.items():
            if any(indicator in page_html.lower() for indicator in indicators):
                technologies['frameworks'].append(framework)
        
        # كشف أدوات التحليل
        analytics_tools = {
            'Google Analytics': ['google-analytics', 'gtag'],
            'Facebook Pixel': ['facebook.net/tr'],
            'Hotjar': ['hotjar']
        }
        
        for tool, indicators in analytics_tools.items():
            if any(indicator in page_html.lower() for indicator in indicators):
                technologies['analytics'].append(tool)
        
        return technologies
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل SEO"""
        seo = {
            'title_length': len(soup.title.string) if soup.title else 0,
            'meta_description': None,
            'meta_keywords': None,
            'h1_count': len(soup.find_all('h1')),
            'h2_count': len(soup.find_all('h2')),
            'alt_texts_missing': 0,
            'score': 0
        }
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            seo['meta_description'] = meta_desc.get('content', '')
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            seo['meta_keywords'] = meta_keywords.get('content', '')
        
        # الصور بدون alt text
        images = soup.find_all('img')
        seo['alt_texts_missing'] = sum(1 for img in images if not img.get('alt'))
        
        # حساب نقاط SEO
        score = 0
        if seo['title_length'] > 0:
            score += 20
        if seo['meta_description']:
            score += 20
        if seo['h1_count'] > 0:
            score += 15
        if seo['alt_texts_missing'] == 0 and len(images) > 0:
            score += 15
        
        seo['score'] = score
        return seo
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل الروابط"""
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        
        for link in links:
            href = link.get('href', '')
            if href.startswith('http'):
                if urlparse(base_url).netloc in href:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(urljoin(base_url, href))
        
        return {
            'total_links': len(links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'internal_links_list': internal_links[:10],  # أول 10 فقط
            'external_links_list': external_links[:10]   # أول 10 فقط
        }
    
    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل الصور"""
        images = soup.find_all('img')
        
        return {
            'total_images': len(images),
            'images_with_alt': sum(1 for img in images if img.get('alt')),
            'images_without_alt': sum(1 for img in images if not img.get('alt')),
            'lazy_loaded': sum(1 for img in images if 'lazy' in img.get('loading', '').lower()),
        }
    
    def _analyze_security_headers(self, response: requests.Response) -> Dict[str, Any]:
        """تحليل headers الأمان"""
        headers = response.headers
        security_headers = {
            'strict_transport_security': headers.get('strict-transport-security'),
            'content_security_policy': headers.get('content-security-policy'),
            'x_frame_options': headers.get('x-frame-options'),
            'x_content_type_options': headers.get('x-content-type-options'),
            'x_xss_protection': headers.get('x-xss-protection'),
            'referrer_policy': headers.get('referrer-policy')
        }
        
        # حساب نقاط الأمان
        security_score = sum(1 for value in security_headers.values() if value) * 15
        security_headers['security_score'] = min(security_score, 100)
        
        return security_headers
    
    def _analyze_performance(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """تحليل الأداء"""
        return {
            'page_size_kb': len(response.content) / 1024,
            'total_requests_estimated': (
                len(soup.find_all('script')) + 
                len(soup.find_all('link', rel='stylesheet')) + 
                len(soup.find_all('img'))
            ),
            'inline_css_count': len(soup.find_all('style')),
            'inline_js_count': len([s for s in soup.find_all('script') if s.string]),
        }
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل البنية"""
        return {
            'has_header': bool(soup.find('header')),
            'has_nav': bool(soup.find('nav')),
            'has_main': bool(soup.find('main')),
            'has_footer': bool(soup.find('footer')),
            'has_aside': bool(soup.find('aside')),
            'semantic_elements': len(soup.find_all(['header', 'nav', 'main', 'aside', 'footer', 'section', 'article']))
        }
    
    def _analyze_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل المحتوى"""
        text_elements = soup.get_text()
        words = text_elements.split()
        
        return {
            'word_count': len(words),
            'character_count': len(text_elements),
            'paragraph_count': len(soup.find_all('p')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table'))
        }
    
    def _analyze_javascript(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل JavaScript"""
        scripts = soup.find_all('script')
        
        external_scripts = []
        inline_scripts = 0
        
        for script in scripts:
            if script.get('src'):
                external_scripts.append(script.get('src'))
            elif script.string:
                inline_scripts += 1
        
        return {
            'total_scripts': len(scripts),
            'external_scripts': len(external_scripts),
            'inline_scripts': inline_scripts,
            'external_scripts_list': external_scripts[:10]  # أول 10 فقط
        }