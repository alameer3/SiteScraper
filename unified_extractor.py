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

class UnifiedWebsiteExtractor:
    """مستخرج المواقع الموحد مع جميع الوظائف المتقدمة"""
    
    def __init__(self):
        self.results = {}
        self.extraction_id = 0
        self.session = self._create_session()
        
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
    
    def extract_website(self, url, extraction_type='basic'):
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
            elif extraction_type == 'advanced':
                result = self._extract_advanced(soup, url, basic_info)
            elif extraction_type == 'complete':
                result = self._extract_complete(soup, url, basic_info)
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
    
    def _extract_basic_info(self, soup, url, response):
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
    
    def _extract_advanced(self, soup, url, basic_info):
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
    
    def _extract_complete(self, soup, url, basic_info):
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
    
    def _detect_technologies(self, soup, content):
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
    
    def _analyze_performance(self, response, content_size):
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
    
    def _analyze_links(self, soup, base_url):
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
    
    def _analyze_images(self, soup, base_url):
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
    
    def _analyze_seo(self, soup):
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
    
    def _analyze_structure(self, soup):
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
    
    def _analyze_security(self, soup, url):
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
    
    def _find_api_endpoints(self, soup):
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
    
    def _analyze_database_structure(self, soup):
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
    
    def _analyze_interactive_elements(self, soup):
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
    
    def _ai_content_analysis(self, soup):
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
    
    def _generate_clone_strategy(self, soup, url):
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
    
    def get_results(self):
        """الحصول على جميع النتائج"""
        return list(self.results.values())
    
    def get_result(self, extraction_id):
        """الحصول على نتيجة محددة"""
        return self.results.get(extraction_id)

# إنشاء مثيل عام
unified_extractor = UnifiedWebsiteExtractor()

def extract_website_unified(url, extraction_type='basic'):
    """دالة سهلة للاستخدام"""
    return unified_extractor.extract_website(url, extraction_type)

if __name__ == '__main__':
    # اختبار سريع
    result = extract_website_unified('https://example.com', 'advanced')
    print(json.dumps(result, indent=2, ensure_ascii=False))