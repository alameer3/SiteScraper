"""
API للاستخراج الشامل المتقدم
Comprehensive Extraction API - Advanced Website Extraction
"""

from flask import Blueprint, request, jsonify, send_file
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any

from core.extractors.comprehensive_extractor import ComprehensiveExtractor, ComprehensiveExtractionConfig

# إنشاء Blueprint
comprehensive_extraction_bp = Blueprint('comprehensive_extraction', __name__)

# متغيرات عامة للتتبع
active_extractions: Dict[str, Dict] = {}
extraction_results: Dict[str, Dict] = {}

@comprehensive_extraction_bp.route('/start-comprehensive-extraction', methods=['POST'])
def start_comprehensive_extraction():
    """بدء الاستخراج الشامل المتقدم"""
    try:
        data = request.get_json()
        target_url = data.get('url', '').strip()
        
        if not target_url:
            return jsonify({'error': 'رابط الموقع مطلوب'}), 400
        
        # إعداد التكوين
        config = ComprehensiveExtractionConfig(
            target_url=target_url,
            extraction_mode=data.get('mode', 'comprehensive'),
            max_crawl_depth=data.get('max_depth', 5),
            max_pages=data.get('max_pages', 100),
            extract_interface=data.get('extract_interface', True),
            extract_technical_structure=data.get('extract_technical', True),
            extract_features=data.get('extract_features', True),
            extract_behavior=data.get('extract_behavior', True),
            enable_ai_analysis=data.get('enable_ai', True),
            enable_smart_replication=data.get('enable_replication', True),
            export_formats=data.get('export_formats', ['json', 'html'])
        )
        
        # إنشاء معرف الاستخراج
        extraction_id = f"comp_extract_{int(time.time())}"
        
        # تسجيل العملية
        active_extractions[extraction_id] = {
            'extraction_id': extraction_id,
            'url': target_url,
            'config': config,
            'started_at': datetime.now().isoformat(),
            'status': 'initializing'
        }
        
        # بدء الاستخراج في الخلفية
        import threading
        extraction_thread = threading.Thread(
            target=lambda: asyncio.run(run_comprehensive_extraction(extraction_id, target_url, config))
        )
        extraction_thread.daemon = True
        extraction_thread.start()
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'message': 'تم بدء الاستخراج الشامل بنجاح',
            'url': target_url,
            'config_summary': {
                'mode': config.extraction_mode,
                'max_pages': config.max_pages,
                'ai_enabled': config.enable_ai_analysis,
                'replication_enabled': config.enable_smart_replication
            }
        })
        
    except Exception as e:
        logging.error(f"خطأ في بدء الاستخراج الشامل: {e}")
        return jsonify({'error': str(e)}), 500

