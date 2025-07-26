"""
Website Cloner Pro Integration Layer
طبقة التكامل لدمج أداة Website Cloner Pro مع النظام الحالي
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time
from datetime import datetime

# Import Website Cloner Pro
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from website_cloner_pro import WebsiteClonerPro, CloningConfig, CloningResult

# Import existing tools for hybrid approach
from .unified_master_extractor import UnifiedMasterExtractor, UnifiedExtractionConfig
from .database_scanner import DatabaseScanner
from .spider_engine import SpiderEngine, SpiderConfig
from ..ai.smart_replication_engine import SmartReplicationEngine, ReplicationConfig

@dataclass
class IntegratedExtractionConfig:
    """تكوين الاستخراج المتكامل"""
    # أداة رئيسية
    primary_tool: str = "website_cloner_pro"  # website_cloner_pro, unified_master, hybrid
    
    # إعدادات Website Cloner Pro
    target_url: str = ""
    max_depth: int = 3
    max_pages: int = 50
    extract_all_content: bool = True
    analyze_with_ai: bool = True
    generate_reports: bool = True
    
    # إعدادات الأدوات المتخصصة
    use_specialized_database_scanner: bool = False
    use_advanced_spider_engine: bool = False
    use_existing_ai_engine: bool = False
    
    # إعدادات التكامل
    merge_results: bool = True
    create_unified_report: bool = True
    output_directory: str = "integrated_extraction"
    
    # إعدادات متقدمة
    enable_parallel_extraction: bool = True
    enable_quality_comparison: bool = True
    fallback_to_existing_tools: bool = True

class WebsiteClonerIntegration:
    """طبقة التكامل الشاملة لأداة Website Cloner Pro"""
    
    def __init__(self, config: Optional[IntegratedExtractionConfig] = None):
        self.config = config or IntegratedExtractionConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize primary tools
        self.website_cloner = None
        self.unified_extractor = None
        self.database_scanner = None
        self.spider_engine = None
        self.ai_engine = None
        
        # Results storage
        self.integrated_results = {}
        self.extraction_stats = {}
        self.comparison_report = {}
        
        self._initialize_tools()
    
    def _initialize_tools(self):
        """تهيئة جميع الأدوات"""
        try:
            # Initialize Website Cloner Pro
            cloner_config = CloningConfig(
                target_url=self.config.target_url,
                max_depth=self.config.max_depth,
                max_pages=self.config.max_pages,
                extract_all_content=self.config.extract_all_content,
                analyze_with_ai=self.config.analyze_with_ai,
                generate_reports=self.config.generate_reports
            )
            self.website_cloner = WebsiteClonerPro(cloner_config)
            
            # Initialize existing tools if needed
            if self.config.primary_tool in ["unified_master", "hybrid"]:
                unified_config = UnifiedExtractionConfig(
                    max_depth=self.config.max_depth,
                    max_pages=self.config.max_pages
                )
                self.unified_extractor = UnifiedMasterExtractor(unified_config)
            
            if self.config.use_specialized_database_scanner:
                self.database_scanner = DatabaseScanner()
            
            if self.config.use_advanced_spider_engine:
                spider_config = SpiderConfig(
                    max_depth=self.config.max_depth,
                    max_pages=self.config.max_pages
                )
                self.spider_engine = SpiderEngine(spider_config)
            
            if self.config.use_existing_ai_engine:
                ai_config = ReplicationConfig()
                self.ai_engine = SmartReplicationEngine(ai_config)
                
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة الأدوات: {e}")
    
    async def extract_website_integrated(self, target_url: str) -> Dict[str, Any]:
        """الاستخراج المتكامل للموقع"""
        start_time = time.time()
        self.config.target_url = target_url
        
        self.logger.info(f"بدء الاستخراج المتكامل للموقع: {target_url}")
        
        integrated_results = {
            'metadata': {
                'extraction_id': f"integrated_{int(time.time())}",
                'target_url': target_url,
                'primary_tool': self.config.primary_tool,
                'start_time': datetime.now().isoformat(),
                'config': asdict(self.config)
            },
            'website_cloner_results': {},
            'unified_extractor_results': {},
            'specialized_tools_results': {},
            'comparison_analysis': {},
            'integrated_summary': {},
            'recommendations': []
        }
        
        try:
            # المرحلة 1: تشغيل Website Cloner Pro
            if self.config.primary_tool in ["website_cloner_pro", "hybrid"]:
                self.logger.info("تشغيل Website Cloner Pro...")
                cloner_result = await self._run_website_cloner(target_url)
                integrated_results['website_cloner_results'] = cloner_result
            
            # المرحلة 2: تشغيل الأدوات الحالية (إذا كان hybrid)
            if self.config.primary_tool in ["unified_master", "hybrid"]:
                self.logger.info("تشغيل الأدوات الحالية...")
                existing_results = await self._run_existing_tools(target_url)
                integrated_results['unified_extractor_results'] = existing_results
            
            # المرحلة 3: تشغيل الأدوات المتخصصة
            if any([self.config.use_specialized_database_scanner,
                   self.config.use_advanced_spider_engine,
                   self.config.use_existing_ai_engine]):
                self.logger.info("تشغيل الأدوات المتخصصة...")
                specialized_results = await self._run_specialized_tools(target_url)
                integrated_results['specialized_tools_results'] = specialized_results
            
            # المرحلة 4: مقارنة النتائج وتحليل الجودة
            if self.config.enable_quality_comparison:
                self.logger.info("مقارنة وتحليل جودة النتائج...")
                comparison_analysis = await self._compare_results(integrated_results)
                integrated_results['comparison_analysis'] = comparison_analysis
            
            # المرحلة 5: دمج النتائج وإنشاء التقرير الموحد
            if self.config.merge_results:
                self.logger.info("دمج النتائج وإنشاء التقرير الموحد...")
                integrated_summary = await self._merge_results(integrated_results)
                integrated_results['integrated_summary'] = integrated_summary
            
            # المرحلة 6: إنشاء التوصيات
            recommendations = await self._generate_integrated_recommendations(integrated_results)
            integrated_results['recommendations'] = recommendations
            
            # حساب الإحصائيات النهائية
            integrated_results['metadata']['duration'] = time.time() - start_time
            integrated_results['metadata']['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"خطأ في الاستخراج المتكامل: {e}")
            integrated_results['metadata']['status'] = 'failed'
            integrated_results['metadata']['error'] = str(e)
        
        return integrated_results
    
    async def _run_website_cloner(self, target_url: str) -> Dict[str, Any]:
        """تشغيل Website Cloner Pro"""
        try:
            # Update config with target URL
            self.website_cloner.config.target_url = target_url
            
            # Run cloning process
            result = await self.website_cloner.clone_website_complete(target_url)
            
            return {
                'success': result.success,
                'output_path': result.output_path,
                'pages_extracted': result.pages_extracted,
                'assets_downloaded': result.assets_downloaded,
                'total_size': result.total_size,
                'duration': result.duration,
                'technologies_detected': result.technologies_detected,
                'security_analysis': result.security_analysis,
                'performance_metrics': result.performance_metrics,
                'recommendations': result.recommendations,
                'detailed_results': result.extracted_content
            }
        except Exception as e:
            self.logger.error(f"خطأ في Website Cloner Pro: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _run_existing_tools(self, target_url: str) -> Dict[str, Any]:
        """تشغيل الأدوات الحالية"""
        try:
            results = {}
            
            if self.unified_extractor:
                self.logger.info("تشغيل Unified Master Extractor...")
                unified_result = await self.unified_extractor.extract_everything(target_url)
                results['unified_extraction'] = unified_result
            
            return results
        except Exception as e:
            self.logger.error(f"خطأ في الأدوات الحالية: {e}")
            return {'error': str(e)}
    
    async def _run_specialized_tools(self, target_url: str) -> Dict[str, Any]:
        """تشغيل الأدوات المتخصصة"""
        try:
            results = {}
            
            # Database Scanner
            if self.database_scanner:
                self.logger.info("تشغيل Database Scanner...")
                try:
                    db_result = await self.database_scanner.scan_website_databases(target_url)
                    results['database_analysis'] = db_result
                except Exception as e:
                    results['database_analysis'] = {'error': str(e)}
            
            # Spider Engine
            if self.spider_engine:
                self.logger.info("تشغيل Spider Engine...")
                try:
                    spider_result = await self.spider_engine.crawl_comprehensive(target_url)
                    results['spider_crawl'] = spider_result
                except Exception as e:
                    results['spider_crawl'] = {'error': str(e)}
            
            # AI Engine
            if self.ai_engine:
                self.logger.info("تشغيل AI Replication Engine...")
                try:
                    # Use Website Cloner results as input for AI analysis
                    ai_result = await self.ai_engine.replicate_website_intelligently({})
                    results['ai_replication'] = ai_result
                except Exception as e:
                    results['ai_replication'] = {'error': str(e)}
            
            return results
        except Exception as e:
            self.logger.error(f"خطأ في الأدوات المتخصصة: {e}")
            return {'error': str(e)}
    
    async def _compare_results(self, integrated_results: Dict[str, Any]) -> Dict[str, Any]:
        """مقارنة نتائج الأدوات المختلفة"""
        comparison = {
            'extraction_speed': {},
            'content_quality': {},
            'asset_coverage': {},
            'technical_depth': {},
            'accuracy_assessment': {},
            'recommendation': ''
        }
        
        try:
            cloner_results = integrated_results.get('website_cloner_results', {})
            unified_results = integrated_results.get('unified_extractor_results', {})
            
            # مقارنة السرعة
            if cloner_results.get('duration') and unified_results.get('unified_extraction', {}).get('duration'):
                cloner_speed = cloner_results['duration']
                unified_speed = unified_results['unified_extraction']['duration']
                
                comparison['extraction_speed'] = {
                    'website_cloner_pro': f"{cloner_speed:.2f}s",
                    'unified_extractor': f"{unified_speed:.2f}s",
                    'faster_tool': 'website_cloner_pro' if cloner_speed < unified_speed else 'unified_extractor'
                }
            
            # مقارنة جودة المحتوى
            cloner_pages = cloner_results.get('pages_extracted', 0)
            unified_pages = unified_results.get('unified_extraction', {}).get('pages_processed', 0)
            
            comparison['content_quality'] = {
                'website_cloner_pro_pages': cloner_pages,
                'unified_extractor_pages': unified_pages,
                'better_coverage': 'website_cloner_pro' if cloner_pages > unified_pages else 'unified_extractor'
            }
            
            # مقارنة تغطية الأصول
            cloner_assets = cloner_results.get('assets_downloaded', 0)
            unified_assets = unified_results.get('unified_extraction', {}).get('assets_count', 0)
            
            comparison['asset_coverage'] = {
                'website_cloner_pro_assets': cloner_assets,
                'unified_extractor_assets': unified_assets,
                'better_assets': 'website_cloner_pro' if cloner_assets > unified_assets else 'unified_extractor'
            }
            
            # تقييم العمق التقني
            cloner_tech = len(cloner_results.get('technologies_detected', []))
            unified_tech = len(unified_results.get('unified_extraction', {}).get('technologies', []))
            
            comparison['technical_depth'] = {
                'website_cloner_pro_technologies': cloner_tech,
                'unified_extractor_technologies': unified_tech,
                'better_detection': 'website_cloner_pro' if cloner_tech > unified_tech else 'unified_extractor'
            }
            
            # تقييم دقة الاستخراج
            cloner_success = cloner_results.get('success', False)
            unified_success = unified_results.get('unified_extraction', {}).get('success', False)
            
            comparison['accuracy_assessment'] = {
                'website_cloner_pro_success': cloner_success,
                'unified_extractor_success': unified_success,
                'overall_assessment': 'both_successful' if cloner_success and unified_success else 'mixed_results'
            }
            
            # توصية نهائية
            if cloner_success and not unified_success:
                comparison['recommendation'] = 'استخدام Website Cloner Pro فقط'
            elif unified_success and not cloner_success:
                comparison['recommendation'] = 'استخدام الأدوات الحالية فقط'
            elif cloner_success and unified_success:
                comparison['recommendation'] = 'النهج الهجين للحصول على أفضل النتائج'
            else:
                comparison['recommendation'] = 'مراجعة الأخطاء وإعادة المحاولة'
                
        except Exception as e:
            self.logger.error(f"خطأ في مقارنة النتائج: {e}")
            comparison['error'] = str(e)
        
        return comparison
    
    async def _merge_results(self, integrated_results: Dict[str, Any]) -> Dict[str, Any]:
        """دمج النتائج من جميع الأدوات"""
        merged_data = {
            'best_extraction': {},
            'combined_technologies': [],
            'comprehensive_assets': [],
            'unified_analysis': {},
            'quality_score': 0
        }
        
        try:
            cloner_results = integrated_results.get('website_cloner_results', {})
            unified_results = integrated_results.get('unified_extractor_results', {})
            specialized_results = integrated_results.get('specialized_tools_results', {})
            
            # اختيار أفضل استخراج
            if cloner_results.get('success') and cloner_results.get('pages_extracted', 0) > 0:
                merged_data['best_extraction'] = cloner_results
                merged_data['primary_source'] = 'website_cloner_pro'
            elif unified_results.get('unified_extraction', {}).get('success'):
                merged_data['best_extraction'] = unified_results['unified_extraction']
                merged_data['primary_source'] = 'unified_extractor'
            
            # دمج التقنيات المكتشفة
            all_technologies = set()
            if cloner_results.get('technologies_detected'):
                all_technologies.update(cloner_results['technologies_detected'])
            if unified_results.get('unified_extraction', {}).get('technologies'):
                all_technologies.update(unified_results['unified_extraction']['technologies'])
            merged_data['combined_technologies'] = list(all_technologies)
            
            # دمج تحليل قواعد البيانات
            if specialized_results.get('database_analysis'):
                merged_data['database_info'] = specialized_results['database_analysis']
            
            # دمج نتائج الذكاء الاصطناعي
            if specialized_results.get('ai_replication'):
                merged_data['ai_insights'] = specialized_results['ai_replication']
            
            # حساب نقاط الجودة
            quality_factors = []
            if merged_data['best_extraction'].get('pages_extracted', 0) > 0:
                quality_factors.append(25)
            if merged_data['best_extraction'].get('assets_downloaded', 0) > 0:
                quality_factors.append(25)
            if len(merged_data['combined_technologies']) > 0:
                quality_factors.append(25)
            if merged_data['best_extraction'].get('security_analysis'):
                quality_factors.append(25)
            
            merged_data['quality_score'] = sum(quality_factors)
            
        except Exception as e:
            self.logger.error(f"خطأ في دمج النتائج: {e}")
            merged_data['error'] = str(e)
        
        return merged_data
    
    async def _generate_integrated_recommendations(self, integrated_results: Dict[str, Any]) -> List[str]:
        """إنشاء توصيات متكاملة"""
        recommendations = []
        
        try:
            comparison = integrated_results.get('comparison_analysis', {})
            merged_summary = integrated_results.get('integrated_summary', {})
            
            # توصيات بناء على المقارنة
            if comparison.get('recommendation'):
                recommendations.append(f"نصيحة أساسية: {comparison['recommendation']}")
            
            # توصيات بناء على الجودة
            quality_score = merged_summary.get('quality_score', 0)
            if quality_score == 100:
                recommendations.append("جودة ممتازة: تم استخراج جميع عناصر الموقع بنجاح")
            elif quality_score >= 75:
                recommendations.append("جودة جيدة: نقص بعض العناصر الثانوية")
            elif quality_score >= 50:
                recommendations.append("جودة متوسطة: يحتاج لتحسين الاستخراج")
            else:
                recommendations.append("جودة ضعيفة: يُنصح بإعادة المحاولة مع إعدادات مختلفة")
            
            # توصيات أدوات محددة
            cloner_results = integrated_results.get('website_cloner_results', {})
            if cloner_results.get('success'):
                recommendations.append("Website Cloner Pro نجح في الاستخراج - يُنصح باستخدامه للمشاريع المماثلة")
            
            # توصيات تقنية
            technologies = merged_summary.get('combined_technologies', [])
            if 'React' in technologies:
                recommendations.append("الموقع يستخدم React - يُنصح بالتركيز على استخراج المكونات")
            if 'WordPress' in technologies:
                recommendations.append("الموقع يستخدم WordPress - يُنصح باستخراج قاعدة البيانات والقوالب")
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء التوصيات: {e}")
            recommendations.append(f"خطأ في تحليل التوصيات: {e}")
        
        return recommendations
    
    def get_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة التكامل"""
        return {
            'tools_initialized': {
                'website_cloner_pro': self.website_cloner is not None,
                'unified_extractor': self.unified_extractor is not None,
                'database_scanner': self.database_scanner is not None,
                'spider_engine': self.spider_engine is not None,
                'ai_engine': self.ai_engine is not None
            },
            'config': asdict(self.config),
            'ready_for_extraction': self.website_cloner is not None
        }

# Factory function for easy integration
def create_integrated_extractor(target_url: str, 
                              primary_tool: str = "website_cloner_pro",
                              use_hybrid: bool = False) -> WebsiteClonerIntegration:
    """إنشاء مستخرج متكامل مع إعدادات محسنة"""
    config = IntegratedExtractionConfig(
        target_url=target_url,
        primary_tool=primary_tool,
        use_specialized_database_scanner=use_hybrid,
        use_advanced_spider_engine=use_hybrid,
        use_existing_ai_engine=use_hybrid,
        enable_quality_comparison=use_hybrid,
        merge_results=True
    )
    
    return WebsiteClonerIntegration(config)