#!/usr/bin/env python3
"""
نظام الزحف المتقدم متعدد المستويات
"""
import asyncio
import aiohttp
import time
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Optional, Any
from bs4 import BeautifulSoup
from pathlib import Path
import re

class AdvancedCrawler:
    """نظام زحف متقدم مع دعم JavaScript و AJAX"""
    
    def __init__(self, max_depth: int = 5, max_pages: int = 200, concurrent_requests: int = 5):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.concurrent_requests = concurrent_requests
        self.visited_urls: Set[str] = set()
        self.crawled_data: List[Dict[str, Any]] = []
        self.base_domain = ""
        self.robots_txt_rules = {}
        
    async def crawl_website(self, start_url: str, output_dir: Path) -> Dict[str, Any]:
        """زحف موقع ويب بشكل متقدم"""
        
        self.base_domain = urlparse(start_url).netloc
        
        results = {
            'start_url': start_url,
            'total_pages_crawled': 0,
            'ajax_endpoints_found': [],
            'api_endpoints_found': [],
            'dynamic_content_detected': [],
            'javascript_analysis': {},
            'database_indicators': [],
            'crawl_duration': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # تحميل robots.txt
            await self._load_robots_txt(start_url)
            
            # بدء الزحف المتقدم
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'Mozilla/5.0 (compatible; AdvancedCrawler/1.0)'}
            ) as session:
                await self._crawl_recursive(session, start_url, 0)
            
            # تحليل البيانات المجمعة
            results.update(self._analyze_crawled_data())
            
            # إنشاء تقارير
            await self._generate_reports(output_dir, results)
            
            results['total_pages_crawled'] = len(self.crawled_data)
            results['crawl_duration'] = round(time.time() - start_time, 2)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    async def _load_robots_txt(self, start_url: str) -> None:
        """تحميل وتحليل robots.txt"""
        
        robots_url = urljoin(start_url, '/robots.txt')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url) as response:
                    if response.status == 200:
                        robots_content = await response.text()
                        self._parse_robots_txt(robots_content)
        except:
            pass  # تجاهل أخطاء robots.txt
    
    def _parse_robots_txt(self, content: str) -> None:
        """تحليل محتوى robots.txt"""
        
        lines = content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('User-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
                if current_user_agent not in self.robots_txt_rules:
                    self.robots_txt_rules[current_user_agent] = {'disallow': [], 'allow': []}
            elif line.startswith('Disallow:') and current_user_agent:
                path = line.split(':', 1)[1].strip()
                if path:
                    self.robots_txt_rules[current_user_agent]['disallow'].append(path)
            elif line.startswith('Allow:') and current_user_agent:
                path = line.split(':', 1)[1].strip()
                if path:
                    self.robots_txt_rules[current_user_agent]['allow'].append(path)
    
    def _should_crawl_url(self, url: str) -> bool:
        """فحص ما إذا كان يجب زحف الرابط حسب robots.txt"""
        
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # فحص قواعد robots.txt
        for user_agent in ['*', 'AdvancedCrawler']:
            if user_agent in self.robots_txt_rules:
                rules = self.robots_txt_rules[user_agent]
                
                # فحص Disallow
                for disallowed_path in rules['disallow']:
                    if path.startswith(disallowed_path):
                        return False
                
                # فحص Allow (إذا كان محظور بواسطة *)
                for allowed_path in rules['allow']:
                    if path.startswith(allowed_path):
                        return True
        
        return True
    
    async def _crawl_recursive(self, session: aiohttp.ClientSession, url: str, depth: int) -> None:
        """زحف تكراري مع دعم متعدد المستويات"""
        
        if (depth > self.max_depth or 
            len(self.visited_urls) >= self.max_pages or 
            url in self.visited_urls or
            not self._should_crawl_url(url)):
            return
        
        self.visited_urls.add(url)
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # تحليل الصفحة
                    page_data = await self._analyze_page(url, content, response, depth)
                    self.crawled_data.append(page_data)
                    
                    # استخراج الروابط للمستوى التالي
                    if depth < self.max_depth:
                        links = self._extract_links_advanced(content, url)
                        
                        # زحف الروابط بشكل متوازي
                        tasks = []
                        for link in links[:10]:  # حد أقصى 10 روابط لكل صفحة
                            if self._is_same_domain(link, url):
                                tasks.append(self._crawl_recursive(session, link, depth + 1))
                        
                        if tasks:
                            await asyncio.gather(*tasks, return_exceptions=True)
                            
        except Exception as e:
            self.crawled_data.append({
                'url': url,
                'depth': depth,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    async def _analyze_page(self, url: str, content: str, response: aiohttp.ClientResponse, depth: int) -> Dict[str, Any]:
        """تحليل صفحة ويب بشكل متقدم"""
        
        soup = BeautifulSoup(content, 'html.parser')
        
        page_data = {
            'url': url,
            'depth': depth,
            'status_code': response.status,
            'content_type': response.headers.get('content-type', ''),
            'content_length': len(content),
            'title': self._get_page_title(soup),
            'meta_description': self._get_meta_description(soup),
            'timestamp': datetime.now().isoformat(),
            
            # تحليل JavaScript
            'javascript_analysis': self._analyze_javascript(soup, content),
            
            # كشف AJAX endpoints
            'ajax_endpoints': self._detect_ajax_endpoints(content),
            
            # كشف API endpoints
            'api_endpoints': self._detect_api_endpoints(content),
            
            # تحليل Forms (مؤشرات قاعدة البيانات)
            'forms_analysis': self._analyze_forms(soup),
            
            # كشف المحتوى الديناميكي
            'dynamic_content': self._detect_dynamic_content(soup, content),
            
            # تحليل الأمان
            'security_analysis': self._analyze_security(soup, response),
            
            # تحليل الأداء
            'performance_indicators': self._analyze_performance(response),
            
            # تحليل SEO
            'seo_analysis': self._analyze_seo(soup),
            
            # كشف التقنيات
            'technologies_detected': self._detect_technologies(content, response)
        }
        
        return page_data
    
    def _analyze_javascript(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """تحليل JavaScript المتقدم"""
        
        analysis = {
            'total_scripts': 0,
            'external_scripts': [],
            'inline_scripts_count': 0,
            'frameworks_detected': [],
            'ajax_patterns': [],
            'api_calls': [],
            'event_listeners': [],
            'dom_manipulation': False,
            'async_loading': False
        }
        
        # العد الإجمالي للسكريبتات
        scripts = soup.find_all('script')
        analysis['total_scripts'] = len(scripts)
        
        # تحليل السكريبتات
        for script in scripts:
            if script.get('src'):
                src = script.get('src')
                analysis['external_scripts'].append(src)
                
                # كشف الframeworks من URLs
                if 'jquery' in src.lower():
                    analysis['frameworks_detected'].append('jQuery')
                elif 'react' in src.lower():
                    analysis['frameworks_detected'].append('React')
                elif 'vue' in src.lower():
                    analysis['frameworks_detected'].append('Vue.js')
                elif 'angular' in src.lower():
                    analysis['frameworks_detected'].append('Angular')
            else:
                analysis['inline_scripts_count'] += 1
                script_content = script.get_text()
                
                # تحليل محتوى السكريبت
                if 'ajax' in script_content.lower() or '$.ajax' in script_content:
                    analysis['ajax_patterns'].append('jQuery AJAX')
                if 'fetch(' in script_content:
                    analysis['ajax_patterns'].append('Fetch API')
                if 'XMLHttpRequest' in script_content:
                    analysis['ajax_patterns'].append('XMLHttpRequest')
                
                # كشف API calls
                api_patterns = [
                    r'["\']https?://[^"\']+/api/[^"\']*["\']',
                    r'["\']https?://[^"\']+\.json["\']',
                    r'/api/[a-zA-Z0-9/_-]+',
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, script_content)
                    analysis['api_calls'].extend(matches)
                
                # كشف event listeners
                if 'addEventListener' in script_content:
                    analysis['event_listeners'].append('addEventListener')
                if 'onclick' in script_content.lower():
                    analysis['event_listeners'].append('onclick')
                
                # كشف DOM manipulation
                if any(keyword in script_content for keyword in ['getElementById', 'querySelector', 'createElement', 'appendChild']):
                    analysis['dom_manipulation'] = True
                
                # كشف async loading
                if any(keyword in script_content for keyword in ['async', 'await', 'Promise']):
                    analysis['async_loading'] = True
        
        # إزالة التكرارات
        analysis['frameworks_detected'] = list(set(analysis['frameworks_detected']))
        analysis['ajax_patterns'] = list(set(analysis['ajax_patterns']))
        analysis['api_calls'] = list(set(analysis['api_calls']))
        analysis['event_listeners'] = list(set(analysis['event_listeners']))
        
        return analysis
    
    def _detect_ajax_endpoints(self, content: str) -> List[str]:
        """كشف نقاط نهاية AJAX"""
        
        patterns = [
            r'url\s*:\s*["\']([^"\']+)["\']',  # jQuery AJAX
            r'fetch\(["\']([^"\']+)["\']',      # Fetch API
            r'open\(["\'](?:GET|POST)["\'],\s*["\']([^"\']+)["\']',  # XMLHttpRequest
            r'action\s*=\s*["\']([^"\']+)["\']',  # Form actions
        ]
        
        endpoints = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints.extend(matches)
        
        # تنظيف وتصفية النتائج
        cleaned_endpoints = []
        for endpoint in endpoints:
            if endpoint and not endpoint.startswith('#') and not endpoint.startswith('javascript:'):
                cleaned_endpoints.append(endpoint)
        
        return list(set(cleaned_endpoints))
    
    def _detect_api_endpoints(self, content: str) -> List[str]:
        """كشف نقاط نهاية API"""
        
        api_patterns = [
            r'["\']https?://[^"\']+/api/[^"\']*["\']',
            r'["\']https?://[^"\']+/rest/[^"\']*["\']',
            r'["\']https?://[^"\']+/graphql[^"\']*["\']',
            r'/api/v\d+/[a-zA-Z0-9/_-]+',
            r'/rest/v\d+/[a-zA-Z0-9/_-]+',
        ]
        
        api_endpoints = []
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            api_endpoints.extend([match.strip('\'"') for match in matches])
        
        return list(set(api_endpoints))
    
    def _analyze_forms(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل النماذج لكشف مؤشرات قاعدة البيانات"""
        
        forms_analysis = {
            'total_forms': 0,
            'form_methods': {},
            'input_types': {},
            'database_indicators': [],
            'crud_operations': [],
            'file_uploads': False,
            'forms_data': []
        }
        
        forms = soup.find_all('form')
        forms_analysis['total_forms'] = len(forms)
        
        for form in forms:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'inputs': [],
                'suggests_database': False
            }
            
            # إحصاء methods
            method = form_data['method']
            forms_analysis['form_methods'][method] = forms_analysis['form_methods'].get(method, 0) + 1
            
            # تحليل inputs
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                input_type = inp.get('type', 'text')
                input_name = inp.get('name', '')
                
                forms_analysis['input_types'][input_type] = forms_analysis['input_types'].get(input_type, 0) + 1
                form_data['inputs'].append({
                    'type': input_type,
                    'name': input_name,
                    'id': inp.get('id', '')
                })
                
                # كشف مؤشرات قاعدة البيانات
                if input_type in ['email', 'password'] or any(keyword in input_name.lower() for keyword in ['user', 'email', 'pass', 'login', 'register']):
                    forms_analysis['database_indicators'].append(f"Authentication form detected: {input_name}")
                    form_data['suggests_database'] = True
                
                if input_name.lower() in ['search', 'query', 'q']:
                    forms_analysis['database_indicators'].append("Search form detected")
                    form_data['suggests_database'] = True
                
                if input_type == 'file':
                    forms_analysis['file_uploads'] = True
            
            # كشف CRUD operations
            action = form_data['action'].lower()
            if any(crud in action for crud in ['create', 'add', 'insert']):
                forms_analysis['crud_operations'].append('CREATE')
            if any(crud in action for crud in ['update', 'edit', 'modify']):
                forms_analysis['crud_operations'].append('UPDATE')
            if any(crud in action for crud in ['delete', 'remove']):
                forms_analysis['crud_operations'].append('DELETE')
            
            forms_analysis['forms_data'].append(form_data)
        
        forms_analysis['crud_operations'] = list(set(forms_analysis['crud_operations']))
        
        return forms_analysis
    
    def _detect_dynamic_content(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """كشف المحتوى الديناميكي"""
        
        dynamic_content = {
            'spa_indicators': [],
            'lazy_loading': False,
            'infinite_scroll': False,
            'dynamic_elements': [],
            'templating_detected': False
        }
        
        # كشف SPA indicators
        if 'ng-app' in content or 'ng-controller' in content:
            dynamic_content['spa_indicators'].append('AngularJS')
        if 'data-react' in content or '_reactInternalInstance' in content:
            dynamic_content['spa_indicators'].append('React')
        if 'v-if' in content or 'v-for' in content:
            dynamic_content['spa_indicators'].append('Vue.js')
        
        # كشف lazy loading
        if any(attr in content.lower() for attr in ['data-src', 'loading="lazy"', 'intersection observer']):
            dynamic_content['lazy_loading'] = True
        
        # كشف infinite scroll
        if any(keyword in content.lower() for keyword in ['infinite scroll', 'load more', 'pagination']):
            dynamic_content['infinite_scroll'] = True
        
        # كشف templating
        template_patterns = [
            r'\{\{[^}]+\}\}',  # Handlebars/Angular
            r'\{%[^%]+%\}',    # Django/Jinja2
            r'<%[^%]+%>',      # ASP/EJS
        ]
        
        for pattern in template_patterns:
            if re.search(pattern, content):
                dynamic_content['templating_detected'] = True
                break
        
        return dynamic_content
    
    def _analyze_security(self, soup: BeautifulSoup, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """تحليل الأمان"""
        
        security = {
            'https_used': False,
            'security_headers': {},
            'csrf_protection': False,
            'content_security_policy': False,
            'secure_cookies': False,
            'form_security': []
        }
        
        # فحص HTTPS
        security['https_used'] = str(response.url).startswith('https://')
        
        # فحص security headers
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
                security['security_headers'][header] = response.headers[header]
        
        # فحص CSP
        if 'content-security-policy' in response.headers:
            security['content_security_policy'] = True
        
        # فحص CSRF tokens
        csrf_inputs = soup.find_all('input', attrs={'name': re.compile(r'csrf|token', re.I)})
        if csrf_inputs:
            security['csrf_protection'] = True
        
        return security
    
    def _analyze_performance(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """تحليل الأداء"""
        
        performance = {
            'response_time': getattr(response, '_response_time', 0),
            'content_encoding': response.headers.get('content-encoding', ''),
            'cache_control': response.headers.get('cache-control', ''),
            'etag': response.headers.get('etag', ''),
            'last_modified': response.headers.get('last-modified', ''),
            'server': response.headers.get('server', '')
        }
        
        return performance
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل SEO"""
        
        seo = {
            'title': self._get_page_title(soup),
            'meta_description': self._get_meta_description(soup),
            'h1_count': len(soup.find_all('h1')),
            'h2_count': len(soup.find_all('h2')),
            'canonical_url': '',
            'meta_robots': '',
            'structured_data': False
        }
        
        # فحص canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            seo['canonical_url'] = canonical.get('href', '')
        
        # فحص meta robots
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta:
            seo['meta_robots'] = robots_meta.get('content', '')
        
        # فحص structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        if json_ld:
            seo['structured_data'] = True
        
        return seo
    
    def _detect_technologies(self, content: str, response: aiohttp.ClientResponse) -> List[str]:
        """كشف التقنيات المستخدمة"""
        
        technologies = []
        
        # Server technologies
        server = response.headers.get('server', '').lower()
        if 'apache' in server:
            technologies.append('Apache')
        elif 'nginx' in server:
            technologies.append('Nginx')
        elif 'iis' in server:
            technologies.append('IIS')
        
        # Programming languages
        if 'x-powered-by' in response.headers:
            powered_by = response.headers['x-powered-by'].lower()
            if 'php' in powered_by:
                technologies.append('PHP')
            elif 'asp.net' in powered_by:
                technologies.append('ASP.NET')
        
        # Content-based detection
        content_lower = content.lower()
        if 'wp-content' in content_lower:
            technologies.append('WordPress')
        if 'drupal' in content_lower:
            technologies.append('Drupal')
        if 'joomla' in content_lower:
            technologies.append('Joomla')
        
        return technologies
    
    def _get_page_title(self, soup: BeautifulSoup) -> str:
        """الحصول على عنوان الصفحة"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """الحصول على وصف meta"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc and meta_desc.get('content') else ''
    
    def _extract_links_advanced(self, content: str, base_url: str) -> List[str]:
        """استخراج الروابط بشكل متقدم"""
        
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # روابط HTML عادية
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if self._is_valid_url(full_url):
                links.append(full_url)
        
        # روابط JavaScript
        script_links = re.findall(r'window\.location\s*=\s*["\']([^"\']+)["\']', content)
        for link in script_links:
            full_url = urljoin(base_url, link)
            if self._is_valid_url(full_url):
                links.append(full_url)
        
        return list(set(links))
    
    def _is_same_domain(self, url: str, base_url: str) -> bool:
        """فحص ما إذا كان الرابط من نفس النطاق"""
        return urlparse(url).netloc == urlparse(base_url).netloc
    
    def _is_valid_url(self, url: str) -> bool:
        """فحص صحة الرابط"""
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
    
    def _analyze_crawled_data(self) -> Dict[str, Any]:
        """تحليل البيانات المجمعة"""
        
        analysis = {
            'ajax_endpoints_found': [],
            'api_endpoints_found': [],
            'dynamic_content_detected': [],
            'javascript_analysis': {},
            'database_indicators': []
        }
        
        all_ajax_endpoints = []
        all_api_endpoints = []
        all_dynamic_content = []
        all_database_indicators = []
        
        js_frameworks = []
        js_features = {
            'dom_manipulation': 0,
            'async_loading': 0,
            'ajax_patterns': []
        }
        
        for page in self.crawled_data:
            if 'error' not in page:
                # جمع AJAX endpoints
                all_ajax_endpoints.extend(page.get('ajax_endpoints', []))
                
                # جمع API endpoints
                all_api_endpoints.extend(page.get('api_endpoints', []))
                
                # جمع dynamic content
                dynamic = page.get('dynamic_content', {})
                all_dynamic_content.extend(dynamic.get('spa_indicators', []))
                
                # جمع database indicators
                forms = page.get('forms_analysis', {})
                all_database_indicators.extend(forms.get('database_indicators', []))
                
                # تحليل JavaScript
                js_analysis = page.get('javascript_analysis', {})
                js_frameworks.extend(js_analysis.get('frameworks_detected', []))
                
                if js_analysis.get('dom_manipulation'):
                    js_features['dom_manipulation'] += 1
                if js_analysis.get('async_loading'):
                    js_features['async_loading'] += 1
                
                js_features['ajax_patterns'].extend(js_analysis.get('ajax_patterns', []))
        
        # إزالة التكرارات وتنظيم النتائج
        analysis['ajax_endpoints_found'] = list(set(all_ajax_endpoints))
        analysis['api_endpoints_found'] = list(set(all_api_endpoints))
        analysis['dynamic_content_detected'] = list(set(all_dynamic_content))
        analysis['database_indicators'] = list(set(all_database_indicators))
        
        analysis['javascript_analysis'] = {
            'frameworks_detected': list(set(js_frameworks)),
            'pages_with_dom_manipulation': js_features['dom_manipulation'],
            'pages_with_async_loading': js_features['async_loading'],
            'ajax_patterns_found': list(set(js_features['ajax_patterns']))
        }
        
        return analysis
    
    async def _generate_reports(self, output_dir: Path, results: Dict[str, Any]) -> None:
        """إنشاء تقارير الزحف المتقدم"""
        
        # تقرير JSON مفصل
        detailed_report = {
            'crawl_summary': results,
            'pages_data': self.crawled_data,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        report_file = output_dir / 'advanced_crawl_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)
        
        # تقرير HTML تفاعلي
        await self._generate_html_report(output_dir, results)