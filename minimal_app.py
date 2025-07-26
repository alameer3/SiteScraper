#!/usr/bin/env python3
"""
تطبيق Flask أدنى لاختبار النظام
"""
import sys
import os

# إضافة المسار إذا لزم الأمر
sys.path.insert(0, '/home/runner/workspace/.pythonlibs/lib/python3.11/site-packages')

try:
    from flask import Flask, jsonify, render_template_string
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>أداة استخراج المواقع</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .card { 
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border: none;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card">
                        <div class="card-body text-center py-5">
                            <h1 class="mb-4">🌐 أداة استخراج المواقع المتقدمة</h1>
                            <p class="lead text-muted mb-4">
                                استخرج وحلل المواقع بتقنيات متقدمة
                            </p>
                            
                            <form id="extractForm" class="mb-4">
                                <div class="mb-3">
                                    <input type="url" class="form-control" id="url" 
                                           placeholder="https://example.com" required>
                                </div>
                                <div class="mb-3">
                                    <select class="form-select" id="type">
                                        <option value="basic">استخراج أساسي</option>
                                        <option value="advanced">استخراج متقدم</option>
                                        <option value="complete">استخراج شامل</option>
                                    </select>
                                </div>
                                <button type="submit" class="btn btn-primary btn-lg">
                                    🚀 بدء الاستخراج
                                </button>
                            </form>
                            
                            <div id="result" class="mt-4" style="display: none;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        document.getElementById('extractForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const type = document.getElementById('type').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '<div class="alert alert-info">⏳ جاري المعالجة...</div>';
            resultDiv.style.display = 'block';
            
            fetch('/api/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, extraction_type: type })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h5>✅ تم الاستخراج بنجاح!</h5>
                            <p><strong>URL:</strong> ${data.result.url}</p>
                            <p><strong>النوع:</strong> ${data.result.extraction_type}</p>
                            <p><strong>الحالة:</strong> ${data.result.message || 'مكتمل'}</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            ❌ خطأ: ${data.error}
                        </div>
                    `;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        ❌ خطأ في الاتصال: ${error.message}
                    </div>
                `;
            });
        });
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/extract', methods=['POST'])
    def api_extract():
        from flask import request
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({'error': 'URL مطلوب'}), 400
            
            url = data['url']
            extraction_type = data.get('extraction_type', 'basic')
            
            # محاكاة عملية الاستخراج
            result = {
                'success': True,
                'url': url,
                'extraction_type': extraction_type,
                'pages_extracted': 1,
                'assets_downloaded': 0,
                'total_size': 1024,
                'message': f'تم {extraction_type} استخراج للموقع بنجاح'
            }
            
            return jsonify({
                'status': 'success',
                'result': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'app': 'website-extractor',
            'version': '1.0.0'
        })
    
    if __name__ == '__main__':
        print("🚀 تشغيل التطبيق المبسط على المنفذ 5000...")
        app.run(host='0.0.0.0', port=5000, debug=True)

except ImportError as e:
    print(f"❌ خطأ في استيراد Flask: {e}")
    print("يرجى تثبيت Flask أولاً")
    sys.exit(1)