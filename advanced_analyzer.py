"""
محلل متقدم للمواقع - استخراج شامل لجميع عناصر الموقع
Advanced Website Analyzer - Comprehensive extraction of all website elements
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import base64
from urllib.parse import urljoin, urlparse
import logging
from collections import defaultdict, Counter
import hashlib

class AdvancedWebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def extract_complete_structure(self, crawl_data):
        """استخراج البنية الكاملة للموقع"""
        structure = {
            'html_structure': {},
            'css_grid_layouts': [],
            'flexbox_layouts': [],
            'responsive_breakpoints': [],
            'component_hierarchy': {},
            'semantic_structure': {},
            'accessibility_features': {},
            'interactive_elements': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # تحليل البنية الهيكلية
                structure['html_structure'][url] = self._analyze_html_structure(soup)
                
                # تحليل تخطيطات CSS
                structure['css_grid_layouts'].extend(self._extract_css_layouts(soup, 'grid'))
                structure['flexbox_layouts'].extend(self._extract_css_layouts(soup, 'flex'))
                
                # تحليل العناصر الدلالية
                structure['semantic_structure'][url] = self._analyze_semantic_elements(soup)
                
                # تحليل ميزات إمكانية الوصول
                structure['accessibility_features'][url] = self._analyze_accessibility(soup)
                
                # تحليل العناصر التفاعلية
                structure['interactive_elements'][url] = self._analyze_interactive_elements(soup)
                
            except Exception as e:
                logging.error(f"خطأ في تحليل {url}: {e}")
        
        return structure
    
    def extract_all_styles(self, crawl_data):
        """استخراج جميع الأنماط والتصاميم"""
        styles = {
            'inline_styles': {},
            'css_variables': {},
            'color_palette': {},
            'typography': {},
            'spacing_system': {},
            'animations': [],
            'media_queries': [],
            'css_frameworks': []
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # استخراج الأنماط المضمنة
                styles['inline_styles'][url] = self._extract_inline_styles(soup)
                
                # استخراج متغيرات CSS
                css_files = page_data.get('assets', {}).get('css', [])
                for css_file in css_files:
                    css_content = self._fetch_css_content(css_file.get('href'))
                    if css_content:
                        styles['css_variables'].update(self._extract_css_variables(css_content))
                        styles['color_palette'].update(self._extract_color_palette(css_content))
                        styles['typography'].update(self._extract_typography_rules(css_content))
                        styles['animations'].extend(self._extract_animations(css_content))
                        styles['media_queries'].extend(self._extract_media_queries(css_content))
                
            except Exception as e:
                logging.error(f"خطأ في استخراج الأنماط من {url}: {e}")
        
        return styles
    
    def extract_all_scripts(self, crawl_data):
        """استخراج جميع السكريبتات والوظائف"""
        scripts = {
            'inline_scripts': {},
            'external_scripts': [],
            'event_handlers': {},
            'ajax_endpoints': [],
            'api_calls': [],
            'data_attributes': {},
            'form_validations': {},
            'interactive_features': []
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # استخراج السكريبتات المضمنة
                scripts['inline_scripts'][url] = self._extract_inline_scripts(soup)
                
                # استخراج معالجات الأحداث
                scripts['event_handlers'][url] = self._extract_event_handlers(soup)
                
                # استخراج خصائص البيانات
                scripts['data_attributes'][url] = self._extract_data_attributes(soup)
                
                # تحليل السكريبتات الخارجية
                js_files = page_data.get('assets', {}).get('javascript', [])
                for js_file in js_files:
                    js_content = self._fetch_js_content(js_file.get('src'))
                    if js_content:
                        scripts['ajax_endpoints'].extend(self._extract_ajax_endpoints(js_content))
                        scripts['api_calls'].extend(self._extract_api_calls(js_content))
                
            except Exception as e:
                logging.error(f"خطأ في استخراج السكريبتات من {url}: {e}")
        
        return scripts
    
    def extract_content_structure(self, crawl_data):
        """استخراج بنية المحتوى الكاملة"""
        content = {
            'text_content': {},
            'images_detailed': {},
            'videos': {},
            'audio': {},
            'documents': {},
            'content_patterns': {},
            'language_detection': {},
            'metadata_complete': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # استخراج المحتوى النصي المنظم
                content['text_content'][url] = self._extract_structured_text(soup)
                
                # استخراج تفاصيل الصور الكاملة
                content['images_detailed'][url] = self._extract_detailed_images(soup, url)
                
                # استخراج ملفات الوسائط
                content['videos'][url] = self._extract_videos(soup, url)
                content['audio'][url] = self._extract_audio(soup, url)
                content['documents'][url] = self._extract_documents(soup, url)
                
                # تحليل أنماط المحتوى
                content['content_patterns'][url] = self._analyze_content_patterns(soup)
                
                # اكتشاف اللغة
                content['language_detection'][url] = self._detect_languages(soup)
                
                # استخراج البيانات الوصفية الكاملة
                content['metadata_complete'][url] = self._extract_complete_metadata(soup)
                
            except Exception as e:
                logging.error(f"خطأ في استخراج المحتوى من {url}: {e}")
        
        return content
    
    def extract_performance_data(self, crawl_data):
        """استخراج بيانات الأداء والتحسين"""
        performance = {
            'loading_performance': {},
            'optimization_opportunities': {},
            'caching_headers': {},
            'compression_analysis': {},
            'resource_hints': {},
            'critical_resources': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                
                # تحليل أداء التحميل
                performance['loading_performance'][url] = self._analyze_loading_performance(response)
                
                # تحليل رؤوس التخزين المؤقت
                performance['caching_headers'][url] = self._analyze_caching_headers(response.headers)
                
                # تحليل فرص التحسين
                soup = BeautifulSoup(response.content, 'html.parser')
                performance['optimization_opportunities'][url] = self._analyze_optimization_opportunities(soup)
                
                # استخراج تلميحات الموارد
                performance['resource_hints'][url] = self._extract_resource_hints(soup)
                
            except Exception as e:
                logging.error(f"خطأ في تحليل الأداء لـ {url}: {e}")
        
        return performance
    
    def generate_recreation_guide(self, analysis_data):
        """إنشاء دليل شامل لإعادة إنشاء الموقع"""
        guide = {
            'project_structure': self._generate_project_structure(analysis_data),
            'html_templates': self._generate_html_templates(analysis_data),
            'css_framework': self._generate_css_framework(analysis_data),
            'javascript_components': self._generate_js_components(analysis_data),
            'asset_requirements': self._generate_asset_requirements(analysis_data),
            'deployment_guide': self._generate_deployment_guide(analysis_data),
            'arabic_localization': self._generate_arabic_guide(analysis_data)
        }
        
        return guide
    
    # Helper methods (implementation details)
    def _analyze_html_structure(self, soup):
        """تحليل البنية HTML"""
        structure = {
            'doctype': str(soup.contents[0]) if soup.contents else '',
            'head_elements': [],
            'body_structure': {},
            'semantic_elements': [],
            'custom_elements': []
        }
        
        # تحليل عناصر head
        head = soup.find('head')
        if head:
            for element in head.find_all():
                structure['head_elements'].append({
                    'tag': element.name,
                    'attributes': dict(element.attrs),
                    'content': element.string if element.string else ''
                })
        
        # تحليل بنية body
        body = soup.find('body')
        if body:
            structure['body_structure'] = self._analyze_element_hierarchy(body)
        
        return structure
    
    def _analyze_element_hierarchy(self, element, depth=0):
        """تحليل التسلسل الهرمي للعناصر"""
        if depth > 10:  # تجنب التكرار اللا نهائي
            return {}
        
        hierarchy = {
            'tag': element.name if hasattr(element, 'name') else 'text',
            'attributes': dict(element.attrs) if hasattr(element, 'attrs') else {},
            'children': [],
            'depth': depth
        }
        
        if hasattr(element, 'children'):
            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    hierarchy['children'].append(self._analyze_element_hierarchy(child, depth + 1))
        
        return hierarchy
    
    def _analyze_semantic_elements(self, soup):
        """تحليل العناصر الدلالية"""
        semantic = {
            'html5_elements': [],
            'headings_structure': {},
            'landmarks': [],
            'microdata': {}
        }
        
        # عناصر HTML5 الدلالية
        semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        for tag in semantic_tags:
            elements = soup.find_all(tag)
            semantic['html5_elements'].extend([{
                'tag': tag,
                'id': el.get('id', ''),
                'class': el.get('class', []),
                'content_length': len(el.get_text(strip=True))
            } for el in elements])
        
        return semantic
    
    def _extract_inline_scripts(self, soup):
        """استخراج السكريبتات المضمنة"""
        scripts = []
        for script in soup.find_all('script'):
            if script.string and not script.get('src'):
                scripts.append({
                    'content': script.string.strip(),
                    'type': script.get('type', 'text/javascript'),
                    'length': len(script.string.strip())
                })
        return scripts
    
    def _extract_videos(self, soup, url):
        """استخراج مقاطع الفيديو"""
        videos = []
        for video in soup.find_all('video'):
            video_data = {
                'src': video.get('src', ''),
                'poster': video.get('poster', ''),
                'controls': video.has_attr('controls'),
                'autoplay': video.has_attr('autoplay')
            }
            videos.append(video_data)
        return videos
    
    def _analyze_loading_performance(self, response):
        """تحليل أداء التحميل"""
        return {
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.content),
            'headers': dict(response.headers)
        }
    
    def _extract_css_layouts(self, soup, layout_type):
        """استخراج تخطيطات CSS"""
        layouts = []
        elements = soup.find_all(style=re.compile(f'display:\s*{layout_type}'))
        
        for element in elements:
            layout = {
                'element': element.name,
                'classes': element.get('class', []),
                'style': element.get('style', ''),
                'layout_type': layout_type
            }
            layouts.append(layout)
        
        return layouts
    
    def _extract_inline_styles(self, soup):
        """استخراج الأنماط المضمنة"""
        styles = {}
        elements_with_style = soup.find_all(style=True)
        
        for element in elements_with_style:
            element_id = f"{element.name}_{hash(str(element))}"
            styles[element_id] = {
                'tag': element.name,
                'classes': element.get('class', []),
                'style': element.get('style', '')
            }
        
        return styles
    
    def _fetch_css_content(self, css_url):
        """جلب محتوى ملف CSS"""
        try:
            response = self.session.get(css_url, timeout=10)
            return response.text
        except Exception as e:
            logging.error(f"خطأ في جلب CSS من {css_url}: {e}")
            return None
    
    def _extract_css_variables(self, css_content):
        """استخراج متغيرات CSS"""
        variables = {}
        pattern = r'--([a-zA-Z0-9-_]+):\s*([^;]+);'
        matches = re.findall(pattern, css_content)
        
        for var_name, var_value in matches:
            variables[f'--{var_name}'] = var_value.strip()
        
        return variables
    
    def _extract_color_palette(self, css_content):
        """استخراج لوحة الألوان"""
        colors = {}
        # البحث عن الألوان بصيغ مختلفة
        patterns = [
            r'#([0-9a-fA-F]{3,6})',  # Hex colors
            r'rgb\(([^)]+)\)',       # RGB colors
            r'rgba\(([^)]+)\)',      # RGBA colors
            r'hsl\(([^)]+)\)',       # HSL colors
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, css_content)
            for match in matches:
                color_value = match if pattern.startswith('#') else f"{pattern.split('(')[0]}({match})"
                colors[color_value] = colors.get(color_value, 0) + 1
        
        # ترتيب الألوان حسب التكرار
        return dict(sorted(colors.items(), key=lambda x: x[1], reverse=True))
    
    def _extract_structured_text(self, soup):
        """استخراج النص المنظم"""
        text_structure = {
            'headings': {},
            'paragraphs': [],
            'lists': [],
            'tables': [],
            'quotes': [],
            'code_blocks': []
        }
        
        # استخراج العناوين
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            text_structure['headings'][f'h{i}'] = [h.get_text().strip() for h in headings]
        
        # استخراج الفقرات
        paragraphs = soup.find_all('p')
        text_structure['paragraphs'] = [p.get_text().strip() for p in paragraphs]
        
        # استخراج القوائم
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = [li.get_text().strip() for li in list_elem.find_all('li')]
            text_structure['lists'].append({
                'type': list_elem.name,
                'items': items
            })
        
        return text_structure
    
    def _extract_detailed_images(self, soup, base_url):
        """استخراج تفاصيل الصور الكاملة"""
        images = []
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            image_data = {
                'src': urljoin(base_url, img.get('src', '')),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'srcset': img.get('srcset', ''),
                'sizes': img.get('sizes', ''),
                'classes': img.get('class', []),
                'style': img.get('style', '')
            }
            images.append(image_data)
        
        return images
    
    def _generate_project_structure(self, analysis_data):
        """إنشاء هيكل المشروع المقترح"""
        structure = {
            'directories': [
                'assets/',
                'assets/css/',
                'assets/js/',
                'assets/images/',
                'assets/fonts/',
                'templates/',
                'components/',
                'data/',
                'docs/'
            ],
            'main_files': [
                'index.html',
                'styles.css',
                'main.js',
                'config.json',
                'README.md'
            ],
            'arabic_structure': {
                'description': 'هيكل مشروع مقترح لإعادة إنشاء الموقع',
                'directories_ar': [
                    'الأصول/',
                    'الأصول/الأنماط/',
                    'الأصول/السكريبتات/',
                    'الأصول/الصور/',
                    'الأصول/الخطوط/',
                    'القوالب/',
                    'المكونات/',
                    'البيانات/',
                    'التوثيق/'
                ]
            }
        }
        
        return structure
    
    def _generate_arabic_guide(self, analysis_data):
        """إنشاء دليل باللغة العربية"""
        guide = {
            'title': 'دليل إعادة إنشاء الموقع',
            'introduction': 'هذا الدليل يوضح كيفية إعادة إنشاء الموقع المحلل بالتفصيل',
            'steps': [
                {
                    'step': 1,
                    'title': 'إعداد هيكل المشروع',
                    'description': 'إنشاء المجلدات والملفات الأساسية',
                    'actions': [
                        'إنشاء مجلد assets للأصول',
                        'إنشاء مجلد templates للقوالب',
                        'إنشاء مجلد components للمكونات'
                    ]
                },
                {
                    'step': 2,
                    'title': 'تطبيق التصميم',
                    'description': 'نسخ الأنماط والتخطيطات',
                    'actions': [
                        'نسخ ملفات CSS',
                        'تطبيق متغيرات الألوان',
                        'إعداد التخطيطات المرنة'
                    ]
                },
                {
                    'step': 3,
                    'title': 'إضافة التفاعلية',
                    'description': 'تطبيق السكريبتات والوظائف',
                    'actions': [
                        'نسخ ملفات JavaScript',
                        'إعداد معالجات الأحداث',
                        'تطبيق التحقق من النماذج'
                    ]
                },
                {
                    'step': 4,
                    'title': 'إضافة المحتوى',
                    'description': 'نسخ النصوص والوسائط',
                    'actions': [
                        'نسخ النصوص والعناوين',
                        'تحميل الصور والوسائط',
                        'إعداد البيانات الوصفية'
                    ]
                }
            ],
            'tips': [
                'تأكد من حقوق الطبع والنشر قبل نسخ المحتوى',
                'استخدم أدوات التحقق من صحة HTML',
                'اختبر الموقع على أجهزة مختلفة',
                'حسّن الأداء وسرعة التحميل'
            ]
        }
        
        return guide
    
    def _analyze_caching_headers(self, headers):
        """تحليل headers التخزين المؤقت"""
        cache_info = {
            'cache_control': headers.get('Cache-Control', ''),
            'expires': headers.get('Expires', ''),
            'etag': headers.get('ETag', ''),
            'last_modified': headers.get('Last-Modified', '')
        }
        return cache_info