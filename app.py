#!/usr/bin/env python3
"""
تطبيق Flask بديل يستخدم working_extractor
"""
import os
import sys
from flask import Flask

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

# استيراد النظام العامل
from working_extractor import WebsiteExtractor, ExtractorHTTPHandler

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-key")

# Create a simple WSGI application that wraps the working extractor
class WSGIWrapper:
    def __init__(self):
        self.extractor = WebsiteExtractor()
        self.handler = ExtractorHTTPHandler
        self.handler.extractor = self.extractor
    
    def __call__(self, environ, start_response):
        # Simple WSGI wrapper for the HTTP handler
        if environ['REQUEST_METHOD'] == 'GET':
            if environ['PATH_INFO'] == '/':
                status = '200 OK'
                headers = [('Content-type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                return [self.get_index_html().encode('utf-8')]
            elif environ['PATH_INFO'] == '/health':
                status = '200 OK'
                headers = [('Content-type', 'application/json')]
                start_response(status, headers)
                return [b'{"status": "healthy", "app": "website-extractor"}']
        
        # Default response
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [b'Not Found']
    
    def get_index_html(self):
        return """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>أداة استخراج المواقع</title>
            <style>
                body { font-family: Arial; text-align: center; margin: 50px; }
                .container { max-width: 600px; margin: 0 auto; }
                h1 { color: #333; }
                .status { background: #d4edda; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 أداة استخراج المواقع</h1>
                <div class="status">
                    <p>النظام يعمل بنجاح!</p>
                    <p>للوصول إلى النظام الكامل، استخدم: <code>python working_extractor.py</code></p>
                </div>
            </div>
        </body>
        </html>
        """

# Create the WSGI app instance for gunicorn
app = WSGIWrapper()

if __name__ == '__main__':
    print("تشغيل النظام...")
    # Run the actual working extractor
    from working_extractor import main
    main()