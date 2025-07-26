#!/usr/bin/env python3
"""
نظام استخراج المواقع الموحد المتطور
====================================

يجمع جميع أدوات الاستخراج والتحليل في نظام واحد متطور
مع واجهات متقدمة وإدارة ذكية للملفات والنتائج

المميزات:
- استخراج شامل ومتطور للمواقع
- تحليل AI ذكي للمحتوى  
- إدارة متقدمة للأصول والملفات
- تقارير تفاعلية وتصدير متعدد الصيغ
- واجهات مستخدم متطورة
- نظام إحصائيات وتتبع شامل
"""

import os
import sys
import json
import time
import asyncio
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, asdict
import hashlib
import sqlite3
import shutil

# إعداد المسارات
sys.path.insert(0, os.path.dirname(__file__))

# استيراد الأدوات المحلية
from working_extractor import WebsiteExtractor
from unified_extractor import UnifiedWebsiteExtractor  
from advanced_tools_manager import AdvancedToolsManager
from file_manager_api import FileManagerAPI


@dataclass
class ExtractionConfig:
    """إعدادات الاستخراج الموحدة"""
    url: str = ""
    extraction_type: str = "basic"  # basic, standard, advanced, complete, ai_powered
    max_depth: int = 3
    extract_assets: bool = True
    extract_media: bool = True
    analyze_content: bool = True
    generate_reports: bool = True
    export_formats: List[str] = None
    organize_files: bool = True
    ai_analysis: bool = False
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["json", "html"]


