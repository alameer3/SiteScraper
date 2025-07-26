"""
Code Analyzer - محلل الكود والتقنيات المتقدم
المرحلة الأولى: محرك الاستخراج العميق

يحلل:
1. بنية الكود والوظائف
2. الـ APIs والروابط
3. قواعد البيانات المحتملة
4. التقنيات المستخدمة
"""

import ast
import re
import json
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime
import hashlib

from bs4 import BeautifulSoup, Tag
import aiohttp

@dataclass
class CodeAnalysisConfig:
    """تكوين تحليل الكود"""
    analyze_javascript: bool = True
    analyze_css: bool = True
    analyze_html_structure: bool = True
    detect_frameworks: bool = True
    analyze_api_endpoints: bool = True
    analyze_database_patterns: bool = True
    extract_functions: bool = True
    analyze_security_patterns: bool = True
    deep_analysis: bool = True

class CodeAnalyzer:
    """محلل الكود المتقدم"""
    
    def __init__(self, config: Optional[CodeAnalysisConfig] = None):
        self.config = config or CodeAnalysisConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # نتائج التحليل
        self.analysis_results = {
            'javascript_analysis': {},
            'css_analysis': {},
            'html_structure': {},
            'frameworks_detected': [],
            'api_endpoints': [],
            'database_patterns': [],
            'functions_extracted': [],
            'security_analysis': {},
            'architecture_patterns': []
        }
        
        # أنماط الإطارات
        self.framework_patterns = {
            'react': [
                r'React\.createElement',
                r'ReactDOM\.render',
                r'import\s+React',
                r'from\s+["\']react["\']',
                r'\.jsx?$',
                r'React\.',
                r'useState',
                r'useEffect'
            ],
            'vue': [
                r'Vue\.component',
                r'new Vue\(',
                r'import\s+Vue',
                r'from\s+["\']vue["\']',
                r'\.vue$',
                r'v-if',
                r'v-for',
                r'v-model'
            ],
            'angular': [
                r'@Component',
                r'@Injectable',
                r'@NgModule',
                r'import.*@angular',
                r'Angular',
                r'\*ngIf',
                r'\*ngFor',
                r'\[\(ngModel\)\]'
            ],
            'jquery': [
                r'\$\(',
                r'jQuery\(',
                r'\.jquery',
                r'jquery\.js',
                r'jquery\.min\.js'
            ],
            'bootstrap': [
                r'bootstrap\.css',
                r'bootstrap\.js',
                r'class=["\'][^"\']*\b(container|row|col-|btn-|card|navbar)',
                r'data-bs-',
                r'Bootstrap'
            ],
            'tailwind': [
                r'tailwindcss',
                r'@tailwind',
                r'class=["\'][^"\']*\b(bg-|text-|p-|m-|w-|h-|flex|grid)',
                r'tailwind\.css'
            ]
        }
        
        # أنماط قواعد البيانات
        self.database_patterns = {
            'mysql': [
                r'mysql://',
                r'SELECT.*FROM',
                r'INSERT INTO',
                r'UPDATE.*SET',
                r'DELETE FROM',
                r'mysqli_',
                r'PDO.*mysql'
            ],
            'postgresql': [
                r'postgresql://',
                r'postgres://',
                r'pg_connect',
                r'psycopg2',
                r'PostgreSQL'
            ],
            'mongodb': [
                r'mongodb://',
                r'db\.collection',
                r'find\(\)',
                r'insertOne',
                r'updateOne',
                r'mongoose'
            ],
            'redis': [
                r'redis://',
                r'Redis',
                r'redis\.get',
                r'redis\.set'
            ]
        }
        
        # أنماط الأمان
        self.security_patterns = {
            'xss_vulnerable': [
                r'innerHTML\s*=',
                r'document\.write\(',
                r'eval\(',
                r'setTimeout\(["\'][^"\']*["\']',
                r'setInterval\(["\'][^"\']*["\']'
            ],
            'sql_injection_vulnerable': [
                r'SELECT.*\+.*["\']',
                r'INSERT.*\+.*["\']',
                r'UPDATE.*\+.*["\']',
                r'DELETE.*\+.*["\']'
            ],
            'csrf_protection': [
                r'csrf_token',
                r'_token',
                r'X-CSRF-TOKEN',
                r'csrfmiddlewaretoken'
            ],
            'authentication': [
                r'login',
                r'password',
                r'authenticate',
                r'session',
                r'token',
                r'jwt',
                r'oauth'
            ]
        }
    
    async def __aenter__(self):
        """بدء جلسة التحليل"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """إنهاء جلسة التحليل"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def analyze_website_code(self, site_map: Dict[str, Dict], base_url: str) -> Dict[str, Any]:
        """تحليل شامل لكود الموقع"""
        logging.info("بدء تحليل كود الموقع...")
        
        # تحليل كل صفحة
        for page_url, page_data in site_map.items():
            try:
                await self._analyze_single_page(page_url)
            except Exception as e:
                logging.error(f"خطأ في تحليل الصفحة {page_url}: {e}")
        
        # التحليل المتقدم
        await self._detect_architecture_patterns()
        await self._analyze_api_structure()
        await self._detect_database_schema()
        
        return self._generate_analysis_report()
    
    async def _analyze_single_page(self, page_url: str):
        """تحليل صفحة واحدة"""
        if not self.session:
            return
        
        try:
            async with self.session.get(page_url) as response:
                if response.status != 200:
                    return
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # تحليل HTML
                if self.config.analyze_html_structure:
                    await self._analyze_html_structure(soup, page_url)
                
                # تحليل JavaScript
                if self.config.analyze_javascript:
                    await self._analyze_javascript_code(soup, page_url)
                
                # تحليل CSS
                if self.config.analyze_css:
                    await self._analyze_css_code(soup, page_url)
                
                # كشف الإطارات
                if self.config.detect_frameworks:
                    await self._detect_frameworks(html_content, page_url)
                
                # تحليل الأمان
                if self.config.analyze_security_patterns:
                    await self._analyze_security(html_content, page_url)
                
        except Exception as e:
            logging.error(f"خطأ في تحليل {page_url}: {e}")
    
    async def _analyze_html_structure(self, soup: BeautifulSoup, page_url: str):
        """تحليل بنية HTML"""
        page_id = hashlib.md5(page_url.encode()).hexdigest()[:8]
        
        structure_analysis = {
            'semantic_elements': {
                'header': len(soup.find_all('header')),
                'nav': len(soup.find_all('nav')),
                'main': len(soup.find_all('main')),
                'section': len(soup.find_all('section')),
                'article': len(soup.find_all('article')),
                'aside': len(soup.find_all('aside')),
                'footer': len(soup.find_all('footer'))
            },
            'forms': self._analyze_forms(soup),
            'interactive_elements': {
                'buttons': len(soup.find_all('button')),
                'inputs': len(soup.find_all('input')),
                'selects': len(soup.find_all('select')),
                'textareas': len(soup.find_all('textarea'))
            },
            'media_elements': {
                'images': len(soup.find_all('img')),
                'videos': len(soup.find_all('video')),
                'audios': len(soup.find_all('audio')),
                'iframes': len(soup.find_all('iframe'))
            },
            'accessibility': self._analyze_accessibility(soup),
            'seo_elements': self._analyze_seo_elements(soup)
        }
        
        self.analysis_results['html_structure'][page_id] = structure_analysis
    
    async def _analyze_javascript_code(self, soup: BeautifulSoup, page_url: str):
        """تحليل كود JavaScript"""
        js_analysis = {
            'inline_scripts': [],
            'external_scripts': [],
            'functions_found': [],
            'variables_found': [],
            'event_handlers': [],
            'ajax_calls': [],
            'dom_manipulations': [],
            'async_patterns': []
        }
        
        # السكريبت الداخلي
        for script in soup.find_all('script'):
            if isinstance(script, Tag) and script.string:
                script_content = script.string
                
                # استخراج الوظائف
                functions = self._extract_js_functions(script_content)
                js_analysis['functions_found'].extend(functions)
                
                # استخراج المتغيرات
                variables = self._extract_js_variables(script_content)
                js_analysis['variables_found'].extend(variables)
                
                # كشف AJAX calls
                ajax_calls = self._detect_ajax_calls(script_content)
                js_analysis['ajax_calls'].extend(ajax_calls)
                
                # كشف DOM manipulations
                dom_ops = self._detect_dom_operations(script_content)
                js_analysis['dom_manipulations'].extend(dom_ops)
                
                js_analysis['inline_scripts'].append({
                    'content_length': len(script_content),
                    'line_count': len(script_content.split('\n')),
                    'has_functions': len(functions) > 0,
                    'has_ajax': len(ajax_calls) > 0
                })
        
        # السكريبت الخارجي
        for script in soup.find_all('script', src=True):
            if isinstance(script, Tag):
                src = script.get('src', '')
                js_analysis['external_scripts'].append({
                    'src': src,
                    'is_external': not src.startswith('/') and '://' in src,
                    'defer': script.has_attr('defer'),
                    'async': script.has_attr('async')
                })
        
        # معالجات الأحداث
        for element in soup.find_all():
            if isinstance(element, Tag) and element.attrs:
                for attr in element.attrs:
                    if attr.startswith('on'):
                        js_analysis['event_handlers'].append({
                            'element': element.name,
                            'event': attr,
                            'handler': element.get(attr, '')[:100]  # أول 100 حرف
                        })
        
        page_id = hashlib.md5(page_url.encode()).hexdigest()[:8]
        self.analysis_results['javascript_analysis'][page_id] = js_analysis
    
    async def _analyze_css_code(self, soup: BeautifulSoup, page_url: str):
        """تحليل كود CSS"""
        css_analysis = {
            'inline_styles': [],
            'external_stylesheets': [],
            'style_tags': [],
            'css_variables': [],
            'media_queries': [],
            'animations': [],
            'grid_flexbox_usage': []
        }
        
        # الأنماط الخارجية
        for link in soup.find_all('link', rel='stylesheet'):
            if isinstance(link, Tag):
                css_analysis['external_stylesheets'].append({
                    'href': link.get('href', ''),
                    'media': link.get('media', 'all')
                })
        
        # علامات النمط
        for style in soup.find_all('style'):
            if isinstance(style, Tag) and style.string:
                style_content = style.string
                css_analysis['style_tags'].append({
                    'content_length': len(style_content),
                    'has_media_queries': '@media' in style_content,
                    'has_animations': '@keyframes' in style_content or 'animation:' in style_content,
                    'has_grid': 'display: grid' in style_content or 'grid-template' in style_content,
                    'has_flexbox': 'display: flex' in style_content or 'flex-direction' in style_content
                })
                
                # استخراج متغيرات CSS
                css_vars = re.findall(r'--[\w-]+:', style_content)
                css_analysis['css_variables'].extend(css_vars)
        
        # الأنماط المباشرة
        inline_count = 0
        for element in soup.find_all(style=True):
            inline_count += 1
        
        css_analysis['inline_styles'] = [{'count': inline_count}]
        
        page_id = hashlib.md5(page_url.encode()).hexdigest()[:8]
        self.analysis_results['css_analysis'][page_id] = css_analysis
    
    def _extract_js_functions(self, js_content: str) -> List[Dict[str, Any]]:
        """استخراج الوظائف من JavaScript"""
        functions = []
        
        # الوظائف العادية
        function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*{'
        matches = re.finditer(function_pattern, js_content)
        for match in matches:
            functions.append({
                'name': match.group(1),
                'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                'type': 'function_declaration'
            })
        
        # Arrow functions
        arrow_pattern = r'(\w+)\s*=\s*\(([^)]*)\)\s*=>'
        matches = re.finditer(arrow_pattern, js_content)
        for match in matches:
            functions.append({
                'name': match.group(1),
                'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                'type': 'arrow_function'
            })
        
        return functions
    
    def _extract_js_variables(self, js_content: str) -> List[Dict[str, Any]]:
        """استخراج المتغيرات من JavaScript"""
        variables = []
        
        # var, let, const
        var_patterns = [
            r'var\s+(\w+)',
            r'let\s+(\w+)',
            r'const\s+(\w+)'
        ]
        
        for pattern in var_patterns:
            matches = re.finditer(pattern, js_content)
            for match in matches:
                variables.append({
                    'name': match.group(1),
                    'type': pattern.split('\\')[0]
                })
        
        return variables
    
    def _detect_ajax_calls(self, js_content: str) -> List[Dict[str, Any]]:
        """كشف استدعاءات AJAX"""
        ajax_calls = []
        
        patterns = [
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'\.ajax\s*\(\s*{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest\(\)',
            r'axios\.\w+\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_content)
            for match in matches:
                ajax_calls.append({
                    'pattern': pattern,
                    'url': match.group(1) if match.groups() else None,
                    'method': self._extract_http_method(match.group(0))
                })
        
        return ajax_calls
    
    def _detect_dom_operations(self, js_content: str) -> List[str]:
        """كشف عمليات DOM"""
        dom_operations = []
        
        patterns = [
            r'document\.getElementById',
            r'document\.querySelector',
            r'document\.createElement',
            r'\.appendChild',
            r'\.removeChild',
            r'\.innerHTML',
            r'\.textContent',
            r'\.addEventListener'
        ]
        
        for pattern in patterns:
            if re.search(pattern, js_content):
                dom_operations.append(pattern)
        
        return dom_operations
    
    def _extract_http_method(self, ajax_code: str) -> str:
        """استخراج HTTP method"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        for method in methods:
            if method.lower() in ajax_code.lower():
                return method
        return 'GET'  # افتراضي
    
    async def _detect_frameworks(self, html_content: str, page_url: str):
        """كشف الإطارات المستخدمة"""
        detected_frameworks = []
        
        for framework, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    detected_frameworks.append({
                        'framework': framework,
                        'pattern_matched': pattern,
                        'page_url': page_url
                    })
                    break
        
        self.analysis_results['frameworks_detected'].extend(detected_frameworks)
    
    async def _analyze_security(self, html_content: str, page_url: str):
        """تحليل الأمان"""
        security_issues = {
            'vulnerabilities': [],
            'security_features': [],
            'recommendations': []
        }
        
        # فحص الثغرات
        for vuln_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    if 'vulnerable' in vuln_type:
                        security_issues['vulnerabilities'].append({
                            'type': vuln_type,
                            'pattern': pattern,
                            'severity': 'high' if 'xss' in vuln_type or 'sql' in vuln_type else 'medium'
                        })
                    else:
                        security_issues['security_features'].append({
                            'type': vuln_type,
                            'pattern': pattern
                        })
        
        page_id = hashlib.md5(page_url.encode()).hexdigest()[:8]
        self.analysis_results['security_analysis'][page_id] = security_issues
    
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """تحليل النماذج"""
        forms_analysis = []
        
        for form in soup.find_all('form'):
            if isinstance(form, Tag):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get').lower(),
                    'inputs': [],
                    'has_file_upload': False,
                    'has_csrf_protection': False
                }
                
                # تحليل الحقول
                for input_tag in form.find_all('input'):
                    if isinstance(input_tag, Tag):
                        input_type = input_tag.get('type', 'text')
                        form_data['inputs'].append({
                            'type': input_type,
                            'name': input_tag.get('name', ''),
                            'required': input_tag.has_attr('required')
                        })
                        
                        if input_type == 'file':
                            form_data['has_file_upload'] = True
                        
                        if input_tag.get('name', '').lower() in ['_token', 'csrf_token', 'csrfmiddlewaretoken']:
                            form_data['has_csrf_protection'] = True
                
                forms_analysis.append(form_data)
        
        return forms_analysis
    
    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل إمكانية الوصول"""
        accessibility = {
            'images_with_alt': 0,
            'images_without_alt': 0,
            'headings_structure': [],
            'aria_labels': 0,
            'skip_links': 0
        }
        
        # فحص الصور
        for img in soup.find_all('img'):
            if isinstance(img, Tag):
                if img.get('alt'):
                    accessibility['images_with_alt'] += 1
                else:
                    accessibility['images_without_alt'] += 1
        
        # فحص العناوين
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            accessibility['headings_structure'].append({
                f'h{i}': len(headings)
            })
        
        # فحص ARIA
        aria_elements = soup.find_all(attrs={'aria-label': True})
        accessibility['aria_labels'] = len(aria_elements)
        
        # روابط التخطي
        skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
        accessibility['skip_links'] = len(skip_links)
        
        return accessibility
    
    def _analyze_seo_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل عناصر SEO"""
        seo = {
            'title_length': 0,
            'meta_description_length': 0,
            'h1_count': len(soup.find_all('h1')),
            'canonical_url': '',
            'og_tags_count': 0,
            'structured_data': False
        }
        
        # العنوان
        title = soup.find('title')
        if title:
            seo['title_length'] = len(title.get_text(strip=True))
        
        # الوصف
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and isinstance(meta_desc, Tag):
            seo['meta_description_length'] = len(meta_desc.get('content', ''))
        
        # Canonical
        canonical = soup.find('link', rel='canonical')
        if canonical and isinstance(canonical, Tag):
            seo['canonical_url'] = canonical.get('href', '')
        
        # Open Graph
        og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
        seo['og_tags_count'] = len(og_tags)
        
        # Structured Data
        structured_data = soup.find_all('script', type='application/ld+json')
        seo['structured_data'] = len(structured_data) > 0
        
        return seo
    
    async def _detect_architecture_patterns(self):
        """كشف أنماط البنية المعمارية"""
        patterns = []
        
        # تحليل الإطارات المكتشفة
        frameworks = [f['framework'] for f in self.analysis_results['frameworks_detected']]
        
        if 'react' in frameworks:
            patterns.append('Single Page Application (SPA)')
        if 'vue' in frameworks:
            patterns.append('Progressive Web App (PWA)')
        if 'bootstrap' in frameworks:
            patterns.append('Responsive Design')
        
        # تحليل JavaScript patterns
        for page_analysis in self.analysis_results['javascript_analysis'].values():
            if page_analysis['ajax_calls']:
                patterns.append('AJAX-driven Interface')
            if any('async' in script for script in page_analysis['external_scripts']):
                patterns.append('Asynchronous Loading')
        
        self.analysis_results['architecture_patterns'] = list(set(patterns))
    
    async def _analyze_api_structure(self):
        """تحليل بنية API"""
        api_endpoints = []
        
        for page_analysis in self.analysis_results['javascript_analysis'].values():
            for ajax_call in page_analysis['ajax_calls']:
                if ajax_call['url']:
                    api_endpoints.append({
                        'url': ajax_call['url'],
                        'method': ajax_call['method'],
                        'type': self._classify_api_endpoint(ajax_call['url'])
                    })
        
        self.analysis_results['api_endpoints'] = api_endpoints
    
    def _classify_api_endpoint(self, url: str) -> str:
        """تصنيف نوع API endpoint"""
        url_lower = url.lower()
        
        if '/api/v' in url_lower:
            return 'versioned_api'
        elif '/rest/' in url_lower:
            return 'rest_api'
        elif '/graphql' in url_lower:
            return 'graphql_api'
        elif '/auth/' in url_lower or '/login' in url_lower:
            return 'authentication_api'
        elif '/upload' in url_lower or '/file' in url_lower:
            return 'file_api'
        elif '/search' in url_lower:
            return 'search_api'
        elif '/admin' in url_lower:
            return 'admin_api'
        else:
            return 'general_api'

    async def _detect_frameworks(self, html_content: str, js_content: str = '') -> List[Dict[str, Any]]:
        """كشف الأطر المستخدمة"""
        frameworks = []
        
        # فحص أطر JavaScript
        js_frameworks = {
            'React': ['react', 'reactdom', 'jsx'],
            'Vue.js': ['vue.js', 'vue.min.js', 'vue'],
            'Angular': ['angular', '@angular', 'ng-'],
            'jQuery': ['jquery', '$.', 'jQuery'],
            'Alpine.js': ['alpine.js', 'x-data'],
            'Svelte': ['svelte', '_svelte']
        }
        
        content_to_check = html_content + js_content
        
        for framework, indicators in js_frameworks.items():
            if any(indicator in content_to_check.lower() for indicator in indicators):
                frameworks.append({
                    'name': framework,
                    'type': 'javascript_framework',
                    'confidence': self._calculate_framework_confidence(content_to_check, indicators)
                })
        
        # فحص أطر CSS
        css_frameworks = {
            'Bootstrap': ['bootstrap', 'btn btn-', 'container-fluid'],
            'Tailwind CSS': ['tailwind', 'tw-', 'text-'],
            'Bulma': ['bulma', 'button is-', 'column'],
            'Foundation': ['foundation', 'grid-x', 'cell'],
            'Materialize': ['materialize', 'material-icons'],
            'Semantic UI': ['semantic', 'ui button']
        }
        
        for framework, indicators in css_frameworks.items():
            if any(indicator in content_to_check.lower() for indicator in indicators):
                frameworks.append({
                    'name': framework,
                    'type': 'css_framework',
                    'confidence': self._calculate_framework_confidence(content_to_check, indicators)
                })
        
        return frameworks

    def _calculate_framework_confidence(self, content: str, indicators: List[str]) -> float:
        """حساب درجة الثقة في وجود الإطار"""
        matches = sum(1 for indicator in indicators if indicator in content.lower())
        return min(matches / len(indicators), 1.0)

    async def _extract_custom_functions(self, js_content: str) -> List[Dict[str, Any]]:
        """استخراج الدوال المخصصة"""
        functions = []
        
        # استخراج دوال JavaScript العادية
        function_pattern = re.compile(
            r'function\s+(\w+)\s*\(([^)]*)\)\s*{([^}]*)}',
            re.MULTILINE | re.DOTALL
        )
        
        for match in function_pattern.finditer(js_content):
            function_name = match.group(1)
            parameters = match.group(2).strip()
            body = match.group(3).strip()
            
            functions.append({
                'name': function_name,
                'type': 'function',
                'parameters': [p.strip() for p in parameters.split(',') if p.strip()],
                'body_length': len(body),
                'complexity': self._calculate_function_complexity(body)
            })
        
        # استخراج Arrow Functions
        arrow_pattern = re.compile(
            r'(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{([^}]*)}',
            re.MULTILINE | re.DOTALL
        )
        
        for match in arrow_pattern.finditer(js_content):
            function_name = match.group(1)
            parameters = match.group(2).strip()
            body = match.group(3).strip()
            
            functions.append({
                'name': function_name,
                'type': 'arrow_function',
                'parameters': [p.strip() for p in parameters.split(',') if p.strip()],
                'body_length': len(body),
                'complexity': self._calculate_function_complexity(body)
            })
        
        return functions

    def _calculate_function_complexity(self, function_body: str) -> str:
        """حساب تعقيد الدالة"""
        complexity_indicators = [
            'if', 'else', 'for', 'while', 'switch', 'case',
            'try', 'catch', 'throw', 'async', 'await'
        ]
        
        complexity_count = sum(
            function_body.lower().count(indicator) 
            for indicator in complexity_indicators
        )
        
        if complexity_count <= 2:
            return 'low'
        elif complexity_count <= 5:
            return 'medium'
        else:
            return 'high'

    async def _detect_design_patterns(self, js_content: str) -> List[str]:
        """كشف أنماط التصميم"""
        patterns = []
        
        # نمط Module
        if 'module.exports' in js_content or 'export' in js_content:
            patterns.append('Module Pattern')
        
        # نمط Observer
        if 'addEventListener' in js_content or 'on(' in js_content:
            patterns.append('Observer Pattern')
        
        # نمط Singleton
        if 'getInstance' in js_content or 'singleton' in js_content.lower():
            patterns.append('Singleton Pattern')
        
        # نمط Factory
        if 'create' in js_content and 'new' in js_content:
            patterns.append('Factory Pattern')
        
        # نمط MVC
        if any(term in js_content.lower() for term in ['controller', 'model', 'view']):
            patterns.append('MVC Pattern')
        
        # نمط Promise/Async
        if 'Promise' in js_content or 'async' in js_content:
            patterns.append('Promise/Async Pattern')
        
        return patterns

    async def _analyze_code_quality(self, js_content: str) -> Dict[str, Any]:
        """تحليل جودة الكود"""
        quality_metrics = {
            'code_style': {},
            'best_practices': {},
            'potential_issues': [],
            'quality_score': 0
        }
        
        # فحص نمط الكود
        quality_metrics['code_style'] = {
            'uses_semicolons': ';' in js_content,
            'uses_const_let': 'const' in js_content or 'let' in js_content,
            'uses_arrow_functions': '=>' in js_content,
            'uses_template_literals': '`' in js_content
        }
        
        # فحص الممارسات الجيدة
        quality_metrics['best_practices'] = {
            'error_handling': 'try' in js_content and 'catch' in js_content,
            'comments_present': '//' in js_content or '/*' in js_content,
            'function_documentation': '/**' in js_content,
            'strict_mode': "'use strict'" in js_content
        }
        
        # فحص المشاكل المحتملة
        potential_issues = []
        
        if 'eval(' in js_content:
            potential_issues.append('استخدام eval() غير آمن')
        
        if 'document.write' in js_content:
            potential_issues.append('استخدام document.write مهجور')
        
        if js_content.count('var') > js_content.count('let') + js_content.count('const'):
            potential_issues.append('استخدام var بدلاً من let/const')
        
        quality_metrics['potential_issues'] = potential_issues
        
        # حساب نقاط الجودة
        score = 0
        score += sum(quality_metrics['code_style'].values()) * 10
        score += sum(quality_metrics['best_practices'].values()) * 15
        score -= len(potential_issues) * 5
        
        quality_metrics['quality_score'] = max(0, min(100, score))
        
        return quality_metrics

    async def generate_analysis_report(self) -> Dict[str, Any]:
        """إنشاء تقرير شامل للتحليل"""
        report = {
            'summary': {
                'total_pages_analyzed': len(self.analysis_results.get('page_analysis', {})),
                'frameworks_detected': len(self.analysis_results.get('frameworks_detected', [])),
                'functions_found': len(self.analysis_results.get('custom_functions', [])),
                'api_endpoints': len(self.analysis_results.get('api_endpoints', [])),
                'design_patterns': len(self.analysis_results.get('design_patterns', []))
            },
            'detailed_analysis': self.analysis_results,
            'recommendations': await self._generate_recommendations(),
            'quality_assessment': await self._assess_overall_quality(),
            'replication_complexity': await self._assess_replication_complexity()
        }
        
        return report

    async def _generate_recommendations(self) -> List[Dict[str, str]]:
        """إنشاء توصيات التحسين"""
        recommendations = []
        
        # توصيات الأداء
        frameworks = self.analysis_results.get('frameworks_detected', [])
        if len(frameworks) > 3:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'recommendation': 'تقليل عدد الأطر المستخدمة',
                'description': 'استخدام عدد كبير من الأطر قد يؤثر على الأداء'
            })
        
        # توصيات الأمان
        custom_functions = self.analysis_results.get('custom_functions', [])
        high_complexity_functions = [f for f in custom_functions if f.get('complexity') == 'high']
        
        if high_complexity_functions:
            recommendations.append({
                'type': 'maintainability',
                'priority': 'medium',
                'recommendation': 'تبسيط الدوال المعقدة',
                'description': f'تم العثور على {len(high_complexity_functions)} دالة معقدة'
            })
        
        return recommendations

    async def _assess_overall_quality(self) -> Dict[str, Any]:
        """تقييم الجودة الإجمالية"""
        quality_scores = []
        
        for page_analysis in self.analysis_results.get('javascript_analysis', {}).values():
            if 'quality_metrics' in page_analysis:
                quality_scores.append(page_analysis['quality_metrics']['quality_score'])
        
        if quality_scores:
            average_quality = sum(quality_scores) / len(quality_scores)
        else:
            average_quality = 0
        
        quality_level = 'ممتاز' if average_quality >= 80 else 'جيد' if average_quality >= 60 else 'متوسط' if average_quality >= 40 else 'ضعيف'
        
        return {
            'overall_score': average_quality,
            'quality_level': quality_level,
            'pages_analyzed': len(quality_scores)
        }

    async def _assess_replication_complexity(self) -> Dict[str, Any]:
        """تقييم تعقيد النسخ"""
        complexity_factors = []
        complexity_score = 0
        
        # تحليل الأطر
        frameworks_count = len(self.analysis_results.get('frameworks_detected', []))
        if frameworks_count > 2:
            complexity_score += 3
            complexity_factors.append(f'استخدام {frameworks_count} أطر مختلفة')
        
        # تحليل الدوال المخصصة
        custom_functions = self.analysis_results.get('custom_functions', [])
        complex_functions = [f for f in custom_functions if f.get('complexity') in ['medium', 'high']]
        
        if len(complex_functions) > 5:
            complexity_score += 2
            complexity_factors.append(f'{len(complex_functions)} دالة معقدة')
        
        # تحليل APIs
        api_endpoints = self.analysis_results.get('api_endpoints', [])
        if len(api_endpoints) > 10:
            complexity_score += 2
            complexity_factors.append(f'{len(api_endpoints)} API endpoint')
        
        # تحليل أنماط التصميم
        design_patterns = self.analysis_results.get('design_patterns', [])
        if len(design_patterns) > 3:
            complexity_score += 1
            complexity_factors.append(f'{len(design_patterns)} نمط تصميم')
        
        # تصنيف التعقيد
        if complexity_score <= 2:
            complexity_level = 'بسيط'
            estimated_time = '1-2 أيام'
        elif complexity_score <= 5:
            complexity_level = 'متوسط'
            estimated_time = '3-5 أيام'
        elif complexity_score <= 8:
            complexity_level = 'معقد'
            estimated_time = '1-2 أسابيع'
        else:
            complexity_level = 'معقد جداً'
            estimated_time = '2-4 أسابيع'
        
        return {
            'complexity_score': complexity_score,
            'complexity_level': complexity_level,
            'complexity_factors': complexity_factors,
            'estimated_replication_time': estimated_time,
            'recommended_approach': self._get_replication_approach(complexity_level)
        }

    def _get_replication_approach(self, complexity_level: str) -> str:
        """الحصول على النهج الموصى به للنسخ"""
        approaches = {
            'بسيط': 'نسخ مباشر مع تعديلات طفيفة',
            'متوسط': 'نسخ مع إعادة بناء جزئية',
            'معقد': 'إعادة بناء كاملة مع الحفاظ على الوظائف',
            'معقد جداً': 'إعادة تصميم وبناء من الصفر'
        }
        
        return approaches.get(complexity_level, 'تحليل إضافي مطلوب') نوع endpoint"""
        url_lower = url.lower()
        
        if 'api' in url_lower:
            return 'REST API'
        elif 'graphql' in url_lower:
            return 'GraphQL'
        elif 'ajax' in url_lower:
            return 'AJAX Endpoint'
        elif any(word in url_lower for word in ['user', 'auth', 'login']):
            return 'Authentication'
        elif any(word in url_lower for word in ['data', 'search', 'query']):
            return 'Data Service'
        else:
            return 'Unknown'
    
    async def _detect_database_schema(self):
        """كشف مخطط قاعدة البيانات"""
        database_hints = []
        
        # تحليل أنماط قواعد البيانات في الكود
        for page_analysis in self.analysis_results['javascript_analysis'].values():
            for ajax_call in page_analysis['ajax_calls']:
                if ajax_call['url']:
                    # فحص عمليات CRUD
                    method = ajax_call['method']
                    url = ajax_call['url'].lower()
                    
                    if method == 'GET' and any(word in url for word in ['list', 'get', 'fetch']):
                        database_hints.append('Read Operations')
                    elif method == 'POST' and any(word in url for word in ['create', 'add', 'new']):
                        database_hints.append('Create Operations')
                    elif method in ['PUT', 'PATCH'] and any(word in url for word in ['update', 'edit']):
                        database_hints.append('Update Operations')
                    elif method == 'DELETE' and any(word in url for word in ['delete', 'remove']):
                        database_hints.append('Delete Operations')
        
        self.analysis_results['database_patterns'] = list(set(database_hints))
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """إنشاء تقرير التحليل النهائي"""
        # إحصائيات إجمالية
        total_pages = len(self.analysis_results['javascript_analysis'])
        total_functions = sum(len(page['functions_found']) for page in self.analysis_results['javascript_analysis'].values())
        total_ajax_calls = sum(len(page['ajax_calls']) for page in self.analysis_results['javascript_analysis'].values())
        
        return {
            'analysis_summary': {
                'total_pages_analyzed': total_pages,
                'frameworks_detected': len(set(f['framework'] for f in self.analysis_results['frameworks_detected'])),
                'total_functions_found': total_functions,
                'total_ajax_calls': total_ajax_calls,
                'api_endpoints_discovered': len(self.analysis_results['api_endpoints']),
                'security_issues_found': sum(len(page.get('vulnerabilities', [])) for page in self.analysis_results['security_analysis'].values())
            },
            
            'detailed_analysis': self.analysis_results,
            
            'recommendations': self._generate_recommendations(),
            
            'technology_stack': {
                'frontend_frameworks': list(set(f['framework'] for f in self.analysis_results['frameworks_detected'])),
                'architecture_patterns': self.analysis_results['architecture_patterns'],
                'database_patterns': self.analysis_results['database_patterns']
            }
        }
    
    def _generate_recommendations(self) -> List[str]:
        """إنشاء توصيات التحسين"""
        recommendations = []
        
        # فحص الأمان
        security_issues = sum(len(page.get('vulnerabilities', [])) for page in self.analysis_results['security_analysis'].values())
        if security_issues > 0:
            recommendations.append("تحسين الأمان: تم العثور على ثغرات أمنية محتملة")
        
        # فحص الأداء
        for page_analysis in self.analysis_results['javascript_analysis'].values():
            if len(page_analysis['external_scripts']) > 10:
                recommendations.append("تحسين الأداء: تقليل عدد ملفات JavaScript الخارجية")
                break
        
        # فحص إمكانية الوصول
        for page_analysis in self.analysis_results['html_structure'].values():
            accessibility = page_analysis.get('accessibility', {})
            if accessibility.get('images_without_alt', 0) > 0:
                recommendations.append("تحسين إمكانية الوصول: إضافة نص بديل للصور")
                break
        
        return recommendations