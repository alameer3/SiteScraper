"""
محرك الاستخراج المتطور - الكلاس الرئيسي
Advanced Extraction Engine - Main Class
"""

import time
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

from .config import ExtractionConfig, get_preset_config
from .session_manager import SessionManager
from .file_manager import FileManager
from .content_extractor import ContentExtractor
from .security_analyzer import SecurityAnalyzer
from .asset_downloader import AssetDownloader


class AdvancedExtractorEngine:
    """محرك استخراج متطور وشامل"""
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """تهيئة محرك الاستخراج"""
        self.config = config or ExtractionConfig()
        self.extraction_id = 0
        self.results_storage = {}
        
        # تهيئة المكونات الأساسية
        self.session_manager = SessionManager(self.config)
        self.file_manager = FileManager(self.config.output_directory)
        self.content_extractor = ContentExtractor(self.config, self.session_manager)
        self.security_analyzer = SecurityAnalyzer(self.config, self.session_manager)
        self.asset_downloader = AssetDownloader(self.config, self.session_manager, self.file_manager)
        
    def extract_website(self, url: str, extraction_type: str = None) -> Dict[str, Any]:
        """استخراج شامل للموقع"""
        
        # تحديد نوع الاستخراج
        if extraction_type:
            self.config.extraction_type = extraction_type
        
        # تحديث الإعدادات إذا كان نوع الاستخراج من الأنواع المُعرَّفة مسبقاً
        if self.config.extraction_type in ['basic', 'standard', 'advanced', 'complete']:
            preset_config = get_preset_config(self.config.extraction_type)
            # دمج الإعدادات مع الحفاظ على URL
            preset_config.target_url = url
            self.config = preset_config
        
        self.config.target_url = url
        self.extraction_id += 1
        
        start_time = time.time()
        
        try:
            print(f"🚀 بدء استخراج الموقع: {url}")
            print(f"📊 نوع الاستخراج: {self.config.extraction_type}")
            
            # التحقق من صحة الرابط
            if not self._validate_url(url):
                raise ValueError(f"رابط غير صحيح: {url}")
            
            # إنشاء مجلد الاستخراج
            extraction_folder = self.file_manager.create_extraction_folder(
                str(self.extraction_id), 
                url
            )
            
            # استخراج المحتوى الأساسي
            print("📥 استخراج المحتوى الأساسي...")
            response = self.session_manager.make_request(url)
            
            if not response:
                raise Exception("فشل في الوصول إلى الموقع")
            
            # تحليل HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # حفظ المحتوى الخام
            self.file_manager.save_html_content(response.text, extraction_folder)
            
            # استخراج المعلومات الأساسية
            basic_info = self.content_extractor.extract_basic_info(soup, url, response)
            
            # بناء النتيجة الأساسية
            result = {
                'extraction_id': self.extraction_id,
                'url': url,
                'extraction_type': self.config.extraction_type,
                'timestamp': datetime.now().isoformat(),
                'extraction_folder': str(extraction_folder),
                'success': True,
                **basic_info
            }
            
            # تحليلات متقدمة حسب نوع الاستخراج
            if self.config.extraction_type in ['standard', 'advanced', 'complete']:
                result.update(self._perform_advanced_analysis(soup, url, response, extraction_folder))
            
            # تحليلات شاملة للاستخراج الكامل
            if self.config.extraction_type in ['advanced', 'complete']:
                result.update(self._perform_comprehensive_analysis(soup, url, response, extraction_folder))
            
            # تنزيل الأصول
            if self.config.extract_assets:
                print("💾 تحميل الأصول...")
                assets_result = self.asset_downloader.download_all_assets(soup, url, extraction_folder)
                result['assets'] = assets_result
            
            # حساب وقت التنفيذ
            result['duration'] = round(time.time() - start_time, 2)
            
            # حفظ النتائج
            self.file_manager.save_json_data(result, extraction_folder, 'extraction_results.json')
            
            # إنشاء التقارير
            if self.config.export_html:
                print("📄 إنشاء التقارير...")
                self.file_manager.generate_html_report(result, extraction_folder)
            
            if self.config.export_csv and 'links_analysis' in result:
                self._export_csv_data(result, extraction_folder)
            
            # إنشاء أرشيف مضغوط للاستخراج الكامل
            if self.config.extraction_type == 'complete':
                print("🗜️ إنشاء الأرشيف...")
                archive_path = self.file_manager.create_archive(extraction_folder)
                if archive_path:
                    result['archive_path'] = str(archive_path)
            
            # حفظ النتائج في الذاكرة
            self.results_storage[self.extraction_id] = result
            
            print(f"✅ اكتمل الاستخراج في {result['duration']} ثانية")
            print(f"📁 مجلد الاستخراج: {extraction_folder}")
            
            return result
            
        except Exception as e:
            error_result = {
                'extraction_id': self.extraction_id,
                'url': url,
                'extraction_type': self.config.extraction_type,
                'success': False,
                'error': str(e),
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results_storage[self.extraction_id] = error_result
            print(f"❌ فشل الاستخراج: {e}")
            return error_result
    
    def _validate_url(self, url: str) -> bool:
        """التحقق من صحة الرابط"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                self.config.target_url = url
            
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme)
        except:
            return False
    
    def _perform_advanced_analysis(self, soup: BeautifulSoup, url: str, response, extraction_folder: Path) -> Dict[str, Any]:
        """تحليلات متقدمة"""
        advanced_data = {}
        
        print("🔍 تحليل الروابط والصور...")
        
        # تحليل الروابط
        if self.config.extract_links:
            links_analysis = self.content_extractor.extract_links_analysis(soup, url)
            advanced_data['links_analysis'] = links_analysis
        
        # تحليل الصور
        if self.config.extract_images:
            images_analysis = self.content_extractor.extract_images_analysis(soup, url)
            advanced_data['images_analysis'] = images_analysis
        
        # تحليل SEO
        if self.config.analyze_seo:
            print("🔍 تحليل SEO...")
            seo_analysis = self.content_extractor.extract_seo_analysis(soup)
            advanced_data['seo_analysis'] = seo_analysis
        
        # تحليل الأداء
        if self.config.analyze_performance:
            print("⚡ تحليل الأداء...")
            performance_analysis = self._analyze_performance(response, len(response.text))
            advanced_data['performance_analysis'] = performance_analysis
        
        return advanced_data
    
    def _perform_comprehensive_analysis(self, soup: BeautifulSoup, url: str, response, extraction_folder: Path) -> Dict[str, Any]:
        """تحليلات شاملة للاستخراج الكامل"""
        comprehensive_data = {}
        
        # تحليل الأمان
        if self.config.analyze_security:
            print("🔒 تحليل الأمان...")
            security_analysis = self.security_analyzer.analyze_security(soup, url, response)
            comprehensive_data['security_analysis'] = security_analysis
        
        # تحليل هيكل الموقع
        print("🏗️ تحليل الهيكل...")
        structure_analysis = self._analyze_website_structure(soup)
        comprehensive_data['structure_analysis'] = structure_analysis
        
        # البحث عن API endpoints
        print("🔗 البحث عن API endpoints...")
        api_endpoints = self._find_api_endpoints(soup, response.text)
        comprehensive_data['api_endpoints'] = api_endpoints
        
        # تحليل محتوى التفاعل
        print("⚡ تحليل العناصر التفاعلية...")
        interactive_analysis = self._analyze_interactive_elements(soup)
        comprehensive_data['interactive_analysis'] = interactive_analysis
        
        return comprehensive_data
    
    def _analyze_performance(self, response, content_size: int) -> Dict[str, Any]:
        """تحليل أداء الموقع"""
        headers = response.headers
        
        return {
            'response_time_seconds': response.elapsed.total_seconds(),
            'content_size_bytes': content_size,
            'content_size_mb': round(content_size / (1024 * 1024), 2),
            'compression_enabled': 'gzip' in headers.get('Content-Encoding', ''),
            'cache_control': headers.get('Cache-Control', ''),
            'expires': headers.get('Expires', ''),
            'etag': headers.get('ETag', ''),
            'last_modified': headers.get('Last-Modified', ''),
            'server': headers.get('Server', ''),
            'content_type': headers.get('Content-Type', ''),
            'performance_score': self._calculate_performance_score(response, content_size)
        }
    
    def _calculate_performance_score(self, response, content_size: int) -> Dict[str, Any]:
        """حساب نقاط الأداء"""
        score = 0
        issues = []
        
        # وقت الاستجابة
        response_time = response.elapsed.total_seconds()
        if response_time < 1:
            score += 25
        elif response_time < 3:
            score += 20
        elif response_time < 5:
            score += 15
        else:
            score += 5
            issues.append(f"وقت استجابة بطيء: {response_time:.1f} ثانية")
        
        # حجم المحتوى
        content_mb = content_size / (1024 * 1024)
        if content_mb < 1:
            score += 25
        elif content_mb < 2:
            score += 20
        elif content_mb < 5:
            score += 15
        else:
            score += 5
            issues.append(f"حجم المحتوى كبير: {content_mb:.1f} MB")
        
        # ضغط المحتوى
        if 'gzip' in response.headers.get('Content-Encoding', ''):
            score += 15
        else:
            issues.append("ضغط المحتوى غير مفعل")
        
        # Cache headers
        if response.headers.get('Cache-Control') or response.headers.get('Expires'):
            score += 15
        else:
            issues.append("إعدادات التخزين المؤقت مفقودة")
        
        # CDN detection
        server = response.headers.get('Server', '').lower()
        cdn_indicators = ['cloudflare', 'amazon', 'fastly', 'akamai']
        if any(indicator in server for indicator in cdn_indicators):
            score += 10
        
        return {
            'score': min(score, 100),
            'percentage': min(score, 100),
            'level': self._get_performance_level(score),
            'issues': issues
        }
    
    def _get_performance_level(self, score: int) -> str:
        """تحديد مستوى الأداء"""
        if score >= 80:
            return 'ممتاز'
        elif score >= 60:
            return 'جيد'
        elif score >= 40:
            return 'متوسط'
        else:
            return 'ضعيف'
    
    def _analyze_website_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل هيكل الموقع"""
        
        # تحليل هيكل HTML
        html_structure = {
            'has_doctype': bool(soup.find(string=lambda text: isinstance(text, str) and 'DOCTYPE' in text)),
            'html_lang': soup.find('html').get('lang', '') if soup.find('html') else '',
            'head_elements': len(soup.find('head').find_all()) if soup.find('head') else 0,
            'body_elements': len(soup.find('body').find_all()) if soup.find('body') else 0
        }
        
        # تحليل الهيكل الدلالي
        semantic_elements = {
            'header': len(soup.find_all('header')),
            'nav': len(soup.find_all('nav')),
            'main': len(soup.find_all('main')),
            'article': len(soup.find_all('article')),
            'section': len(soup.find_all('section')),
            'aside': len(soup.find_all('aside')),
            'footer': len(soup.find_all('footer'))
        }
        
        # تحليل accessibility
        accessibility = {
            'images_with_alt': len(soup.find_all('img', alt=True)),
            'total_images': len(soup.find_all('img')),
            'form_labels': len(soup.find_all('label')),
            'heading_structure': {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)},
            'skip_links': len(soup.find_all('a', href=lambda href: href and href.startswith('#')))
        }
        
        return {
            'html_structure': html_structure,
            'semantic_elements': semantic_elements,
            'accessibility': accessibility,
            'structure_score': self._calculate_structure_score(html_structure, semantic_elements, accessibility)
        }
    
    def _calculate_structure_score(self, html_structure: Dict, semantic_elements: Dict, accessibility: Dict) -> Dict[str, Any]:
        """حساب نقاط الهيكل"""
        score = 0
        issues = []
        
        # HTML structure
        if html_structure['has_doctype']:
            score += 10
        else:
            issues.append("DOCTYPE مفقود")
        
        if html_structure['html_lang']:
            score += 10
        else:
            issues.append("خاصية lang مفقودة في HTML")
        
        # Semantic elements
        semantic_count = sum(semantic_elements.values())
        if semantic_count >= 5:
            score += 20
        elif semantic_count >= 3:
            score += 15
        elif semantic_count >= 1:
            score += 10
        else:
            issues.append("عناصر دلالية قليلة أو مفقودة")
        
        # Accessibility
        total_images = accessibility['total_images']
        images_with_alt = accessibility['images_with_alt']
        
        if total_images > 0:
            alt_ratio = images_with_alt / total_images
            if alt_ratio >= 0.9:
                score += 15
            elif alt_ratio >= 0.7:
                score += 10
            elif alt_ratio >= 0.5:
                score += 5
            else:
                issues.append("نصوص Alt مفقودة للصور")
        
        # Heading structure
        headings = accessibility['heading_structure']
        if headings['h1'] == 1:
            score += 10
        elif headings['h1'] > 1:
            issues.append("أكثر من H1 واحد")
        elif headings['h1'] == 0:
            issues.append("H1 مفقود")
        
        return {
            'score': min(score, 100),
            'percentage': min(score, 100),
            'issues': issues
        }
    
    def _find_api_endpoints(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """البحث عن API endpoints"""
        import re
        
        endpoints = {
            'ajax_calls': [],
            'api_urls': [],
            'rest_patterns': [],
            'graphql_endpoints': []
        }
        
        # البحث عن AJAX calls في JavaScript
        ajax_patterns = [
            r'\.ajax\s*\(\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.[get|post|put|delete]+\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in ajax_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints['ajax_calls'].extend(matches[:5])  # أول 5 نتائج
        
        # البحث عن API URLs
        api_url_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*\/v\d+\/[^"\']*)["\']'
        ]
        
        for pattern in api_url_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints['api_urls'].extend(matches[:5])
        
        # البحث عن GraphQL
        if 'graphql' in content.lower():
            graphql_matches = re.findall(r'["\']([^"\']*graphql[^"\']*)["\']', content, re.IGNORECASE)
            endpoints['graphql_endpoints'].extend(graphql_matches[:3])
        
        return {
            'endpoints': endpoints,
            'total_found': sum(len(v) for v in endpoints.values()),
            'has_api_integration': any(len(v) > 0 for v in endpoints.values())
        }
    
    def _analyze_interactive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل العناصر التفاعلية"""
        
        interactive_elements = {
            'forms': len(soup.find_all('form')),
            'buttons': len(soup.find_all('button')) + len(soup.find_all('input', type='button')),
            'input_fields': len(soup.find_all('input')),
            'select_dropdowns': len(soup.find_all('select')),
            'textareas': len(soup.find_all('textarea')),
            'clickable_elements': len(soup.find_all(['a', 'button'])),
            'modal_triggers': len(soup.find_all(attrs={'data-toggle': 'modal'})),
            'tabs': len(soup.find_all(attrs={'role': 'tab'})),
            'accordions': len(soup.find_all(class_=lambda x: x and 'accordion' in str(x).lower()))
        }
        
        # تحليل JavaScript events
        script_tags = soup.find_all('script')
        js_events = {
            'onclick_handlers': 0,
            'event_listeners': 0,
            'jquery_events': 0
        }
        
        for script in script_tags:
            if script.string:
                content = script.string.lower()
                js_events['onclick_handlers'] += content.count('onclick')
                js_events['event_listeners'] += content.count('addeventlistener')
                js_events['jquery_events'] += content.count('.on(') + content.count('.click(')
        
        return {
            'interactive_elements': interactive_elements,
            'javascript_events': js_events,
            'interactivity_score': self._calculate_interactivity_score(interactive_elements, js_events),
            'total_interactive_elements': sum(interactive_elements.values())
        }
    
    def _calculate_interactivity_score(self, interactive_elements: Dict, js_events: Dict) -> Dict[str, Any]:
        """حساب نقاط التفاعل"""
        score = 0
        
        # نقاط العناصر التفاعلية
        total_elements = sum(interactive_elements.values())
        if total_elements >= 20:
            score += 30
        elif total_elements >= 10:
            score += 25
        elif total_elements >= 5:
            score += 20
        elif total_elements >= 1:
            score += 15
        
        # نقاط JavaScript events
        total_events = sum(js_events.values())
        if total_events >= 10:
            score += 25
        elif total_events >= 5:
            score += 20
        elif total_events >= 1:
            score += 15
        
        # مكافآت للعناصر المتقدمة
        advanced_elements = ['modal_triggers', 'tabs', 'accordions']
        advanced_count = sum(interactive_elements.get(elem, 0) for elem in advanced_elements)
        if advanced_count >= 3:
            score += 15
        elif advanced_count >= 1:
            score += 10
        
        level = 'عالي' if score >= 60 else 'متوسط' if score >= 30 else 'منخفض'
        
        return {
            'score': min(score, 100),
            'percentage': min(score, 100),
            'level': level
        }
    
    def _export_csv_data(self, result: Dict[str, Any], extraction_folder: Path):
        """تصدير البيانات بصيغة CSV"""
        
        # تصدير الروابط
        if 'links_analysis' in result:
            links_data = []
            links_analysis = result['links_analysis']
            
            for link in links_analysis.get('internal_links', []):
                links_data.append({
                    'type': 'Internal',
                    'url': link.get('href', ''),
                    'text': link.get('text', ''),
                    'title': link.get('title', '')
                })
            
            for link in links_analysis.get('external_links', []):
                links_data.append({
                    'type': 'External',
                    'url': link.get('href', ''),
                    'text': link.get('text', ''),
                    'title': link.get('title', '')
                })
            
            if links_data:
                self.file_manager.save_csv_data(links_data, extraction_folder, 'links.csv')
        
        # تصدير الصور
        if 'images_analysis' in result:
            images_data = []
            for img in result['images_analysis'].get('images', []):
                images_data.append({
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                    'format': img.get('format', '')
                })
            
            if images_data:
                self.file_manager.save_csv_data(images_data, extraction_folder, 'images.csv')
    
    def get_extraction_results(self, extraction_id: int = None) -> Dict[str, Any]:
        """الحصول على نتائج الاستخراج"""
        if extraction_id:
            return self.results_storage.get(extraction_id, {})
        return self.results_storage
    
    def get_statistics(self) -> Dict[str, Any]:
        """إحصائيات المحرك"""
        successful_extractions = sum(1 for result in self.results_storage.values() if result.get('success', False))
        failed_extractions = len(self.results_storage) - successful_extractions
        
        return {
            'total_extractions': len(self.results_storage),
            'successful_extractions': successful_extractions,
            'failed_extractions': failed_extractions,
            'success_rate': round((successful_extractions / max(len(self.results_storage), 1)) * 100, 1),
            'session_stats': self.session_manager.get_session_stats(),
            'storage_stats': self.file_manager.get_storage_stats()
        }
    
    def cleanup(self):
        """تنظيف الموارد"""
        self.session_manager.close()
        self.file_manager.cleanup_temp_files()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()