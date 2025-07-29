"""
واجهة Flask للاستخراج المتطور
Advanced Extraction Flask Interface
"""

import os
import time
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, current_app
from werkzeug.middleware.proxy_fix import ProxyFix

# استيراد محرك الاستخراج المطور
from .advanced_extractor import AdvancedWebsiteExtractor, quick_extract, batch_extract


# إعداد Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# مجلد الاستخراج الرئيسي
OUTPUT_DIR = Path("extracted_sites")
OUTPUT_DIR.mkdir(exist_ok=True)


# متغيرات النظام
extraction_history = []
active_extractions = {}


@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('unified_extractor.html', 
                         recent_extractions=extraction_history[-10:])


@app.route('/extract', methods=['POST'])
def extract_website():
    """استخراج موقع واحد"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        url = data.get('url', '').strip()
        extraction_type = data.get('extraction_type', 'standard')
        custom_options = data.get('options', {})
        
        if not url:
            return jsonify({'success': False, 'error': 'الرجاء إدخال رابط صحيح'})
        
        # إعداد الاستخراج
        extractor = AdvancedWebsiteExtractor(str(OUTPUT_DIR))
        
        # بدء الاستخراج
        extraction_id = str(int(time.time() * 1000))
        active_extractions[extraction_id] = {
            'status': 'running',
            'url': url,
            'extraction_type': extraction_type,
            'start_time': time.time()
        }
        
        # تنفيذ الاستخراج
        if custom_options and isinstance(custom_options, dict):
            result = extractor.extract_with_custom_config(url, custom_options)
        else:
            result = extractor.extract(url, extraction_type)
        
        # تحديث الحالة
        active_extractions[extraction_id]['status'] = 'completed'
        active_extractions[extraction_id]['result'] = result
        
        # إضافة للتاريخ
        extraction_record = {
            'id': extraction_id,
            'url': url,
            'extraction_type': extraction_type,
            'timestamp': time.time(),
            'success': result.get('success', False),
            'duration': result.get('duration', 0),
            'files_count': len(result.get('assets', {}).get('downloaded_files', [])),
            'folder_path': result.get('output_folder', '')
        }
        extraction_history.append(extraction_record)
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'result': result,
            'message': 'تم الاستخراج بنجاح'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الاستخراج: {str(e)}'
        })


@app.route('/batch_extract', methods=['POST'])
def batch_extract_websites():
    """استخراج متعدد المواقع"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        urls_text = data.get('urls', '').strip()
        extraction_type = data.get('extraction_type', 'standard')
        
        if not urls_text:
            return jsonify({'success': False, 'error': 'الرجاء إدخال روابط صحيحة'})
        
        # تحليل الروابط
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            return jsonify({'success': False, 'error': 'لم يتم العثور على روابط صحيحة'})
        
        # بدء الاستخراج المتعدد
        extraction_id = str(int(time.time() * 1000))
        active_extractions[extraction_id] = {
            'status': 'running',
            'urls': urls,
            'extraction_type': extraction_type,
            'start_time': time.time(),
            'type': 'batch'
        }
        
        # تنفيذ الاستخراج المتعدد
        result = batch_extract(urls, extraction_type)
        
        # تحديث الحالة
        active_extractions[extraction_id]['status'] = 'completed'
        active_extractions[extraction_id]['result'] = result
        
        # إضافة للتاريخ
        extraction_record = {
            'id': extraction_id,
            'url': f"{len(urls)} مواقع",
            'extraction_type': f"batch_{extraction_type}",
            'timestamp': time.time(),
            'success': result.get('successful_extractions', 0) > 0,
            'total_sites': result.get('total_sites', 0),
            'successful': result.get('successful_extractions', 0),
            'failed': result.get('failed_extractions', 0)
        }
        extraction_history.append(extraction_record)
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'result': result,
            'message': f'تم استخراج {result.get("successful_extractions", 0)} من {len(urls)} مواقع'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الاستخراج المتعدد: {str(e)}'
        })


