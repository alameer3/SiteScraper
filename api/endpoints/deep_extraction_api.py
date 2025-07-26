"""
API endpoints لمحرك الاستخراج العميق
Deep Extraction API - Advanced Website Extraction Endpoints

توفر واجهات برمجية متقدمة للتحكم في عملية الاستخراج العميق
"""

from flask import Blueprint, request, jsonify, current_app
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

# استيراد محركات الاستخراج
from core.extractors.deep_extraction_engine import DeepExtractionEngine, ExtractionConfig
from core.extractors.website_replicator import WebsiteReplicator
from core.extractors.asset_downloader import AssetDownloader, AssetDownloadConfig

# إنشاء Blueprint
deep_extraction_bp = Blueprint('deep_extraction', __name__, url_prefix='/api/deep-extraction')

# تخزين مؤقت للعمليات الجارية
active_extractions = {}
extraction_results = {}

@deep_extraction_bp.route('/start', methods=['POST'])
def start_deep_extraction():
    """بدء عملية الاستخراج العميق"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        target_url = data['url']
        config_data = data.get('config', {})
        
        # إنشاء تكوين الاستخراج
        config = ExtractionConfig(
            mode=config_data.get('mode', 'comprehensive'),
            max_depth=config_data.get('max_depth', 3),
            max_pages=config_data.get('max_pages', 50),
            include_assets=config_data.get('include_assets', True),
            include_javascript=config_data.get('include_javascript', True),
            include_css=config_data.get('include_css', True),
            extract_apis=config_data.get('extract_apis', True),
            analyze_behavior=config_data.get('analyze_behavior', True),
            extract_database_schema=config_data.get('extract_database_schema', False),
            timeout=config_data.get('timeout', 30),
            delay_between_requests=config_data.get('delay_between_requests', 1.0),
            respect_robots_txt=config_data.get('respect_robots_txt', True),
            enable_playwright=config_data.get('enable_playwright', True),
            enable_selenium=config_data.get('enable_selenium', True),
            output_directory=config_data.get('output_directory', 'extracted_sites')
        )
        
        # إنشاء محرك الاستخراج
        extraction_engine = DeepExtractionEngine(config)
        
        # بدء الاستخراج في خيط منفصل
        extraction_id = f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # تشغيل الاستخراج بشكل غير متزامن
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        def run_extraction():
            try:
                result = loop.run_until_complete(extraction_engine.extract_complete_website(target_url))
                extraction_results[extraction_id] = {
                    'status': 'completed',
                    'result': result,
                    'completed_at': datetime.now().isoformat()
                }
            except Exception as e:
                extraction_results[extraction_id] = {
                    'status': 'failed',
                    'error': str(e),
                    'failed_at': datetime.now().isoformat()
                }
            finally:
                if extraction_id in active_extractions:
                    del active_extractions[extraction_id]
        
        # تشغيل في خيط منفصل
        import threading
        thread = threading.Thread(target=run_extraction)
        thread.start()
        
        # تسجيل العملية النشطة
        active_extractions[extraction_id] = {
            'url': target_url,
            'config': config_data,
            'started_at': datetime.now().isoformat(),
            'status': 'running',
            'thread': thread
        }
        
        return jsonify({
            'extraction_id': extraction_id,
            'status': 'started',
            'message': 'تم بدء عملية الاستخراج العميق',
            'url': target_url,
            'config': config_data
        })
        
    except Exception as e:
        logging.error(f"خطأ في بدء الاستخراج العميق: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/status/<extraction_id>', methods=['GET'])
def get_extraction_status(extraction_id):
    """الحصول على حالة عملية الاستخراج"""
    try:
        # فحص العمليات النشطة
        if extraction_id in active_extractions:
            extraction_info = active_extractions[extraction_id]
            return jsonify({
                'extraction_id': extraction_id,
                'status': 'running',
                'started_at': extraction_info['started_at'],
                'url': extraction_info['url'],
                'message': 'عملية الاستخراج جارية...'
            })
        
        # فحص النتائج المكتملة
        if extraction_id in extraction_results:
            result_info = extraction_results[extraction_id]
            return jsonify({
                'extraction_id': extraction_id,
                'status': result_info['status'],
                'completed_at': result_info.get('completed_at'),
                'failed_at': result_info.get('failed_at'),
                'error': result_info.get('error'),
                'has_result': 'result' in result_info
            })
        
        return jsonify({'error': 'عملية الاستخراج غير موجودة'}), 404
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على حالة الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/result/<extraction_id>', methods=['GET'])
def get_extraction_result(extraction_id):
    """الحصول على نتائج الاستخراج"""
    try:
        if extraction_id not in extraction_results:
            return jsonify({'error': 'نتائج الاستخراج غير موجودة'}), 404
        
        result_info = extraction_results[extraction_id]
        
        if result_info['status'] != 'completed':
            return jsonify({
                'error': 'عملية الاستخراج لم تكتمل بعد',
                'status': result_info['status']
            }), 400
        
        return jsonify({
            'extraction_id': extraction_id,
            'status': 'completed',
            'result': result_info['result'],
            'completed_at': result_info['completed_at']
        })
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على نتائج الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/replicate', methods=['POST'])
def start_website_replication():
    """بدء عملية النسخ المتماثل للموقع"""
    try:
        data = request.get_json()
        
        if not data or 'extraction_id' not in data:
            return jsonify({'error': 'معرف الاستخراج مطلوب'}), 400
        
        extraction_id = data['extraction_id']
        
        # التحقق من وجود نتائج الاستخراج
        if extraction_id not in extraction_results:
            return jsonify({'error': 'نتائج الاستخراج غير موجودة'}), 404
        
        result_info = extraction_results[extraction_id]
        if result_info['status'] != 'completed':
            return jsonify({'error': 'عملية الاستخراج لم تكتمل بعد'}), 400
        
        # إعداد تكوين النسخ
        replication_config_data = data.get('config', {})
        # تكوين النسخ (تم تبسيطه)
        replication_settings = {
            'framework': replication_config_data.get('framework', 'html'),
            'output_directory': replication_config_data.get('target_directory', f'replicated_site_{extraction_id}')
        }
        
        # إنشاء مولد النسخ المتماثل
        replicator = WebsiteReplicator()
        
        # بدء عملية النسخ
        replication_result = replicator.replicate_website(result_info['result'])
        
        return jsonify({
            'extraction_id': extraction_id,
            'replication_status': 'completed',
            'result': replication_result,
            'message': 'تم إنشاء الموقع المطابق بنجاح'
        })
        
    except Exception as e:
        logging.error(f"خطأ في النسخ المتماثل: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/analyze-with-ai', methods=['POST'])
def analyze_with_ai():
    """تحليل بالذكاء الاصطناعي"""
    try:
        data = request.get_json()
        
        if not data or 'extraction_id' not in data:
            return jsonify({'error': 'معرف الاستخراج مطلوب'}), 400
        
        extraction_id = data['extraction_id']
        
        # التحقق من وجود نتائج الاستخراج
        if extraction_id not in extraction_results:
            return jsonify({'error': 'نتائج الاستخراج غير موجودة'}), 404
        
        result_info = extraction_results[extraction_id]
        if result_info['status'] != 'completed':
            return jsonify({'error': 'عملية الاستخراج لم تكتمل بعد'}), 400
        
        # إعداد تكوين الذكاء الاصطناعي
        ai_config_data = data.get('config', {})
        # تكوين AI مبسط
        ai_settings = {
            'depth': ai_config_data.get('analysis_depth', 'comprehensive'),
            'confidence': ai_config_data.get('confidence_threshold', 0.8)
        }
        
        # استخدام AI Analyzer الموجود
        from core.analyzers.ai_analyzer import AIAnalyzer
        ai_engine = AIAnalyzer()
        
        # تحليل بالذكاء الاصطناعي
        ai_analysis = ai_engine.analyze_content(result_info['result'])
        
        return jsonify({
            'extraction_id': extraction_id,
            'ai_analysis_status': 'completed',
            'analysis_result': ai_analysis,
            'message': 'تم التحليل بالذكاء الاصطناعي بنجاح'
        })
        
    except Exception as e:
        logging.error(f"خطأ في التحليل بالذكاء الاصطناعي: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/list-extractions', methods=['GET'])
def list_extractions():
    """قائمة جميع عمليات الاستخراج"""
    try:
        extractions = []
        
        # إضافة العمليات النشطة
        for extraction_id, info in active_extractions.items():
            extractions.append({
                'extraction_id': extraction_id,
                'status': 'running',
                'url': info['url'],
                'started_at': info['started_at']
            })
        
        # إضافة النتائج المكتملة
        for extraction_id, result in extraction_results.items():
            extractions.append({
                'extraction_id': extraction_id,
                'status': result['status'],
                'completed_at': result.get('completed_at'),
                'failed_at': result.get('failed_at'),
                'has_error': 'error' in result
            })
        
        return jsonify({
            'extractions': extractions,
            'total_count': len(extractions),
            'active_count': len(active_extractions),
            'completed_count': len([e for e in extractions if e['status'] == 'completed'])
        })
        
    except Exception as e:
        logging.error(f"خطأ في جلب قائمة الاستخراجات: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/cancel/<extraction_id>', methods=['POST'])
def cancel_extraction(extraction_id):
    """إلغاء عملية استخراج جارية"""
    try:
        if extraction_id not in active_extractions:
            return jsonify({'error': 'عملية الاستخراج غير موجودة أو مكتملة'}), 404
        
        # إيقاف العملية
        extraction_info = active_extractions[extraction_id]
        thread = extraction_info.get('thread')
        
        if thread and thread.is_alive():
            # في بيئة الإنتاج، ستحتاج إلى آلية أكثر تطوراً لإيقاف العمليات
            pass  # Thread cancellation would be implemented here
        
        # تنظيف البيانات
        del active_extractions[extraction_id]
        
        return jsonify({
            'extraction_id': extraction_id,
            'status': 'cancelled',
            'message': 'تم إلغاء عملية الاستخراج'
        })
        
    except Exception as e:
        logging.error(f"خطأ في إلغاء الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@deep_extraction_bp.route('/cleanup', methods=['POST'])
def cleanup_old_extractions():
    """تنظيف النتائج القديمة"""
    try:
        data = request.get_json()
        max_age_hours = data.get('max_age_hours', 24) if data else 24
        
        # تنظيف النتائج القديمة
        current_time = datetime.now()
        cleaned_count = 0
        
        extraction_ids_to_remove = []
        for extraction_id, result in extraction_results.items():
            completed_at = result.get('completed_at')
            failed_at = result.get('failed_at')
            
            timestamp_str = completed_at or failed_at
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
                age_hours = (current_time - timestamp).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    extraction_ids_to_remove.append(extraction_id)
        
        for extraction_id in extraction_ids_to_remove:
            del extraction_results[extraction_id]
            cleaned_count += 1
        
        return jsonify({
            'cleaned_count': cleaned_count,
            'remaining_count': len(extraction_results),
            'message': f'تم حذف {cleaned_count} نتيجة قديمة'
        })
        
    except Exception as e:
        logging.error(f"خطأ في تنظيف النتائج: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@deep_extraction_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'طلب غير صحيح'}), 400

@deep_extraction_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'المورد غير موجود'}), 404

@deep_extraction_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'خطأ داخلي في الخادم'}), 500