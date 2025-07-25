"""
محرك الاستخراج الشامل - Comprehensive Extraction Engine
أداة متقدمة تدمج جميع قدرات التحليل والاستخراج في نظام واحد
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# تكوين المسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtractionType(Enum):
    """أنواع الاستخراج المختلفة"""
    ANALYSIS_ONLY = "analysis_only"           # تحليل فقط بدون استخراج
    CONTENT_EXTRACTION = "content_extraction" # استخراج المحتوى النصي
    ASSET_EXTRACTION = "asset_extraction"     # استخراج الأصول والملفات
    FULL_WEBSITE_CLONE = "full_website_clone" # نسخ كامل للموقع
    SECURITY_AUDIT = "security_audit"         # تدقيق أمني شامل
    PERFORMANCE_ANALYSIS = "performance_analysis" # تحليل الأداء
    SEO_ANALYSIS = "seo_analysis"            # تحليل SEO
    COMPETITOR_RESEARCH = "competitor_research" # بحث المنافسين

class Priority(Enum):
    """مستويات الأولوية"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ExtractionJob:
    """وظيفة استخراج"""
    job_id: str
    url: str
    extraction_type: ExtractionType
    priority: Priority
    config: Dict[str, Any]
    created_at: str
    status: str = "pending"
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class ExtractionEngine:
    """محرك الاستخراج الشامل"""
    
    def __init__(self, output_directory: str = "extractions"):
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(exist_ok=True)
        
        # قائمة الوظائف والحالات
        self.jobs: Dict[str, ExtractionJob] = {}
        self.active_jobs: Dict[str, threading.Thread] = {}
        self.job_counter = 0
        
        # إحصائيات النظام
        self.system_stats = {
            'total_jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'jobs_running': 0,
            'jobs_pending': 0,
            'average_completion_time': 0.0,
            'total_processing_time': 0.0,
            'system_uptime': time.time()
        }
        
        # تهيئة الأدوات المدمجة
        self._init_integrated_tools()
        
        logger.info("تم تهيئة محرك الاستخراج الشامل")

    def _init_integrated_tools(self):
        """تهيئة الأدوات المدمجة"""
        try:
            # محاولة استيراد الأدوات المدمجة
            from analyzers.comprehensive_analyzer import ComprehensiveAnalyzer
            from extractors.master_extractor import MasterExtractor
            from blockers.advanced_blocker import AdvancedBlocker
            from scrapers.smart_scraper import SmartScraper
            
            self.analyzer = ComprehensiveAnalyzer
            self.extractor = MasterExtractor
            self.blocker = AdvancedBlocker
            self.scraper = SmartScraper
            
            logger.info("تم تحميل جميع الأدوات المدمجة بنجاح")
            
        except ImportError as e:
            logger.warning(f"لا يمكن تحميل بعض الأدوات المدمجة: {e}")
            # استخدام أدوات احتياطية
            self._init_fallback_tools()

    def _init_fallback_tools(self):
        """تهيئة أدوات احتياطية"""
        logger.info("استخدام أدوات احتياطية...")
        
        # يمكن إضافة أدوات احتياطية هنا
        self.analyzer = None
        self.extractor = None
        self.blocker = None
        self.scraper = None

    def create_job(self, 
                   url: str, 
                   extraction_type: ExtractionType, 
                   priority: Priority = Priority.MEDIUM,
                   config: Dict[str, Any] = None) -> str:
        """إنشاء وظيفة استخراج جديدة"""
        
        self.job_counter += 1
        job_id = f"job_{self.job_counter}_{int(time.time())}"
        
        if config is None:
            config = self._get_default_config(extraction_type)
        
        job = ExtractionJob(
            job_id=job_id,
            url=url,
            extraction_type=extraction_type,
            priority=priority,
            config=config,
            created_at=datetime.now().isoformat()
        )
        
        self.jobs[job_id] = job
        self.system_stats['total_jobs_created'] += 1
        self.system_stats['jobs_pending'] += 1
        
        logger.info(f"تم إنشاء وظيفة جديدة: {job_id} للموقع {url}")
        
        return job_id

    def _get_default_config(self, extraction_type: ExtractionType) -> Dict[str, Any]:
        """الحصول على إعدادات افتراضية حسب نوع الاستخراج"""
        base_config = {
            'timeout': 30,
            'max_pages': 50,
            'delay_between_requests': 1.0,
            'respect_robots_txt': True,
            'user_agent': 'Website-Analyzer-Tool/1.0'
        }
        
        if extraction_type == ExtractionType.ANALYSIS_ONLY:
            return {**base_config, 'max_pages': 5, 'extract_assets': False}
        
        elif extraction_type == ExtractionType.CONTENT_EXTRACTION:
            return {**base_config, 'max_pages': 20, 'extract_images': False}
        
        elif extraction_type == ExtractionType.ASSET_EXTRACTION:
            return {**base_config, 'extract_images': True, 'extract_css': True, 'extract_js': True}
        
        elif extraction_type == ExtractionType.FULL_WEBSITE_CLONE:
            return {**base_config, 'max_pages': 100, 'extract_all': True, 'create_local_copy': True}
        
        elif extraction_type == ExtractionType.SECURITY_AUDIT:
            return {**base_config, 'max_pages': 10, 'deep_security_scan': True}
        
        elif extraction_type == ExtractionType.PERFORMANCE_ANALYSIS:
            return {**base_config, 'max_pages': 10, 'measure_performance': True}
        
        elif extraction_type == ExtractionType.SEO_ANALYSIS:
            return {**base_config, 'max_pages': 20, 'analyze_seo': True}
        
        elif extraction_type == ExtractionType.COMPETITOR_RESEARCH:
            return {**base_config, 'max_pages': 15, 'compare_competitors': True}
        
        return base_config

    def start_job(self, job_id: str) -> bool:
        """بدء تشغيل وظيفة"""
        if job_id not in self.jobs:
            logger.error(f"وظيفة غير موجودة: {job_id}")
            return False
        
        job = self.jobs[job_id]
        
        if job.status != "pending":
            logger.warning(f"الوظيفة {job_id} ليست في حالة انتظار")
            return False
        
        # تشغيل الوظيفة في خيط منفصل
        thread = threading.Thread(target=self._execute_job, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        self.active_jobs[job_id] = thread
        job.status = "running"
        job.started_at = datetime.now().isoformat()
        
        self.system_stats['jobs_pending'] -= 1
        self.system_stats['jobs_running'] += 1
        
        logger.info(f"تم بدء تشغيل الوظيفة: {job_id}")
        return True

    def _execute_job(self, job_id: str):
        """تنفيذ وظيفة الاستخراج"""
        job = self.jobs[job_id]
        start_time = time.time()
        
        try:
            logger.info(f"بدء تنفيذ الوظيفة {job_id}: {job.extraction_type.value}")
            
            # اختيار الأداة المناسبة حسب نوع الاستخراج
            if job.extraction_type == ExtractionType.ANALYSIS_ONLY:
                result = self._execute_analysis(job)
            
            elif job.extraction_type == ExtractionType.CONTENT_EXTRACTION:
                result = self._execute_content_extraction(job)
            
            elif job.extraction_type == ExtractionType.ASSET_EXTRACTION:
                result = self._execute_asset_extraction(job)
            
            elif job.extraction_type == ExtractionType.FULL_WEBSITE_CLONE:
                result = self._execute_full_clone(job)
            
            elif job.extraction_type == ExtractionType.SECURITY_AUDIT:
                result = self._execute_security_audit(job)
            
            elif job.extraction_type == ExtractionType.PERFORMANCE_ANALYSIS:
                result = self._execute_performance_analysis(job)
            
            elif job.extraction_type == ExtractionType.SEO_ANALYSIS:
                result = self._execute_seo_analysis(job)
            
            elif job.extraction_type == ExtractionType.COMPETITOR_RESEARCH:
                result = self._execute_competitor_research(job)
            
            else:
                raise ValueError(f"نوع استخراج غير مدعوم: {job.extraction_type}")
            
            # تحديث الوظيفة بالنتيجة
            job.result = result
            job.status = "completed"
            job.progress = 100.0
            job.completed_at = datetime.now().isoformat()
            
            # حفظ النتيجة
            self._save_job_result(job)
            
            # تحديث الإحصائيات
            execution_time = time.time() - start_time
            self.system_stats['jobs_completed'] += 1
            self.system_stats['jobs_running'] -= 1
            self.system_stats['total_processing_time'] += execution_time
            self.system_stats['average_completion_time'] = (
                self.system_stats['total_processing_time'] / 
                self.system_stats['jobs_completed']
            )
            
            logger.info(f"اكتملت الوظيفة {job_id} بنجاح في {execution_time:.2f} ثانية")
            
        except Exception as e:
            job.error = str(e)
            job.status = "failed"
            job.completed_at = datetime.now().isoformat()
            
            self.system_stats['jobs_failed'] += 1
            self.system_stats['jobs_running'] -= 1
            
            logger.error(f"فشلت الوظيفة {job_id}: {e}")
        
        finally:
            # تنظيف
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

    def _execute_analysis(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ تحليل شامل"""
        job.progress = 10.0
        
        if self.analyzer is None:
            # تحليل احتياطي بسيط
            return self._basic_analysis(job.url)
        
        analyzer = self.analyzer()
        job.progress = 30.0
        
        result = analyzer.analyze_comprehensive(job.url)
        job.progress = 80.0
        
        return result

    def _execute_content_extraction(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ استخراج المحتوى"""
        job.progress = 10.0
        
        # استخدام الكاشط لاستخراج المحتوى
        if self.scraper is None:
            return self._basic_content_extraction(job.url)
        
        from scrapers.smart_scraper import ScrapingConfig, ScrapingMode
        
        config = ScrapingConfig(
            base_url=job.url,
            mode=ScrapingMode.BASIC,
            max_pages=job.config.get('max_pages', 5)
        )
        
        scraper = self.scraper(config)
        job.progress = 50.0
        
        result = scraper.scrape_website()
        job.progress = 90.0
        
        return result

    def _execute_asset_extraction(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ استخراج الأصول"""
        job.progress = 10.0
        
        if self.extractor is None:
            return self._basic_asset_extraction(job.url)
        
        from extractors.master_extractor import ExtractionConfig, ExtractionMode
        
        config = ExtractionConfig(
            url=job.url,
            mode=ExtractionMode.STANDARD,
            extract_images=True,
            extract_css=True,
            extract_js=True
        )
        
        extractor = self.extractor(config)
        job.progress = 50.0
        
        result = extractor.extract_website()
        job.progress = 90.0
        
        return result

    def _execute_full_clone(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ نسخ كامل للموقع"""
        job.progress = 5.0
        
        if self.extractor is None:
            return self._basic_clone(job.url)
        
        from extractors.master_extractor import ExtractionConfig, ExtractionMode
        
        config = ExtractionConfig(
            url=job.url,
            mode=ExtractionMode.ULTRA,
            max_pages=job.config.get('max_pages', 100),
            extract_images=True,
            extract_css=True,
            extract_js=True,
            extract_fonts=True,
            extract_videos=True,
            compress_output=True
        )
        
        extractor = self.extractor(config)
        job.progress = 30.0
        
        result = extractor.extract_website()
        job.progress = 95.0
        
        return result

    def _execute_security_audit(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ تدقيق أمني"""
        job.progress = 10.0
        
        if self.analyzer is None:
            return self._basic_security_audit(job.url)
        
        analyzer = self.analyzer()
        job.progress = 40.0
        
        result = analyzer.analyze_security_comprehensive(job.url)
        job.progress = 90.0
        
        return result

    def _execute_performance_analysis(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ تحليل الأداء"""
        job.progress = 10.0
        
        if self.analyzer is None:
            return self._basic_performance_analysis(job.url)
        
        analyzer = self.analyzer()
        job.progress = 40.0
        
        result = analyzer.analyze_performance_comprehensive(job.url)
        job.progress = 90.0
        
        return result

    def _execute_seo_analysis(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ تحليل SEO"""
        job.progress = 10.0
        
        if self.analyzer is None:
            return self._basic_seo_analysis(job.url)
        
        analyzer = self.analyzer()
        job.progress = 40.0
        
        result = analyzer.analyze_seo_comprehensive(job.url)
        job.progress = 90.0
        
        return result

    def _execute_competitor_research(self, job: ExtractionJob) -> Dict[str, Any]:
        """تنفيذ بحث المنافسين"""
        job.progress = 10.0
        
        if self.analyzer is None:
            return self._basic_competitor_research(job.url)
        
        analyzer = self.analyzer()
        job.progress = 40.0
        
        result = analyzer.get_competitor_insights(job.url)
        job.progress = 90.0
        
        return result

    def _save_job_result(self, job: ExtractionJob):
        """حفظ نتيجة الوظيفة"""
        try:
            job_dir = self.output_dir / job.job_id
            job_dir.mkdir(exist_ok=True)
            
            # حفظ معلومات الوظيفة
            job_info_path = job_dir / "job_info.json"
            with open(job_info_path, 'w', encoding='utf-8') as f:
                job_data = asdict(job)
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            # حفظ النتيجة منفصلة
            if job.result:
                result_path = job_dir / "result.json"
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump(job.result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"تم حفظ نتيجة الوظيفة {job.job_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ نتيجة الوظيفة {job.job_id}: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على حالة الوظيفة"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        return {
            'job_id': job.job_id,
            'url': job.url,
            'extraction_type': job.extraction_type.value,
            'status': job.status,
            'progress': job.progress,
            'created_at': job.created_at,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
            'error': job.error
        }

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """الحصول على جميع الوظائف"""
        return [self.get_job_status(job_id) for job_id in self.jobs.keys()]

    def get_system_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        current_time = time.time()
        uptime = current_time - self.system_stats['system_uptime']
        
        return {
            **self.system_stats,
            'uptime_seconds': round(uptime, 2),
            'uptime_hours': round(uptime / 3600, 2),
            'success_rate': round(
                (self.system_stats['jobs_completed'] / 
                 max(1, self.system_stats['total_jobs_created'])) * 100, 2
            ),
            'active_jobs_count': len(self.active_jobs)
        }

    def cancel_job(self, job_id: str) -> bool:
        """إلغاء وظيفة"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        if job.status == "running" and job_id in self.active_jobs:
            # محاولة إيقاف الخيط (لا يمكن قتل الخيط بالقوة في Python)
            job.status = "cancelled"
            job.completed_at = datetime.now().isoformat()
            
            self.system_stats['jobs_running'] -= 1
            logger.info(f"تم إلغاء الوظيفة {job_id}")
            return True
        
        elif job.status == "pending":
            job.status = "cancelled"
            job.completed_at = datetime.now().isoformat()
            
            self.system_stats['jobs_pending'] -= 1
            logger.info(f"تم إلغاء الوظيفة {job_id}")
            return True
        
        return False

    # Basic fallback methods
    def _basic_analysis(self, url: str) -> Dict[str, Any]:
        """تحليل احتياطي بسيط"""
        import requests
        from bs4 import BeautifulSoup
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': url,
                'title': soup.find('title').get_text() if soup.find('title') else '',
                'status_code': response.status_code,
                'content_length': len(response.content),
                'basic_analysis': True
            }
        except Exception as e:
            return {'error': str(e), 'basic_analysis': True}

    def _basic_content_extraction(self, url: str) -> Dict[str, Any]:
        """استخراج محتوى احتياطي"""
        return {'url': url, 'content_extraction': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}

    def _basic_asset_extraction(self, url: str) -> Dict[str, Any]:
        """استخراج أصول احتياطي"""
        return {'url': url, 'asset_extraction': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}

    def _basic_clone(self, url: str) -> Dict[str, Any]:
        """نسخ احتياطي"""
        return {'url': url, 'clone': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}

    def _basic_security_audit(self, url: str) -> Dict[str, Any]:
        """تدقيق أمني احتياطي"""
        return {'url': url, 'security_audit': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}

    def _basic_performance_analysis(self, url: str) -> Dict[str, Any]:
        """تحليل أداء احتياطي"""
        return {'url': url, 'performance_analysis': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}

    def _basic_seo_analysis(self, url: str) -> Dict[str, Any]:
        """تحليل SEO احتياطي"""
        return {'url': url, 'seo_analysis': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}

    def _basic_competitor_research(self, url: str) -> Dict[str, Any]:
        """بحث منافسين احتياطي"""
        return {'url': url, 'competitor_research': 'basic', 'message': 'أدوات متقدمة غير متوفرة'}