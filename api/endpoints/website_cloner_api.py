"""
Website Cloner Pro API Endpoints
واجهات برمجة التطبيقات لأداة Website Cloner Pro
"""

from flask import Blueprint, request, jsonify, send_file
import asyncio
import logging
import json
import os
import time
from typing import Dict, Any
from datetime import datetime
import threading
from pathlib import Path

# Import Website Cloner Integration
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.extractors.website_cloner_integration import (
    WebsiteClonerIntegration, 
    IntegratedExtractionConfig,
    create_integrated_extractor
)
from website_cloner_pro import WebsiteClonerPro, CloningConfig

# Create Blueprint
cloner_api = Blueprint('cloner_api', __name__)

# Global storage for async results
extraction_results = {}
extraction_status = {}

def run_async_extraction(extraction_id: str, target_url: str, config: Dict[str, Any]):
    """تشغيل الاستخراج غير المتزامن"""
    async def extract():
        try:
            extraction_status[extraction_id] = {
                'status': 'running',
                'progress': 0,
                'start_time': datetime.now().isoformat(),
                'message': 'بدء عملية الاستخراج...'
            }
            
            # Create integrated extractor
            integrator = create_integrated_extractor(
                target_url=target_url,
                primary_tool=config.get('primary_tool', 'website_cloner_pro'),
                use_hybrid=config.get('use_hybrid', False)
            )
            
            extraction_status[extraction_id]['progress'] = 10
            extraction_status[extraction_id]['message'] = 'تهيئة أدوات الاستخراج...'
            
            # Run extraction
            result = await integrator.extract_website_integrated(target_url)
            
            extraction_status[extraction_id]['progress'] = 100
            extraction_status[extraction_id]['status'] = 'completed'
            extraction_status[extraction_id]['message'] = 'تم الانتهاء من الاستخراج'
            extraction_status[extraction_id]['end_time'] = datetime.now().isoformat()
            
            extraction_results[extraction_id] = result
            
        except Exception as e:
            extraction_status[extraction_id]['status'] = 'failed'
            extraction_status[extraction_id]['error'] = str(e)
            extraction_status[extraction_id]['message'] = f'فشل في الاستخراج: {e}'
            logging.error(f"خطأ في الاستخراج {extraction_id}: {e}")
    
    # Run in new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(extract())
    loop.close()

