#!/usr/bin/env python3
"""
نقطة دخول التطبيق الرئيسية - Website Extractor App
Fixed version that works with or without gunicorn
"""
import sys
import os

# إضافة المسار الحالي للتأكد من الوصول للملفات
sys.path.insert(0, os.path.dirname(__file__))

def run_server():
    """تشغيل الخادم بأفضل طريقة متاحة"""
    print("🚀 بدء تشغيل أداة استخراج المواقع...")
    
    try:
        # استيراد وتشغيل working_extractor مباشرة
        from working_extractor import main as extractor_main
        print("✅ تحميل النظام الأساسي...")
        extractor_main()
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام الأساسي: {e}")
        # حل بديل - خادم HTTP بسيط
        import http.server
        import socketserver
        
        class SimpleHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "basic_server_active"}')
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>أداة استخراج المواقع</title></head>
<body style="font-family:Arial;text-align:center;margin:50px">
<h1>🌐 أداة استخراج المواقع</h1>
<p>الخادم البديل يعمل</p>
<p>للنظام الكامل: <code>python working_extractor.py</code></p>
</body></html>'''
                    self.wfile.write(html.encode('utf-8'))
        
        print("🔄 تشغيل خادم بديل على المنفذ 5000...")
        with socketserver.TCPServer(("0.0.0.0", 5000), SimpleHandler) as httpd:
            print("✅ خادم جاهز على http://0.0.0.0:5000")
            httpd.serve_forever()

if __name__ == '__main__':
    run_server()

# للاستخدام مع خوادم WSGI
def application(environ, start_response):
    """WSGI application wrapper for working_extractor"""
    try:
        from working_extractor import WebsiteExtractor
        import json
        import urllib.parse
        
        # إنشاء مستخرج المواقع  
        extractor = WebsiteExtractor()
        
        # الحصول على معلومات الطلب
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        query_string = environ.get('QUERY_STRING', '')
        
        def send_response(content, content_type='text/html; charset=utf-8', status='200 OK'):
            if isinstance(content, str):
                content = content.encode('utf-8')
            headers = [
                ('Content-type', content_type),
                ('Content-Length', str(len(content)))
            ]
            start_response(status, headers)
            return [content]
        
        if path == '/' and method == 'GET':
            # الصفحة الرئيسية - استخدم HTML بسيط مدمج
            html = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>أداة استخراج المواقع</title>
    <style>
        body { font-family: Arial; margin: 50px; background: #f0f2f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; }
        button:hover { background: #45a049; }
        .footer { text-align: center; margin-top: 30px; color: #666; }
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
        
        <div class="footer">
            <p><a href="/health">فحص النظام</a> | <a href="/results">النتائج السابقة</a></p>
        </div>
    </div>
</body>
</html>'''
            return send_response(html)
            
        elif path == '/health' and method == 'GET':
            # فحص الصحة
            health_data = {
                'status': 'healthy',
                'app': 'website-extractor-wsgi',
                'server': 'working'
            }
            return send_response(
                json.dumps(health_data, ensure_ascii=False, indent=2),
                'application/json'
            )
            
        elif path == '/extract' and method == 'POST':
            # استخراج موقع
            try:
                # قراءة بيانات POST
                content_length = int(environ.get('CONTENT_LENGTH', '0'))
                if content_length > 0:
                    post_data = environ['wsgi.input'].read(content_length)
                    if environ.get('CONTENT_TYPE', '').startswith('application/json'):
                        data = json.loads(post_data.decode('utf-8'))
                        url = data.get('url')
                        extraction_type = data.get('extraction_type', 'basic')
                    else:
                        # form data
                        parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                        url = parsed_data.get('url', [''])[0]
                        extraction_type = parsed_data.get('extraction_type', ['basic'])[0]
                else:
                    url = ''
                    extraction_type = 'basic'
                
                if not url:
                    return send_response(
                        json.dumps({'error': 'URL required'}, ensure_ascii=False),
                        'application/json',
                        '400 Bad Request'
                    )
                
                # تنفيذ الاستخراج
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                    
                result = extractor.extract_website(url, extraction_type)
                return send_response(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    'application/json'
                )
                
            except Exception as e:
                return send_response(
                    json.dumps({'error': str(e)}, ensure_ascii=False),
                    'application/json',
                    '500 Internal Server Error'
                )
        
        else:
            # 404 للمسارات غير المعروفة
            return send_response(
                json.dumps({'error': 'Not found'}, ensure_ascii=False),
                'application/json',
                '404 Not Found'
            )
            
    except Exception as e:
        # خطأ عام
        error_response = f'{{"error": "Server error: {str(e)}"}}'
        headers = [('Content-type', 'application/json')]
        start_response('500 Internal Server Error', headers)
        return [error_response.encode('utf-8')]

# إنشاء app للـ WSGI
app = application