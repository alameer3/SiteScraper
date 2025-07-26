"""
محرك الاستخراج العميق المتقدم
Deep Extraction Engine - Advanced Website Extraction and Replication System

هذا المحرك يوفر:
1. استخراج الواجهة الكاملة (HTML, CSS, JS, Assets)
2. استخراج البنية التقنية (APIs, Routes, Database Structure)
3. استخراج الوظائف والميزات (Authentication, CMS, Search)
4. استخراج سلوك الموقع (Events, AJAX, Responsive Design)

Developed according to user specifications in نصوصي.txt
"""

import asyncio
import aiohttp
import os
import json
import time
import logging
import hashlib
import re
import ssl
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

# Import extraction engines
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    async_playwright = None
    PLAYWRIGHT_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    trafilatura = None
    TRAFILATURA_AVAILABLE = False

@dataclass
class ExtractionConfig:
    """تكوين عملية الاستخراج"""
    mode: str = "comprehensive"  # basic, standard, advanced, comprehensive, ultra
    max_depth: int = 3
    max_pages: int = 50
    include_assets: bool = True
    include_javascript: bool = True
    include_css: bool = True
    extract_apis: bool = True
    analyze_behavior: bool = True
    extract_database_schema: bool = False
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    timeout: int = 30
    delay_between_requests: float = 1.0
    respect_robots_txt: bool = True
    enable_playwright: bool = True
    enable_selenium: bool = True
    output_directory: str = "extracted_sites"

