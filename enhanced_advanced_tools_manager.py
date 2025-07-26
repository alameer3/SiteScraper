#!/usr/bin/env python3
"""
مدير الأدوات المتقدمة المحسن مع نظام حفظ الملفات المنظم
Enhanced Advanced Tools Manager with Organized File System
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# استيراد منظم الملفات
try:
    from file_organizer import file_organizer
except ImportError:
    file_organizer = None

class EnhancedAdvancedToolsManager:
    """مدير الأدوات المتقدمة مع نظام الملفات المنظم"""
    
    def __init__(self):
        self.tools_pro_path = Path('tools_pro')
        self.available_tools = self._detect_tools()
        self.extraction_counter = 0
    
    def _detect_tools(self) -> Dict[str, bool]:
        """كشف الأدوات المتاحة"""
        tools = {
            'website_cloner_pro': False,
            'ai_analyzer': False,
            'spider_engine': False,
            'asset_downloader': False,
            'database_scanner': False,
            'deep_extraction_engine': False
        }
        
        if self.tools_pro_path.exists():
            for tool_name in tools.keys():
                tool_file = self.tools_pro_path / f"{tool_name}.py"
                if tool_file.exists():
                    tools[tool_name] = True
        
        return tools
    
    def get_tools_status(self) -> Dict[str, Any]:
        """الحصول على حالة الأدوات"""
        return {
            'total_tools': len(self.available_tools),
            'active_tools': sum(self.available_tools.values()),
            'available_tools': self.available_tools,
            'tools_pro_path': str(self.tools_pro_path),
            'file_organizer_active': file_organizer is not None,
            'extraction_counter': self.extraction_counter
        }
    
    def extract_with_cloner_pro(self, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """استخراج باستخدام Website Cloner Pro مع حفظ منظم"""
        self.extraction_counter += 1
        extraction_id = self.extraction_counter
        
        start_time = time.time()
        
        # إنشاء مجلد الاستخراج
        extraction_folder = None
        if file_organizer:
            try:
                extraction_folder = file_organizer.create_extraction_folder('cloner_pro', url, extraction_id)
            except Exception as e:
                print(f"تحذير: فشل في إنشاء مجلد منظم: {e}")
        
        try:
            # محاولة استيراد واستخدام Website Cloner Pro
            if self.available_tools.get('website_cloner_pro'):
                try:
                    sys.path.append(str(self.tools_pro_path))
                    from website_cloner_pro import WebsiteClonerPro, CloningConfig
                    
                    # إعداد التكوين
                    cloning_config = CloningConfig()
                    if config:
                        for key, value in config.items():
                            if hasattr(cloning_config, key):
                                setattr(cloning_config, key, value)
                    
                    # تشغيل الاستخراج
                    cloner = WebsiteClonerPro(cloning_config)
                    result = cloner.extract_complete_website(url)
                    
                    # معالجة النتائج وحفظها
                    if extraction_folder and file_organizer:
                        self._save_cloner_pro_results(extraction_folder, result, url)
                    
                    result.update({
                        'extraction_id': extraction_id,
                        'tool_used': 'website_cloner_pro',
                        'duration': round(time.time() - start_time, 2),
                        'extraction_folder': str(extraction_folder) if extraction_folder else None
                    })
                    
                    return result
                    
                except Exception as e:
                    return self._create_error_result(extraction_id, url, 'website_cloner_pro', str(e), start_time)
            else:
                return self._create_fallback_result(extraction_id, url, 'website_cloner_pro', start_time, extraction_folder)
                
        except Exception as e:
            return self._create_error_result(extraction_id, url, 'website_cloner_pro', str(e), start_time)
    
    def analyze_with_ai(self, content: str, analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """تحليل المحتوى بالذكاء الاصطناعي مع حفظ منظم"""
        self.extraction_counter += 1
        extraction_id = self.extraction_counter
        
        start_time = time.time()
        
        # إنشاء مجلد التحليل
        extraction_folder = None
        if file_organizer:
            try:
                # استخدام اسم مؤقت للتحليل
                temp_url = f"ai_analysis_{extraction_id}"
                extraction_folder = file_organizer.create_extraction_folder('ai_analysis', temp_url, extraction_id)
            except Exception as e:
                print(f"تحذير: فشل في إنشاء مجلد منظم: {e}")
        
        try:
            # تحليل أساسي للمحتوى
            analysis_result = {
                'content_length': len(content),
                'word_count': len(content.split()),
                'line_count': len(content.splitlines()),
                'analysis_type': analysis_type,
                'language_detected': self._detect_language(content),
                'content_quality': self._assess_content_quality(content),
                'key_phrases': self._extract_key_phrases(content),
                'sentiment': self._basic_sentiment_analysis(content),
                'topics': self._extract_topics(content)
            }
            
            # حفظ النتائج
            if extraction_folder and file_organizer:
                # حفظ المحتوى الأصلي
                file_organizer.save_content(extraction_folder, 'text', content, 'original_content.txt')
                
                # حفظ نتائج التحليل
                file_organizer.save_content(extraction_folder, 'analysis', analysis_result, 'ai_analysis_results.json')
                
                # إنهاء التحليل
                file_organizer.finalize_extraction(extraction_folder, analysis_result)
            
            analysis_result.update({
                'extraction_id': extraction_id,
                'tool_used': 'ai_analyzer',
                'duration': round(time.time() - start_time, 2),
                'extraction_folder': str(extraction_folder) if extraction_folder else None,
                'success': True
            })
            
            return analysis_result
            
        except Exception as e:
            return self._create_error_result(extraction_id, content[:50] + "...", 'ai_analyzer', str(e), start_time)
    
    def extract_with_spider(self, url: str, max_depth: int = 2) -> Dict[str, Any]:
        """استخراج باستخدام Spider Engine مع حفظ منظم"""
        self.extraction_counter += 1
        extraction_id = self.extraction_counter
        
        start_time = time.time()
        
        # إنشاء مجلد الاستخراج
        extraction_folder = None
        if file_organizer:
            try:
                extraction_folder = file_organizer.create_extraction_folder('spider_crawl', url, extraction_id)
            except Exception as e:
                print(f"تحذير: فشل في إنشاء مجلد منظم: {e}")
        
        try:
            # تنفيذ الزحف الأساسي
            spider_result = self._basic_spider_crawl(url, max_depth)
            
            # حفظ النتائج
            if extraction_folder and file_organizer:
                # حفظ خريطة الموقع
                file_organizer.save_content(extraction_folder, 'structure', spider_result['sitemap'], 'sitemap.json')
                
                # حفظ الصفحات المكتشفة
                for i, page in enumerate(spider_result['pages']):
                    file_organizer.save_content(extraction_folder, 'html', page['content'], f'page_{i+1}.html')
                
                # حفظ النتائج الكاملة
                file_organizer.save_content(extraction_folder, 'analysis', spider_result, 'spider_results.json')
                
                # إنهاء الاستخراج
                file_organizer.finalize_extraction(extraction_folder, spider_result)
            
            spider_result.update({
                'extraction_id': extraction_id,
                'tool_used': 'spider_engine',
                'duration': round(time.time() - start_time, 2),
                'extraction_folder': str(extraction_folder) if extraction_folder else None
            })
            
            return spider_result
            
        except Exception as e:
            return self._create_error_result(extraction_id, url, 'spider_engine', str(e), start_time)
    
    def download_assets(self, url: str, asset_types: List[str] = None) -> Dict[str, Any]:
        """تحميل الأصول مع حفظ منظم"""
        self.extraction_counter += 1
        extraction_id = self.extraction_counter
        
        if asset_types is None:
            asset_types = ['images', 'css', 'js']
        
        start_time = time.time()
        
        # إنشاء مجلد الاستخراج
        extraction_folder = None
        if file_organizer:
            try:
                extraction_folder = file_organizer.create_extraction_folder('assets', url, extraction_id)
            except Exception as e:
                print(f"تحذير: فشل في إنشاء مجلد منظم: {e}")
        
        try:
            # تحميل الأصول
            assets_result = self._download_website_assets(url, asset_types)
            
            # حفظ الأصول
            if extraction_folder and file_organizer:
                saved_assets = file_organizer.save_assets_batch(
                    extraction_folder, 
                    assets_result['discovered_assets'], 
                    assets_result.get('downloaded_files', {})
                )
                
                # حفظ تقرير الأصول
                assets_report = {
                    'total_discovered': assets_result['total_discovered'],
                    'total_downloaded': assets_result['total_downloaded'],
                    'saved_assets': {k: [str(p) for p in v] for k, v in saved_assets.items()},
                    'asset_types': asset_types
                }
                
                file_organizer.save_content(extraction_folder, 'analysis', assets_report, 'assets_report.json')
                file_organizer.finalize_extraction(extraction_folder, assets_result)
            
            assets_result.update({
                'extraction_id': extraction_id,
                'tool_used': 'asset_downloader',
                'duration': round(time.time() - start_time, 2),
                'extraction_folder': str(extraction_folder) if extraction_folder else None
            })
            
            return assets_result
            
        except Exception as e:
            return self._create_error_result(extraction_id, url, 'asset_downloader', str(e), start_time)
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """الحصول على ملخص جميع العمليات"""
        if file_organizer:
            return file_organizer.get_extraction_summary()
        else:
            return {
                'total_extractions': self.extraction_counter,
                'file_organizer_available': False,
                'tools_status': self.get_tools_status()
            }
    
    # Helper methods
    def _save_cloner_pro_results(self, extraction_folder: Path, result: Dict[str, Any], url: str):
        """حفظ نتائج Website Cloner Pro"""
        try:
            # حفظ المحتوى المستخرج
            if 'extracted_content' in result:
                content = result['extracted_content']
                if isinstance(content, dict):
                    for content_type, data in content.items():
                        file_organizer.save_content(extraction_folder, content_type, data, f"{content_type}_data")
                elif isinstance(content, str):
                    file_organizer.save_content(extraction_folder, 'html', content, 'cloned_website.html')
            
            # حفظ الأصول إن وجدت
            if 'assets' in result:
                file_organizer.save_assets_batch(extraction_folder, result['assets'])
            
            # حفظ النتائج الكاملة
            file_organizer.save_content(extraction_folder, 'analysis', result, 'cloner_pro_results.json')
            
        except Exception as e:
            print(f"خطأ في حفظ نتائج Cloner Pro: {e}")
    
    def _create_error_result(self, extraction_id: int, url: str, tool: str, error: str, start_time: float) -> Dict[str, Any]:
        """إنشاء نتيجة خطأ"""
        return {
            'extraction_id': extraction_id,
            'url': url,
            'tool_used': tool,
            'success': False,
            'error': error,
            'duration': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_result(self, extraction_id: int, url: str, tool: str, start_time: float, extraction_folder: Path = None) -> Dict[str, Any]:
        """إنشاء نتيجة بديلة عند عدم توفر الأداة"""
        fallback_result = {
            'extraction_id': extraction_id,
            'url': url,
            'tool_used': f"{tool}_fallback",
            'success': True,
            'message': f'الأداة {tool} غير متاحة، تم استخدام نظام بديل',
            'basic_info': self._get_basic_url_info(url),
            'duration': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat(),
            'extraction_folder': str(extraction_folder) if extraction_folder else None
        }
        
        # حفظ النتيجة البديلة
        if extraction_folder and file_organizer:
            file_organizer.save_content(extraction_folder, 'analysis', fallback_result, 'fallback_result.json')
            file_organizer.finalize_extraction(extraction_folder, fallback_result)
        
        return fallback_result
    
    def _get_basic_url_info(self, url: str) -> Dict[str, Any]:
        """الحصول على معلومات أساسية عن الرابط"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return {
            'domain': parsed.netloc,
            'path': parsed.path,
            'scheme': parsed.scheme,
            'query': parsed.query
        }
    
    def _detect_language(self, content: str) -> str:
        """كشف اللغة الأساسي"""
        # كشف بسيط للغة العربية والإنجليزية
        arabic_chars = len([c for c in content if '\u0600' <= c <= '\u06FF'])
        english_chars = len([c for c in content if c.isalpha() and ord(c) < 128])
        
        if arabic_chars > english_chars:
            return 'Arabic'
        elif english_chars > 0:
            return 'English'
        else:
            return 'Unknown'
    
    def _assess_content_quality(self, content: str) -> Dict[str, Any]:
        """تقييم جودة المحتوى"""
        words = content.split()
        sentences = content.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': round(len(words) / max(len(sentences), 1), 2),
            'reading_time_minutes': round(len(words) / 200, 1),  # متوسط 200 كلمة في الدقيقة
            'quality_score': min(100, len(words) / 10)  # نقاط بسيطة حسب عدد الكلمات
        }
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """استخراج العبارات المفتاحية"""
        words = content.lower().split()
        # البحث عن الكلمات المتكررة
        word_count = {}
        for word in words:
            if len(word) > 3:  # تجاهل الكلمات القصيرة
                word_count[word] = word_count.get(word, 0) + 1
        
        # أكثر 10 كلمات تكراراً
        return sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _basic_sentiment_analysis(self, content: str) -> Dict[str, Any]:
        """تحليل مشاعر أساسي"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'جيد', 'ممتاز', 'رائع']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'سيء', 'مروع', 'فظيع']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'confidence': abs(positive_count - negative_count) / max(positive_count + negative_count, 1)
        }
    
    def _extract_topics(self, content: str) -> List[str]:
        """استخراج المواضيع الأساسية"""
        # مواضيع أساسية بناءً على كلمات مفتاحية
        topics = {
            'technology': ['tech', 'software', 'computer', 'programming', 'تقنية', 'برمجة', 'كمبيوتر'],
            'business': ['business', 'company', 'market', 'sales', 'أعمال', 'شركة', 'سوق'],
            'education': ['education', 'school', 'university', 'learning', 'تعليم', 'مدرسة', 'جامعة'],
            'health': ['health', 'medical', 'doctor', 'hospital', 'صحة', 'طبي', 'مستشفى'],
            'news': ['news', 'report', 'article', 'أخبار', 'تقرير', 'مقال']
        }
        
        content_lower = content.lower()
        detected_topics = []
        
        for topic, keywords in topics.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _basic_spider_crawl(self, url: str, max_depth: int) -> Dict[str, Any]:
        """زحف أساسي للموقع"""
        import urllib.request
        import re
        from urllib.parse import urljoin, urlparse
        
        crawled_pages = []
        discovered_links = set()
        sitemap = {'root': url, 'pages': [], 'links': []}
        
        try:
            # تحميل الصفحة الرئيسية
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                # استخراج الروابط
                links = re.findall(r'<a[^>]+href=[\'"([^\'">]+)', content)
                
                for link in links[:20]:  # تحديد عدد الروابط
                    full_link = urljoin(url, link)
                    if urlparse(full_link).netloc == urlparse(url).netloc:
                        discovered_links.add(full_link)
                
                crawled_pages.append({
                    'url': url,
                    'title': re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE).group(1) if re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE) else 'No title',
                    'content': content,
                    'links_found': len(links),
                    'depth': 0
                })
        
        except Exception as e:
            print(f"خطأ في الزحف: {e}")
        
        return {
            'total_pages': len(crawled_pages),
            'total_links': len(discovered_links),
            'pages': crawled_pages,
            'sitemap': sitemap,
            'max_depth_reached': min(1, max_depth),
            'discovered_links': list(discovered_links)
        }
    
    def _download_website_assets(self, url: str, asset_types: List[str]) -> Dict[str, Any]:
        """تحميل أصول الموقع"""
        import urllib.request
        import re
        from urllib.parse import urljoin, urlparse
        
        discovered_assets = {asset_type: [] for asset_type in asset_types}
        downloaded_files = {}
        
        try:
            # تحميل الصفحة الرئيسية لاستخراج الأصول
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
            
            # استخراج الصور
            if 'images' in asset_types:
                img_links = re.findall(r'<img[^>]+src=[\'"([^\'">]+)', content)
                for img in img_links[:10]:  # تحديد العدد
                    full_url = urljoin(url, img)
                    discovered_assets['images'].append(full_url)
            
            # استخراج CSS
            if 'css' in asset_types:
                css_links = re.findall(r'<link[^>]+href=[\'"([^\'">]+\.css[^\'">]*)', content)
                for css in css_links:
                    full_url = urljoin(url, css)
                    discovered_assets['css'].append(full_url)
            
            # استخراج JavaScript
            if 'js' in asset_types:
                js_links = re.findall(r'<script[^>]+src=[\'"([^\'">]+\.js[^\'">]*)', content)
                for js in js_links:
                    full_url = urljoin(url, js)
                    discovered_assets['js'].append(full_url)
        
        except Exception as e:
            print(f"خطأ في اكتشاف الأصول: {e}")
        
        total_discovered = sum(len(assets) for assets in discovered_assets.values())
        
        return {
            'discovered_assets': discovered_assets,
            'downloaded_files': downloaded_files,
            'total_discovered': total_discovered,
            'total_downloaded': 0,  # لم يتم التحميل الفعلي في هذا المثال
            'asset_types': asset_types
        }

# إنشاء مدير الأدوات المحسن
enhanced_advanced_tools = EnhancedAdvancedToolsManager()