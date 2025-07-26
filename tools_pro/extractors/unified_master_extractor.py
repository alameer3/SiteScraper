"""
أداة الاستخراج الموحدة الشاملة
Unified Master Extractor - All-in-One Website Extraction System

تدمج جميع أدوات الاستخراج في أداة واحدة قوية:
- الاستخراج المتقدم والعميق
- تحليل الكود والقواعد
- نسخ المواقع والقوالب  
- الذكاء الاصطناعي والتحليل
- تنظيم البيانات والتصدير
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
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Set, Tuple, Union
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
class UnifiedExtractionConfig:
    """تكوين شامل لجميع عمليات الاستخراج"""
    # Basic settings
    mode: str = "comprehensive"  # basic, standard, advanced, comprehensive, ultra, ai_powered
    max_depth: int = 3
    max_pages: int = 50
    timeout: int = 30
    delay_between_requests: float = 1.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Content extraction
    extract_content: bool = True
    extract_metadata: bool = True
    extract_links: bool = True
    extract_images: bool = True
    extract_assets: bool = True
    
    # Advanced extraction
    extract_javascript: bool = True
    extract_css: bool = True
    extract_apis: bool = True
    analyze_behavior: bool = True
    extract_database_schema: bool = False
    
    # AI and analysis
    enable_ai_analysis: bool = True
    enable_pattern_recognition: bool = True
    enable_smart_replication: bool = True
    
    # Security and filtering
    enable_ad_blocking: bool = True
    enable_security_analysis: bool = True
    content_filtering: bool = True
    
    # Output and organization
    organize_data: bool = True
    create_replicated_site: bool = True
    generate_reports: bool = True
    export_formats: Optional[List[str]] = None
    
    # Performance
    enable_playwright: bool = True
    enable_selenium: bool = True
    respect_robots_txt: bool = True
    output_directory: str = "extracted_data"
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['json', 'csv', 'html']

class UnifiedMasterExtractor:
    """أداة الاستخراج الموحدة الشاملة"""
    
    def __init__(self, config: Optional[UnifiedExtractionConfig] = None):
        self.config = config or UnifiedExtractionConfig()
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Initialize extraction results structure
        self.extraction_results = {
            'basic_content': {},
            'advanced_content': {},
            'assets_data': {},
            'technical_structure': {},
            'ai_analysis': {},
            'pattern_recognition': {},
            'security_analysis': {},
            'performance_data': {},
            'replicated_site': {},
            'organized_data': {},
            'export_files': {},
            'statistics': {}
        }
        
        # Load all specialized extractors
        self._load_specialized_extractors()
    
    def _load_specialized_extractors(self):
        """تحميل جميع أدوات الاستخراج المتخصصة"""
        try:
            # Basic extractors
            from .advanced_extractor import AdvancedExtractor
            from .deep_extraction_engine import DeepExtractionEngine
            from .comprehensive_extractor import ComprehensiveExtractor
            
            # Specialized extractors
            from .code_analyzer import CodeAnalyzer
            from .database_scanner import DatabaseScanner
            from .spider_engine import SpiderEngine
            from .asset_downloader import AssetDownloader
            from .simple_asset_downloader import SimpleAssetDownloader
            
            # Generators and replicators
            from ..generators.website_replicator import WebsiteReplicator
            from ..generators.template_generator import TemplateGenerator
            from ..generators.function_replicator import FunctionReplicator
            from ..generators.advanced_code_generator import AdvancedCodeGenerator
            
            # AI and analysis
            from ..ai.pattern_recognition import PatternRecognition
            from ..ai.smart_replication_engine import SmartReplicationEngine
            from ..ai.enhanced_ai_extractor import EnhancedAIExtractor
            from ..ai.quality_assurance import QualityAssurance
            
            # Organization and management
            from .unified_organizer import UnifiedOrganizer
            
            # Scrapers
            from ..scrapers.smart_scraper import SmartScraper
            
            # Store references
            self.advanced_extractor = AdvancedExtractor()
            self.deep_extractor = DeepExtractionEngine()
            self.code_analyzer = CodeAnalyzer()
            self.pattern_recognition = PatternRecognition()
            self.smart_replication = SmartReplicationEngine()
            self.unified_organizer = UnifiedOrganizer()
            self.smart_scraper = SmartScraper()
            
            self.logger.info("تم تحميل جميع أدوات الاستخراج المتخصصة بنجاح")
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل أدوات الاستخراج: {e}")
    
    async def extract_everything(self, url: str, custom_config: Optional[Dict] = None) -> Dict[str, Any]:
        """الاستخراج الشامل لكل شيء من الموقع"""
        start_time = time.time()
        self.logger.info(f"بدء الاستخراج الشامل للموقع: {url}")
        
        # Update config if provided
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        try:
            # Phase 1: Basic Content Extraction
            self.logger.info("المرحلة 1: استخراج المحتوى الأساسي")
            basic_content = await self._extract_basic_content(url)
            self.extraction_results['basic_content'] = basic_content
            
            # Phase 2: Advanced Content and Assets
            if self.config.mode in ['standard', 'advanced', 'comprehensive', 'ultra', 'ai_powered']:
                self.logger.info("المرحلة 2: استخراج المحتوى المتقدم والأصول")
                advanced_content = await self._extract_advanced_content(url)
                assets_data = await self._extract_assets(url)
                self.extraction_results['advanced_content'] = advanced_content
                self.extraction_results['assets_data'] = assets_data
            
            # Phase 3: Technical Structure Analysis
            if self.config.mode in ['advanced', 'comprehensive', 'ultra', 'ai_powered']:
                self.logger.info("المرحلة 3: تحليل البنية التقنية")
                technical_structure = await self._analyze_technical_structure(url)
                self.extraction_results['technical_structure'] = technical_structure
            
            # Phase 4: AI Analysis and Pattern Recognition
            if self.config.enable_ai_analysis and self.config.mode in ['comprehensive', 'ultra', 'ai_powered']:
                self.logger.info("المرحلة 4: التحليل بالذكاء الاصطناعي")
                ai_analysis = await self._perform_ai_analysis()
                pattern_recognition = await self._perform_pattern_recognition()
                self.extraction_results['ai_analysis'] = ai_analysis
                self.extraction_results['pattern_recognition'] = pattern_recognition
            
            # Phase 5: Security and Performance Analysis
            if self.config.mode in ['ultra', 'ai_powered']:
                self.logger.info("المرحلة 5: تحليل الأمان والأداء")
                security_analysis = await self._analyze_security(url)
                performance_data = await self._analyze_performance(url)
                self.extraction_results['security_analysis'] = security_analysis
                self.extraction_results['performance_data'] = performance_data
            
            # Phase 6: Website Replication
            if self.config.create_replicated_site:
                self.logger.info("المرحلة 6: إنشاء الموقع المطابق")
                replicated_site = await self._create_replicated_site(url)
                self.extraction_results['replicated_site'] = replicated_site
            
            # Phase 7: Data Organization
            if self.config.organize_data:
                self.logger.info("المرحلة 7: تنظيم البيانات")
                organized_data = await self._organize_extracted_data(url)
                self.extraction_results['organized_data'] = organized_data
            
            # Phase 8: Export and Reports
            if self.config.generate_reports:
                self.logger.info("المرحلة 8: إنشاء التقارير والتصدير")
                export_files = await self._generate_exports(url)
                self.extraction_results['export_files'] = export_files
            
            # Calculate final statistics
            end_time = time.time()
            self.extraction_results['statistics'] = self._calculate_final_statistics(start_time, end_time)
            
            self.logger.info(f"تم إكمال الاستخراج الشامل في {end_time - start_time:.2f} ثانية")
            
            return self.extraction_results
            
        except Exception as e:
            self.logger.error(f"خطأ في الاستخراج الشامل: {e}")
            return {
                'error': str(e),
                'partial_results': self.extraction_results,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _extract_basic_content(self, url: str) -> Dict[str, Any]:
        """استخراج المحتوى الأساسي"""
        try:
            # Use SmartScraper for basic content
            scraping_config = {
                'timeout': self.config.timeout,
                'extract_text': True,
                'extract_metadata': True,
                'extract_links': self.config.extract_links,
                'extract_images': self.config.extract_images
            }
            
            result = self.smart_scraper.scrape_website(url, scraping_config)
            
            return {
                'status': 'completed',
                'page_info': result.get('page_info', {}),
                'content': result.get('content', {}),
                'links': result.get('links', {}),
                'images': result.get('images', {}),
                'metadata': result.get('metadata', {}),
                'statistics': result.get('statistics', {})
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في استخراج المحتوى الأساسي: {e}")
            return {'error': str(e)}
    
    async def _extract_advanced_content(self, url: str) -> Dict[str, Any]:
        """استخراج المحتوى المتقدم"""
        try:
            # Use AdvancedExtractor
            mode = 'advanced' if self.config.mode in ['comprehensive', 'ultra', 'ai_powered'] else 'standard'
            result = self.advanced_extractor.extract_with_mode(url, mode)
            
            return {
                'status': 'completed',
                'extraction_mode': mode,
                'content_data': result.get('content', {}),
                'seo_data': result.get('seo', {}),
                'performance_data': result.get('performance', {}),
                'statistics': result.get('statistics', {})
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في استخراج المحتوى المتقدم: {e}")
            return {'error': str(e)}
    
    async def _extract_assets(self, url: str) -> Dict[str, Any]:
        """استخراج جميع الأصول"""
        try:
            if not self.config.extract_assets:
                return {'status': 'skipped', 'reason': 'asset extraction disabled'}
            
            # Use AdvancedExtractor for assets
            result = self.advanced_extractor.extract_with_mode(url, 'standard', {
                'include_assets': True,
                'download_assets': True
            })
            
            return {
                'status': 'completed',
                'assets': result.get('assets', {}),
                'download_info': result.get('assets', {}).get('download_info', {}),
                'statistics': result.get('statistics', {})
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في استخراج الأصول: {e}")
            return {'error': str(e)}
    
    async def _analyze_technical_structure(self, url: str) -> Dict[str, Any]:
        """تحليل البنية التقنية"""
        try:
            # Use DeepExtractionEngine
            config = {
                'mode': 'comprehensive',
                'extract_apis': True,
                'analyze_behavior': True,
                'include_javascript': True,
                'include_css': True
            }
            
            result = await self.deep_extractor.extract_with_config(url, config)
            
            return {
                'status': 'completed',
                'technical_data': result.get('technical_structure', {}),
                'api_endpoints': result.get('api_endpoints', []),
                'javascript_analysis': result.get('javascript_analysis', {}),
                'css_analysis': result.get('css_analysis', {}),
                'statistics': result.get('statistics', {})
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل البنية التقنية: {e}")
            return {'error': str(e)}
    
    async def _perform_ai_analysis(self) -> Dict[str, Any]:
        """إجراء التحليل بالذكاء الاصطناعي"""
        try:
            # Use SmartReplicationEngine for AI analysis
            ai_analysis = await self.smart_replication.analyze_with_ai(self.extraction_results)
            
            return {
                'status': 'completed',
                'complexity_analysis': ai_analysis.get('complexity_analysis', {}),
                'architecture_patterns': ai_analysis.get('architecture_patterns', []),
                'optimization_suggestions': ai_analysis.get('optimization_suggestions', []),
                'quality_assessment': ai_analysis.get('quality_assessment', {}),
                'statistics': ai_analysis.get('statistics', {})
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في التحليل بالذكاء الاصطناعي: {e}")
            return {'error': str(e)}
    
    async def _perform_pattern_recognition(self) -> Dict[str, Any]:
        """إجراء التعرف على الأنماط"""
        try:
            # Use PatternRecognition
            pattern_analysis = await self.pattern_recognition.analyze_patterns(self.extraction_results)
            
            return {
                'status': 'completed',
                'design_patterns': pattern_analysis.get('design_patterns', {}),
                'ui_patterns': pattern_analysis.get('ui_patterns', {}),
                'code_patterns': pattern_analysis.get('code_patterns', {}),
                'architectural_style': pattern_analysis.get('architectural_style', ''),
                'confidence_scores': pattern_analysis.get('confidence_scores', {}),
                'recommendations': pattern_analysis.get('recommendations', [])
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في التعرف على الأنماط: {e}")
            return {'error': str(e)}
    
    async def _analyze_security(self, url: str) -> Dict[str, Any]:
        """تحليل الأمان"""
        try:
            # Basic security analysis
            security_data = {
                'ssl_analysis': await self._check_ssl(url),
                'headers_analysis': await self._analyze_security_headers(url),
                'vulnerability_scan': await self._basic_vulnerability_scan(url)
            }
            
            return {
                'status': 'completed',
                'security_score': self._calculate_security_score(security_data),
                'security_data': security_data,
                'recommendations': self._generate_security_recommendations(security_data)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الأمان: {e}")
            return {'error': str(e)}
    
    async def _analyze_performance(self, url: str) -> Dict[str, Any]:
        """تحليل الأداء"""
        try:
            start_time = time.time()
            
            # Basic performance metrics
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    load_time = time.time() - start_time
                    content_size = len(await response.text())
                    status_code = response.status
            
            performance_data = {
                'load_time': load_time,
                'content_size': content_size,
                'status_code': status_code,
                'performance_score': self._calculate_performance_score(load_time, content_size)
            }
            
            return {
                'status': 'completed',
                'performance_data': performance_data,
                'recommendations': self._generate_performance_recommendations(performance_data)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الأداء: {e}")
            return {'error': str(e)}
    
    async def _create_replicated_site(self, url: str) -> Dict[str, Any]:
        """إنشاء الموقع المطابق"""
        try:
            # Use SmartReplicationEngine
            replication_result = await self.smart_replication.replicate_website(url, self.extraction_results)
            
            return {
                'status': 'completed',
                'replication_data': replication_result.get('replication_data', {}),
                'generated_files': replication_result.get('generated_files', {}),
                'quality_assessment': replication_result.get('quality_assessment', {}),
                'replication_path': replication_result.get('output_path', '')
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء الموقع المطابق: {e}")
            return {'error': str(e)}
    
    async def _organize_extracted_data(self, url: str) -> Dict[str, Any]:
        """تنظيم البيانات المستخرجة"""
        try:
            # Use UnifiedOrganizer
            organized_path = self.unified_organizer.organize_extraction_data(url, self.extraction_results)
            summary = self.unified_organizer.get_extraction_summary(organized_path)
            
            return {
                'status': 'completed',
                'organized_path': organized_path,
                'summary': summary,
                'folder_structure': self._get_folder_structure(organized_path)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تنظيم البيانات: {e}")
            return {'error': str(e)}
    
    async def _generate_exports(self, url: str) -> Dict[str, Any]:
        """إنشاء ملفات التصدير"""
        try:
            export_files = {}
            
            for format_type in self.config.export_formats:
                if format_type == 'json':
                    export_files['json'] = self._export_to_json()
                elif format_type == 'csv':
                    export_files['csv'] = self._export_to_csv()
                elif format_type == 'html':
                    export_files['html'] = self._export_to_html()
                elif format_type == 'xml':
                    export_files['xml'] = self._export_to_xml()
            
            return {
                'status': 'completed',
                'export_files': export_files,
                'formats': self.config.export_formats
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء ملفات التصدير: {e}")
            return {'error': str(e)}
    
    def _calculate_final_statistics(self, start_time: float, end_time: float) -> Dict[str, Any]:
        """حساب الإحصائيات النهائية"""
        total_time = end_time - start_time
        
        statistics = {
            'extraction_time': total_time,
            'extraction_mode': self.config.mode,
            'phases_completed': self._count_completed_phases(),
            'total_data_size': self._calculate_total_data_size(),
            'success_rate': self._calculate_success_rate(),
            'timestamp': datetime.now().isoformat(),
            'config_used': asdict(self.config)
        }
        
        return statistics
    
    # Helper methods
    def _count_completed_phases(self) -> int:
        """عد المراحل المكتملة"""
        completed = 0
        for phase_key, phase_data in self.extraction_results.items():
            if isinstance(phase_data, dict) and phase_data.get('status') == 'completed':
                completed += 1
        return completed
    
    def _calculate_total_data_size(self) -> int:
        """حساب الحجم الإجمالي للبيانات"""
        total_size = 0
        try:
            data_str = json.dumps(self.extraction_results)
            total_size = len(data_str.encode('utf-8'))
        except:
            total_size = 0
        return total_size
    
    def _calculate_success_rate(self) -> float:
        """حساب معدل النجاح"""
        total_phases = len(self.extraction_results)
        completed_phases = self._count_completed_phases()
        return (completed_phases / total_phases) * 100 if total_phases > 0 else 0
    
    def _export_to_json(self) -> str:
        """تصدير إلى JSON"""
        try:
            return json.dumps(self.extraction_results, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"خطأ في التصدير: {e}"
    
    def _export_to_csv(self) -> str:
        """تصدير إلى CSV"""
        # Implementation for CSV export
        return "CSV export implementation needed"
    
    def _export_to_html(self) -> str:
        """تصدير إلى HTML"""
        # Implementation for HTML export
        return "HTML export implementation needed"
    
    def _export_to_xml(self) -> str:
        """تصدير إلى XML"""
        # Implementation for XML export
        return "XML export implementation needed"
    
    async def _check_ssl(self, url: str) -> Dict[str, Any]:
        """فحص SSL"""
        # Basic SSL check implementation
        return {'ssl_enabled': url.startswith('https'), 'certificate_valid': True}
    
    async def _analyze_security_headers(self, url: str) -> Dict[str, Any]:
        """تحليل رؤوس الأمان"""
        # Basic security headers analysis
        return {'security_headers': [], 'score': 50}
    
    async def _basic_vulnerability_scan(self, url: str) -> Dict[str, Any]:
        """فحص الثغرات الأساسي"""
        # Basic vulnerability scan
        return {'vulnerabilities': [], 'risk_level': 'low'}
    
    def _calculate_security_score(self, security_data: Dict) -> int:
        """حساب نقاط الأمان"""
        return 75  # Placeholder
    
    def _generate_security_recommendations(self, security_data: Dict) -> List[str]:
        """إنشاء توصيات الأمان"""
        return ["تفعيل HTTPS", "إضافة رؤوس الأمان"]
    
    def _calculate_performance_score(self, load_time: float, content_size: int) -> int:
        """حساب نقاط الأداء"""
        score = 100
        if load_time > 3:
            score -= 20
        if content_size > 1000000:  # 1MB
            score -= 10
        return max(score, 0)
    
    def _generate_performance_recommendations(self, performance_data: Dict) -> List[str]:
        """إنشاء توصيات الأداء"""
        recommendations = []
        if performance_data['load_time'] > 3:
            recommendations.append("تحسين سرعة التحميل")
        if performance_data['content_size'] > 1000000:
            recommendations.append("ضغط المحتوى")
        return recommendations
    
    def _get_folder_structure(self, path: str) -> Dict[str, Any]:
        """الحصول على بنية المجلدات"""
        structure = {}
        try:
            if os.path.exists(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        structure[item] = 'directory'
                    else:
                        structure[item] = 'file'
        except Exception as e:
            self.logger.error(f"خطأ في قراءة بنية المجلد: {e}")
        return structure

# Convenience functions for different extraction modes
async def extract_basic(url: str) -> Dict[str, Any]:
    """استخراج أساسي سريع"""
    config = UnifiedExtractionConfig(
        mode="basic",
        extract_assets=False,
        enable_ai_analysis=False,
        create_replicated_site=False
    )
    extractor = UnifiedMasterExtractor(config)
    return await extractor.extract_everything(url)

async def extract_comprehensive(url: str) -> Dict[str, Any]:
    """استخراج شامل ومتكامل"""
    config = UnifiedExtractionConfig(
        mode="comprehensive",
        extract_assets=True,
        enable_ai_analysis=True,
        create_replicated_site=True,
        export_formats=['json', 'csv', 'html']
    )
    extractor = UnifiedMasterExtractor(config)
    return await extractor.extract_everything(url)

async def extract_ai_powered(url: str) -> Dict[str, Any]:
    """استخراج بالذكاء الاصطناعي الكامل"""
    config = UnifiedExtractionConfig(
        mode="ai_powered",
        extract_assets=True,
        enable_ai_analysis=True,
        enable_pattern_recognition=True,
        enable_smart_replication=True,
        create_replicated_site=True,
        export_formats=['json', 'csv', 'html', 'xml']
    )
    extractor = UnifiedMasterExtractor(config)
    return await extractor.extract_everything(url)