@cloner_api.route('/api/website-cloner/extract', methods=['POST'])
def start_extraction():
    """بدء عملية استخراج جديدة"""
    try:
        data = request.get_json()
        
        if not data or not data.get('target_url'):
            return jsonify({
                'success': False,
                'error': 'رابط الموقع مطلوب'
            }), 400
        
        target_url = data['target_url']
        
        # Generate extraction ID
        extraction_id = f"extract_{int(time.time())}"
        
        # Extract configuration
        config = {
            'primary_tool': data.get('primary_tool', 'website_cloner_pro'),
            'max_depth': data.get('max_depth', 3),
            'max_pages': data.get('max_pages', 50),
            'extract_all_content': data.get('extract_all_content', True),
            'analyze_with_ai': data.get('analyze_with_ai', True),
            'generate_reports': data.get('generate_reports', True),
            'extract_assets': data.get('extract_assets', True),
            'use_hybrid': data.get('use_hybrid', False)
        }
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=run_async_extraction,
            args=(extraction_id, target_url, config)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'message': 'تم بدء عملية الاستخراج',
            'status_url': f'/api/website-cloner/status/{extraction_id}',
            'results_url': f'/api/website-cloner/results/{extraction_id}'
        })
        
    except Exception as e:
        logging.error(f"خطأ في بدء الاستخراج: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@cloner_api.route('/api/website-cloner/status/<extraction_id>', methods=['GET'])
def get_extraction_status(extraction_id: str):
    """الحصول على حالة الاستخراج"""
    try:
        if extraction_id not in extraction_status:
            return jsonify({
                'success': False,
                'error': 'معرف الاستخراج غير موجود'
            }), 404
        
        status = extraction_status[extraction_id]
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'status': status['status'],
            'progress': status['progress'],
            'message': status['message'],
            'start_time': status.get('start_time'),
            'end_time': status.get('end_time'),
            'error': status.get('error')
        })
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على حالة الاستخراج: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@cloner_api.route('/api/website-cloner/results/<extraction_id>', methods=['GET'])
def get_extraction_results(extraction_id: str):
    """الحصول على نتائج الاستخراج"""
    try:
        if extraction_id not in extraction_results:
            return jsonify({
                'success': False,
                'error': 'نتائج الاستخراج غير متوفرة'
            }), 404
        
        results = extraction_results[extraction_id]
        status = extraction_status.get(extraction_id, {})
        
        # Create summary response
        response = {
            'success': True,
            'extraction_id': extraction_id,
            'status': status.get('status', 'unknown'),
            'metadata': results.get('metadata', {}),
            'summary': {
                'primary_tool': results.get('metadata', {}).get('primary_tool'),
                'duration': results.get('metadata', {}).get('duration'),
                'target_url': results.get('metadata', {}).get('target_url')
            }
        }
        
        # Add Website Cloner Pro results
        cloner_results = results.get('website_cloner_results', {})
        if cloner_results:
            response['website_cloner_summary'] = {
                'success': cloner_results.get('success', False),
                'pages_extracted': cloner_results.get('pages_extracted', 0),
                'assets_downloaded': cloner_results.get('assets_downloaded', 0),
                'total_size': cloner_results.get('total_size', 0),
                'technologies_detected': cloner_results.get('technologies_detected', []),
                'output_path': cloner_results.get('output_path')
            }
        
        # Add comparison analysis
        comparison = results.get('comparison_analysis', {})
        if comparison:
            response['comparison_analysis'] = comparison
        
        # Add integrated summary
        integrated_summary = results.get('integrated_summary', {})
        if integrated_summary:
            response['integrated_summary'] = {
                'quality_score': integrated_summary.get('quality_score', 0),
                'primary_source': integrated_summary.get('primary_source'),
                'combined_technologies': integrated_summary.get('combined_technologies', [])
            }
        
        # Add recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            response['recommendations'] = recommendations
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على نتائج الاستخراج: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@cloner_api.route('/api/website-cloner/results/<extraction_id>/detailed', methods=['GET'])
def get_detailed_results(extraction_id: str):
    """الحصول على النتائج المفصلة كاملة"""
    try:
        if extraction_id not in extraction_results:
            return jsonify({
                'success': False,
                'error': 'نتائج الاستخراج غير متوفرة'
            }), 404
        
        results = extraction_results[extraction_id]
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'detailed_results': results
        })
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على النتائج المفصلة: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@cloner_api.route('/api/website-cloner/download/<extraction_id>/<file_type>', methods=['GET'])
def download_extraction_file(extraction_id: str, file_type: str):
    """تحميل ملفات الاستخراج"""
    try:
        if extraction_id not in extraction_results:
            return jsonify({
                'success': False,
                'error': 'نتائج الاستخراج غير متوفرة'
            }), 404
        
        results = extraction_results[extraction_id]
        cloner_results = results.get('website_cloner_results', {})
        output_path = cloner_results.get('output_path')
        
        if not output_path or not os.path.exists(output_path):
            return jsonify({
                'success': False,
                'error': 'ملفات الاستخراج غير متوفرة'
            }), 404
        
        # Determine file path based on type
        file_path = None
        download_name = None
        
        if file_type == 'json':
            # Look for JSON export files
            exports_dir = os.path.join(output_path, '06_exports')
            if os.path.exists(exports_dir):
                for file in os.listdir(exports_dir):
                    if file.endswith('.json'):
                        file_path = os.path.join(exports_dir, file)
                        download_name = f"extraction_{extraction_id}.json"
                        break
        
        elif file_type == 'csv':
            # Look for CSV export files
            exports_dir = os.path.join(output_path, '06_exports')
            if os.path.exists(exports_dir):
                for file in os.listdir(exports_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(exports_dir, file)
                        download_name = f"extraction_{extraction_id}.csv"
                        break
        
        elif file_type == 'site':
            # Look for replicated site
            site_dir = os.path.join(output_path, '05_replicated_site')
            if os.path.exists(site_dir):
                # Create zip file of the site
                import zipfile
                import tempfile
                
                temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(site_dir):
                        for file in files:
                            file_path_full = os.path.join(root, file)
                            arcname = os.path.relpath(file_path_full, site_dir)
                            zipf.write(file_path_full, arcname)
                
                file_path = temp_zip.name
                download_name = f"replicated_site_{extraction_id}.zip"
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'نوع الملف {file_type} غير متوفر'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logging.error(f"خطأ في تحميل الملف: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@cloner_api.route('/api/website-cloner/list', methods=['GET'])
def list_extractions():
    """قائمة جميع عمليات الاستخراج"""
    try:
        extractions = []
        
        for extraction_id, status in extraction_status.items():
            extraction_info = {
                'extraction_id': extraction_id,
                'status': status['status'],
                'start_time': status.get('start_time'),
                'end_time': status.get('end_time'),
                'message': status.get('message', '')
            }
            
            # Add results summary if available
            if extraction_id in extraction_results:
                results = extraction_results[extraction_id]
                cloner_results = results.get('website_cloner_results', {})
                extraction_info['summary'] = {
                    'target_url': results.get('metadata', {}).get('target_url'),
                    'pages_extracted': cloner_results.get('pages_extracted', 0),
                    'success': cloner_results.get('success', False)
                }
            
            extractions.append(extraction_info)
        
        # Sort by start time (newest first)
        extractions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'extractions': extractions,
            'total_count': len(extractions)
        })
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على قائمة الاستخراج: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@cloner_api.route('/api/website-cloner/health', methods=['GET'])
def health_check():
    """فحص حالة الخدمة"""
    try:
        # Test Website Cloner Pro import
        from website_cloner_pro import WebsiteClonerPro
        
        return jsonify({
            'success': True,
            'service': 'Website Cloner Pro API',
            'status': 'healthy',
            'version': '1.0.0',
            'endpoints': [
                '/api/website-cloner/extract',
                '/api/website-cloner/status/<id>',
                '/api/website-cloner/results/<id>',
                '/api/website-cloner/download/<id>/<type>',
                '/api/website-cloner/list'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': 'Website Cloner Pro API',
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Cleanup function for old results
def cleanup_old_results():
    """تنظيف النتائج القديمة"""
    try:
        current_time = time.time()
        # Remove results older than 24 hours
        old_extractions = []
        
        for extraction_id, status in extraction_status.items():
            start_time_str = status.get('start_time')
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                age = current_time - start_time.timestamp()
                if age > 86400:  # 24 hours
                    old_extractions.append(extraction_id)
        
        for extraction_id in old_extractions:
            extraction_status.pop(extraction_id, None)
            extraction_results.pop(extraction_id, None)
            
        logging.info(f"تم تنظيف {len(old_extractions)} نتيجة قديمة")
        
    except Exception as e:
        logging.error(f"خطأ في تنظيف النتائج القديمة: {e}")

# Auto cleanup every hour
import atexit
import threading
def schedule_cleanup():
    cleanup_old_results()
    timer = threading.Timer(3600.0, schedule_cleanup)  # 1 hour
    timer.daemon = True
    timer.start()

# Start cleanup scheduler
schedule_cleanup()
atexit.register(lambda: logging.info("Website Cloner API shutting down"))