@app.route('/quick_extract', methods=['POST'])
def quick_extract_endpoint():
    """استخراج سريع"""
    try:
        data = request.get_json() if request.is_json else request.form
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'الرجاء إدخال رابط صحيح'})
        
        # استخراج سريع
        result = quick_extract(url, 'basic')
        
        return jsonify({
            'success': True,
            'result': {
                'title': result.get('title', 'غير متوفر'),
                'description': result.get('description', 'غير متوفر'),
                'language': result.get('language', 'غير محدد'),
                'content_length': len(result.get('content', '')),
                'links_count': len(result.get('links_analysis', {}).get('internal_links', [])),
                'images_count': len(result.get('images_analysis', {}).get('images', [])),
                'extraction_time': result.get('duration', 0)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الاستخراج السريع: {str(e)}'
        })


@app.route('/status/<extraction_id>')
def extraction_status(extraction_id):
    """حالة الاستخراج"""
    
    if extraction_id not in active_extractions:
        return jsonify({'success': False, 'error': 'معرف الاستخراج غير موجود'})
    
    extraction_info = active_extractions[extraction_id]
    
    return jsonify({
        'success': True,
        'status': extraction_info['status'],
        'url': extraction_info.get('url', ''),
        'extraction_type': extraction_info.get('extraction_type', ''),
        'duration': round(time.time() - extraction_info['start_time'], 2),
        'result': extraction_info.get('result', {})
    })


@app.route('/results/<extraction_id>')
def view_results(extraction_id):
    """عرض نتائج الاستخراج"""
    
    if extraction_id not in active_extractions:
        flash('معرف الاستخراج غير موجود', 'error')
        return redirect(url_for('index'))
    
    extraction_info = active_extractions[extraction_id]
    result = extraction_info.get('result', {})
    
    return render_template('extraction_results.html', 
                         extraction_id=extraction_id,
                         extraction_info=extraction_info,
                         result=result)


@app.route('/download/<extraction_id>')
def download_results(extraction_id):
    """تحميل نتائج الاستخراج"""
    
    if extraction_id not in active_extractions:
        return jsonify({'success': False, 'error': 'معرف الاستخراج غير موجود'})
    
    extraction_info = active_extractions[extraction_id]
    result = extraction_info.get('result', {})
    
    # البحث عن ملف الأرشيف
    archive_path = result.get('archive_path')
    if archive_path and Path(archive_path).exists():
        return send_file(archive_path, as_attachment=True)
    
    # إنشاء ملف JSON للنتائج
    results_file = OUTPUT_DIR / f"extraction_{extraction_id}_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return send_file(results_file, as_attachment=True)


@app.route('/history')
def extraction_history_page():
    """صفحة تاريخ الاستخراج"""
    return render_template('extraction_history.html', 
                         extractions=reversed(extraction_history))


@app.route('/api/presets')
def get_presets():
    """الحصول على الإعدادات المُعرّفة مسبقاً"""
    
    extractor = AdvancedWebsiteExtractor()
    presets = extractor.get_available_presets()
    
    presets_info = {}
    for preset in presets:
        config = extractor.create_custom_config(extraction_type=preset)
        presets_info[preset] = {
            'name': preset,
            'description': {
                'basic': 'استخراج أساسي سريع - معلومات أساسية فقط',
                'standard': 'استخراج قياسي - محتوى + تحليلات',
                'advanced': 'استخراج متقدم - محتوى + أصول + لقطات شاشة',
                'complete': 'استخراج شامل - جميع الميزات + زحف متعدد الصفحات'
            }.get(preset, 'غير محدد'),
            'features': {
                'extract_content': config.get('features', {}).get('extract_content', False),
                'extract_assets': config.get('features', {}).get('extract_assets', False),
                'capture_screenshots': config.get('features', {}).get('capture_screenshots', False),
                'analyze_security': config.get('features', {}).get('analyze_security', False),
                'detect_technologies': config.get('features', {}).get('detect_technologies', False)
            }
        }
    
    return jsonify({'success': True, 'presets': presets_info})


@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_extractions():
    """تنظيف الاستخراجات القديمة"""
    
    try:
        # حذف الاستخراجات المكتملة الأقدم من ساعة
        current_time = time.time()
        cleanup_threshold = 3600  # ساعة واحدة
        
        cleaned_count = 0
        for extraction_id in list(active_extractions.keys()):
            extraction_info = active_extractions[extraction_id]
            if (extraction_info.get('status') == 'completed' and 
                current_time - extraction_info.get('start_time', 0) > cleanup_threshold):
                del active_extractions[extraction_id]
                cleaned_count += 1
        
        # الحفاظ على آخر 100 عملية في التاريخ
        if len(extraction_history) > 100:
            extraction_history[:] = extraction_history[-100:]
        
        return jsonify({
            'success': True,
            'cleaned_extractions': cleaned_count,
            'active_extractions': len(active_extractions),
            'history_size': len(extraction_history)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في التنظيف: {str(e)}'
        })


@app.route('/api/stats')
def get_statistics():
    """إحصائيات النظام"""
    
    total_extractions = len(extraction_history)
    successful_extractions = sum(1 for e in extraction_history if e.get('success', False))
    
    # إحصائيات أنواع الاستخراج
    extraction_types = {}
    for extraction in extraction_history:
        ext_type = extraction.get('extraction_type', 'unknown')
        extraction_types[ext_type] = extraction_types.get(ext_type, 0) + 1
    
    # متوسط وقت الاستخراج
    durations = [e.get('duration', 0) for e in extraction_history if e.get('duration')]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    stats = {
        'total_extractions': total_extractions,
        'successful_extractions': successful_extractions,
        'success_rate': round((successful_extractions / max(total_extractions, 1)) * 100, 2),
        'active_extractions': len(active_extractions),
        'extraction_types_distribution': extraction_types,
        'average_extraction_time': round(avg_duration, 2),
        'output_directory_size': get_directory_size(OUTPUT_DIR),
        'uptime': round(time.time(), 2)  # سيتم تحسينه لاحقاً
    }
    
    return jsonify({'success': True, 'stats': stats})


def get_directory_size(directory: Path) -> str:
    """حساب حجم المجلد"""
    try:
        total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
        
        # تحويل إلى وحدات مناسبة
        if total_size < 1024:
            return f"{total_size} B"
        elif total_size < 1024**2:
            return f"{total_size/1024:.1f} KB"
        elif total_size < 1024**3:
            return f"{total_size/(1024**2):.1f} MB"
        else:
            return f"{total_size/(1024**3):.1f} GB"
            
    except Exception:
        return "غير محدد"


# معالج الأخطاء
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)