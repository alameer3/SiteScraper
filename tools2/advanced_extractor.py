"""
واجهة الاستخراج المتطورة الموحدة
Unified Advanced Extraction Interface
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import re

try:
    from .core.extractor_engine import AdvancedExtractorEngine
    from .core.config import ExtractionConfig, get_preset_config
except ImportError:
    # معالجة مشكلة الاستيراد النسبي
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from core.extractor_engine import AdvancedExtractorEngine
    from core.config import ExtractionConfig, get_preset_config


class AdvancedWebsiteExtractor:
    """واجهة مبسطة لاستخدام محرك الاستخراج المتطور"""
    
    def __init__(self, output_directory: str = "extracted_files"):
        """تهيئة أداة الاستخراج"""
        self.output_directory = Path(output_directory)
        self.engine = None
        self.extraction_id = 0
        self.results = {}
        
        # إعداد جلسة HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # إنشاء مجلدات الإخراج
        self._setup_extraction_directories()
    
    def _setup_extraction_directories(self):
        """إعداد مجلدات الإخراج"""
        base_dirs = ['content', 'assets', 'analysis', 'exports', 'screenshots']
        for dir_name in base_dirs:
            (self.output_directory / dir_name).mkdir(parents=True, exist_ok=True)
        
    def extract(self, url: str, extraction_type: str = "standard", custom_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        استخراج شامل للموقع
        
        Args:
            url: رابط الموقع المراد استخراجه
            extraction_type: نوع الاستخراج (basic, standard, advanced, complete, ai_powered)
            custom_config: إعدادات مخصصة اختيارية
            
        Returns:
            Dict: نتائج الاستخراج الشاملة
        """
        
        # إعداد التكوين
        if custom_config:
            config = ExtractionConfig.from_dict(custom_config)
        else:
            config = get_preset_config(extraction_type)
        
        config.target_url = url
        config.output_directory = str(self.output_directory)
        
        # تهيئة المحرك
        self.engine = AdvancedExtractorEngine(config)
        
        # استخدام المحرك الجديد المحسن
        result = self._extract_website_enhanced(url, extraction_type)
            
        return result
    
    def _extract_website_enhanced(self, url: str, extraction_type: str) -> Dict[str, Any]:
        """محرك الاستخراج المحسن مع الوظائف المتقدمة"""
        self.extraction_id += 1
        extraction_id = f"extract_{self.extraction_id}_{int(time.time())}"
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
            elif extraction_type == 'standard':
                result = self._extract_advanced(soup, url, basic_info)
            elif extraction_type == 'advanced':
                result = self._extract_complete(soup, url, basic_info)
            elif extraction_type in ['complete', 'ai_powered']:
                result = self._extract_complete(soup, url, basic_info)
                # إضافة تحليل إضافي للـ ai_powered
                if extraction_type == 'ai_powered':
                    result['ai_features'] = {
                        'intelligent_analysis': True,
                        'pattern_recognition': True,
                        'smart_replication': True,
                        'quality_assessment': True
                    }
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
                'extractor': 'AdvancedWebsiteExtractor'
            })
            
            # حفظ الملفات المستخرجة
            extraction_folder = self._save_extraction_files(result, content, soup)
            result['extraction_folder'] = str(extraction_folder)
            
            # التقاط لقطات الشاشة (للأنواع المتقدمة)
            if extraction_type in ['advanced', 'complete', 'ai_powered']:
                try:
                    screenshot_result = self._capture_screenshots_simple(url, extraction_folder)
                    result['screenshots'] = screenshot_result
                except Exception as e:
                    result['screenshots'] = {'error': str(e), 'total_screenshots': 0}
            
            # تحليل AI متقدم (للنوع ai_powered)
            if extraction_type == 'ai_powered':
                try:
                    ai_result = self._advanced_ai_analysis(result, content, soup)
                    result['ai_analysis'] = ai_result
                except Exception as e:
                    result['ai_analysis'] = {'error': str(e), 'enabled': False}
            
            # إضافة إحصائيات شاملة
            result['extraction_stats'] = {
                'files_created': len(list(extraction_folder.rglob('*'))) if extraction_folder else 0,
                'folder_size_mb': self._calculate_folder_size(extraction_folder) if extraction_folder else 0,
                'extraction_quality': self._assess_extraction_quality(result),
                'completeness_score': self._calculate_completeness_score(result)
            }
            
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
                'extractor': 'AdvancedWebsiteExtractor'
            }
            self.results[extraction_id] = error_result
            return error_result
    
    def _extract_basic_info(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """استخراج المعلومات الأساسية"""
        domain = urlparse(url).netloc
        
        # العنوان
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'No title'
        
        # الوصف
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = ''
        if description_tag and hasattr(description_tag, 'get'):
            content = description_tag.get('content', '')
            description = str(content) if content else ''
        
        # الكلمات المفتاحية
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = ''
        if keywords_tag and hasattr(keywords_tag, 'get'):
            content = keywords_tag.get('content', '')
            keywords = str(content) if content else ''
        
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
    
    def _extract_advanced(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def _extract_complete(self, soup: BeautifulSoup, url: str, basic_info: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def extract_basic(self, url: str) -> Dict[str, Any]:
        """استخراج أساسي سريع"""
        return self.extract(url, "basic")
    
    def extract_standard(self, url: str) -> Dict[str, Any]:
        """استخراج قياسي مع تحليلات متقدمة"""
        return self.extract(url, "standard")
    
    def extract_advanced(self, url: str) -> Dict[str, Any]:
        """استخراج متقدم مع تحميل الأصول"""
        return self.extract(url, "advanced")
    
    def extract_complete(self, url: str) -> Dict[str, Any]:
        """استخراج شامل مع جميع الميزات"""
        return self.extract(url, "complete")
    
    def extract_with_custom_config(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج مع إعدادات مخصصة"""
        return self.extract(url, "custom", config)
    
    def get_available_presets(self) -> List[str]:
        """الحصول على أنواع الاستخراج المتاحة"""
        return ["basic", "standard", "advanced", "complete", "ai_powered"]
    
    def create_custom_config(self, 
                           extraction_type: str = "standard",
                           extract_assets: bool = True,
                           extract_images: bool = True,
                           capture_screenshots: bool = False,
                           analyze_security: bool = True,
                           analyze_seo: bool = True,
                           export_formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        إنشاء إعدادات مخصصة
        
        Args:
            extraction_type: نوع الاستخراج الأساسي
            extract_assets: تحميل الأصول
            extract_images: تحليل الصور
            capture_screenshots: التقاط لقطات الشاشة
            analyze_security: تحليل الأمان
            analyze_seo: تحليل SEO
            export_formats: صيغ التصدير ['json', 'csv', 'html', 'pdf']
            
        Returns:
            Dict: إعدادات مخصصة
        """
        
        if export_formats is None:
            export_formats = ['json', 'html']
        
        config = get_preset_config(extraction_type)
        
        # تحديث الإعدادات المخصصة
        config.extract_assets = extract_assets
        config.extract_images = extract_images
        config.capture_screenshots = capture_screenshots
        config.analyze_security = analyze_security
        config.analyze_seo = analyze_seo
        
        # إعدادات التصدير
        config.export_json = 'json' in export_formats
        config.export_csv = 'csv' in export_formats
        config.export_html = 'html' in export_formats
        config.export_pdf = 'pdf' in export_formats
        
        return config.to_dict()
    
    # ==================== الوظائف المساعدة المتقدمة ====================
    
    def _detect_technologies(self, soup: BeautifulSoup, content: str) -> List[str]:
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
    
    def _analyze_performance(self, response, content_size: int) -> Dict[str, Any]:
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
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل الروابط"""
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        email_links = []
        
        for link in links:
            href = link.get('href') if hasattr(link, 'get') else None
            text = link.get_text().strip() if hasattr(link, 'get_text') else ''
            
            if href and isinstance(href, str):
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
    
    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل الصور"""
        images = soup.find_all('img', src=True)
        
        image_analysis = []
        for img in images[:20]:  # أول 20 صورة
            src = img.get('src') if hasattr(img, 'get') else None
            alt = img.get('alt', '') if hasattr(img, 'get') else ''
            
            if src and isinstance(src, str):
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                
                width = img.get('width', '') if hasattr(img, 'get') else ''
                height = img.get('height', '') if hasattr(img, 'get') else ''
                img_class = img.get('class', []) if hasattr(img, 'get') else []
                
                image_analysis.append({
                    'src': src,
                    'alt': str(alt) if alt else '',
                    'width': str(width) if width else '',
                    'height': str(height) if height else '',
                    'class': img_class if isinstance(img_class, list) else []
                })
        
        return {
            'total_images': len(images),
            'images': image_analysis,
            'lazy_loading': len(soup.find_all('img', loading='lazy'))
        }
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل SEO"""
        # Meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            if hasattr(meta, 'get'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[str(name)] = str(content)
        
        # Headings structure
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        schema_data = []
        for script in schema_scripts:
            try:
                if script.string:
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
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
    
    def _analyze_security(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
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
            src = script.get('src') if hasattr(script, 'get') else None
            if src and isinstance(src, str) and not src.startswith('/'):
                security_analysis['external_scripts'].append(src)
        
        # تحليل الـ stylesheets الخارجية
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href') if hasattr(link, 'get') else None
            if href and isinstance(href, str) and not href.startswith('/'):
                security_analysis['external_stylesheets'].append(href)
        
        # تحليل النماذج
        for form in soup.find_all('form'):
            method = 'get'
            action = ''
            if hasattr(form, 'get'):
                method_attr = form.get('method', 'get')
                method = str(method_attr).lower() if method_attr else 'get'
                action_attr = form.get('action', '')
                action = str(action_attr) if action_attr else ''
            
            has_csrf = bool(form.find('input', attrs={'name': re.compile('csrf|token', re.I)}) if hasattr(form, 'find') else False)
            inputs_count = len(form.find_all('input')) if hasattr(form, 'find_all') else 0
            
            security_analysis['forms_analysis'].append({
                'method': method,
                'action': action,
                'has_csrf_protection': has_csrf,
                'inputs_count': inputs_count
            })
        
        return security_analysis
    
    def _find_api_endpoints(self, soup: BeautifulSoup) -> List[str]:
        """البحث عن API endpoints"""
        endpoints = []
        
        # البحث في الـ JavaScript
        for script in soup.find_all('script'):
            script_content = script.string if hasattr(script, 'string') and script.string else ''
            if script_content and isinstance(script_content, str):
                # البحث عن fetch أو Ajax calls
                api_calls = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]', script_content)
                api_calls.extend(re.findall(r'\.get\([\'"`]([^\'"`]+)[\'"`]', script_content))
                api_calls.extend(re.findall(r'\.post\([\'"`]([^\'"`]+)[\'"`]', script_content))
                endpoints.extend(api_calls)
        
        return list(set(endpoints))
    
    def _analyze_database_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
        
        database_hints['field_names'] = list(database_hints['field_names'])
        return database_hints
    
    def _analyze_interactive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
    
    def _ai_content_analysis(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
    
    def _generate_clone_strategy(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
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
    
    # ==================== وظائف التقييم والإحصائيات ====================
    
    def _calculate_folder_size(self, folder: Path) -> float:
        """حساب حجم المجلد بالميجابايت"""
        try:
            total_size = 0
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return round(total_size / (1024 * 1024), 2)  # تحويل إلى MB
        except Exception:
            return 0.0
    
    def _assess_extraction_quality(self, result: Dict[str, Any]) -> str:
        """تقييم جودة الاستخراج"""
        score = 0
        
        # فحص وجود البيانات الأساسية
        if result.get('title'): score += 1
        if result.get('description'): score += 1
        if result.get('links_count', 0) > 0: score += 1
        if result.get('images_count', 0) > 0: score += 1
        if result.get('technologies'): score += 1
        
        # فحص البيانات المتقدمة
        if result.get('seo_analysis'): score += 1
        if result.get('structure_analysis'): score += 1
        if result.get('security_analysis'): score += 1
        
        if score >= 7:
            return 'ممتازة'
        elif score >= 5:
            return 'جيدة'
        elif score >= 3:
            return 'متوسطة'
        else:
            return 'ضعيفة'
    
    def _calculate_completeness_score(self, result: Dict[str, Any]) -> int:
        """حساب نسبة اكتمال الاستخراج من 100"""
        total_possible = 20  # إجمالي النقاط الممكنة
        score = 0
        
        # البيانات الأساسية (10 نقاط)
        if result.get('title'): score += 2
        if result.get('description'): score += 2
        if result.get('links_count', 0) > 0: score += 2
        if result.get('images_count', 0) > 0: score += 2
        if result.get('technologies'): score += 2
        
        # التحليل المتقدم (10 نقاط)
        if result.get('seo_analysis'): score += 2
        if result.get('structure_analysis'): score += 2
        if result.get('security_analysis'): score += 2
        if result.get('performance'): score += 2
        if result.get('screenshots'): score += 2
        
        return int((score / total_possible) * 100)
    
    def _advanced_ai_analysis(self, result: Dict[str, Any], content: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل AI متقدم للنتائج"""
        ai_analysis = {
            'content_analysis': self._ai_content_analysis(soup),
            'structure_analysis': {
                'page_sections': len(soup.find_all(['section', 'article', 'div'])),
                'navigation_complexity': len(soup.find_all('nav')) + len(soup.find_all('ul')),
                'form_complexity': sum(len(form.find_all('input')) for form in soup.find_all('form'))
            },
            'quality_assessment': {
                'seo_score': self._calculate_seo_score(result.get('seo_analysis', {})),
                'security_score': self._calculate_security_score(result.get('security_analysis', {})),
                'performance_score': self._calculate_performance_score(result.get('performance', {})),
                'overall_quality': result.get('extraction_stats', {}).get('extraction_quality', 'متوسطة')
            },
            'recommendations': self._generate_improvement_recommendations(result)
        }
        
        return ai_analysis
    
    def _calculate_seo_score(self, seo_data: Dict[str, Any]) -> int:
        """حساب نقاط SEO"""
        score = 0
        max_score = 10
        
        if seo_data.get('meta_tags', {}).get('description'): score += 2
        if seo_data.get('meta_tags', {}).get('keywords'): score += 1
        if seo_data.get('headings_structure', {}).get('h1', 0) > 0: score += 2
        if seo_data.get('open_graph'): score += 2
        if seo_data.get('canonical_url'): score += 1
        if seo_data.get('schema_markup'): score += 2
        
        return int((score / max_score) * 100)
    
    def _calculate_security_score(self, security_data: Dict[str, Any]) -> int:
        """حساب نقاط الأمان"""
        score = 0
        max_score = 10
        
        if security_data.get('https_used'): score += 3
        if len(security_data.get('external_scripts', [])) < 5: score += 2
        if security_data.get('inline_scripts', 0) < 3: score += 2
        
        forms = security_data.get('forms_analysis', [])
        if forms:
            csrf_protected = sum(1 for form in forms if form.get('has_csrf_protection'))
            if csrf_protected == len(forms): score += 3
            elif csrf_protected > 0: score += 1
        else:
            score += 3  # لا توجد نماذج = أمان أعلى
        
        return int((score / max_score) * 100)
    
    def _calculate_performance_score(self, performance_data: Dict[str, Any]) -> int:
        """حساب نقاط الأداء"""
        score = 0
        max_score = 10
        
        response_time = performance_data.get('response_time', 0)
        if response_time < 1: score += 3
        elif response_time < 3: score += 2
        elif response_time < 5: score += 1
        
        content_size = performance_data.get('content_size', 0)
        if content_size < 100000: score += 2  # أقل من 100KB
        elif content_size < 500000: score += 1  # أقل من 500KB
        
        if performance_data.get('compression'): score += 2
        if performance_data.get('cache_control'): score += 1
        if performance_data.get('etag'): score += 1
        if performance_data.get('expires'): score += 1
        
        return int((score / max_score) * 100)
    
    def _generate_improvement_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """توليد توصيات للتحسين"""
        recommendations = []
        
        # توصيات SEO
        seo_analysis = result.get('seo_analysis', {})
        if not seo_analysis.get('meta_tags', {}).get('description'):
            recommendations.append('إضافة وصف meta للصفحة')
        if not seo_analysis.get('headings_structure', {}).get('h1'):
            recommendations.append('إضافة عنوان H1 للصفحة')
        if not seo_analysis.get('open_graph'):
            recommendations.append('إضافة بيانات Open Graph للشبكات الاجتماعية')
        
        # توصيات الأمان
        security_analysis = result.get('security_analysis', {})
        if not security_analysis.get('https_used'):
            recommendations.append('استخدام HTTPS بدلاً من HTTP')
        if len(security_analysis.get('external_scripts', [])) > 5:
            recommendations.append('تقليل عدد الأسكريبت الخارجية')
        
        # توصيات الأداء
        performance = result.get('performance', {})
        if performance.get('response_time', 0) > 3:
            recommendations.append('تحسين سرعة استجابة الخادم')
        if not performance.get('compression'):
            recommendations.append('تفعيل ضغط المحتوى (gzip)')
        
        return recommendations
    
    # ==================== وظائف إدارة الملفات ====================
    
    def _save_extraction_files(self, result: Dict[str, Any], content: str, soup: BeautifulSoup) -> Path:
        """حفظ ملفات الاستخراج"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extraction_folder = self.output_directory / 'content' / f"{result['extraction_id']}_{timestamp}"
        extraction_folder.mkdir(parents=True, exist_ok=True)
        
        # حفظ HTML الأصلي
        html_file = extraction_folder / 'page.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # حفظ النتائج JSON
        results_file = extraction_folder / 'extraction_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        # حفظ تقرير مفصل
        self._save_detailed_report(result, extraction_folder)
        
        # تحميل الأصول (للأنواع المتقدمة)
        if result.get('extraction_type') in ['advanced', 'complete', 'ai_powered']:
            self._download_assets(soup, result['url'], extraction_folder)
        
        # تصدير للصيغ المختلفة
        self._export_to_formats(result, extraction_folder)
        
        return extraction_folder
    
    def _save_detailed_report(self, result: Dict[str, Any], extraction_folder: Path):
        """حفظ تقرير مفصل"""
        report_content = f"""# تقرير الاستخراج المفصل

## معلومات أساسية
- **الموقع:** {result['url']}
- **نوع الاستخراج:** {result['extraction_type']}
- **وقت البدء:** {result['timestamp']}
- **المدة:** {result['duration']} ثانية
- **حالة النجاح:** {"نجح" if result['success'] else "فشل"}

## الإحصائيات
- **عدد الروابط:** {result.get('links_count', 0)}
- **عدد الصور:** {result.get('images_count', 0)}
- **عدد الأسكريبت:** {result.get('scripts_count', 0)}
- **حجم المحتوى:** {result.get('content_length', 0)} حرف

## التقنيات المكتشفة
{chr(10).join(f"- {tech}" for tech in result.get('technologies', []))}

## جودة الاستخراج
- **نوعية الاستخراج:** {result.get('extraction_stats', {}).get('extraction_quality', 'غير محدد')}
- **نسبة الاكتمال:** {result.get('extraction_stats', {}).get('completeness_score', 0)}%

## الملفات المنشأة
- **عدد الملفات:** {result.get('extraction_stats', {}).get('files_created', 0)}
- **حجم البيانات:** {result.get('extraction_stats', {}).get('folder_size_mb', 0)} MB

---
تم إنشاء هذا التقرير بواسطة AdvancedWebsiteExtractor
"""
        
        report_file = extraction_folder / 'report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def _download_assets(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path):
        """تحميل الأصول (الصور، CSS، JS)"""
        assets_folder = extraction_folder / 'assets'
        
        downloaded_assets = {
            'images': [],
            'css': [],
            'js': [],
            'failed': []
        }
        
        try:
            # تحميل الصور (أول 10)
            images_folder = assets_folder / 'images'
            images_folder.mkdir(parents=True, exist_ok=True)
            
            for img in soup.find_all('img', src=True)[:10]:
                src = img.get('src')
                if src and isinstance(src, str):
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(base_url, src)
                    
                    try:
                        response = self.session.get(src, timeout=5)
                        if response.status_code == 200:
                            filename = src.split('/')[-1] or 'image.jpg'
                            if '?' in filename:
                                filename = filename.split('?')[0]
                            
                            file_path = images_folder / filename
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            downloaded_assets['images'].append(filename)
                    except:
                        downloaded_assets['failed'].append(src)
            
            # تحميل CSS (أول 5)
            css_folder = assets_folder / 'css'
            css_folder.mkdir(parents=True, exist_ok=True)
            
            for link in soup.find_all('link', rel='stylesheet', href=True)[:5]:
                href = link.get('href')
                if href and isinstance(href, str):
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(base_url, href)
                    
                    try:
                        response = self.session.get(href, timeout=5)
                        if response.status_code == 200:
                            filename = href.split('/')[-1] or 'style.css'
                            if '?' in filename:
                                filename = filename.split('?')[0]
                            
                            file_path = css_folder / filename
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            downloaded_assets['css'].append(filename)
                    except:
                        downloaded_assets['failed'].append(href)
            
            # تحميل JS (أول 5)
            js_folder = assets_folder / 'js'
            js_folder.mkdir(parents=True, exist_ok=True)
            
            for script in soup.find_all('script', src=True)[:5]:
                src = script.get('src')
                if src and isinstance(src, str):
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(base_url, src)
                    
                    try:
                        response = self.session.get(src, timeout=5)
                        if response.status_code == 200:
                            filename = src.split('/')[-1] or 'script.js'
                            if '?' in filename:
                                filename = filename.split('?')[0]
                            
                            file_path = js_folder / filename
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            downloaded_assets['js'].append(filename)
                    except:
                        downloaded_assets['failed'].append(src)
        
        except Exception as e:
            downloaded_assets['error'] = str(e)
        
        # حفظ تقرير الأصول
        assets_report = assets_folder / 'assets_report.json'
        with open(assets_report, 'w', encoding='utf-8') as f:
            json.dump(downloaded_assets, f, ensure_ascii=False, indent=2)
        
        return downloaded_assets
    
    def _export_to_formats(self, result: Dict[str, Any], extraction_folder: Path):
        """تصدير النتائج لصيغ مختلفة"""
        exports_folder = extraction_folder / 'exports'
        exports_folder.mkdir(parents=True, exist_ok=True)
        
        # تصدير JSON مُنسق
        json_file = exports_folder / 'results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        # تصدير CSV للروابط
        if result.get('links_analysis'):
            csv_file = exports_folder / 'links.csv'
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('النوع,الرابط,النص\n')
                
                for link in result['links_analysis'].get('internal_links', []):
                    f.write(f"داخلي,{link['href']},{link['text']}\n")
                
                for link in result['links_analysis'].get('external_links', []):
                    f.write(f"خارجي,{link['href']},{link['text']}\n")
        
        # تصدير HTML تقرير
        html_file = exports_folder / 'report.html'
        html_content = self._generate_html_report(result)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html_report(self, result: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML"""
        return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير استخراج الموقع</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .quality-score {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; }}
        .excellent {{ background-color: #28a745; }}
        .good {{ background-color: #17a2b8; }}
        .medium {{ background-color: #ffc107; color: #000; }}
        .poor {{ background-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>تقرير استخراج الموقع</h1>
            <p><strong>الموقع:</strong> {result['url']}</p>
            <p><strong>التاريخ:</strong> {result['timestamp']}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{result.get('links_count', 0)}</div>
                <div>الروابط</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{result.get('images_count', 0)}</div>
                <div>الصور</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(result.get('technologies', []))}</div>
                <div>التقنيات</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{result.get('extraction_stats', {}).get('completeness_score', 0)}%</div>
                <div>نسبة الاكتمال</div>
            </div>
        </div>
        
        <h2>جودة الاستخراج</h2>
        <p>نوعية الاستخراج: <span class="quality-score good">{result.get('extraction_stats', {}).get('extraction_quality', 'غير محدد')}</span></p>
        
        <h2>التقنيات المكتشفة</h2>
        <ul>
            {''.join(f'<li>{tech}</li>' for tech in result.get('technologies', []))}
        </ul>
        
        <h2>تفاصيل الأداء</h2>
        <ul>
            <li><strong>وقت الاستجابة:</strong> {result.get('performance', {}).get('response_time', 0)} ثانية</li>
            <li><strong>حجم المحتوى:</strong> {result.get('content_length', 0)} حرف</li>
            <li><strong>مدة الاستخراج:</strong> {result['duration']} ثانية</li>
        </ul>
    </div>
</body>
</html>"""
    
    def _capture_screenshots_simple(self, url: str, extraction_folder: Path) -> Dict[str, Any]:
        """التقاط لقطات شاشة بسيطة (placeholder)"""
        # هذه دالة بديلة بسيطة لحين توفر مكتبة لقطات الشاشة
        screenshots_folder = extraction_folder / 'screenshots'
        screenshots_folder.mkdir(parents=True, exist_ok=True)
        
        # إنشاء تقرير لقطات الشاشة
        screenshot_report = {
            'total_screenshots': 0,
            'desktop_screenshot': None,
            'mobile_screenshot': None,
            'status': 'مُعطل مؤقتاً - يتطلب مكتبة selenium أو playwright',
            'note': 'سيتم تفعيل هذه الميزة عند توفر المكتبات المطلوبة'
        }
        
        # حفظ HTML معاينة
        preview_html = f"""<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>معاينة الموقع</title>
</head>
<body>
    <h1>معاينة الموقع</h1>
    <p><strong>الرابط:</strong> <a href="{url}" target="_blank">{url}</a></p>
    <iframe src="{url}" width="100%" height="600px" frameborder="0"></iframe>
</body>
</html>"""
        
        preview_file = screenshots_folder / 'preview.html'
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write(preview_html)
        
        return screenshot_report


# دوال مساعدة للاستخدام السريع
def quick_extract(url: str, extraction_type: str = "standard") -> Dict[str, Any]:
    """استخراج سريع بإعدادات افتراضية"""
    extractor = AdvancedWebsiteExtractor()
    return extractor.extract(url, extraction_type)


def extract_basic_info(url: str) -> Dict[str, Any]:
    """استخراج المعلومات الأساسية فقط"""
    return quick_extract(url, "basic")


def extract_with_assets(url: str) -> Dict[str, Any]:
    """استخراج مع تحميل جميع الأصول"""
    return quick_extract(url, "advanced")


def extract_complete_analysis(url: str) -> Dict[str, Any]:
    """تحليل شامل مع جميع الميزات"""
    return quick_extract(url, "complete")


def extract_ai_powered(url: str) -> Dict[str, Any]:
    """استخراج بالذكاء الاصطناعي مع جميع الميزات المتقدمة"""
    return quick_extract(url, "ai_powered")


def batch_extract(urls: List[str], extraction_type: str = "standard") -> Dict[str, Any]:
    """
    استخراج متعدد المواقع
    
    Args:
        urls: قائمة بروابط المواقع
        extraction_type: نوع الاستخراج
        
    Returns:
        Dict: نتائج الاستخراج لجميع المواقع
    """
    
    extractor = AdvancedWebsiteExtractor()
    results = {}
    
    for i, url in enumerate(urls):
        print(f"استخراج الموقع {i+1}/{len(urls)}: {url}")
        try:
            result = extractor.extract(url, extraction_type)
            results[url] = result
        except Exception as e:
            results[url] = {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    return {
        'total_sites': len(urls),
        'successful_extractions': sum(1 for r in results.values() if r.get('success', False)),
        'failed_extractions': sum(1 for r in results.values() if not r.get('success', False)),
        'results': results
    }


# مثال للاستخدام
if __name__ == "__main__":
    # استخراج أساسي
    result = extract_basic_info("https://example.com")
    print(f"استخراج أساسي: {result.get('title', 'غير متوفر')}")
    
    # استخراج متقدم
    result = extract_with_assets("https://example.com")
    print(f"عدد الأصول المحملة: {len(result.get('assets', {}).get('images', []))}")
    
    # استخراج مخصص
    extractor = AdvancedWebsiteExtractor()
    custom_config = extractor.create_custom_config(
        extraction_type="advanced",
        capture_screenshots=True,
        export_formats=['json', 'html', 'csv']
    )
    
    result = extractor.extract_with_custom_config("https://example.com", custom_config)
    print(f"استخراج مخصص مكتمل: {result.get('success', False)}")