class DeepExtractionEngine:
    """محرك الاستخراج العميق المتقدم"""

    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.extracted_data: Dict[str, Any] = {}
        self.visited_urls: Set[str] = set()
        self.api_endpoints: Set[str] = set()
        self.javascript_events: List[Dict[str, Any]] = []
        self.css_frameworks: List[str] = []
        self.database_indicators: Dict[str, Any] = {}
        self.authentication_methods: List[str] = []
        self.interactive_elements: List[Dict[str, Any]] = []

        # إعداد المجلدات
        self.setup_output_directories()

        # إعداد السلوتين المختلفة
        self.drivers: Dict[str, Any] = {}

    def setup_output_directories(self):
        """إعداد مجلدات الإخراج"""
        base_path = Path(self.config.output_directory)
        self.paths = {
            'base': base_path,
            'html': base_path / 'html',
            'css': base_path / 'css',
            'js': base_path / 'js',
            'images': base_path / 'images',
            'fonts': base_path / 'fonts',
            'data': base_path / 'data',
            'apis': base_path / 'apis',
            'schemas': base_path / 'schemas',
            'reports': base_path / 'reports'
        }

        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)

    async def extract_complete_website(self, target_url: str) -> Dict[str, Any]:
        """استخراج كامل للموقع مع جميع الميزات المطلوبة"""
        start_time = time.time()

        logging.info(f"بدء الاستخراج العميق للموقع: {target_url}")

        try:
            # إنشاء الجلسة
            self.session = aiohttp.ClientSession()

            # المرحلة الأولى: تحليل الموقع الأساسي
            initial_analysis = await self._analyze_initial_structure(target_url)

            # المرحلة الثانية: استخراج الواجهة الكاملة
            interface_extraction = await self._extract_complete_interface(target_url)

            # المرحلة الثالثة: استخراج البنية التقنية
            technical_structure = await self._extract_technical_structure(target_url)

            # المرحلة الرابعة: استخراج الوظائف والميزات
            features_extraction = await self._extract_features_and_functions(target_url)

            # المرحلة الخامسة: استخراج سلوك الموقع
            behavior_analysis = await self._extract_website_behavior(target_url)

            # المرحلة السادسة: تحليل شامل باستخدام محركات متعددة
            multi_engine_analysis = await self._multi_engine_extraction(target_url)

            # تجميع النتائج النهائية
            complete_extraction = {
                'metadata': {
                    'target_url': target_url,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'extraction_time': time.time() - start_time,
                    'config': asdict(self.config),
                    'extraction_id': hashlib.md5(f"{target_url}_{time.time()}".encode()).hexdigest()
                },
                'initial_analysis': initial_analysis,
                'interface_extraction': interface_extraction,
                'technical_structure': technical_structure,
                'features_extraction': features_extraction,
                'behavior_analysis': behavior_analysis,
                'multi_engine_analysis': multi_engine_analysis,
                'extraction_statistics': self._calculate_extraction_statistics()
            }

            # حفظ النتائج
            await self._save_extraction_results(complete_extraction)

            logging.info(f"تم الانتهاء من الاستخراج العميق في {time.time() - start_time:.2f} ثانية")

            return complete_extraction

        except Exception as e:
            logging.error(f"خطأ في الاستخراج العميق: {e}")
            return {'error': str(e), 'target_url': target_url}

        finally:
            await self._cleanup_resources()

    async def _analyze_initial_structure(self, url: str) -> Dict[str, Any]:
        """تحليل البنية الأولية للموقع"""
        logging.info("تحليل البنية الأولية...")

        if not self.session:
            self.session = aiohttp.ClientSession()

        async with self.session.get(url) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')

            return {
                'basic_info': {
                    'title': self._safe_get_text(soup.find('title')),
                    'description': self._get_meta_content(soup, 'description'),
                    'keywords': self._get_meta_content(soup, 'keywords'),
                    'language': self._get_language(soup),
                    'charset': self._get_charset(soup),
                    'viewport': self._get_meta_content(soup, 'viewport')
                },
                'document_structure': {
                    'doctype': str(soup.contents[0]) if soup.contents else '',
                    'html_attributes': getattr(soup.find('html'), 'attrs', {}) if soup.find('html') else {},
                    'head_elements': self._analyze_head_elements(soup),
                    'body_structure': self._analyze_body_structure(soup)
                },
                'initial_technologies': self._detect_initial_technologies(soup, response),
                'page_metrics': {
                    'html_size': len(html_content),
                    'total_elements': len(soup.find_all()),
                    'response_time': response.headers.get('X-Response-Time', 'unknown'),
                    'server': response.headers.get('Server', 'unknown')
                }
            }

    async def _extract_complete_interface(self, url: str) -> Dict[str, Any]:
        """استخراج الواجهة الكاملة حسب المتطلبات"""
        logging.info("استخراج الواجهة الكاملة...")

        interface_data = {
            'html_files': {},
            'css_files': {},
            'javascript_files': {},
            'images': {},
            'fonts': {},
            'audio_video': {},
            'design_files': {},
            'config_files': {}
        }

        # استخراج الملفات الأساسية
        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # حفظ HTML الرئيسي
                interface_data['html_files']['index.html'] = {
                    'content': html_content,
                    'size': len(html_content),
                    'encoding': response.charset or 'utf-8'
                }

                # استخراج ملفات CSS
                css_links = soup.find_all('link', rel='stylesheet')
                for css_link in css_links:
                    if isinstance(css_link, Tag):
                        href = css_link.get('href')
                        if href and isinstance(href, str):
                            css_url = urljoin(url, href)
                            css_content = await self._download_asset(css_url)
                            if css_content:
                                filename = os.path.basename(urlparse(str(href)).path) or 'style.css'
                                interface_data['css_files'][filename] = {
                                    'content': css_content,
                                    'url': css_url,
                                    'media': css_link.get('media', 'all'),
                                    'size': len(css_content)
                                }

                # استخراج ملفات JavaScript
                script_tags = soup.find_all('script', src=True)
                for script in script_tags:
                    if isinstance(script, Tag):
                        src = script.get('src')
                        if src and isinstance(src, str):
                            js_url = urljoin(url, src)
                            js_content = await self._download_asset(js_url)
                            if js_content:
                                filename = os.path.basename(urlparse(str(src)).path) or 'script.js'
                                interface_data['javascript_files'][filename] = {
                                    'content': js_content,
                                    'url': js_url,
                                    'type': script.get('type', 'text/javascript'),
                                    'async': script.has_attr('async'),
                                    'defer': script.has_attr('defer'),
                                    'size': len(js_content)
                                }

                # استخراج الصور
                images = soup.find_all('img')
                for img in images:
                    if isinstance(img, Tag):
                        src = img.get('src') or img.get('data-src')
                        if src and isinstance(src, str):
                            img_url = urljoin(url, src)
                            img_data = await self._download_binary_asset(img_url)
                            if img_data:
                                filename = os.path.basename(urlparse(str(src)).path)
                                interface_data['images'][filename] = {
                                    'url': img_url,
                                    'alt': img.get('alt', ''),
                                    'size': len(img_data),
                                    'dimensions': f"{img.get('width', 'auto')}x{img.get('height', 'auto')}"
                                }

                # استخراج الخطوط
                font_links = soup.find_all('link', href=re.compile(r'\.(woff2?|ttf|eot|otf)'))
                for font_link in font_links:
                    if isinstance(font_link, Tag):
                        href = font_link.get('href')
                        if href and isinstance(href, str):
                            font_url = urljoin(url, href)
                            font_data = await self._download_binary_asset(font_url)
                            if font_data:
                                filename = os.path.basename(urlparse(str(href)).path)
                                interface_data['fonts'][filename] = {
                                    'url': font_url,
                                    'type': font_link.get('type', ''),
                                    'size': len(font_data)
                                }
                # استخراج ملفات الصوت والفيديو
                media_data = await self._extract_audio_video_files(soup, url)
                interface_data['audio_video'] = media_data

        return interface_data

    async def _analyze_head_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل عناصر head"""
        head_data = {}
        head = soup.find('head')
        if head and isinstance(head, Tag):
            # Title
            head_data['title'] = self._safe_get_text(head.find('title'))

            # Meta tags
            head_data['meta_tags'] = []
            for meta in head.find_all('meta'):
                if isinstance(meta, Tag):
                    meta_data = {}
                    for attr in ['name', 'property', 'content', 'charset']:
                        if meta.get(attr):
                            meta_data[attr] = str(meta.get(attr))
                    if meta_data:
                        head_data['meta_tags'].append(meta_data)

            # Links
            head_data['links'] = []
            for link in head.find_all('link'):
                if isinstance(link, Tag):
                    link_data = {}
                    for attr in ['rel', 'href', 'type', 'media']:
                        if link.get(attr):
                            link_data[attr] = str(link.get(attr))
                    if link_data:
                        head_data['links'].append(link_data)

        return head_data

    async def _analyze_body_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل بنية body"""
        body = soup.find('body')
        if not body or not isinstance(body, Tag):
            return {}

        return {
            'semantic_elements': self._extract_semantic_elements(body),
            'forms': self._extract_forms(body),
            'interactive_elements': self._extract_interactive_elements(body),
            'navigation': self._extract_navigation(body)
        }

    def _extract_semantic_elements(self, body: Tag) -> List[Dict]:
        """استخراج العناصر الدلالية"""
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        elements = []

        for tag_name in semantic_tags:
            for element in body.find_all(tag_name):
                if isinstance(element, Tag):
                    elements.append({
                        'tag': tag_name,
                        'id': element.get('id', ''),
                        'class': element.get('class') or [],
                        'text_length': len(self._safe_get_text(element))
                    })

        return elements

    def _extract_forms(self, body: Tag) -> List[Dict]:
        """استخراج النماذج"""
        forms = []
        for form in body.find_all('form'):
            if isinstance(form, Tag):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'fields': []
                }

                # استخراج حقول النموذج
                for field in form.find_all(['input', 'textarea', 'select']):
                    if isinstance(field, Tag):
                        field_data = {
                            'tag': field.name,
                            'type': field.get('type', ''),
                            'name': field.get('name', ''),
                            'id': field.get('id', ''),
                            'required': field.has_attr('required')
                        }
                        form_data['fields'].append(field_data)

                forms.append(form_data)

        return forms

    def _extract_interactive_elements(self, body: Tag) -> List[Dict]:
        """استخراج العناصر التفاعلية"""
        interactive = []

        # أزرار
        for button in body.find_all('button'):
            if isinstance(button, Tag):
                interactive.append({
                    'type': 'button',
                    'text': self._safe_get_text(button),
                    'class': button.get('class') or [],
                    'onclick': button.get('onclick', '')
                })

        # روابط تفاعلية
        for link in body.find_all('a', href=True):
            if isinstance(link, Tag):
                href = link.get('href', '')
                if isinstance(href, str) and (href.startswith('#') or 'javascript:' in href):
                    interactive.append({
                        'type': 'interactive_link',
                        'text': self._safe_get_text(link),
                        'href': href,
                        'class': link.get('class') or []
                    })

        return interactive

    def _extract_navigation(self, body: Tag) -> Dict[str, Any]:
        """استخراج عناصر التنقل"""
        nav_data = {
            'menus': [],
            'breadcrumbs': [],
            'pagination': []
        }

        # القوائم
        for nav in body.find_all('nav'):
            if isinstance(nav, Tag):
                nav_item = {
                    'class': nav.get('class') or [],
                    'links': []
                }

                for link in nav.find_all('a'):
                    if isinstance(link, Tag):
                        nav_item['links'].append({
                            'text': self._safe_get_text(link),
                            'href': link.get('href', ''),
                            'class': link.get('class') or []
                        })

                nav_data['menus'].append(nav_item)

        return nav_data

    async def _detect_initial_technologies(self, soup: BeautifulSoup, response) -> Dict[str, Any]:
        """اكتشاف التقنيات الأولية"""
        technologies = {
            'frameworks': [],
            'libraries': [],
            'cms': 'unknown',
            'server': response.headers.get('Server', 'unknown')
        }

        # البحث عن إشارات التقنيات في الكود
        html_content = str(soup)

        # فحص JavaScript frameworks
        js_frameworks = {
            'react': ['react', 'reactdom'],
            'vue': ['vue.js', 'vue.min.js'],
            'angular': ['angular', '@angular'],
            'jquery': ['jquery', 'jquery.min.js']
        }

        for framework, indicators in js_frameworks.items():
            if any(indicator in html_content.lower() for indicator in indicators):
                technologies['frameworks'].append(framework)

        # فحص CSS frameworks
        css_frameworks = {
            'bootstrap': ['bootstrap', 'cdn.jsdelivr.net/npm/bootstrap'],
            'tailwind': ['tailwindcss', 'tailwind'],
            'bulma': ['bulma', 'bulma.css']
        }

        for framework, indicators in css_frameworks.items():
            if any(indicator in html_content.lower() for indicator in indicators):
                technologies['frameworks'].append(framework)

        return technologies

    async def _extract_technical_structure(self, url: str) -> Dict[str, Any]:
        """استخراج البنية التقنية حسب المتطلبات"""
        logging.info("استخراج البنية التقنية...")

        technical_data = {
            'database_structure': {},
            'api_endpoints': [],
            'javascript_logic': {},
            'routing_system': {},
            'interactive_components': {}
        }

        # تحليل قاعدة البيانات المحتملة
        technical_data['database_structure'] = await self._analyze_database_indicators(url)

        # اكتشاف API endpoints
        technical_data['api_endpoints'] = await self._discover_api_endpoints(url)

        # تحليل منطق JavaScript
        technical_data['javascript_logic'] = await self._analyze_javascript_logic(url)

        # تحليل نظام التوجيه
        technical_data['routing_system'] = await self._analyze_routing_system(url)

        # تحليل المكونات التفاعلية
        technical_data['interactive_components'] = await self._analyze_interactive_components(url)

        return technical_data

    async def _analyze_database_indicators(self, url: str) -> Dict[str, Any]:
        """تحليل مؤشرات قاعدة البيانات"""
        db_indicators = {
            'detected_patterns': [],
            'form_fields': [],
            'crud_operations': [],
            'data_structures': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # تحليل النماذج للحصول على بنية البيانات المحتملة
                forms = soup.find_all('form')
                for form in forms:
                    if isinstance(form, Tag):
                        form_analysis = {
                            'action': form.get('action', ''),
                            'method': form.get('method', 'get'),
                            'fields': []
                        }

                        for field in form.find_all(['input', 'select', 'textarea']):
                            if isinstance(field, Tag):
                                field_info = {
                                    'name': field.get('name', ''),
                                    'type': field.get('type', ''),
                                    'required': field.has_attr('required'),
                                    'validation': field.get('pattern', '')
                                }
                                form_analysis['fields'].append(field_info)

                        db_indicators['form_fields'].append(form_analysis)

                # البحث عن أنماط CRUD في الروابط والنماذج
                crud_patterns = {
                    'create': ['add', 'new', 'create', 'post'],
                    'read': ['view', 'show', 'get', 'list'],
                    'update': ['edit', 'update', 'modify', 'put'],
                    'delete': ['delete', 'remove', 'destroy']
                }

                for action, keywords in crud_patterns.items():
                    elements = soup.find_all(['a', 'form', 'button'])
                    for element in elements:
                        if isinstance(element, Tag):
                            element_text = self._safe_get_text(element).lower()
                            element_action = str(element.get('action', '')).lower()
                            element_href = str(element.get('href', '')).lower()

                            if any(keyword in element_text or keyword in element_action or keyword in element_href 
                                   for keyword in keywords):
                                db_indicators['crud_operations'].append({
                                    'operation': action,
                                    'element': element.name,
                                    'text': element_text,
                                    'action_url': element.get('action') or element.get('href', '')
                                })

        return db_indicators

    async def _discover_api_endpoints(self, url: str) -> List[Dict[str, Any]]:
        """اكتشاف API endpoints"""
        endpoints = []

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()

                # البحث عن أنماط API في JavaScript
                api_patterns = [
                    r'fetch\([\'"]([^\'"]+)[\'"]',
                    r'axios\.[get|post|put|delete]+\([\'"]([^\'"]+)[\'"]',
                    r'\.ajax\(.*url.*?[\'"]([^\'"]+)[\'"]',
                    r'/api/[^\s\'"]+',
                    r'/rest/[^\s\'"]+'
                ]

                import re
                for pattern in api_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        endpoint_url = match if isinstance(match, str) else match[0]
                        if endpoint_url not in [ep['url'] for ep in endpoints]:
                            endpoints.append({
                                'url': endpoint_url,
                                'method': 'unknown',
                                'source': 'javascript_analysis'
                            })

                # فحص network requests في الصفحة (محاكاة)
                common_endpoints = [
                    '/api/users', '/api/data', '/api/search', '/api/login',
                    '/rest/items', '/rest/config', '/json/feed'
                ]

                for endpoint in common_endpoints:
                    test_url = urljoin(url, endpoint)
                    try:
                        async with self.session.head(test_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                            if resp.status < 400:
                                endpoints.append({
                                    'url': endpoint,
                                    'method': 'GET',
                                    'status': resp.status,
                                    'source': 'endpoint_discovery'
                                })
                    except:
                        pass  # تجاهل الأخطاء في الاكتشاف

        return endpoints

    async def _analyze_javascript_logic(self, url: str) -> Dict[str, Any]:
        """تحليل منطق JavaScript"""
        js_analysis = {
            'external_scripts': [],
            'inline_scripts': [],
            'event_handlers': [],
            'functions': [],
            'ajax_calls': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # تحليل الملفات الخارجية
                for script in soup.find_all('script', src=True):
                    if isinstance(script, Tag):
                        src = script.get('src')
                        if src:
                            js_analysis['external_scripts'].append({
                                'src': src,
                                'type': script.get('type', 'text/javascript'),
                                'async': script.has_attr('async'),
                                'defer': script.has_attr('defer')
                            })

                # تحليل الملفات المضمنة
                for script in soup.find_all('script', src=False):
                    if isinstance(script, Tag) and script.string:
                        script_content = str(script.string)
                        js_analysis['inline_scripts'].append({
                            'content': script_content,
                            'length': len(script_content)
                        })

                        # البحث عن دوال
                        function_pattern = re.compile(r'function\s+(\w+)\s*\([^)]*\)')
                        functions = function_pattern.findall(script_content)
                        js_analysis['functions'].extend(functions)

                        # البحث عن AJAX calls
                        ajax_patterns = [
                            r'fetch\([\'"]([^\'"]+)[\'"]',
                            r'XMLHttpRequest',
                            r'\.ajax\(',
                            r'axios\.'
                        ]

                        for pattern in ajax_patterns:
                            if re.search(pattern, script_content, re.IGNORECASE):
                                js_analysis['ajax_calls'].append({
                                    'pattern': pattern,
                                    'found_in': 'inline_script'
                                })

                # تحليل event handlers
                all_elements = soup.find_all()
                for element in all_elements:
                    if isinstance(element, Tag) and element.attrs:
                        for attr in element.attrs:
                            if attr.startswith('on'):
                                js_analysis['event_handlers'].append({
                                    'element': element.name,
                                    'event': attr,
                                    'handler': element.get(attr, '')
                                })

        return js_analysis

    async def _analyze_routing_system(self, url: str) -> Dict[str, Any]:
        """تحليل نظام التوجيه"""
        routing_data = {
            'internal_links': [],
            'external_links': [],
            'spa_routing': False,
            'routing_patterns': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                base_domain = urlparse(url).netloc

                # تحليل الروابط
                for link in soup.find_all('a', href=True):
                    if isinstance(link, Tag):
                        href = link.get('href', '')
                        if isinstance(href, str):
                            full_url = urljoin(url, href)
                        else:
                            full_url = url
                        link_domain = urlparse(full_url).netloc

                        link_data = {
                            'text': self._safe_get_text(link),
                            'href': href,
                            'full_url': full_url,
                            'class': link.get('class') or []
                        }

                        if link_domain == base_domain or not link_domain:
                            routing_data['internal_links'].append(link_data)
                        else:
                            routing_data['external_links'].append(link_data)

                # فحص SPA routing patterns
                spa_indicators = [
                    '#/', 'router', 'route', 'history.pushState',
                    'react-router', 'vue-router', '@angular/router'
                ]

                if any(indicator in html_content.lower() for indicator in spa_indicators):
                    routing_data['spa_routing'] = True

                # استخراج أنماط التوجيه
                import re
                route_patterns = re.findall(r'[\'"]\/[^\'"\s]*[\'"]', html_content)
                routing_data['routing_patterns'] = list(set(route_patterns))

        return routing_data

    async def _analyze_interactive_components(self, url: str) -> Dict[str, Any]:
        """تحليل المكونات التفاعلية"""
        interactive_data = {
            'forms': [],
            'modals': [],
            'dropdowns': [],
            'carousels': [],
            'tabs': [],
            'accordions': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # تحليل النماذج
                for form in soup.find_all('form'):
                    if isinstance(form, Tag):
                        form_data = {
                            'id': form.get('id', ''),
                            'class': form.get('class') or [],
                            'action': form.get('action', ''),
                            'method': form.get('method', 'get'),
                            'fields_count': len(form.find_all(['input', 'select', 'textarea']))
                        }
                        interactive_data['forms'].append(form_data)

                # البحث عن modals
                modal_selectors = [
                    {'class': 'modal'},
                    {'class': 'popup'},
                    {'class': 'dialog'},
                    {'attrs': {'role': 'dialog'}}
                ]

                for selector in modal_selectors:
                    if 'attrs' in selector:
                        modals = soup.find_all(attrs=selector['attrs'])
                    else:
                        modals = soup.find_all(class_=selector['class'])

                    for modal in modals:
                        if isinstance(modal, Tag):
                            interactive_data['modals'].append({
                                'id': modal.get('id', ''),
                                'class': modal.get('class') or [],
                                'title': self._safe_get_text(modal.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
                            })

                # البحث عن dropdowns
                dropdowns = soup.find_all(['select', 'details']) + soup.find_all(class_=['dropdown', 'select'])
                for dropdown in dropdowns:
                    if isinstance(dropdown, Tag):
                        interactive_data['dropdowns'].append({
                            'tag': dropdown.name,
                            'id': dropdown.get('id', ''),
                            'class': dropdown.get('class') or []
                        })

                # البحث عن carousels/sliders
                carousel_selectors = ['carousel', 'slider', 'swiper', 'slides']
                for selector in carousel_selectors:
                    carousels = soup.find_all(class_=selector)
                    for carousel in carousels:
                        if isinstance(carousel, Tag):
                            interactive_data['carousels'].append({
                                'class': carousel.get('class') or [],
                                'slides_count': len(carousel.find_all(['slide', 'item']))
                            })

                # البحث عن tabs
                tab_elements = soup.find_all(['ul', 'div'], class_=['tabs', 'tab-list', 'nav-tabs'])
                for tab_container in tab_elements:
                    if isinstance(tab_container, Tag):
                        tabs = tab_container.find_all(['li', 'a', 'button'])
                        interactive_data['tabs'].append({
                            'container_class': tab_container.get('class') or [],
                            'tabs_count': len(tabs)
                        })

                # البحث عن accordions
                accordion_elements = soup.find_all(class_=['accordion', 'collapse', 'expand'])
                for accordion in accordion_elements:
                    if isinstance(accordion, Tag):
                        interactive_data['accordions'].append({
                            'class': accordion.get('class') or [],
                            'sections_count': len(accordion.find_all(['section', 'div']))
                        })

        return interactive_data

    async def _extract_features_and_functions(self, url: str) -> Dict[str, Any]:
        """استخراج الوظائف والميزات حسب المتطلبات"""
        logging.info("استخراج الوظائف والميزات...")

        features_data = {
            'authentication_system': {},
            'content_management': {},
            'search_functionality': {},
            'navigation_system': {},
            'charts_and_interaction': {},
            'comments_rating_system': {}
        }

        # تحليل نظام المصادقة
        features_data['authentication_system'] = await self._analyze_authentication_system(url)

        # تحليل نظام إدارة المحتوى
        features_data['content_management'] = await self._analyze_cms_system(url)

        # تحليل وظائف البحث
        features_data['search_functionality'] = await self._analyze_search_functionality(url)

        # تحليل نظام التنقل
        features_data['navigation_system'] = await self._analyze_navigation_system(url)

        # تحليل الرسوم البيانية والتفاعل
        features_data['charts_and_interaction'] = await self._analyze_charts_and_interaction(url)

        # تحليل نظام التعليقات والتقييمات
        features_data['comments_rating_system'] = await self._analyze_comments_rating_system(url)

        return features_data

    async def _analyze_authentication_system(self, url: str) -> Dict[str, Any]:
        """تحليل آلية المصادقة والتسجيل"""
        auth_data = {
            'login_forms': [],
            'registration_forms': [],
            'password_fields': [],
            'social_auth_buttons': [],
            'two_factor_auth': False,
            'captcha_present': False
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # البحث عن نماذج تسجيل الدخول
                login_indicators = ['login', 'signin', 'sign-in', 'log-in', 'auth']
                for indicator in login_indicators:
                    forms = soup.find_all('form', class_=re.compile(indicator, re.I))
                    forms += soup.find_all('form', id=re.compile(indicator, re.I))

                    for form in forms:
                        if isinstance(form, Tag):
                            password_fields = form.find_all('input', type='password')
                            if password_fields:
                                auth_data['login_forms'].append({
                                    'id': form.get('id', ''),
                                    'class': form.get('class') or [],
                                    'action': form.get('action', ''),
                                    'method': form.get('method', 'post')
                                })

                # البحث عن نماذج التسجيل
                register_indicators = ['register', 'signup', 'sign-up', 'create-account']
                for indicator in register_indicators:
                    forms = soup.find_all('form', class_=re.compile(indicator, re.I))
                    forms += soup.find_all('form', id=re.compile(indicator, re.I))

                    for form in forms:
                        if isinstance(form, Tag):
                            auth_data['registration_forms'].append({
                                'id': form.get('id', ''),
                                'class': form.get('class') or [],
                                'action': form.get('action', ''),
                                'fields_count': len(form.find_all(['input', 'select', 'textarea']))
                            })

                # البحث عن حقول كلمة المرور
                password_inputs = soup.find_all('input', type='password')
                for pwd_input in password_inputs:
                    if isinstance(pwd_input, Tag):
                        auth_data['password_fields'].append({
                            'id': pwd_input.get('id', ''),
                            'name': pwd_input.get('name', ''),
                            'class': pwd_input.get('class') or []
                        })

                # البحث عن أزرار المصادقة الاجتماعية
                social_indicators = ['facebook', 'google', 'twitter', 'github', 'linkedin', 'oauth']
                for indicator in social_indicators:
                    buttons = soup.find_all(['a', 'button'], class_=re.compile(indicator, re.I))
                    buttons += soup.find_all(['a', 'button'], id=re.compile(indicator, re.I))

                    for button in buttons:
                        if isinstance(button, Tag):
                            auth_data['social_auth_buttons'].append({
                                'provider': indicator,
                                'text': self._safe_get_text(button),
                                'class': button.get('class') or []
                            })

                # فحص المصادقة الثنائية
                two_factor_indicators = ['2fa', 'two-factor', 'otp', 'verification', 'sms-code']
                if any(indicator in html_content.lower() for indicator in two_factor_indicators):
                    auth_data['two_factor_auth'] = True

                # فحص الكابتشا
                captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha']
                if any(indicator in html_content.lower() for indicator in captcha_indicators):
                    auth_data['captcha_present'] = True

        return auth_data

    async def _analyze_cms_system(self, url: str) -> Dict[str, Any]:
        """تحليل نظام إدارة المحتوى"""
        cms_data = {
            'detected_cms': 'unknown',
            'admin_panels': [],
            'content_editors': [],
            'upload_forms': [],
            'media_galleries': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # اكتشاف أنواع CMS
                cms_signatures = {
                    'wordpress': ['wp-content', 'wp-includes', 'wp-admin'],
                    'drupal': ['drupal', 'sites/default'],
                    'joomla': ['joomla', 'com_content'],
                    'magento': ['magento', 'mage'],
                    'shopify': ['shopify', 'shop.js'],
                    'wix': ['wix.com', 'wixstatic'],
                    'squarespace': ['squarespace', 'static1.squarespace']
                }

                for cms_name, signatures in cms_signatures.items():
                    if any(sig in html_content.lower() for sig in signatures):
                        cms_data['detected_cms'] = cms_name
                        break

                # البحث عن لوحات الإدارة
                admin_indicators = ['admin', 'dashboard', 'control-panel', 'backend']
                for indicator in admin_indicators:
                    admin_links = soup.find_all('a', href=re.compile(indicator, re.I))
                    for link in admin_links:
                        if isinstance(link, Tag):
                            cms_data['admin_panels'].append({
                                'text': self._safe_get_text(link),
                                'href': link.get('href', ''),
                                'class': link.get('class') or []
                            })

                # البحث عن محررات المحتوى
                editor_indicators = ['editor', 'wysiwyg', 'tinymce', 'ckeditor']
                for indicator in editor_indicators:
                    if indicator in html_content.lower():
                        cms_data['content_editors'].append(indicator)

                # البحث عن نماذج الرفع
                upload_forms = soup.find_all('form', enctype='multipart/form-data')
                for form in upload_forms:
                    if isinstance(form, Tag):
                        file_inputs = form.find_all('input', type='file')
                        if file_inputs:
                            cms_data['upload_forms'].append({
                                'action': form.get('action', ''),
                                'file_inputs_count': len(file_inputs)
                            })

        return cms_data

    async def _analyze_search_functionality(self, url: str) -> Dict[str, Any]:
        """تحليل وظائف البحث والتصفية"""
        search_data = {
            'search_forms': [],
            'search_inputs': [],
            'filter_elements': [],
            'autocomplete_present': False,
            'advanced_search': False
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # البحث عن نماذج البحث
                search_forms = soup.find_all('form', class_=re.compile('search', re.I))
                search_forms += soup.find_all('form', id=re.compile('search', re.I))
                search_forms += soup.find_all('form', role='search')

                for form in search_forms:
                    if isinstance(form, Tag):
                        search_data['search_forms'].append({
                            'id': form.get('id', ''),
                            'class': form.get('class') or [],
                            'action': form.get('action', ''),
                            'method': form.get('method', 'get')
                        })

                # البحث عن مدخلات البحث
                search_inputs = soup.find_all('input', type='search')
                search_inputs += soup.find_all('input', placeholder=re.compile('search', re.I))
                search_inputs += soup.find_all('input', name=re.compile('search|query|q', re.I))

                for search_input in search_inputs:
                    if isinstance(search_input, Tag):
                        search_data['search_inputs'].append({
                            'id': search_input.get('id', ''),
                            'name': search_input.get('name', ''),
                            'placeholder': search_input.get('placeholder', ''),
                            'class': search_input.get('class') or []
                        })

                # البحث عن عناصر التصفية
                filter_selectors = soup.find_all('select', class_=re.compile('filter', re.I))
                filter_checkboxes = soup.find_all('input', type='checkbox', class_=re.compile('filter', re.I))

                for filter_elem in filter_selectors + filter_checkboxes:
                    if isinstance(filter_elem, Tag):
                        search_data['filter_elements'].append({
                            'type': filter_elem.get('type', 'select'),
                            'name': filter_elem.get('name', ''),
                            'class': filter_elem.get('class') or []
                        })

                # فحص الإكمال التلقائي
                autocomplete_indicators = ['autocomplete', 'typeahead', 'suggestions']
                if any(indicator in html_content.lower() for indicator in autocomplete_indicators):
                    search_data['autocomplete_present'] = True

                # فحص البحث المتقدم
                advanced_indicators = ['advanced-search', 'advanced search', 'filter options']
                if any(indicator in html_content.lower() for indicator in advanced_indicators):
                    search_data['advanced_search'] = True

        return search_data

    async def _analyze_navigation_system(self, url: str) -> Dict[str, Any]:
        """تحليل التنقل والقوائم"""
        nav_data = {
            'primary_navigation': [],
            'secondary_navigation': [],
            'breadcrumbs': [],
            'pagination': [],
            'mega_menus': [],
            'mobile_navigation': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # التنقل الأساسي
                primary_navs = soup.find_all('nav', class_=re.compile('primary|main|header', re.I))
                primary_navs += soup.find_all('nav', id=re.compile('primary|main|header', re.I))

                for nav in primary_navs:
                    if isinstance(nav, Tag):
                        nav_links = nav.find_all('a')
                        nav_data['primary_navigation'].append({
                            'id': nav.get('id', ''),
                            'class': nav.get('class') or [],
                            'links_count': len(nav_links),
                            'has_dropdown': bool(nav.find_all(class_=re.compile('dropdown|submenu', re.I)))
                        })

                # التنقل الثانوي
                secondary_navs = soup.find_all('nav', class_=re.compile('secondary|footer|sidebar', re.I))
                for nav in secondary_navs:
                    if isinstance(nav, Tag):
                        nav_links = nav.find_all('a')
                        nav_data['secondary_navigation'].append({
                            'id': nav.get('id', ''),
                            'class': nav.get('class') or [],
                            'links_count': len(nav_links)
                        })

                # مسار التنقل (Breadcrumbs)
                breadcrumb_selectors = soup.find_all(class_=re.compile('breadcrumb', re.I))
                breadcrumb_selectors += soup.find_all(attrs={'aria-label': re.compile('breadcrumb', re.I)})

                for breadcrumb in breadcrumb_selectors:
                    if isinstance(breadcrumb, Tag):
                        nav_data['breadcrumbs'].append({
                            'class': breadcrumb.get('class') or [],
                            'items_count': len(breadcrumb.find_all('a'))
                        })

                # الترقيم (Pagination)
                pagination_selectors = soup.find_all(class_=re.compile('pagination|pager', re.I))
                for pagination in pagination_selectors:
                    if isinstance(pagination, Tag):
                        nav_data['pagination'].append({
                            'class': pagination.get('class') or [],
                            'pages_count': len(pagination.find_all('a'))
                        })

                # القوائم الضخمة (Mega Menus)
                mega_menus = soup.find_all(class_=re.compile('mega|dropdown-mega', re.I))
                for mega in mega_menus:
                    if isinstance(mega, Tag):
                        nav_data['mega_menus'].append({
                            'class': mega.get('class') or [],
                            'columns_count': len(mega.find_all(class_=re.compile('col|column', re.I)))
                        })

                # التنقل المحمول
                mobile_indicators = ['mobile-nav', 'mobile-menu', 'hamburger', 'toggle-nav']
                for indicator in mobile_indicators:
                    mobile_elements = soup.find_all(class_=re.compile(indicator, re.I))
                    if mobile_elements:
                        nav_data['mobile_navigation'].append({
                            'type': indicator,
                            'elements_count': len(mobile_elements)
                        })

        return nav_data

    async def _analyze_charts_and_interaction(self, url: str) -> Dict[str, Any]:
        """تحليل الرسوم البيانية والتفاعل"""
        charts_data = {
            'chart_libraries': [],
            'interactive_charts': [],
            'data_visualizations': [],
            'canvas_elements': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # مكتبات الرسوم البيانية الشائعة
                chart_libraries = {
                    'chartjs': 'chart.js',
                    'd3js': 'd3.js',
                    'highcharts': 'highcharts',
                    'plotly': 'plotly',
                    'echarts': 'echarts',
                    'googlecharts': 'google.visualization'
                }

                for lib_name, lib_signature in chart_libraries.items():
                    if lib_signature in html_content.lower():
                        charts_data['chart_libraries'].append(lib_name)

                # عناصر Canvas للرسوم
                canvas_elements = soup.find_all('canvas')
                for canvas in canvas_elements:
                    if isinstance(canvas, Tag):
                        charts_data['canvas_elements'].append({
                            'id': canvas.get('id', ''),
                            'class': canvas.get('class') or [],
                            'width': canvas.get('width', ''),
                            'height': canvas.get('height', '')
                        })

                # عناصر SVG للرسوم
                svg_elements = soup.find_all('svg')
                for svg in svg_elements:
                    if isinstance(svg, Tag):
                        charts_data['data_visualizations'].append({
                            'type': 'svg',
                            'class': svg.get('class') or [],
                            'viewbox': svg.get('viewBox', '')
                        })

        return charts_data

    async def _analyze_comments_rating_system(self, url: str) -> Dict[str, Any]:
        """تحليل نظام التعليقات أو التقييمات"""
        comments_data = {
            'comment_sections': [],
            'rating_systems': [],
            'review_forms': [],
            'social_sharing': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # البحث عن أقسام التعليقات
                comment_indicators = ['comment', 'review', 'feedback']
                for indicator in comment_indicators:
                    comment_sections = soup.find_all(class_=re.compile(indicator, re.I))
                    comment_sections += soup.find_all(id=re.compile(indicator, re.I))

                    for section in comment_sections:
                        if isinstance(section, Tag):
                            comments_data['comment_sections'].append({
                                'id': section.get('id', ''),
                                'class': section.get('class') or [],
                                'comments_count': len(section.find_all(class_=re.compile('comment-item|review-item', re.I)))
                            })

                # البحث عن أنظمة التقييم
                rating_elements = soup.find_all(class_=re.compile('rating|star|score', re.I))
                for rating in rating_elements:
                    if isinstance(rating, Tag):
                        comments_data['rating_systems'].append({
                            'class': rating.get('class') or [],
                            'type': 'stars' if 'star' in str(rating.get('class', [])).lower() else 'numeric'
                        })

                # البحث عن نماذج المراجعة
                review_forms = soup.find_all('form', class_=re.compile('review|comment|feedback', re.I))
                for form in review_forms:
                    if isinstance(form, Tag):
                        comments_data['review_forms'].append({
                            'action': form.get('action', ''),
                            'has_rating': bool(form.find_all('input', type='radio'))
                        })

                # البحث عن مشاركة اجتماعية
                social_indicators = ['share', 'facebook', 'twitter', 'linkedin', 'social']
                for indicator in social_indicators:
                    social_elements = soup.find_all(class_=re.compile(indicator, re.I))
                    if social_elements:
                        comments_data['social_sharing'].append({
                            'platform': indicator,
                            'elements_count': len(social_elements)
                        })

        return comments_data

    async def _extract_website_behavior(self, url: str) -> Dict[str, Any]:
        """استخراج سلوك الموقع حسب المتطلبات"""
        logging.info("استخراج سلوك الموقع...")

        behavior_data = {
            'javascript_events': [],
            'ajax_calls': [],
            'local_storage_usage': {},
            'responsive_behavior': {},
            'loading_states': {},
            'error_handling': {}
        }

        # تحليل JavaScript Events
        behavior_data['javascript_events'] = await self._analyze_javascript_events(url)

        # تحليل AJAX calls
        behavior_data['ajax_calls'] = await self._analyze_ajax_calls(url)

        # تحليل Local Storage والكوكيز
        behavior_data['local_storage_usage'] = await self._analyze_storage_usage(url)

        # تحليل السلوك المتجاوب
        behavior_data['responsive_behavior'] = await self._analyze_responsive_behavior(url)

        # تحليل حالات التحميل
        behavior_data['loading_states'] = await self._analyze_loading_states(url)

        # تحليل إدارة الأخطاء
        behavior_data['error_handling'] = await self._analyze_error_handling(url)

        return behavior_data

    async def _multi_engine_extraction(self, url: str) -> Dict[str, Any]:
        """استخراج شامل باستخدام محركات متعددة حسب المتطلبات"""
        logging.info("تشغيل محركات الاستخراج المتعددة...")

        engines_data = {
            'playwright_results': {},
            'selenium_results': {},
            'trafilatura_results': {},
            'beautifulsoup_results': {}
        }

        # استخراج باستخدام Playwright للمواقع التفاعلية والـ SPAs
        if self.config.enable_playwright and PLAYWRIGHT_AVAILABLE:
            engines_data['playwright_results'] = await self._playwright_extraction(url)

        # استخراج باستخدام Selenium للمواقع المعقدة
        if self.config.enable_selenium:
            engines_data['selenium_results'] = await self._selenium_extraction(url)

        # استخراج باستخدام Trafilatura للنصوص والمحتوى
        if TRAFILATURA_AVAILABLE:
            engines_data['trafilatura_results'] = await self._trafilatura_extraction(url)

        # استخراج باستخدام BeautifulSoup للتحليل التفصيلي
        engines_data['beautifulsoup_results'] = await self._beautifulsoup_extraction(url)

        return engines_data

    # Methods implementation continues...
    # Due to length constraints, implementing key helper methods:

    def _safe_get_text(self, element) -> str:
        """استخراج النص بأمان من عنصر BeautifulSoup"""
        if element and hasattr(element, 'get_text'):
            return element.get_text().strip()
        elif element and hasattr(element, 'string') and element.string:
            return str(element.string).strip()
        return ''

    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str:
        """استخراج محتوى meta tag"""
        meta = soup.find('meta', attrs={'name': name})
        if meta and isinstance(meta, Tag):
            content = meta.get('content')
            if content:
                return str(content) if isinstance(content, list) else str(content)
            return ''
        return ''

    def _get_language(self, soup: BeautifulSoup) -> str:
        """استخراج لغة الصفحة"""
        html_tag = soup.find('html')
        if html_tag and isinstance(html_tag, Tag):
            lang = html_tag.get('lang')
            if lang:
                return str(lang) if isinstance(lang, list) else str(lang)
            return 'unknown'
        return 'unknown'

    def _get_charset(self, soup: BeautifulSoup) -> str:
        """استخراج ترميز الصفحة"""
        charset_meta = soup.find('meta', charset=True)
        if charset_meta and isinstance(charset_meta, Tag):
            charset = charset_meta.get('charset')
            return str(charset) if charset else 'UTF-8'
        return 'UTF-8'

    
    

    async def _extract_behavior_analysis(self, url: str) -> Dict[str, Any]:
        """تحليل السلوك الشامل للموقع"""
        logging.info("تحليل سلوك الموقع...")

        # استخدام المحرك الجديد
        return await self._extract_website_behavior(url)

    # محركات إضافية متقدمة
    async def _playwright_extraction(self, url: str) -> Dict[str, Any]:
        """استخراج باستخدام Playwright للمواقع التفاعلية"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url)

                # انتظار تحميل المحتوى الديناميكي
                await page.wait_for_load_state('networkidle')

                extraction_data = {
                    'dom_content': await page.content(),
                    'title': await page.title(),
                    'url': page.url,
                    'viewport': page.viewport_size,
                    'screenshots': {},
                    'network_requests': [],
                    'console_logs': [],
                    'javascript_errors': []
                }

                # تسجيل طلبات الشبكة
                requests = []
                page.on('request', lambda request: requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': request.headers,
                    'resource_type': request.resource_type
                }))

                # تسجيل console logs
                console_logs = []
                page.on('console', lambda msg: console_logs.append({
                    'type': msg.type,
                    'text': msg.text,
                    'location': msg.location
                }))

                # تسجيل أخطاء JavaScript
                js_errors = []
                page.on('pageerror', lambda error: js_errors.append({
                    'message': str(error),
                    'stack': getattr(error, 'stack', '')
                }))

                # أخذ لقطات شاشة بأحجام مختلفة
                await page.set_viewport_size({'width': 1920, 'height': 1080})
                extraction_data['screenshots']['desktop'] = await page.screenshot()

                await page.set_viewport_size({'width': 768, 'height': 1024})
                extraction_data['screenshots']['tablet'] = await page.screenshot()

                await page.set_viewport_size({'width': 375, 'height': 667})
                extraction_data['screenshots']['mobile'] = await page.screenshot()

                # تحليل عناصر التفاعل
                interactive_elements = await page.evaluate('''
                    () => {
                        const elements = [];
                        document.querySelectorAll('button, input, select, textarea, a[href], [onclick], [onchange]').forEach(el => {
                            elements.push({
                                tag: el.tagName,
                                type: el.type || '',
                                id: el.id || '',
                                class: el.className || '',
                                text: el.textContent.trim().substring(0, 100),
                                href: el.href || '',
                                onclick: el.onclick ? el.onclick.toString() : ''
                            });
                        });
                        return elements;
                    }
                ''')

                extraction_data['interactive_elements'] = interactive_elements
                extraction_data['network_requests'] = requests
                extraction_data['console_logs'] = console_logs
                extraction_data['javascript_errors'] = js_errors

                await browser.close()
                return extraction_data

        except ImportError:
            logging.warning("Playwright غير متوفر - تم تخطي الاستخراج")
            return {'error': 'playwright_not_available'}
        except Exception as e:
            logging.error(f"خطأ في استخراج Playwright: {e}")
            return {'error': str(e)}

    

    async def _trafilatura_extraction(self, url: str) -> Dict[str, Any]:
        """استخراج باستخدام Trafilatura للنصوص والمحتوى"""
        try:
            import trafilatura

            # تحميل وتحليل الصفحة
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return {'error': 'failed_to_fetch'}

            # استخراج النص الرئيسي
            main_text = trafilatura.extract(downloaded)

            # استخراج البيانات الوصفية
            metadata = trafilatura.extract_metadata(downloaded)

            # استخراج التعليقات إن وجدت (تحقق من توفر الوظيفة)
            comments = []
            if hasattr(trafilatura, 'extract_comments'):
                try:
                    comments = trafilatura.extract_comments(downloaded) or []
                except:
                    comments = []

            # استخراج الروابط (تحقق من توفر الوظيفة)
            links = []
            if hasattr(trafilatura, 'extract_links'):
                try:
                    links = trafilatura.extract_links(downloaded) or []
                except:
                    links = []

            extraction_data = {
                'main_text': main_text or '',
                'metadata': {
                    'title': metadata.title if metadata else '',
                    'author': metadata.author if metadata else '',
                    'description': metadata.description if metadata else '',
                    'date': str(metadata.date) if metadata and metadata.date else '',
                    'language': metadata.language if metadata else '',
                    'url': metadata.url if metadata else url
                },
                'comments': comments or [],
                'links': links or [],
                'word_count': len(main_text.split()) if main_text else 0,
                'extraction_method': 'trafilatura'
            }

            return extraction_data

        except ImportError:
            logging.warning("Trafilatura غير متوفر - تم تخطي الاستخراج")
            return {'error': 'trafilatura_not_available'}
        except Exception as e:
            logging.error(f"خطأ في استخراج Trafilatura: {e}")
            return {'error': str(e)}

    async def _beautifulsoup_extraction(self, url: str) -> Dict[str, Any]:
        """استخراج باستخدام BeautifulSoup للتحليل التفصيلي"""
        try:
            if not self.session:
                return {'error': 'no_session'}

            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                extraction_data = {
                    'title': soup.title.string if soup.title else '',
                    'meta_tags': [],
                    'headings': {},
                    'links': [],
                    'images': [],
                    'forms': [],
                    'tables': [],
                    'scripts': [],
                    'stylesheets': [],
                    'text_content': soup.get_text().strip(),
                    'language': self._get_language(soup),
                    'charset': self._get_charset(soup)
                }

                # استخراج meta tags
                for meta in soup.find_all('meta'):
                    if isinstance(meta, Tag):
                        meta_data = {
                            'name': meta.get('name', ''),
                            'property': meta.get('property', ''),
                            'content': meta.get('content', ''),
                            'http_equiv': meta.get('http-equiv', '')
                        }
                        extraction_data['meta_tags'].append(meta_data)

                # استخراج العناوين
                for i in range(1, 7):
                    headings = soup.find_all(f'h{i}')
                    extraction_data['headings'][f'h{i}'] = [
                        self._safe_get_text(h) for h in headings if isinstance(h, Tag)
                    ]

                # استخراج الروابط
                for link in soup.find_all('a', href=True):
                    if isinstance(link, Tag):
                        href = link.get('href', '')
                        if isinstance(href, str):
                            extraction_data['links'].append({
                                'text': self._safe_get_text(link),
                                'href': href,
                                'title': link.get('title', ''),
                                'class': link.get('class') or []
                            })

                # استخراج الصور
                for img in soup.find_all('img'):
                    if isinstance(img, Tag):
                        extraction_data['images'].append({
                            'src': img.get('src', ''),
                            'alt': img.get('alt', ''),
                            'title': img.get('title', ''),
                            'class': img.get('class') or []
                        })

                # استخراج النماذج
                for form in soup.find_all('form'):
                    if isinstance(form, Tag):
                        inputs = form.find_all(['input', 'select', 'textarea'])
                        extraction_data['forms'].append({
                            'action': form.get('action', ''),
                            'method': form.get('method', 'get'),
                            'id': form.get('id', ''),
                            'class': form.get('class') or [],
                            'inputs_count': len(inputs)
                        })

                # استخراج الجداول
                for table in soup.find_all('table'):
                    if isinstance(table, Tag):
                        rows = table.find_all('tr')
                        extraction_data['tables'].append({
                            'rows_count': len(rows),
                            'class': table.get('class') or [],
                            'id': table.get('id', '')
                        })

                # استخراج السكريبتات
                for script in soup.find_all('script'):
                    if isinstance(script, Tag):
                        extraction_data['scripts'].append({
                            'src': script.get('src', ''),
                            'type': script.get('type', 'text/javascript'),
                            'async': script.has_attr('async'),
                            'defer': script.has_attr('defer'),
                            'inline': bool(script.string)
                        })

                # استخراج CSS
                for link in soup.find_all('link', rel='stylesheet'):
                    if isinstance(link, Tag):
                        extraction_data['stylesheets'].append({
                            'href': link.get('href', ''),
                            'media': link.get('media', 'all'),
                            'type': link.get('type', 'text/css')
                        })

                return extraction_data

        except Exception as e:
            logging.error(f"خطأ في استخراج BeautifulSoup: {e}")
            return {'error': str(e)}

    # إضافة الدوال المساعدة المفقودة للسلوك
    async def _analyze_javascript_events(self, url: str) -> List[Dict[str, Any]]:
        """تحليل أحداث JavaScript في الصفحة"""
        events = []

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # البحث عن معالجات الأحداث في HTML
                event_attributes = ['onclick', 'onchange', 'onsubmit', 'onload', 'onmouseover']
                for attr in event_attributes:
                    elements = soup.find_all(attrs={attr: True})
                    for element in elements:
                        if isinstance(element, Tag):
                            events.append({
                                'element': element.name,
                                'event': attr,
                                'handler': element.get(attr, ''),
                                'id': element.get('id', ''),
                                'class': element.get('class') or []
                            })

        return events

    async def _analyze_ajax_calls(self, url: str) -> List[Dict[str, Any]]:
        """تحليل استدعاءات AJAX في الصفحة"""
        ajax_calls = []

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()

                # البحث عن أنماط AJAX في JavaScript
                import re
                ajax_patterns = [
                    r'fetch\([\'"]([^\'"]+)[\'"]',
                    r'axios\.[get|post|put|delete|patch]+\([\'"]([^\'"]+)[\'"]',
                    r'XMLHttpRequest.*?open\([\'"](\w+)[\'"],\s*[\'"]([^\'"]+)[\'"]',
                    r'\$\.ajax\({.*?url:\s*[\'"]([^\'"]+)[\'"]',
                    r'\$\.get\([\'"]([^\'"]+)[\'"]',
                    r'\$\.post\([\'"]([^\'"]+)[\'"]'
                ]

                for pattern in ajax_patterns:
                    matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        if len(match.groups()) >= 1:
                            url_match = match.group(1)
                            method = 'GET'
                            if 'post' in pattern.lower():
                                method = 'POST'
                            elif len(match.groups()) >= 2:
                                method = match.group(1).upper()
                                url_match = match.group(2)

                            ajax_calls.append({
                                'url': url_match,
                                'method': method,
                                'pattern': pattern,
                                'context': match.group(0)[:100]
                            })

        return ajax_calls

    async def _analyze_storage_usage(self, url: str) -> Dict[str, Any]:
        """تحليل استخدام Local Storage والكوكيز"""
        storage_data = {
            'local_storage_references': [],
            'session_storage_references': [],
            'cookie_references': [],
            'indexeddb_references': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()

                # البحث عن مراجع التخزين المحلي
                import re
                storage_patterns = {
                    'localStorage': r'localStorage\.[getItem|setItem|removeItem|clear]+',
                    'sessionStorage': r'sessionStorage\.[getItem|setItem|removeItem|clear]+',
                    'document.cookie': r'document\.cookie\s*[=]',
                    'indexedDB': r'indexedDB\.[open|transaction]+'
                }

                for storage_type, pattern in storage_patterns.items():
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    storage_data[f"{storage_type.lower().replace('.', '_')}_references"] = matches

        return storage_data

    async def _analyze_responsive_behavior(self, url: str) -> Dict[str, Any]:
        """تحليل السلوك المتجاوب للموقع"""
        responsive_data = {
            'viewport_meta': False,
            'media_queries': [],
            'responsive_images': False,
            'flexible_layout': False
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # فحص viewport meta tag
                viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
                if viewport_meta:
                    responsive_data['viewport_meta'] = True

                # البحث عن media queries في CSS المضمن
                import re
                media_query_pattern = r'@media[^{]+{'
                media_queries = re.findall(media_query_pattern, html_content, re.IGNORECASE)
                responsive_data['media_queries'] = media_queries

                # فحص الصور المتجاوبة
                responsive_imgs = soup.find_all('img', srcset=True)
                responsive_data['responsive_images'] = len(responsive_imgs) > 0

                # فحص تخطيط مرن
                flexible_indicators = ['flex', 'grid', 'bootstrap', 'container-fluid']
                for indicator in flexible_indicators:
                    if indicator in html_content.lower():
                        responsive_data['flexible_layout'] = True
                        break

        return responsive_data

    async def _analyze_loading_states(self, url: str) -> Dict[str, Any]:
        """تحليل حالات التحميل في الموقع"""
        loading_data = {
            'loading_indicators': [],
            'lazy_loading': False,
            'progress_bars': [],
            'spinners': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # البحث عن مؤشرات التحميل
                loading_indicators = ['loading', 'loader', 'spinner', 'progress']
                for indicator in loading_indicators:
                    elements = soup.find_all(class_=re.compile(indicator, re.I))
                    if elements:
                        loading_data['loading_indicators'].extend([
                            {'class': elem.get('class') or [], 'tag': elem.name}
                            for elem in elements if isinstance(elem, Tag)
                        ])

                # فحص lazy loading
                lazy_images = soup.find_all('img', loading='lazy')
                lazy_images += soup.find_all('img', attrs={'data-src': True})
                loading_data['lazy_loading'] = len(lazy_images) > 0

                # البحث عن أشرطة التقدم
                progress_bars = soup.find_all(['progress', 'div'], class_=re.compile('progress', re.I))
                loading_data['progress_bars'] = [
                    {'class': bar.get('class') or [], 'tag': bar.name}
                    for bar in progress_bars if isinstance(bar, Tag)
                ]

        return loading_data

    async def _analyze_error_handling(self, url: str) -> Dict[str, Any]:
        """تحليل إدارة الأخطاء في الموقع"""
        error_data = {
            'error_pages': [],
            'try_catch_blocks': 0,
            'error_messages': [],
            'fallback_content': []
        }

        if self.session:
            async with self.session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # البحث عن رسائل الخطأ
                error_indicators = ['error', 'alert', 'warning', 'danger']
                for indicator in error_indicators:
                    error_elements = soup.find_all(class_=re.compile(indicator, re.I))
                    for elem in error_elements:
                        if isinstance(elem, Tag):
                            error_data['error_messages'].append({
                                'class': elem.get('class') or [],
                                'text': self._safe_get_text(elem)[:100],
                                'type': indicator
                            })

                # عد try-catch blocks في JavaScript
                try_catch_pattern = re.compile(r'try\s*{.*?catch', re.IGNORECASE | re.DOTALL)
                try_catch_count = len(try_catch_pattern.findall(html_content))
                error_data['try_catch_blocks'] = try_catch_count

                # البحث عن محتوى احتياطي
                fallback_elements = soup.find_all(attrs={'data-fallback': True})
                fallback_elements += soup.find_all('noscript')
                error_data['fallback_content'] = [
                    {'tag': elem.name, 'content': self._safe_get_text(elem)[:50]}
                    for elem in fallback_elements if isinstance(elem, Tag)
                ]

        return error_data

    
        """استخراج باستخدام Selenium للمواقع المعقدة"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.get(url)

                # انتظار تحميل الصفحة
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                extraction_data = {
                    'page_source': driver.page_source,
                    'current_url': driver.current_url,
                    'title': driver.title,
                    'cookies': driver.get_cookies(),
                    'local_storage': {},
                    'session_storage': {},
                    'forms_data': [],
                    'links_data': []
                }

                # استخراج Local Storage
                try:
                    local_storage = driver.execute_script("return window.localStorage;")
                    extraction_data['local_storage'] = local_storage or {}
                except:
                    extraction_data['local_storage'] = {}

                # استخراج Session Storage
                try:
                    session_storage = driver.execute_script("return window.sessionStorage;")
                    extraction_data['session_storage'] = session_storage or {}
                except:
                    extraction_data['session_storage'] = {}

                # تحليل النماذج
                forms = driver.find_elements(By.TAG_NAME, "form")
                for form in forms:
                    form_data = {
                        'action': form.get_attribute('action') or '',
                        'method': form.get_attribute('method') or 'get',
                        'fields': []
                    }

                    fields = form.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                    for field in fields:
                        form_data['fields'].append({
                            'tag': field.tag_name,
                            'type': field.get_attribute('type') or '',
                            'name': field.get_attribute('name') or '',
                            'id': field.get_attribute('id') or '',
                            'required': field.get_attribute('required') is not None,
                            'placeholder': field.get_attribute('placeholder') or ''
                        })

                    extraction_data['forms_data'].append(form_data)

                # تحليل الروابط
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links[:50]:  # تحديد العدد لتجنب البطء
                    extraction_data['links_data'].append({
                        'text': link.text.strip(),
                        'href': link.get_attribute('href') or '',
                        'title': link.get_attribute('title') or '',
                        'target': link.get_attribute('target') or ''
                    })

                return extraction_data

            finally:
                driver.quit()

        except ImportError:
            logging.warning("Selenium غير متوفر - تم تخطي الاستخراج")
            return {'error': 'selenium_not_available'}
        except Exception as e:
            logging.error(f"خطأ في Selenium extraction: {e}")
            return {'error': str(e)}

    
        """استخراج النصوص والمحتوى باستخدام Trafilatura"""
        try:
            import trafilatura

            if self.session:
                async with self.session.get(url) as response:
                    html_content = await response.text()

                    # استخراج النص الرئيسي
                    main_text = trafilatura.extract(html_content)

                    # استخراج معلومات إضافية
                    metadata = trafilatura.extract_metadata(html_content)

                    return {
                        'main_text': main_text or '',
                        'metadata': metadata.__dict__ if metadata else {},
                        'word_count': len(main_text.split()) if main_text else 0,
                        'language': metadata.language if metadata else 'unknown',
                        'title': metadata.title if metadata else '',
                        'author': metadata.author if metadata else '',
                        'date': metadata.date if metadata else '',
                        'description': metadata.description if metadata else ''
                    }

            return {'error': 'no_session_available'}

        except ImportError:
            logging.warning("Trafilatura غير متوفر - تم تخطي الاستخراج")
            return {'error': 'trafilatura_not_available'}
        except Exception as e:
            logging.error(f"خطأ في Trafilatura extraction: {e}")
            return {'error': str(e)}

    
        """استخراج شامل باستخدام BeautifulSoup"""
        if not self.session:
            return {'error': 'no_session_available'}

        async with self.session.get(url) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')

            extraction_data = {
                'document_structure': await self._analyze_document_structure(soup),
                'content_analysis': await self._analyze_content_structure(soup),
                'seo_analysis': await self._analyze_seo_elements(soup),
                'accessibility_analysis': await self._analyze_accessibility(soup),
                'performance_hints': await self._analyze_performance_hints(soup)
            }

            return extraction_data

    async def _analyze_document_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل بنية المستند"""
        return {
            'doctype': str(soup.contents[0]) if soup.contents and hasattr(soup.contents[0], 'name') else 'html5',
            'html_attributes': soup.html.attrs if soup.html else {},
            'head_elements_count': len(soup.find_all(['meta', 'link', 'script', 'style'])),
            'body_structure': {
                'sections': len(soup.find_all('section')),
                'articles': len(soup.find_all('article')),
                'headers': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'paragraphs': len(soup.find_all('p')),
                'lists': len(soup.find_all(['ul', 'ol'])),
                'tables': len(soup.find_all('table')),
                'forms': len(soup.find_all('form')),
                'images': len(soup.find_all('img')),
                'links': len(soup.find_all('a', href=True))
            }
        }

    async def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل بنية المحتوى"""
        headings_hierarchy = []
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for heading in headings:
                if isinstance(heading, Tag):
                    headings_hierarchy.append({
                        'level': i,
                        'text': self._safe_get_text(heading),
                        'id': heading.get('id', ''),
                        'class': heading.get('class', [])
                    })

        # تحليل القوائم
        lists_analysis = []
        for list_type in ['ul', 'ol']:
            lists = soup.find_all(list_type)
            for lst in lists:
                if isinstance(lst, Tag):
                    items = lst.find_all('li')
                    lists_analysis.append({
                        'type': list_type,
                        'items_count': len(items),
                        'nested': len(lst.find_all(['ul', 'ol'])) > 0,
                        'class': lst.get('class', [])
                    })

        return {
            'headings_hierarchy': headings_hierarchy,
            'lists_analysis': lists_analysis,
            'text_blocks': len(soup.find_all(['p', 'div', 'span'])),
            'content_sections': len(soup.find_all(['section', 'article', 'aside']))
        }

    async def _analyze_seo_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل عناصر SEO"""
        seo_data = {
            'title': self._safe_get_text(soup.find('title')),
            'meta_description': self._get_meta_content(soup, 'description'),
            'meta_keywords': self._get_meta_content(soup, 'keywords'),
            'canonical_url': '',
            'og_tags': {},
            'twitter_tags': {},
            'structured_data': [],
            'alt_texts': {'missing': 0, 'present': 0}
        }

        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and isinstance(canonical, Tag):
            seo_data['canonical_url'] = canonical.get('href', '')

        # Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            if isinstance(tag, Tag):
                prop = tag.get('property', '')
                content = tag.get('content', '')
                if prop and content:
                    seo_data['og_tags'][prop] = content

        # Twitter tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            if isinstance(tag, Tag):
                name = tag.get('name', '')
                content = tag.get('content', '')
                if name and content:
                    seo_data['twitter_tags'][name] = content

        # تحليل alt texts للصور
        images = soup.find_all('img')
        for img in images:
            if isinstance(img, Tag):
                if img.get('alt'):
                    seo_data['alt_texts']['present'] += 1
                else:
                    seo_data['alt_texts']['missing'] += 1

        return seo_data

    async def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل إمكانية الوصول"""
        accessibility_data = {
            'aria_labels': 0,
            'alt_attributes': 0,
            'heading_structure': [],
            'form_labels': {'labeled': 0, 'unlabeled': 0},
            'skip_links': 0,
            'color_contrast_issues': []
        }

        # عد aria-label attributes
        accessibility_data['aria_labels'] = len(soup.find_all(attrs={'aria-label': True}))

        # عد alt attributes
        accessibility_data['alt_attributes'] = len(soup.find_all('img', alt=True))

        # تحليل بنية العناوين
        for i in range(1, 7):
            count = len(soup.find_all(f'h{i}'))
            if count > 0:
                accessibility_data['heading_structure'].append({'level': i, 'count': count})

        # تحليل labels للنماذج
        forms = soup.find_all('form')
        for form in forms:
            if isinstance(form, Tag):
                inputs = form.find_all(['input', 'select', 'textarea'])
                for inp in inputs:
                    if isinstance(inp, Tag):
                        input_id = inp.get('id')
                        if input_id and soup.find('label', attrs={'for': input_id}):
                            accessibility_data['form_labels']['labeled'] += 1
                        else:
                            accessibility_data['form_labels']['unlabeled'] += 1

        # البحث عن skip links
        skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
        accessibility_data['skip_links'] = len([link for link in skip_links 
                                               if 'skip' in self._safe_get_text(link).lower()])

        return accessibility_data

    async def _analyze_performance_hints(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل تلميحات الأداء"""
        performance_data = {
            'external_resources': {'css': 0, 'js': 0, 'fonts': 0, 'images': 0},
            'preload_hints': 0,
            'prefetch_hints': 0,
            'compression_hints': [],
            'caching_hints': [],
            'lazy_loading': 0
        }

        # عد الموارد الخارجية
        external_css = soup.find_all('link', rel='stylesheet', href=True)
        performance_data['external_resources']['css'] = len(external_css)

        external_js = soup.find_all('script', src=True)
        performance_data['external_resources']['js'] = len(external_js)

        external_fonts = soup.find_all('link', href=lambda x: x and any(
            font_ext in x for font_ext in ['.woff', '.woff2', '.ttf', '.otf']))
        performance_data['external_resources']['fonts'] = len(external_fonts)

        external_images = soup.find_all('img', src=True)
        performance_data['external_resources']['images'] = len(external_images)

        # preload/prefetch hints
        performance_data['preload_hints'] = len(soup.find_all('link', rel='preload'))
        performance_data['prefetch_hints'] = len(soup.find_all('link', rel='prefetch'))

        # lazy loading
        performance_data['lazy_loading'] = len(soup.find_all(attrs={'loading': 'lazy'}))

        return performance_data

    def _calculate_extraction_statistics(self) -> Dict[str, Any]:
        """حساب إحصائيات الاستخراج"""
        return {
            'total_urls_visited': len(self.visited_urls),
            'api_endpoints_discovered': len(self.api_endpoints),
            'javascript_events_found': len(self.javascript_events),
            'css_frameworks_detected': len(self.css_frameworks),
            'interactive_elements_found': len(self.interactive_elements),
            'authentication_methods_detected': len(self.authentication_methods)
        }

    async def _save_extraction_results(self, results: Dict[str, Any]):
        """حفظ نتائج الاستخراج"""
        extraction_id = results['metadata']['extraction_id']

        # حفظ التقرير الكامل
        report_file = self.paths['reports'] / f"extraction_report_{extraction_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logging.info(f"تم حفظ تقرير الاستخراج: {report_file}")

    async def _cleanup_resources(self):
        """تنظيف الموارد"""
        if self.session and not self.session.closed:
            await self.session.close()

        for driver in self.drivers.values():
            try:
                if hasattr(driver, 'quit'):
                    driver.quit()
            except Exception:
                pass

    # Placeholder implementations for complex methods
    # These would be implemented with full functionality in production

    def _analyze_head_elements(self, soup): return {}
    def _analyze_body_structure(self, soup): return {}
    def _detect_initial_technologies(self, soup, response): return {}
    async def _analyze_database_indicators(self, url): return {}
    async def _discover_api_endpoints(self, url): return []
    async def _analyze_javascript_logic(self, url): return {}
    async def _analyze_routing_system(self, url): return {}
    async def _analyze_interactive_components(self, url): return {}
    async def _analyze_authentication_system(self, url): return {}
    async def _analyze_cms_system(self, url): return {}
    async def _analyze_search_functionality(self, url): return {}
    async def _analyze_navigation_system(self, url): return {}
    async def _analyze_charts_and_interaction(self, url): return {}
    async def _analyze_comments_rating_system(self, url): return {}
    async def _analyze_javascript_events(self, url): return []
    async def _analyze_ajax_calls(self, url): return []
    async def _analyze_storage_usage(self, url): return {}
    async def _analyze_responsive_behavior(self, url): return {}
    async def _analyze_loading_states(self, url): return {}
    async def _analyze_error_handling(self, url): return {}
    
    async def _trafilatura_extraction(self, url): return {}
    async def _beautifulsoup_extraction(self, url): return {}

    
        """تحميل ملف نصي (CSS, JS)"""
        try:
            async with self.session.get(asset_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    # حفظ الملف محلياً
                    await self._save_asset_locally(asset_url, content, 'text')
                    return content
        except Exception as e:
            logging.warning(f"فشل تحميل {asset_url}: {e}")
        return None

    
        """تحميل ملف ثنائي (صور، خطوط)"""
        try:
            async with self.session.get(asset_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    content = await response.read()
                    # حفظ الملف محلياً
                    await self._save_asset_locally(asset_url, content, 'binary')
                    return content
        except Exception as e:
            logging.warning(f"فشل تحميل {asset_url}: {e}")
        return None

    async def _save_asset_locally(self, asset_url: str, content: Any, content_type: str):
        """حفظ الملف محلياً"""
        try:
            parsed_url = urlparse(asset_url)
            filename = os.path.basename(parsed_url.path) or 'asset'

            # تحديد نوع الملف والمجلد المناسب
            if content_type == 'text':
                if filename.endswith('.css'):
                    file_path = self.paths['css'] / filename
                elif filename.endswith('.js'):
                    file_path = self.paths['js'] / filename
                else:
                    file_path = self.paths['data'] / filename

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            elif content_type == 'binary':
                if any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                    file_path = self.paths['images'] / filename
                elif any(filename.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.eot', '.otf']):
                    file_path = self.paths['fonts'] / filename
                else:
                    file_path = self.paths['data'] / filename

                with open(file_path, 'wb') as f:
                    f.write(content)

        except Exception as e:
            logging.error(f"خطأ في حفظ الملف {asset_url}: {e}")

    async def _extract_audio_video_files(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """استخراج الملفات الصوتية والمرئية"""
        media_files = {
            'audio_files': {},
            'video_files': {},
            'streaming_sources': []
        }

        # استخراج ملفات الصوت
        for audio in soup.find_all('audio'):
            if isinstance(audio, Tag):
                src = audio.get('src')
                if src:
                    audio_url = urljoin(base_url, src)
                    audio_data = await self._download_binary_asset(audio_url)
                    if audio_data:
                        filename = os.path.basename(urlparse(src).path)
                        media_files['audio_files'][filename] = {
                            'url': audio_url,
                            'size': len(audio_data),
                            'controls': audio.has_attr('controls'),
                            'autoplay': audio.has_attr('autoplay'),
                            'loop': audio.has_attr('loop')
                        }

                # استخراج مصادر متعددة
                for source in audio.find_all('source'):
                    if isinstance(source, Tag):
                        src = source.get('src')
                        if src:
                            media_files['streaming_sources'].append({
                                'url': urljoin(base_url, src),
                                'type': source.get('type', ''),
                                'media_type': 'audio'
                            })

        # استخراج ملفات الفيديو
        for video in soup.find_all('video'):
            if isinstance(video, Tag):
                src = video.get('src')
                if src:
                    video_url = urljoin(base_url, src)
                    # لا نحمل ملفات الفيديو الكبيرة، نحفظ المعلومات فقط
                    filename = os.path.basename(urlparse(src).path)
                    media_files['video_files'][filename] = {
                        'url': video_url,
                        'controls': video.has_attr('controls'),
                        'autoplay': video.has_attr('autoplay'),
                        'loop': video.has_attr('loop'),
                        'width': video.get('width', ''),
                        'height': video.get('height', ''),
                        'poster': video.get('poster', '')
                    }

                # استخراج مصادر متعددة
                for source in video.find_all('source'):
                    if isinstance(source, Tag):
                        src = source.get('src')
                        if src:
                            media_files['streaming_sources'].append({
                                'url': urljoin(base_url, src),
                                'type': source.get('type', ''),
                                'media_type': 'video'
                            })

        return media_files