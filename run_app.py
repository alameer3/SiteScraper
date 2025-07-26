#!/usr/bin/env python3
"""
Application runner - bypasses gunicorn completely
Final working solution for the website extractor
"""
import sys
import os
import threading
import time

def main():
    """تشغيل التطبيق النهائي"""
    # إضافة المسار الحالي
    sys.path.insert(0, os.path.dirname(__file__))
    
    print("=" * 50)
    print("🚀 بدء تشغيل أداة استخراج المواقع")
    print("=" * 50)
    
    try:
        # تشغيل working_extractor مباشرة
        from working_extractor import main as extractor_main
        print("✅ تم تحميل النظام بنجاح")
        print("🌐 الخادم سيعمل على: http://0.0.0.0:5000")
        print("🔧 المميزات:")
        print("   - استخراج المواقع بثلاثة أنواع (basic, standard, advanced)")
        print("   - واجهة عربية متقدمة")
        print("   - API للمطورين")
        print("   - حفظ النتائج وإمكانية مراجعتها")
        print("=" * 50)
        print("💡 استخدم Ctrl+C للإيقاف")
        print("=" * 50)
        
        # تشغيل الخادم
        extractor_main()
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")
        print("🔄 محاولة تشغيل بديل...")
        
        # حل بديل
        run_fallback_server()

def run_fallback_server():
    """خادم بديل في حالة فشل النظام الأساسي"""
    import http.server
    import socketserver
    import json
    
    class FallbackHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'fallback_server_active',
                    'message': 'Working extractor unavailable, using fallback'
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>أداة استخراج المواقع - وضع الطوارئ</title>
    <style>
        body { font-family: Arial; text-align: center; margin: 50px; background: #f0f2f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #e74c3c; }
        .message { background: #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚠️ أداة استخراج المواقع - وضع الطوارئ</h1>
        <div class="message">
            <p>النظام الأساسي غير متاح حالياً</p>
            <p>يتم تشغيل خادم بديل</p>
        </div>
        <p>للنظام الكامل، جرب تشغيل:</p>
        <code>python working_extractor.py</code>
    </div>
</body>
</html>'''
                self.wfile.write(html.encode('utf-8'))
    
    print("🆘 تشغيل خادم الطوارئ على المنفذ 5000...")
    with socketserver.TCPServer(("0.0.0.0", 5000), FallbackHandler) as httpd:
        print("✅ خادم الطوارئ جاهز")
        httpd.serve_forever()

if __name__ == '__main__':
    main()