@comprehensive_extraction_bp.route('/comprehensive-status/<extraction_id>', methods=['GET'])
def get_comprehensive_status(extraction_id):
    """الحصول على حالة الاستخراج الشامل"""
    try:
        # فحص العمليات النشطة
        if extraction_id in active_extractions:
            extraction_info = active_extractions[extraction_id]
            return jsonify({
                'extraction_id': extraction_id,
                'status': extraction_info.get('status', 'running'),
                'started_at': extraction_info['started_at'],
                'url': extraction_info['url'],
                'progress': extraction_info.get('progress', {}),
                'message': 'الاستخراج الشامل جاري...'
            })
        
        # فحص النتائج المكتملة
        if extraction_id in extraction_results:
            result_info = extraction_results[extraction_id]
            return jsonify({
                'extraction_id': extraction_id,
                'status': result_info['status'],
                'completed_at': result_info.get('completed_at'),
                'failed_at': result_info.get('failed_at'),
                'url': result_info.get('url', ''),
                'summary': result_info.get('summary', {}),
                'download_links': result_info.get('download_links', [])
            })
        
        return jsonify({
            'extraction_id': extraction_id,
            'status': 'not_found',
            'message': 'معرف الاستخراج غير موجود'
        }), 404
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على حالة الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@comprehensive_extraction_bp.route('/comprehensive-result/<extraction_id>', methods=['GET'])
def get_comprehensive_result(extraction_id):
    """الحصول على نتائج الاستخراج الشامل"""
    try:
        if extraction_id not in extraction_results:
            return jsonify({
                'error': 'نتائج الاستخراج غير متوفرة أو العملية لم تكتمل بعد'
            }), 404
        
        result_info = extraction_results[extraction_id]
        
        if result_info['status'] != 'completed':
            return jsonify({
                'error': 'الاستخراج لم يكتمل بعد',
                'status': result_info['status']
            }), 400
        
        # إعادة النتائج الكاملة
        return jsonify({
            'extraction_id': extraction_id,
            'status': 'completed',
            'result': result_info.get('data', {}),
            'summary': result_info.get('summary', {}),
            'download_links': result_info.get('download_links', [])
        })
        
    except Exception as e:
        logging.error(f"خطأ في جلب نتائج الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@comprehensive_extraction_bp.route('/download-extraction/<extraction_id>/<file_type>', methods=['GET'])
def download_extraction_file(extraction_id, file_type):
    """تحميل ملفات الاستخراج"""
    try:
        if extraction_id not in extraction_results:
            return jsonify({'error': 'نتائج الاستخراج غير متوفرة'}), 404
        
        result_info = extraction_results[extraction_id]
        download_links = result_info.get('download_links', {})
        
        if file_type not in download_links:
            return jsonify({'error': f'نوع الملف {file_type} غير متوفر'}), 404
        
        file_path = download_links[file_type]
        
        # تحديد نوع المحتوى
        content_types = {
            'json': 'application/json',
            'html': 'text/html',
            'zip': 'application/zip'
        }
        
        return send_file(
            file_path,
            as_attachment=True,
            mimetype=content_types.get(file_type, 'application/octet-stream'),
            download_name=f"extraction_{extraction_id}.{file_type}"
        )
        
    except Exception as e:
        logging.error(f"خطأ في تحميل الملف: {e}")
        return jsonify({'error': str(e)}), 500

@comprehensive_extraction_bp.route('/comprehensive-history', methods=['GET'])
def get_comprehensive_history():
    """الحصول على تاريخ عمليات الاستخراج"""
    try:
        history = []
        
        # إضافة العمليات النشطة
        for extraction_id, info in active_extractions.items():
            history.append({
                'extraction_id': extraction_id,
                'url': info['url'],
                'status': info.get('status', 'running'),
                'started_at': info['started_at'],
                'type': 'comprehensive'
            })
        
        # إضافة النتائج المكتملة
        for extraction_id, info in extraction_results.items():
            history.append({
                'extraction_id': extraction_id,
                'url': info.get('url', ''),
                'status': info['status'],
                'started_at': info.get('started_at', ''),
                'completed_at': info.get('completed_at', ''),
                'type': 'comprehensive'
            })
        
        # ترتيب حسب التاريخ
        history.sort(key=lambda x: x.get('started_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'history': history[:20],  # آخر 20 عملية
            'total_active': len(active_extractions),
            'total_completed': len(extraction_results)
        })
        
    except Exception as e:
        logging.error(f"خطأ في جلب التاريخ: {e}")
        return jsonify({'error': str(e)}), 500

async def run_comprehensive_extraction(extraction_id: str, target_url: str, config: ComprehensiveExtractionConfig):
    """تشغيل الاستخراج الشامل في الخلفية"""
    try:
        # تحديث الحالة
        active_extractions[extraction_id]['status'] = 'running'
        active_extractions[extraction_id]['progress'] = {'stage': 'initialization', 'percentage': 0}
        
        # إنشاء محرك الاستخراج الشامل
        extractor = ComprehensiveExtractor(config)
        
        # تشغيل الاستخراج
        extraction_results_data = await extractor.extract_website_comprehensive(target_url)
        
        # معالجة النتائج
        summary = {
            'pages_extracted': extraction_results_data.get('statistics', {}).get('pages_extracted', 0),
            'assets_downloaded': extraction_results_data.get('statistics', {}).get('assets_downloaded', 0),
            'features_detected': extraction_results_data.get('statistics', {}).get('features_detected', 0),
            'apis_discovered': extraction_results_data.get('statistics', {}).get('apis_discovered', 0),
            'extraction_time': extraction_results_data.get('statistics', {}).get('total_time', 0)
        }
        
        # إعداد روابط التحميل
        download_links = {}
        export_results = extraction_results_data.get('export_results', {})
        
        for file_path in export_results.get('exported_files', []):
            if file_path.endswith('.json'):
                download_links['json'] = file_path
            elif file_path.endswith('.html'):
                download_links['html'] = file_path
        
        # حفظ النتائج
        extraction_results[extraction_id] = {
            'extraction_id': extraction_id,
            'status': 'completed',
            'url': target_url,
            'started_at': active_extractions[extraction_id]['started_at'],
            'completed_at': datetime.now().isoformat(),
            'data': extraction_results_data,
            'summary': summary,
            'download_links': download_links
        }
        
        # إزالة من العمليات النشطة
        if extraction_id in active_extractions:
            del active_extractions[extraction_id]
        
        logging.info(f"اكتمل الاستخراج الشامل {extraction_id} بنجاح")
        
    except Exception as e:
        logging.error(f"خطأ في الاستخراج الشامل {extraction_id}: {e}")
        
        # تسجيل الفشل
        extraction_results[extraction_id] = {
            'extraction_id': extraction_id,
            'status': 'failed',
            'url': target_url,
            'started_at': active_extractions.get(extraction_id, {}).get('started_at', ''),
            'failed_at': datetime.now().isoformat(),
            'error': str(e)
        }
        
        # إزالة من العمليات النشطة
        if extraction_id in active_extractions:
            del active_extractions[extraction_id]