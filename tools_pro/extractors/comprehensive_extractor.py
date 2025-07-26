"""
محرك الاستخراج الشامل المطور
Comprehensive Extractor - Advanced Implementation Based on نصوصي.txt Requirements

هذا المحرك يوفر:
1. استخراج الواجهة الكاملة (HTML, CSS, JS, Assets)
2. استخراج البنية التقنية (APIs, Database, Routes)
3. استخراج الوظائف والميزات (Authentication, CMS, Search)
4. استخراج سلوك الموقع (Events, AJAX, Responsive)
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Import extraction engines
from .spider_engine import SpiderEngine, SpiderConfig
from .asset_downloader import AssetDownloader, AssetDownloadConfig
from .deep_extraction_engine import DeepExtractionEngine, ExtractionConfig
from ..ai.smart_replication_engine import SmartReplicationEngine, ReplicationConfig
from ..generators.template_generator import TemplateGenerator
from ..generators.code_generator import CodeGenerator

@dataclass
class ComprehensiveExtractionConfig:
    """تكوين الاستخراج الشامل"""
    # إعدادات عامة
    extraction_mode: str = "comprehensive"  # basic, standard, advanced, comprehensive, ultra
    target_url: str = ""
    max_extraction_time: int = 1800  # 30 minutes
    
    # إعدادات الزحف
    max_crawl_depth: int = 5
    max_pages: int = 100
    respect_robots_txt: bool = True
    
    # إعدادات الاستخراج
    extract_interface: bool = True
    extract_technical_structure: bool = True
    extract_features: bool = True
    extract_behavior: bool = True
    
    # إعدادات متقدمة
    enable_ai_analysis: bool = True
    enable_smart_replication: bool = True
    enable_database_analysis: bool = False
    
    # إعدادات التصدير
    output_directory: str = "extracted_websites"
    export_formats: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["json", "html", "project"]

class ComprehensiveExtractor:
    """محرك الاستخراج الشامل المتقدم"""
    
    def __init__(self, config: Optional[ComprehensiveExtractionConfig] = None):
        self.config = config or ComprehensiveExtractionConfig()
        self.logger = logging.getLogger(__name__)
        
        # إعداد المحركات الفرعية
        self.spider_engine = None
        self.asset_downloader = None
        self.deep_extractor = None
        self.replication_engine = None
        self.template_generator = None
        self.code_generator = None
        
        # نتائج الاستخراج
        self.extraction_results = {}
        self.extraction_stats = {
            'start_time': None,
            'end_time': None,
            'total_time': 0,
            'pages_extracted': 0,
            'assets_downloaded': 0,
            'features_detected': 0,
            'apis_discovered': 0
        }
    
    async def extract_website_comprehensive(self, target_url: str) -> Dict[str, Any]:
        """الاستخراج الشامل للموقع"""
        self.extraction_stats['start_time'] = datetime.now()
        self.config.target_url = target_url
        
        self.logger.info(f"بدء الاستخراج الشامل للموقع: {target_url}")
        
        extraction_results = {
            'metadata': {
                'extraction_id': f"extract_{int(time.time())}",
                'target_url': target_url,
                'extraction_mode': self.config.extraction_mode,
                'start_time': self.extraction_stats['start_time'].isoformat(),
                'config': asdict(self.config)
            },
            'interface_extraction': {},
            'technical_structure': {},
            'features_extraction': {},
            'behavior_analysis': {},
            'ai_analysis': {},
            'replication_data': {},
            'export_results': {}
        }
        
        try:
            # المرحلة 1: استخراج الواجهة الكاملة
            if self.config.extract_interface:
                extraction_results['interface_extraction'] = await self._extract_complete_interface(target_url)
            
            # المرحلة 2: استخراج البنية التقنية
            if self.config.extract_technical_structure:
                extraction_results['technical_structure'] = await self._extract_technical_structure(target_url)
            
            # المرحلة 3: استخراج الوظائف والميزات
            if self.config.extract_features:
                extraction_results['features_extraction'] = await self._extract_features_and_functionality(target_url)
            
            # المرحلة 4: تحليل سلوك الموقع
            if self.config.extract_behavior:
                extraction_results['behavior_analysis'] = await self._analyze_website_behavior(target_url)
            
            # المرحلة 5: التحليل بالذكاء الاصطناعي
            if self.config.enable_ai_analysis:
                extraction_results['ai_analysis'] = await self._perform_ai_analysis(extraction_results)
            
            # المرحلة 6: النسخ الذكي
            if self.config.enable_smart_replication:
                extraction_results['replication_data'] = await self._generate_smart_replication(extraction_results)
            
            # المرحلة 7: التصدير
            extraction_results['export_results'] = await self._export_extraction_results(extraction_results)
            
            # إحصائيات نهائية
            self.extraction_stats['end_time'] = datetime.now()
            self.extraction_stats['total_time'] = (
                self.extraction_stats['end_time'] - self.extraction_stats['start_time']
            ).total_seconds()
            
            extraction_results['statistics'] = self.extraction_stats
            extraction_results['metadata']['status'] = 'completed'
            extraction_results['metadata']['end_time'] = self.extraction_stats['end_time'].isoformat()
            
            self.logger.info(f"اكتمل الاستخراج الشامل في {self.extraction_stats['total_time']:.2f} ثانية")
            
        except Exception as e:
            self.logger.error(f"خطأ في الاستخراج الشامل: {e}")
            extraction_results['metadata']['status'] = 'failed'
            extraction_results['metadata']['error'] = str(e)
        
        return extraction_results
    
    async def _extract_complete_interface(self, target_url: str) -> Dict[str, Any]:
        """استخراج الواجهة الكاملة"""
        self.logger.info("بدء استخراج الواجهة الكاملة...")
        
        # إعداد محرك العنكبوت
        spider_config = SpiderConfig(
            max_depth=self.config.max_crawl_depth,
            max_pages=self.config.max_pages,
            respect_robots_txt=self.config.respect_robots_txt
        )
        
        interface_data = {
            'html_files': {},
            'css_files': {},
            'javascript_files': {},
            'images': {},
            'fonts': {},
            'media_files': {},
            'other_assets': {},
            'site_structure': {}
        }
        
        async with SpiderEngine(spider_config) as spider:
            # زحف الموقع
            crawl_results = await spider.crawl_website(target_url)
            interface_data['site_structure'] = crawl_results
            
            # تجميع جميع الأصول
            all_assets = []
            for page_url, page_data in crawl_results.get('site_map', {}).items():
                # إضافة روابط CSS
                if 'css_links' in page_data:
                    all_assets.extend(page_data['css_links'])
                
                # إضافة روابط JavaScript
                if 'js_links' in page_data:
                    all_assets.extend(page_data['js_links'])
                
                # إضافة الصور
                if 'images' in page_data:
                    all_assets.extend([img.get('src', '') for img in page_data['images']])
            
            # تحميل الأصول
            asset_config = AssetDownloadConfig(
                save_directory=f"{self.config.output_directory}/assets",
                organize_by_type=True
            )
            
            async with AssetDownloader(asset_config) as downloader:
                download_results = await downloader.download_all_assets(all_assets, target_url)
                
                # تنظيم الأصول حسب النوع
                organized_assets = download_results.get('organized_structure', {})
                for asset_type, assets in organized_assets.items():
                    if asset_type in interface_data:
                        interface_data[asset_type] = assets
        
        self.extraction_stats['assets_downloaded'] = len(interface_data.get('images', {}).get('files', []))
        return interface_data
    
    async def _extract_technical_structure(self, target_url: str) -> Dict[str, Any]:
        """استخراج البنية التقنية"""
        self.logger.info("بدء استخراج البنية التقنية...")
        
        technical_data = {
            'apis_discovered': [],
            'routing_system': {},
            'database_structure': {},
            'server_technology': {},
            'frameworks_detected': [],
            'security_features': {}
        }
        
        # استخدام محرك الاستخراج العميق
        extraction_config = ExtractionConfig(
            mode=self.config.extraction_mode,
            extract_apis=True,
            analyze_behavior=True,
            extract_database_schema=self.config.enable_database_analysis
        )
        
        async with DeepExtractionEngine(extraction_config) as deep_extractor:
            deep_results = await deep_extractor.extract_deep_data(target_url)
            
            # استخراج APIs
            if 'network_analysis' in deep_results:
                technical_data['apis_discovered'] = deep_results['network_analysis'].get('api_calls', [])
                self.extraction_stats['apis_discovered'] = len(technical_data['apis_discovered'])
            
            # تحليل الأطر التقنية
            if 'technology_analysis' in deep_results:
                technical_data['frameworks_detected'] = deep_results['technology_analysis'].get('frameworks', [])
                technical_data['server_technology'] = deep_results['technology_analysis'].get('server_info', {})
            
            # تحليل الأمان
            if 'security_analysis' in deep_results:
                technical_data['security_features'] = deep_results['security_analysis']
        
        return technical_data
    
    async def _extract_features_and_functionality(self, target_url: str) -> Dict[str, Any]:
        """استخراج الوظائف والميزات"""
        self.logger.info("بدء استخراج الوظائف والميزات...")
        
        features_data = {
            'authentication_system': {},
            'content_management': {},
            'search_functionality': {},
            'navigation_system': {},
            'interactive_components': {},
            'data_visualization': {}
        }
        
        # تحليل النماذج والتفاعل
        spider_config = SpiderConfig(max_depth=2, max_pages=20)
        async with SpiderEngine(spider_config) as spider:
            crawl_results = await spider.crawl_website(target_url)
            
            forms_found = []
            search_forms = []
            login_forms = []
            
            for page_url, page_data in crawl_results.get('site_map', {}).items():
                if 'forms' in page_data:
                    for form in page_data['forms']:
                        forms_found.append(form)
                        
                        # تصنيف النماذج
                        form_action = form.get('action', '').lower()
                        if any(keyword in form_action for keyword in ['login', 'signin', 'auth']):
                            login_forms.append(form)
                        elif any(keyword in form_action for keyword in ['search', 'find']):
                            search_forms.append(form)
            
            # تحليل نظام المصادقة
            features_data['authentication_system'] = {
                'login_forms': login_forms,
                'registration_forms': [],  # سيتم تطويرها
                'password_fields': len([f for f in forms_found if f.get('has_password_field', False)])
            }
            
            # تحليل وظائف البحث
            features_data['search_functionality'] = {
                'search_forms': search_forms,
                'search_endpoints': []  # سيتم تطويرها
            }
            
            # تحليل نظام التنقل
            nav_menus = []
            for page_data in crawl_results.get('site_map', {}).values():
                if 'navigation' in page_data:
                    nav_menus.extend(page_data['navigation'])
            
            features_data['navigation_system'] = {
                'main_menus': nav_menus,
                'breadcrumbs': [],  # سيتم تطويرها
                'pagination': []   # سيتم تطويرها
            }
        
        self.extraction_stats['features_detected'] = len(forms_found)
        return features_data
    
    async def _analyze_website_behavior(self, target_url: str) -> Dict[str, Any]:
        """تحليل سلوك الموقع"""
        self.logger.info("بدء تحليل سلوك الموقع...")
        
        behavior_data = {
            'javascript_events': {},
            'ajax_calls': {},
            'local_storage_usage': {},
            'responsive_behavior': {},
            'loading_states': {},
            'error_handling': {}
        }
        
        # استخدام محرك الاستخراج العميق مع Playwright
        extraction_config = ExtractionConfig(
            enable_playwright=True,
            analyze_behavior=True
        )
        
        async with DeepExtractionEngine(extraction_config) as deep_extractor:
            behavior_results = await deep_extractor.analyze_website_behavior(target_url)
            
            if behavior_results:
                behavior_data.update(behavior_results)
        
        return behavior_data
    
    async def _perform_ai_analysis(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """التحليل بالذكاء الاصطناعي"""
        self.logger.info("بدء التحليل بالذكاء الاصطناعي...")
        
        if not self.replication_engine:
            replication_config = ReplicationConfig(
                enable_ai_analysis=True,
                enable_pattern_recognition=True
            )
            self.replication_engine = SmartReplicationEngine(replication_config)
        
        ai_analysis = await self.replication_engine.replicate_website_intelligently(extraction_results)
        return ai_analysis.get('ai_analysis', {})
    
    async def _generate_smart_replication(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """النسخ الذكي"""
        self.logger.info("بدء النسخ الذكي...")
        
        if not self.replication_engine:
            replication_config = ReplicationConfig(
                enable_smart_replication=True,
                enable_quality_assurance=True
            )
            self.replication_engine = SmartReplicationEngine(replication_config)
        
        replication_results = await self.replication_engine.replicate_website_intelligently(extraction_results)
        return replication_results.get('smart_replication', {})
    
    async def _export_extraction_results(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """تصدير نتائج الاستخراج"""
        self.logger.info("بدء تصدير النتائج...")
        
        export_results = {
            'exported_files': [],
            'export_formats': self.config.export_formats,
            'output_directory': self.config.output_directory
        }
        
        # إنشاء مجلد الإخراج
        output_path = Path(self.config.output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # تصدير JSON
        if 'json' in self.config.export_formats:
            json_file = output_path / 'extraction_results.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(extraction_results, f, ensure_ascii=False, indent=2, default=str)
            export_results['exported_files'].append(str(json_file))
        
        # تصدير تقرير HTML
        if 'html' in self.config.export_formats:
            html_file = output_path / 'extraction_report.html'
            html_report = self._generate_html_report(extraction_results)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            export_results['exported_files'].append(str(html_file))
        
        # إنشاء مشروع كامل
        if 'project' in self.config.export_formats:
            project_path = output_path / 'replicated_project'
            project_path.mkdir(parents=True, exist_ok=True)
            
            # سيتم توسيعها لاحقاً لإنشاء مشروع كامل
            export_results['project_directory'] = str(project_path)
        
        return export_results
    
    def _generate_html_report(self, extraction_results: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML"""
        metadata = extraction_results.get('metadata', {})
        stats = extraction_results.get('statistics', {})
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير الاستخراج الشامل</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
                .header {{ background: #007bff; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>تقرير الاستخراج الشامل</h1>
                <p>الموقع المُستخرج: {metadata.get('target_url', 'غير محدد')}</p>
                <p>وقت الاستخراج: {metadata.get('start_time', 'غير محدد')}</p>
            </div>
            
            <div class="section">
                <h2>إحصائيات الاستخراج</h2>
                <div class="stats">
                    <div class="stat">
                        <h3>{stats.get('pages_extracted', 0)}</h3>
                        <p>صفحات مُستخرجة</p>
                    </div>
                    <div class="stat">
                        <h3>{stats.get('assets_downloaded', 0)}</h3>
                        <p>ملفات محملة</p>
                    </div>
                    <div class="stat">
                        <h3>{stats.get('features_detected', 0)}</h3>
                        <p>ميزات مكتشفة</p>
                    </div>
                    <div class="stat">
                        <h3>{stats.get('apis_discovered', 0)}</h3>
                        <p>APIs مكتشفة</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>تفاصيل الاستخراج</h2>
                <pre>{json.dumps(extraction_results, ensure_ascii=False, indent=2, default=str)}</pre>
            </div>
        </body>
        </html>
        """
        
        return html_template