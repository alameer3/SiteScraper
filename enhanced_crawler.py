#!/usr/bin/env python3
"""
نظام استخراج محسن مع تجاوز الحماية المتطور
Enhanced Crawler with Advanced Protection Bypass
"""

import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag
import logging

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تحديد المواقع الآمنة للاختبار
SAFE_TEST_SITES = [
    'https://httpbin.org/',
    'https://example.com/',
    'https://jsonplaceholder.typicode.com/',
    'https://httpstat.us/',
    'https://postman-echo.com/',
    'https://reqres.in/',
]

class EnhancedCrawler:
    """نظام استخراج محسن مع تجاوز حماية متطور"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = self._create_enhanced_session()
        
        # User agents متنوعة
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0'
        ]
        
        # قائمة المواقع المحظورة (لأسباب أمنية)
        self.blocked_domains = {
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'tiktok.com', 'snapchat.com', 'whatsapp.com', 'telegram.org',
            'banking-sites.com', 'adult-content.com'  # أمثلة
        }
        
    def _create_enhanced_session(self) -> requests.Session:
        """إنشاء جلسة HTTP محسنة مع إعدادات متطورة"""
        session = requests.Session()
        
        # إعداد retry strategy محسن
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers أساسية
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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
    
    def _is_domain_blocked(self, url: str) -> bool:
        """التحقق من كون النطاق محظوراً"""
        try:
            domain = urlparse(url).netloc.lower()
            for blocked in self.blocked_domains:
                if blocked in domain:
                    return True
            return False
        except Exception:
            return True
    
    def _get_random_user_agent(self) -> str:
        """الحصول على User-Agent عشوائي"""
        return random.choice(self.user_agents)
    
    def _add_random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """إضافة تأخير عشوائي لتجنب الحظر"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def fetch_with_protection_bypass(self, url: str, max_attempts: int = 3) -> dict:
        """
        جلب صفحة مع تجاوز حماية متطور
        
        Returns:
            dict: {'success': bool, 'response': Response, 'method': str, 'error': str}
        """
        if self._is_domain_blocked(url):
            return {
                'success': False,
                'response': None,
                'method': 'blocked',
                'error': f'النطاق محظور لأسباب أمنية: {urlparse(url).netloc}'
            }
        
        methods = [
            self._method_basic_request,
            self._method_browser_simulation,
            self._method_mobile_simulation,
            self._method_slow_request
        ]
        
        for attempt, method in enumerate(methods, 1):
            try:
                self.logger.info(f"المحاولة {attempt}: استخدام {method.__name__}")
                
                # تغيير User-Agent لكل محاولة
                self.session.headers['User-Agent'] = self._get_random_user_agent()
                
                # تأخير عشوائي
                if attempt > 1:
                    self._add_random_delay(2.0, 5.0)
                
                response = method(url)
                
                if response and response.status_code == 200:
                    return {
                        'success': True,
                        'response': response,
                        'method': method.__name__,
                        'error': None
                    }
                elif response and response.status_code == 403:
                    self.logger.warning(f"403 Forbidden مع {method.__name__}")
                    continue
                else:
                    self.logger.warning(f"فشل {method.__name__}: {response.status_code if response else 'No response'}")
                    continue
                    
            except Exception as e:
                self.logger.error(f"خطأ في {method.__name__}: {str(e)}")
                continue
        
        # إذا فشلت جميع الطرق، اقترح مواقع آمنة
        return {
            'success': False,
            'response': None,
            'method': 'all_failed',
            'error': f'فشل في الوصول للموقع. المواقع الآمنة للاختبار: {", ".join(SAFE_TEST_SITES[:3])}'
        }
    
    def _method_basic_request(self, url: str) -> requests.Response:
        """طريقة الطلب الأساسي"""
        return self.session.get(url, timeout=15, verify=False)
    
    def _method_browser_simulation(self, url: str) -> requests.Response:
        """محاكاة متصفح متطورة"""
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Referer': 'https://www.google.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        return self.session.get(url, headers=headers, timeout=20, verify=False)
    
    def _method_mobile_simulation(self, url: str) -> requests.Response:
        """محاكاة جهاز محمول"""
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        return self.session.get(url, headers=mobile_headers, timeout=25, verify=False)
    
    def _method_slow_request(self, url: str) -> requests.Response:
        """طلب بطيء لتجنب rate limiting"""
        self._add_random_delay(3.0, 6.0)
        
        slow_headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        
        return self.session.get(url, headers=slow_headers, timeout=30, verify=False)
    
    def analyze_website_enhanced(self, url: str) -> dict:
        """تحليل موقع مع نظام الحماية المحسن"""
        start_time = time.time()
        
        result = {
            'url': url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': False,
            'method_used': None,
            'execution_time': 0,
            'data': {},
            'error': None,
            'suggestions': []
        }
        
        try:
            # محاولة جلب الصفحة
            fetch_result = self.fetch_with_protection_bypass(url)
            
            if not fetch_result['success']:
                result['error'] = fetch_result['error']
                result['suggestions'] = SAFE_TEST_SITES
                return result
            
            response = fetch_result['response']
            result['method_used'] = fetch_result['method']
            
            # تحليل المحتوى
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج المعلومات الأساسية
            result['data'] = {
                'title': soup.title.string.strip() if soup.title and soup.title.string else 'بدون عنوان',
                'status_code': response.status_code,
                'content_length': len(response.content),
                'server': response.headers.get('server', 'غير محدد'),
                'content_type': response.headers.get('content-type', ''),
                'last_modified': response.headers.get('last-modified'),
                'cache_control': response.headers.get('cache-control'),
                
                # إحصائيات العناصر
                'elements': {
                    'links': len(soup.find_all('a')),
                    'images': len(soup.find_all('img')),
                    'scripts': len(soup.find_all('script')),
                    'stylesheets': len(soup.find_all('link', rel='stylesheet')),
                    'forms': len(soup.find_all('form')),
                    'headings': {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
                },
                
                # معلومات Meta
                'meta_tags': self._extract_meta_tags(soup),
                
                # تحليل التقنيات
                'technologies': self._detect_technologies_basic(soup, response),
                
                # معلومات الأمان
                'security': {
                    'https': url.startswith('https://'),
                    'security_headers': {
                        'strict_transport_security': bool(response.headers.get('strict-transport-security')),
                        'content_security_policy': bool(response.headers.get('content-security-policy')),
                        'x_frame_options': bool(response.headers.get('x-frame-options')),
                    }
                }
            }
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"خطأ في التحليل: {str(e)}")
            result['error'] = f"خطأ في التحليل: {str(e)}"
        
        finally:
            result['execution_time'] = round(time.time() - start_time, 2)
        
        return result
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> dict:
        """استخراج Meta tags"""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            if isinstance(meta, Tag):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[str(name)] = str(content)
        return meta_tags
    
    def _detect_technologies_basic(self, soup: BeautifulSoup, response: requests.Response) -> dict:
        """كشف التقنيات الأساسية"""
        html_content = str(soup).lower()
        
        technologies = {
            'cms': 'غير محدد',
            'frameworks': [],
            'server': response.headers.get('server', 'غير محدد')
        }
        
        # كشف CMS
        cms_indicators = {
            'WordPress': ['wp-content', 'wp-includes'],
            'Drupal': ['drupal', 'sites/default'],
            'Joomla': ['joomla', 'option=com_'],
            'Shopify': ['shopify'],
            'Django': ['csrfmiddlewaretoken']
        }
        
        for cms, indicators in cms_indicators.items():
            if any(indicator in html_content for indicator in indicators):
                technologies['cms'] = cms
                break
        
        # كشف JavaScript frameworks
        js_frameworks = {
            'React': ['react'],
            'Vue': ['vue.js'],
            'Angular': ['angular'],
            'jQuery': ['jquery']
        }
        
        for framework, indicators in js_frameworks.items():
            if any(indicator in html_content for indicator in indicators):
                technologies['frameworks'].append(framework)
        
        return technologies

# إنشاء instance عام
enhanced_crawler = EnhancedCrawler()