class UnifiedWebsiteSystem:
    """النظام الموحد لاستخراج ونسخ المواقع"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # مستخرجات متعددة
        self.basic_extractor = WebsiteExtractor()
        self.unified_extractor = UnifiedWebsiteExtractor()
        self.advanced_tools = AdvancedToolsManager()
        self.file_manager = FileManagerAPI()
        
        # إعدادات النظام
        self.results_db = Path("unified_results.db")
        self.outputs_dir = Path("extracted_websites")
        self.outputs_dir.mkdir(exist_ok=True)
        
        # إنشاء قاعدة البيانات
        self._init_database()
        
        # إحصائيات
        self.stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_data_extracted_mb': 0,
            'start_time': datetime.now()
        }
        
        self.logger.info("تم تشغيل النظام الموحد لاستخراج المواقع")
    
    def _setup_logging(self):
        """إعداد نظام التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('unified_system.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _init_database(self):
        """إنشاء قاعدة البيانات للنتائج"""
        with sqlite3.connect(self.results_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    extraction_type TEXT,
                    status TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    pages_extracted INTEGER,
                    assets_downloaded INTEGER,
                    total_size_mb REAL,
                    output_path TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS extraction_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT UNIQUE,
                    stat_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def extract_website(self, config: ExtractionConfig) -> Dict[str, Any]:
        """استخراج شامل للموقع مع جميع المميزات"""
        extraction_id = f"extract_{int(time.time() * 1000)}"
        start_time = time.time()
        
        self.logger.info(f"بدء استخراج موقع: {config.url}")
        self.stats['total_extractions'] += 1
        
        # إنشاء مجلد مخصص للاستخراج
        output_path = self.outputs_dir / extraction_id
        output_path.mkdir(exist_ok=True)
        
        # تسجيل بداية العملية في قاعدة البيانات
        with sqlite3.connect(self.results_db) as conn:
            conn.execute("""
                INSERT INTO extractions 
                (url, extraction_type, status, start_time, output_path)
                VALUES (?, ?, ?, ?, ?)
            """, (config.url, config.extraction_type, 'processing', 
                  datetime.now(), str(output_path)))
        
        try:
            # اختيار المستخرج المناسب
            if config.extraction_type == "basic":
                result = self.basic_extractor.extract_website(config.url, config.extraction_type)
            elif config.extraction_type in ["advanced", "complete"]:
                result = self.unified_extractor.extract_website(config.url, config.extraction_type)
            elif config.extraction_type == "ai_powered":
                result = await self._extract_with_ai(config)
            else:
                result = self.basic_extractor.extract_website(config.url, config.extraction_type)
            
            # إضافة تحليل محتوى إضافي
            if config.analyze_content and 'content' in result:
                ai_analysis = self.advanced_tools.analyze_with_ai(
                    result['content'], 'comprehensive'
                )
                result['ai_analysis'] = ai_analysis
            
            # تنظيم الملفات
            if config.organize_files:
                organized_result = await self._organize_extraction_files(
                    result, output_path, extraction_id
                )
                result.update(organized_result)
            
            # إنشاء التقارير
            if config.generate_reports:
                reports = await self._generate_reports(result, output_path, config.export_formats)
                result['reports'] = reports
            
            # حساب الإحصائيات
            duration = time.time() - start_time
            total_size_mb = self._calculate_extraction_size(output_path)
            
            # تحديث قاعدة البيانات
            with sqlite3.connect(self.results_db) as conn:
                conn.execute("""
                    UPDATE extractions 
                    SET status=?, end_time=?, duration_seconds=?, 
                        pages_extracted=?, assets_downloaded=?, total_size_mb=?,
                        metadata=?
                    WHERE output_path=?
                """, ('completed', datetime.now(), duration,
                      result.get('pages_extracted', 1),
                      result.get('assets_downloaded', 0),
                      total_size_mb,
                      json.dumps(result.get('metadata', {})),
                      str(output_path)))
            
            # تحديث الإحصائيات العامة
            self.stats['successful_extractions'] += 1
            self.stats['total_data_extracted_mb'] += total_size_mb
            
            # إعداد النتيجة النهائية
            final_result = {
                'extraction_id': extraction_id,
                'success': True,
                'url': config.url,
                'extraction_type': config.extraction_type,
                'duration_seconds': round(duration, 2),
                'output_path': str(output_path),
                'total_size_mb': round(total_size_mb, 2),
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            
            self.logger.info(f"تم الانتهاء من الاستخراج بنجاح: {extraction_id}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"خطأ في الاستخراج: {str(e)}")
            self.stats['failed_extractions'] += 1
            
            # تحديث حالة قاعدة البيانات
            with sqlite3.connect(self.results_db) as conn:
                conn.execute("""
                    UPDATE extractions 
                    SET status=?, end_time=?, metadata=?
                    WHERE output_path=?
                """, ('failed', datetime.now(), 
                      json.dumps({'error': str(e)}),
                      str(output_path)))
            
            return {
                'extraction_id': extraction_id,
                'success': False,
                'error': str(e),
                'url': config.url,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _extract_with_ai(self, config: ExtractionConfig) -> Dict[str, Any]:
        """استخراج متقدم بالذكاء الاصطناعي"""
        try:
            # استخدام الأدوات المتقدمة
            ai_result = self.advanced_tools.extract_with_cloner_pro(
                config.url, {'analyze_with_ai': True}
            )
            return ai_result
        except Exception as e:
            self.logger.error(f"خطأ في الاستخراج بالذكاء الاصطناعي: {e}")
            # العودة للاستخراج العادي
            return self.unified_extractor.extract_website(config.url, 'advanced')
    
    async def _organize_extraction_files(self, result: Dict, output_path: Path, extraction_id: str) -> Dict[str, Any]:
        """تنظيم ملفات الاستخراج"""
        organized_structure = {
            '01_content': output_path / '01_content',
            '02_assets': output_path / '02_assets', 
            '03_reports': output_path / '03_reports',
            '04_metadata': output_path / '04_metadata'
        }
        
        # إنشاء المجلدات
        for folder in organized_structure.values():
            folder.mkdir(exist_ok=True)
        
        # حفظ المحتوى الرئيسي
        if 'content' in result:
            content_file = organized_structure['01_content'] / 'main_content.html'
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(result['content'])
        
        # حفظ البيانات الوصفية
        metadata_file = organized_structure['04_metadata'] / 'extraction_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return {
            'organized_structure': {k: str(v) for k, v in organized_structure.items()},
            'organization_completed': True
        }
    
    async def _generate_reports(self, result: Dict, output_path: Path, formats: List[str]) -> Dict[str, str]:
        """إنشاء التقارير بصيغ متعددة"""
        reports = {}
        reports_dir = output_path / '03_reports'
        
        for format_type in formats:
            if format_type == 'json':
                report_file = reports_dir / 'extraction_report.json'
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                reports['json'] = str(report_file)
            
            elif format_type == 'html':
                report_file = reports_dir / 'extraction_report.html'
                html_content = self._generate_html_report(result)
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                reports['html'] = str(report_file)
        
        return reports
    
    def _generate_html_report(self, result: Dict) -> str:
        """إنشاء تقرير HTML متطور"""
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير استخراج الموقع - {result.get('url', 'غير محدد')}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    direction: rtl;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 2px solid #eee;
                    margin-bottom: 30px;
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background: #f8f9fa;
                }}
                .section h3 {{
                    color: #333;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                .data-item {{
                    margin: 10px 0;
                    padding: 8px;
                    background: white;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌐 تقرير استخراج الموقع</h1>
                    <p><strong>الموقع:</strong> {result.get('url', 'غير محدد')}</p>
                    <p><strong>التاريخ:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="metric-grid">
                    <div class="metric-card">
                        <h3>📊 العنوان</h3>
                        <p>{result.get('title', 'غير محدد')}</p>
                    </div>
                    <div class="metric-card">
                        <h3>🔗 الروابط</h3>
                        <p>{result.get('links_count', 0)}</p>
                    </div>
                    <div class="metric-card">
                        <h3>🖼️ الصور</h3>
                        <p>{result.get('images_count', 0)}</p>
                    </div>
                    <div class="metric-card">
                        <h3>⚙️ السكريبتات</h3>
                        <p>{result.get('scripts_count', 0)}</p>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🔍 التقنيات المكتشفة</h3>
                    <div class="data-item">
                        {json.dumps(result.get('technologies', {}), ensure_ascii=False, indent=2)}
                    </div>
                </div>
                
                <div class="section">
                    <h3>📈 إحصائيات الاستخراج</h3>
                    <div class="data-item">
                        <p><strong>حالة الاستجابة:</strong> {result.get('status_code', 'غير محدد')}</p>
                        <p><strong>نوع المحتوى:</strong> {result.get('content_type', 'غير محدد')}</p>
                        <p><strong>طول المحتوى:</strong> {result.get('content_length', 0)} حرف</p>
                        <p><strong>وقت الاستخراج:</strong> {result.get('extraction_time', 0)} ثانية</p>
                    </div>
                </div>
                
                <div class="footer" style="text-align: center; margin-top: 40px; color: #666;">
                    <p>تم إنشاء هذا التقرير بواسطة النظام الموحد لاستخراج المواقع</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _calculate_extraction_size(self, path: Path) -> float:
        """حساب حجم الاستخراج بالميجابايت"""
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except:
            pass
        return total_size / (1024 * 1024)  # تحويل إلى ميجابايت
    
    def get_system_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        uptime = datetime.now() - self.stats['start_time']
        
        # إحصائيات قاعدة البيانات
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
                    AVG(duration_seconds) as avg_duration,
                    SUM(total_size_mb) as total_size_mb
                FROM extractions
            """)
            db_stats = cursor.fetchone()
        
        return {
            'system_uptime': str(uptime),
            'memory_stats': self.stats,
            'database_stats': {
                'total_extractions': db_stats[0] or 0,
                'completed_extractions': db_stats[1] or 0,
                'failed_extractions': db_stats[2] or 0,
                'average_duration_seconds': round(db_stats[3] or 0, 2),
                'total_data_extracted_mb': round(db_stats[4] or 0, 2)
            },
            'tools_status': self.advanced_tools.get_tools_status(),
            'file_manager_stats': self.file_manager.get_storage_stats(),
            'system_health': 'excellent' if (db_stats[1] or 0) > (db_stats[2] or 0) else 'good'
        }
    
    def get_recent_extractions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """الحصول على آخر عمليات الاستخراج"""
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute("""
                SELECT url, extraction_type, status, duration_seconds,
                       pages_extracted, total_size_mb, created_at
                FROM extractions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'url': row[0],
                    'extraction_type': row[1],
                    'status': row[2],
                    'duration_seconds': row[3],
                    'pages_extracted': row[4],
                    'total_size_mb': row[5],
                    'created_at': row[6]
                })
            
            return results
    
    async def cleanup_old_extractions(self, days_old: int = 30) -> Dict[str, Any]:
        """تنظيف الاستخراجات القديمة"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # البحث عن الاستخراجات القديمة
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute("""
                SELECT output_path, total_size_mb
                FROM extractions
                WHERE created_at < ?
            """, (cutoff_date,))
            
            old_extractions = cursor.fetchall()
            
            # حذف الملفات والمجلدات
            cleaned_size = 0
            cleaned_count = 0
            
            for output_path, size_mb in old_extractions:
                try:
                    path = Path(output_path)
                    if path.exists():
                        shutil.rmtree(path)
                        cleaned_size += size_mb or 0
                        cleaned_count += 1
                except Exception as e:
                    self.logger.error(f"خطأ في حذف {output_path}: {e}")
            
            # حذف السجلات من قاعدة البيانات
            conn.execute("""
                DELETE FROM extractions
                WHERE created_at < ?
            """, (cutoff_date,))
        
        return {
            'cleaned_extractions': cleaned_count,
            'freed_space_mb': round(cleaned_size, 2),
            'cutoff_date': cutoff_date.isoformat()
        }


# إنشاء نسخة عامة من النظام
unified_system = UnifiedWebsiteSystem()


def create_flask_integration(app):
    """دمج النظام مع Flask"""
    
    @app.route('/api/unified/extract', methods=['POST'])
    def api_unified_extract():
        """API موحد للاستخراج"""
        from flask import request, jsonify
        
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        config = ExtractionConfig(
            url=data['url'],
            extraction_type=data.get('extraction_type', 'basic'),
            max_depth=data.get('max_depth', 3),
            extract_assets=data.get('extract_assets', True),
            analyze_content=data.get('analyze_content', True),
            generate_reports=data.get('generate_reports', True),
            export_formats=data.get('export_formats', ['json', 'html']),
            ai_analysis=data.get('ai_analysis', False)
        )
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(unified_system.extract_website(config))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/unified/stats')
    def api_unified_stats():
        """API إحصائيات النظام"""
        from flask import jsonify
        return jsonify(unified_system.get_system_stats())
    
    @app.route('/api/unified/recent')
    def api_unified_recent():
        """API آخر الاستخراجات"""
        from flask import jsonify, request
        limit = request.args.get('limit', 10, type=int)
        return jsonify(unified_system.get_recent_extractions(limit))


if __name__ == '__main__':
    print("🚀 النظام الموحد لاستخراج المواقع")
    print("=" * 50)
    
    # عرض إحصائيات النظام
    stats = unified_system.get_system_stats()
    print(f"📊 إجمالي الاستخراجات: {stats['database_stats']['total_extractions']}")
    print(f"✅ الناجحة: {stats['database_stats']['completed_extractions']}")
    print(f"❌ الفاشلة: {stats['database_stats']['failed_extractions']}")
    print(f"💾 البيانات المستخرجة: {stats['database_stats']['total_data_extracted_mb']:.2f} MB")
    print(f"🏥 حالة النظام: {stats['system_health']}")