"""
نقطة دخول التطبيق الرئيسية
Main Application Entry Point
"""
# استيراد التطبيق الأساسي
from app import app

# إضافة routes للنظام المطور
from tools2.advanced_extractor import AdvancedWebsiteExtractor, quick_extract, batch_extract
from flask import jsonify, request
import time
import json

@app.route('/api/advanced_extract', methods=['POST'])
def advanced_extract_api():
    """API للاستخراج المتطور"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        url = data.get('url', '').strip()
        extraction_type = data.get('extraction_type', 'standard')
        
        if not url:
            return jsonify({'success': False, 'error': 'الرجاء إدخال رابط صحيح'})
        
        # استخدام النظام المطور
        extractor = AdvancedWebsiteExtractor("extracted_files")
        result = extractor.extract(url, extraction_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'message': 'تم الاستخراج بنجاح باستخدام النظام المطور'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الاستخراج المتطور: {str(e)}'
        })

@app.route('/api/quick_extract_advanced', methods=['POST'])
def quick_extract_advanced_api():
    """API للاستخراج السريع المتطور"""
    try:
        data = request.get_json() if request.is_json else request.form
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'الرجاء إدخال رابط صحيح'})
        
        # استخراج سريع متطور
        result = quick_extract(url, 'basic')
        
        return jsonify({
            'success': True,
            'result': {
                'title': result.get('title', 'غير متوفر'),
                'description': result.get('description', 'غير متوفر'),
                'cms_detected': result.get('cms_analysis', {}).get('detected_cms', 'غير محدد'),
                'technologies': result.get('database_analysis', {}).get('technology_stack', [])[:3],
                'content_length': len(result.get('content', '')),
                'extraction_time': result.get('duration', 0),
                'advanced_features': 'متوفرة'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الاستخراج السريع: {str(e)}'
        })

print("✅ تم دمج النظام المطور مع التطبيق الأساسي")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)