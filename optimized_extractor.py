#!/usr/bin/env python3
"""
نظام استخراج محسن وسريع للمواقع
Optimized Fast Website Extractor
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
import json
import random
from pathlib import Path
from datetime import datetime
import logging

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OptimizedExtractor:
    """نظام استخراج محسن وسريع"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ]
        
        # المواقع الآمنة للاختبار
        self.safe_sites = [
            'https://httpbin.org/',
            'https://example.com/',
            'https://jsonplaceholder.typicode.com/'
        ]
    
    def create_fast_session(self) -> requests.Session:
        """إنشاء جلسة سريعة محسنة"""
        session = requests.Session()
        
        # إعداد retry سريع
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=5)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers محسنة
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        })
        
        return session
    
    def fast_fetch(self, url: str, timeout: int = 8) -> dict:
        """جلب سريع مع timeout محدود"""
        result = {
            'success': False,
            'response': None,
            'error': None,
            'method': 'fast_fetch'
        }
        
        try:
            # التحقق من النطاق
            domain = urlparse(url).netloc.lower()
            if any(blocked in domain for blocked in ['facebook.com', 'twitter.com', 'instagram.com']):
                result['error'] = f'النطاق مقيد: {domain}'
                return result
            
            session = self.create_fast_session()
            
            # محاولة سريعة
            response = session.get(url, timeout=timeout, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                result['success'] = True
                result['response'] = response
            elif response.status_code == 403:
                # محاولة بـ mobile user agent
                session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
                response = session.get(url, timeout=timeout//2, verify=False)
                
                if response.status_code == 200:
                    result['success'] = True
                    result['response'] = response
                    result['method'] = 'mobile_fallback'
                else:
                    result['error'] = f'403 Forbidden - المحتوى محمي'
            else:
                result['error'] = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            result['error'] = 'انتهت مهلة الاتصال'
        except requests.exceptions.ConnectionError:
            result['error'] = 'فشل في الاتصال'
        except Exception as e:
            result['error'] = f'خطأ: {str(e)}'
        
        return result
    
    def extract_comprehensive_fast(self, url: str) -> dict:
        """استخراج شامل سريع"""
        start_time = time.time()
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'method_used': None,
            'execution_time': 0,
            'data': {},
            'error': None,
            'suggestions': self.safe_sites
        }
        
        try:
            # جلب الصفحة
            fetch_result = self.fast_fetch(url)
            
            if not fetch_result['success']:
                result['error'] = fetch_result['error']
                return result
            
            response = fetch_result['response']
            result['method_used'] = fetch_result['method']
            
            # تحليل المحتوى
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج المعلومات الأساسية
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else 'بدون عنوان'
            
            # Meta tags
            meta_desc = soup.find('meta', {'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc and isinstance(meta_desc, Tag) else ''
            
            # عد العناصر
            links = soup.find_all('a', href=True)
            images = soup.find_all('img')
            scripts = soup.find_all('script')
            forms = soup.find_all('form')
            
            # تحليل العناوين
            headings = {}
            for i in range(1, 7):
                headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
            
            # تحليل التقنيات الأساسية
            technologies = self.detect_basic_tech(soup, response)
            
            # تحليل الأمان الأساسي
            security = {
                'https': url.startswith('https://'),
                'ssl_info': response.headers.get('strict-transport-security') is not None,
                'content_security_policy': response.headers.get('content-security-policy') is not None
            }
            
            # بناء النتيجة النهائية
            result['data'] = {
                'basic_info': {
                    'title': title,
                    'description': description,
                    'url': url,
                    'domain': urlparse(url).netloc,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'server': response.headers.get('server', 'غير محدد')
                },
                'content_analysis': {
                    'word_count': len(soup.get_text().split()),
                    'character_count': len(soup.get_text()),
                    'paragraph_count': len(soup.find_all('p'))
                },
                'elements': {
                    'links': len(links),
                    'internal_links': len([l for l in links if isinstance(l, Tag) and self.is_internal_link(l.get('href', ''), url)]),
                    'external_links': len([l for l in links if isinstance(l, Tag) and not self.is_internal_link(l.get('href', ''), url)]),
                    'images': len(images),
                    'images_with_alt': len([img for img in images if isinstance(img, Tag) and img.get('alt')]),
                    'scripts': len(scripts),
                    'forms': len(forms),
                    'headings': headings
                },
                'technologies': technologies,
                'security': security,
                'performance': {
                    'response_time': response.elapsed.total_seconds(),
                    'page_size_kb': round(len(response.content) / 1024, 2),
                    'compression': 'gzip' in response.headers.get('content-encoding', ''),
                }
            }
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"خطأ في التحليل: {str(e)}")
            result['error'] = f"خطأ في التحليل: {str(e)}"
        
        finally:
            result['execution_time'] = round(time.time() - start_time, 2)
        
        return result
    
    def is_internal_link(self, href: str, base_url: str) -> bool:
        """التحقق من كون الرابط داخلي"""
        if not href or not isinstance(href, str):
            return False
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            return True
        if href.startswith('/'):
            return True
        if href.startswith('http'):
            return urlparse(base_url).netloc in href
        return True
    
    def detect_basic_tech(self, soup: BeautifulSoup, response: requests.Response) -> dict:
        """كشف التقنيات الأساسية"""
        html_content = str(soup).lower()
        
        technologies = {
            'cms': 'غير محدد',
            'frameworks': [],
            'server': response.headers.get('server', 'غير محدد'),
            'programming_language': 'غير محدد'
        }
        
        # كشف CMS
        cms_indicators = {
            'WordPress': ['wp-content', 'wp-includes', 'wp-admin'],
            'Drupal': ['drupal', 'sites/default'],
            'Joomla': ['joomla', 'option=com_'],
            'Django': ['csrfmiddlewaretoken'],
            'Laravel': ['laravel_session'],
            'React': ['react', '__reactInternalInstance'],
            'Vue.js': ['vue.js', 'vue.min.js'],
            'Angular': ['angular', 'ng-app']
        }
        
        for tech, indicators in cms_indicators.items():
            if any(indicator in html_content for indicator in indicators):
                if tech in ['React', 'Vue.js', 'Angular']:
                    technologies['frameworks'].append(tech)
                else:
                    technologies['cms'] = tech
                break
        
        # كشف لغة البرمجة من headers
        server_header = response.headers.get('server', '').lower()
        if 'php' in server_header:
            technologies['programming_language'] = 'PHP'
        elif 'apache' in server_header:
            technologies['programming_language'] = 'متعدد'
        elif 'nginx' in server_header:
            technologies['programming_language'] = 'متعدد'
        
        return technologies
    
    def save_extraction_results(self, result: dict, output_dir: str = "extracted_files") -> str:
        """حفظ نتائج الاستخراج"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(result['url']).netloc.replace('.', '_')
            filename = f"{domain}_{timestamp}.json"
            
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"خطأ في حفظ النتائج: {str(e)}")
            return ""

# إنشاء instance عام للاستخدام
optimized_extractor = OptimizedExtractor()