#!/usr/bin/env python3
"""
تطبيق Flask بسيط لأداة استخراج المواقع
يستخدم النظام العامل working_extractor مباشرة
"""
import os
import sys
import json
from datetime import datetime

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
    from working_extractor import WebsiteExtractor
except ImportError as e:
    print(f"Import error: {e}")
    print("Running with basic HTTP server instead...")
    from working_extractor import main
    if __name__ == '__main__':
        main()
    sys.exit(0)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "simple-secret-key")

# إنشاء مستخرج المواقع
extractor = WebsiteExtractor()

# تخزين النتائج في الذاكرة للبساطة
results_storage = {}
next_id = 1

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    try:
        recent_results = list(results_storage.values())[-5:]  # آخر 5 نتائج
        return render_template('index.html', recent_results=recent_results)
    except Exception:
        # تحميل صفحة بسيطة في حالة عدم وجود templates
        return get_simple_html()

@app.route('/extract', methods=['POST'])
def extract():
    """استخراج موقع جديد"""
    global next_id
    
    url = request.form.get('url') or request.args.get('url')
    extraction_type = request.form.get('extraction_type', 'basic')
    
    if not url:
        if request.content_type == 'application/json':
            return jsonify({'error': 'URL is required'}), 400
        flash('يرجى إدخال رابط الموقع', 'error')
        return redirect(url_for('index'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # استخراج الموقع
        result = extractor.extract_website(url, extraction_type)
        
        # حفظ النتيجة في الذاكرة
        result_id = next_id
        next_id += 1
        
        results_storage[result_id] = {
            'id': result_id,
            'url': url,
            'title': result.get('title', 'No title'),
            'extraction_type': extraction_type,
            'data': result,
            'created_at': datetime.now().isoformat()
        }
        
        if request.content_type == 'application/json':
            return jsonify({
                'success': True,
                'result_id': result_id,
                'data': result
            })
        
        try:
            return redirect(url_for('result_detail', result_id=result_id))
        except Exception:
            return jsonify(result)  # عرض JSON إذا فشل الـ template
        
    except Exception as e:
        error_msg = f'خطأ في استخراج الموقع: {str(e)}'
        if request.content_type == 'application/json':
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """صفحة جميع النتائج"""
    try:
        all_results = list(results_storage.values())
        return render_template('results.html', results=all_results)
    except Exception:
        return jsonify(list(results_storage.values()))

@app.route('/result/<int:result_id>')
def result_detail(result_id):
    """تفاصيل النتيجة"""
    result = results_storage.get(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404
    
    try:
        return render_template('result_detail.html', result=result)
    except Exception:
        return jsonify(result)

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API لاستخراج الموقع"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    extraction_type = data.get('extraction_type', 'basic')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        result = extractor.extract_website(url, extraction_type)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """فحص صحة النظام"""
    return jsonify({
        'status': 'healthy',
        'app': 'website-analyzer-simple',
        'results_count': len(results_storage)
    })

def get_simple_html():
    """صفحة HTML بسيطة في حالة عدم وجود templates"""
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>أداة استخراج المواقع</title>
        <style>
            body { font-family: Arial; text-align: center; margin: 50px; background: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 30px; }
            .form-group { margin: 20px 0; text-align: right; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="url"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .recent-results { margin-top: 40px; text-align: right; }
            .result-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 أداة استخراج المواقع</h1>
            
            <form method="POST" action="/extract">
                <div class="form-group">
                    <label for="url">رابط الموقع:</label>
                    <input type="url" id="url" name="url" required placeholder="https://example.com">
                </div>
                
                <div class="form-group">
                    <label for="extraction_type">نوع الاستخراج:</label>
                    <select id="extraction_type" name="extraction_type">
                        <option value="basic">أساسي - سريع</option>
                        <option value="standard">متوسط</option>
                        <option value="advanced">متقدم - شامل</option>
                    </select>
                </div>
                
                <button type="submit">استخراج الموقع</button>
            </form>
            
            <div class="recent-results">
                <h3>آخر العمليات:</h3>
                <p>عدد النتائج المحفوظة: ''' + str(len(results_storage)) + '''</p>
                <a href="/results">عرض جميع النتائج</a> | 
                <a href="/health">فحص النظام</a>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("تشغيل التطبيق على المنفذ 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)