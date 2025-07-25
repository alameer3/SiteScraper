"""
مستخرج تقني متقدم - استخراج شامل للتقنيات والأكواد
Advanced Technical Extractor - Comprehensive extraction of technologies and code
"""

import re
import json
import hashlib
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup
import requests

class TechnicalExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # قواعد بيانات شاملة للتقنيات
        self.framework_signatures = {
            'React': [
                r'React\.createElement',
                r'react-dom',
                r'reactjs',
                r'jsx',
                r'data-reactroot',
                r'__REACT_DEVTOOLS_GLOBAL_HOOK__'
            ],
            'Vue.js': [
                r'Vue\.js',
                r'vue@',
                r'v-if',
                r'v-for',
                r'v-model',
                r'__VUE__'
            ],
            'Angular': [
                r'@angular',
                r'ng-app',
                r'ng-controller',
                r'ng-repeat',
                r'angular\.module'
            ],
            'jQuery': [
                r'jquery',
                r'\$\(',
                r'jQuery\(',
                r'jquery\.min\.js'
            ],
            'Bootstrap': [
                r'bootstrap',
                r'btn-primary',
                r'container-fluid',
                r'row',
                r'col-md'
            ],
            'Tailwind': [
                r'tailwindcss',
                r'bg-blue-500',
                r'text-center',
                r'flex items-center'
            ],
            'Material-UI': [
                r'@mui',
                r'material-ui',
                r'MuiButton',
                r'makeStyles'
            ],
            'Next.js': [
                r'next\.js',
                r'_next',
                r'__NEXT_DATA__',
                r'next/router'
            ],
            'Nuxt.js': [
                r'nuxt\.js',
                r'_nuxt',
                r'__NUXT__'
            ],
            'Gatsby': [
                r'gatsby',
                r'___gatsby',
                r'gatsby-browser'
            ]
        }
        
        self.backend_signatures = {
            'WordPress': [
                r'wp-content',
                r'wp-includes',
                r'wp_enqueue_script',
                r'/wp-json/',
                r'WordPress'
            ],
            'Drupal': [
                r'drupal',
                r'sites/default',
                r'modules/',
                r'Drupal\.settings'
            ],
            'Joomla': [
                r'joomla',
                r'/components/',
                r'/templates/',
                r'JFactory'
            ],
            'Magento': [
                r'magento',
                r'skin/frontend',
                r'Mage\.',
                r'/checkout/cart'
            ],
            'Shopify': [
                r'shopify',
                r'cdn\.shopify\.com',
                r'Shopify\.theme',
                r'liquid'
            ],
            'WooCommerce': [
                r'woocommerce',
                r'wc-',
                r'add-to-cart',
                r'shop/'
            ]
        }
        
        self.analytics_signatures = {
            'Google Analytics': [
                r'google-analytics\.com',
                r'gtag\(',
                r'ga\(',
                r'GoogleAnalyticsObject'
            ],
            'Google Tag Manager': [
                r'googletagmanager\.com',
                r'GTM-',
                r'dataLayer'
            ],
            'Facebook Pixel': [
                r'facebook\.net/tr',
                r'fbq\(',
                r'FB_PIXEL_ID'
            ],
            'Hotjar': [
                r'hotjar\.com',
                r'hj\(',
                r'_hjSettings'
            ]
        }
    
    def extract_complete_technology_stack(self, crawl_data):
        """استخراج المكدس التقني الكامل"""
        tech_stack = {
            'frontend_frameworks': {},
            'backend_technologies': {},
            'css_frameworks': {},
            'javascript_libraries': {},
            'analytics_tools': {},
            'cdn_services': {},
            'hosting_details': {},
            'security_headers': {},
            'performance_tools': {},
            'third_party_services': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                page_content = response.text
                headers = response.headers
                
                # تحليل Frontend Frameworks
                tech_stack['frontend_frameworks'].update(
                    self._detect_frameworks(page_content, self.framework_signatures)
                )
                
                # تحليل Backend Technologies
                tech_stack['backend_technologies'].update(
                    self._detect_frameworks(page_content, self.backend_signatures)
                )
                
                # تحليل أدوات التحليلات
                tech_stack['analytics_tools'].update(
                    self._detect_frameworks(page_content, self.analytics_signatures)
                )
                
                # تحليل خدمات CDN
                tech_stack['cdn_services'].update(
                    self._detect_cdn_services(soup)
                )
                
                # تحليل تفاصيل الاستضافة
                tech_stack['hosting_details'].update(
                    self._analyze_hosting_details(headers)
                )
                
                # تحليل رؤوس الأمان
                tech_stack['security_headers'].update(
                    self._analyze_security_headers(headers)
                )
                
                # تحليل أدوات الأداء
                performance_tools = self._detect_performance_tools(soup, page_content)
                tech_stack['performance_tools'][url] = performance_tools
                
                # تحليل الخدمات الخارجية
                third_party = self._detect_third_party_services(soup, page_content)
                tech_stack['third_party_services'][url] = third_party
                
            except Exception as e:
                logging.error(f"خطأ في تحليل التقنيات لـ {url}: {e}")
        
        return tech_stack
    
    def extract_complete_code_structure(self, crawl_data):
        """استخراج بنية الكود الكاملة"""
        code_structure = {
            'html_patterns': {},
            'css_architecture': {},
            'javascript_structure': {},
            'component_patterns': {},
            'design_patterns': {},
            'code_quality_metrics': {},
            'reusable_components': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # تحليل أنماط HTML
                code_structure['html_patterns'][url] = self._analyze_html_patterns(soup)
                
                # تحليل معمارية CSS
                css_files = page_data.get('assets', {}).get('css', [])
                for css_file in css_files:
                    css_content = self._fetch_css_content(css_file.get('href'))
                    if css_content:
                        code_structure['css_architecture'][css_file.get('href')] = \
                            self._analyze_css_architecture(css_content)
                
                # تحليل بنية JavaScript
                js_files = page_data.get('assets', {}).get('javascript', [])
                for js_file in js_files:
                    js_content = self._fetch_js_content(js_file.get('src'))
                    if js_content:
                        code_structure['javascript_structure'][js_file.get('src')] = \
                            self._analyze_js_structure(js_content)
                
                # تحليل أنماط المكونات
                code_structure['component_patterns'][url] = self._analyze_component_patterns(soup)
                
                # تحليل أنماط التصميم
                code_structure['design_patterns'][url] = self._analyze_design_patterns(soup)
                
            except Exception as e:
                logging.error(f"خطأ في تحليل بنية الكود لـ {url}: {e}")
        
        return code_structure
    
    def extract_assets_complete_details(self, crawl_data):
        """استخراج تفاصيل كاملة للأصول"""
        assets_details = {
            'images_analysis': {},
            'fonts_details': {},
            'icons_analysis': {},
            'videos_analysis': {},
            'performance_metrics': {},
            'loading_optimization': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                # تحليل الصور
                images = page_data.get('assets', {}).get('images', [])
                assets_details['images_analysis'][url] = self._analyze_images_details(images)
                
                # تحليل الخطوط
                fonts = page_data.get('assets', {}).get('fonts', [])
                assets_details['fonts_details'][url] = self._analyze_fonts_details(fonts)
                
                # تحليل الأيقونات
                icons = page_data.get('assets', {}).get('icons', [])
                assets_details['icons_analysis'][url] = self._analyze_icons_details(icons)
                
                # تحليل الفيديوهات
                videos = page_data.get('assets', {}).get('videos', [])
                assets_details['videos_analysis'][url] = self._analyze_videos_details(videos)
                
            except Exception as e:
                logging.error(f"خطأ في تحليل الأصول لـ {url}: {e}")
        
        return assets_details
    
    def _analyze_images_details(self, images):
        """تحليل تفاصيل الصور"""
        return {
            'total_count': len(images),
            'formats': list(set([img.get('format', 'unknown') for img in images])),
            'average_size': sum([img.get('size', 0) for img in images]) / len(images) if images else 0,
            'lazy_loading': sum([1 for img in images if img.get('loading') == 'lazy'])
        }
    
    def _analyze_fonts_details(self, fonts):
        """تحليل تفاصيل الخطوط"""
        return {
            'total_count': len(fonts),
            'families': list(set([font.get('family', 'unknown') for font in fonts])),
            'formats': list(set([font.get('format', 'unknown') for font in fonts]))
        }
    
    def _analyze_icons_details(self, icons):
        """تحليل تفاصيل الأيقونات"""
        return {
            'total_count': len(icons),
            'types': list(set([icon.get('type', 'unknown') for icon in icons]))
        }
    
    def _analyze_videos_details(self, videos):
        """تحليل تفاصيل الفيديوهات"""
        return {
            'total_count': len(videos),
            'formats': list(set([video.get('format', 'unknown') for video in videos]))
        }
    
    def generate_code_templates(self, analysis_data):
        """إنشاء قوالب كود للتطبيق"""
        templates = {
            'html_structure': self._generate_html_template(analysis_data),
            'css_framework': self._generate_css_framework(analysis_data),
            'javascript_components': self._generate_js_components(analysis_data),
            'responsive_breakpoints': self._generate_responsive_css(analysis_data),
            'component_library': self._generate_component_library(analysis_data)
        }
        
        return templates
    
    # Helper Methods
    def _detect_frameworks(self, content, signatures):
        """كشف الإطارات والمكتبات"""
        detected = {}
        for framework, patterns in signatures.items():
            confidence = 0
            evidence = []
            
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    confidence += matches
                    evidence.append(f"Found {matches} matches for '{pattern}'")
            
            if confidence > 0:
                detected[framework] = {
                    'confidence': min(confidence, 100),
                    'evidence': evidence
                }
        
        return detected
    
    def _detect_cdn_services(self, soup):
        """كشف خدمات CDN"""
        cdn_services = {}
        
        # البحث في ملفات CSS و JS
        for link in soup.find_all(['link', 'script'], src=True) + soup.find_all(['link'], href=True):
            url = link.get('src') or link.get('href', '')
            domain = urlparse(url).netloc
            
            cdn_patterns = {
                'Cloudflare': ['cdnjs.cloudflare.com', 'cloudflare.com'],
                'JSDelivr': ['cdn.jsdelivr.net'],
                'unpkg': ['unpkg.com'],
                'Google Fonts': ['fonts.googleapis.com', 'fonts.gstatic.com'],
                'Bootstrap CDN': ['stackpath.bootstrapcdn.com', 'maxcdn.bootstrapcdn.com'],
                'jQuery CDN': ['code.jquery.com', 'ajax.googleapis.com']
            }
            
            for cdn_name, patterns in cdn_patterns.items():
                if any(pattern in domain for pattern in patterns):
                    if cdn_name not in cdn_services:
                        cdn_services[cdn_name] = []
                    cdn_services[cdn_name].append(url)
        
        return cdn_services
    
    def _analyze_hosting_details(self, headers):
        """تحليل تفاصيل الاستضافة"""
        hosting = {}
        
        # خادم الويب
        server = headers.get('Server', '')
        if server:
            hosting['web_server'] = server
            
            # تحديد نوع الخادم
            if 'nginx' in server.lower():
                hosting['server_type'] = 'Nginx'
            elif 'apache' in server.lower():
                hosting['server_type'] = 'Apache'
            elif 'cloudflare' in server.lower():
                hosting['cdn'] = 'Cloudflare'
        
        # تقنية الخادم
        powered_by = headers.get('X-Powered-By', '')
        if powered_by:
            hosting['powered_by'] = powered_by
        
        # معلومات إضافية
        hosting['headers_analysis'] = {
            'cache_control': headers.get('Cache-Control', ''),
            'content_encoding': headers.get('Content-Encoding', ''),
            'content_type': headers.get('Content-Type', '')
        }
        
        return hosting
    
    def _analyze_security_headers(self, headers):
        """تحليل رؤوس الأمان"""
        security = {}
        
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        for header in security_headers:
            value = headers.get(header)
            if value:
                security[header] = value
        
        return security
    
    def _analyze_html_patterns(self, soup):
        """تحليل أنماط HTML"""
        patterns = {
            'semantic_elements': [],
            'custom_attributes': [],
            'microdata': [],
            'aria_labels': [],
            'data_attributes': []
        }
        
        # العناصر الدلالية
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        for tag in semantic_tags:
            elements = soup.find_all(tag)
            if elements:
                patterns['semantic_elements'].append({
                    'tag': tag,
                    'count': len(elements)
                })
        
        # خصائص ARIA
        aria_elements = soup.find_all(attrs={'aria-label': True})
        patterns['aria_labels'].append(len(aria_elements))
        
        # خصائص البيانات
        data_elements = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        patterns['data_attributes'].append(len(data_elements))
        
        return patterns
    
    def _fetch_css_content(self, css_url):
        """جلب محتوى CSS"""
        try:
            response = self.session.get(css_url, timeout=10)
            return response.text
        except Exception:
            return None
    
    def _fetch_js_content(self, js_url):
        """جلب محتوى JavaScript"""
        try:
            response = self.session.get(js_url, timeout=10)
            return response.text
        except Exception:
            return None
    
    def _analyze_css_architecture(self, css_content):
        """تحليل معمارية CSS"""
        architecture = {
            'variables': {},
            'mixins': [],
            'functions': [],
            'classes_count': 0,
            'ids_count': 0,
            'media_queries': [],
            'animations': []
        }
        
        # متغيرات CSS
        var_pattern = r'--([a-zA-Z0-9-_]+):\s*([^;]+);'
        variables = re.findall(var_pattern, css_content)
        for var_name, var_value in variables:
            architecture['variables'][var_name] = var_value.strip()
        
        # عدد الكلاسات
        class_pattern = r'\.([a-zA-Z0-9-_]+)'
        architecture['classes_count'] = len(re.findall(class_pattern, css_content))
        
        # عدد المعرفات
        id_pattern = r'#([a-zA-Z0-9-_]+)'
        architecture['ids_count'] = len(re.findall(id_pattern, css_content))
        
        # Media Queries
        media_pattern = r'@media\s+([^{]+)'
        architecture['media_queries'] = re.findall(media_pattern, css_content)
        
        # الرسوم المتحركة
        animation_pattern = r'@keyframes\s+([a-zA-Z0-9-_]+)'
        architecture['animations'] = re.findall(animation_pattern, css_content)
        
        return architecture
    
    def _analyze_js_structure(self, js_content):
        """تحليل بنية JavaScript"""
        structure = {
            'functions_count': 0,
            'classes_count': 0,
            'variables_count': 0,
            'event_listeners': [],
            'ajax_calls': [],
            'frameworks_used': []
        }
        
        # عدد الوظائف
        function_pattern = r'function\s+([a-zA-Z0-9_$]+)'
        structure['functions_count'] = len(re.findall(function_pattern, js_content))
        
        # عدد الكلاسات
        class_pattern = r'class\s+([a-zA-Z0-9_$]+)'
        structure['classes_count'] = len(re.findall(class_pattern, js_content))
        
        # متغيرات
        var_pattern = r'(?:var|let|const)\s+([a-zA-Z0-9_$]+)'
        structure['variables_count'] = len(re.findall(var_pattern, js_content))
        
        # Event Listeners
        event_pattern = r'addEventListener\s*\(\s*[\'"]([^"\']+)[\'"]'
        structure['event_listeners'] = re.findall(event_pattern, js_content)
        
        # AJAX Calls
        ajax_patterns = [r'fetch\s*\(', r'XMLHttpRequest', r'axios\.', r'\$\.ajax']
        for pattern in ajax_patterns:
            if re.search(pattern, js_content):
                structure['ajax_calls'].append(pattern)
        
        return structure
    
    def _generate_html_template(self, analysis_data):
        """إنشاء قالب HTML"""
        template = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    
    <!-- CSS Files -->
    {{css_links}}
    
    <!-- Custom Styles -->
    <style>
    {{custom_styles}}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="{{header_classes}}">
        {{header_content}}
    </header>
    
    <!-- Navigation -->
    <nav class="{{nav_classes}}">
        {{nav_content}}
    </nav>
    
    <!-- Main Content -->
    <main class="{{main_classes}}">
        {{main_content}}
    </main>
    
    <!-- Footer -->
    <footer class="{{footer_classes}}">
        {{footer_content}}
    </footer>
    
    <!-- JavaScript Files -->
    {{js_scripts}}
    
    <!-- Custom Scripts -->
    <script>
    {{custom_scripts}}
    </script>
</body>
</html>"""
        
        return template
    
    def _generate_css_framework(self, analysis_data):
        """إنشاء إطار عمل CSS"""
        css_framework = """
/* CSS Variables - متغيرات CSS */
:root {
    {{css_variables}}
}

/* Base Styles - الأنماط الأساسية */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: {{primary_font}};
    line-height: 1.6;
    color: {{text_color}};
    background-color: {{bg_color}};
}

/* Layout - التخطيط */
.container {
    max-width: {{container_width}};
    margin: 0 auto;
    padding: 0 1rem;
}

/* Grid System - نظام الشبكة */
.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -0.5rem;
}

.col {
    flex: 1;
    padding: 0 0.5rem;
}

/* Components - المكونات */
{{component_styles}}

/* Responsive Design - التصميم المتجاوب */
{{media_queries}}
"""
        
        return css_framework
    
    def _generate_component_library(self, analysis_data):
        """إنشاء مكتبة المكونات"""
        components = {
            'button': {
                'html': '<button class="btn btn-primary">{{text}}</button>',
                'css': '''
.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
'''
            },
            'card': {
                'html': '''
<div class="card">
    <div class="card-header">{{header}}</div>
    <div class="card-body">{{body}}</div>
    <div class="card-footer">{{footer}}</div>
</div>
''',
                'css': '''
.card {
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-header {
    padding: 1rem;
    background-color: #f8f9fa;
    border-bottom: 1px solid #ddd;
    font-weight: bold;
}

.card-body {
    padding: 1rem;
}

.card-footer {
    padding: 1rem;
    background-color: #f8f9fa;
    border-top: 1px solid #ddd;
}
'''
            },
            'navigation': {
                'html': '''
<nav class="navbar">
    <div class="navbar-brand">{{brand}}</div>
    <ul class="navbar-nav">
        {{nav_items}}
    </ul>
</nav>
''',
                'css': '''
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: var(--primary-color);
    color: white;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
}

.navbar-nav {
    display: flex;
    list-style: none;
    gap: 1rem;
}

.navbar-nav a {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    transition: background-color 0.3s ease;
}

.navbar-nav a:hover {
    background-color: rgba(255,255,255,0.1);
}
'''
            }
        }
        
        return components
    
    def _detect_performance_tools(self, soup, content):
        """اكتشاف أدوات الأداء"""
        tools = []
        performance_patterns = {
            'Google Analytics': r'google-analytics|gtag|ga\(',
            'GTM': r'googletagmanager',
            'Hotjar': r'hotjar',
            'New Relic': r'newrelic'
        }
        
        for tool, pattern in performance_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                tools.append(tool)
        
        return tools
    
    def _analyze_component_patterns(self, soup):
        """تحليل أنماط المكونات"""
        patterns = {
            'cards': len(soup.find_all(class_=re.compile(r'card'))),
            'buttons': len(soup.find_all('button')) + len(soup.find_all(class_=re.compile(r'btn'))),
            'forms': len(soup.find_all('form')),
            'modals': len(soup.find_all(class_=re.compile(r'modal')))
        }
        return patterns
    
    def _analyze_images_detailed(self, soup, url):
        """تحليل تفصيلي للصور"""
        images = []
        for img in soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'loading': img.get('loading', ''),
                'sizes': img.get('sizes', ''),
                'srcset': img.get('srcset', '')
            }
            images.append(img_data)
        return images
    
    def _generate_js_components(self, analysis_data):
        """إنشاء مكونات JavaScript"""
        components = {
            'detected_frameworks': [],
            'component_structure': {},
            'interactive_elements': []
        }
        return components
    
    def _analyze_fonts(self, soup):
        """تحليل الخطوط المستخدمة"""
        fonts = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if 'font' in href.lower():
                fonts.append(href)
        return fonts
    
    def _analyze_icons(self, soup):
        """تحليل الأيقونات"""
        icons = []
        for link in soup.find_all('link', rel=['icon', 'shortcut icon']):
            icons.append(link.get('href', ''))
        return icons
    
    def _analyze_videos(self, soup, url):
        """تحليل ملفات الفيديو"""
        videos = []
        for video in soup.find_all('video'):
            videos.append({
                'src': video.get('src', ''),
                'poster': video.get('poster', '')
            })
        return videos
    
    def _analyze_loading_strategies(self, soup):
        """تحليل استراتيجيات التحميل"""
        strategies = {
            'lazy_loading': len(soup.find_all(attrs={'loading': 'lazy'})),
            'preload': len(soup.find_all('link', rel='preload')),
            'prefetch': len(soup.find_all('link', rel='prefetch'))
        }
        return strategies
    
    def _analyze_optimization(self, soup):
        """تحليل التحسين"""
        optimization = {
            'minified_css': len([l for l in soup.find_all('link') if 'min.css' in l.get('href', '')]),
            'minified_js': len([s for s in soup.find_all('script') if 'min.js' in s.get('src', '')]),
            'compressed': False
        }
        return optimization
    
    def _generate_responsive_css(self, analysis_data):
        """إنشاء CSS متجاوب"""
        css = {
            'breakpoints': {
                'mobile': '768px',
                'tablet': '1024px',
                'desktop': '1200px'
            }
        }
        return css
    
    def _detect_third_party_services(self, soup, content):
        """كشف الخدمات الخارجية"""
        services = []
        patterns = {
            'Google Analytics': r'google-analytics|gtag',
            'Facebook Pixel': r'facebook\.net|fbq\(',
            'Twitter': r'twitter\.com/widgets',
            'LinkedIn': r'linkedin\.com'
        }
        
        for service, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                services.append(service)
        return services
    
    def _analyze_design_patterns(self, soup):
        """تحليل أنماط التصميم"""
        patterns = {
            'grid_system': len(soup.find_all(class_=re.compile(r'grid|row|col'))),
            'flexbox': len(soup.find_all(style=re.compile(r'display:\s*flex'))),
            'responsive_images': len(soup.find_all('img', srcset=True))
        }
        return patterns