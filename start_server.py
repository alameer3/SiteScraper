#!/usr/bin/env python3
"""
مشغل الخادم البديل - يتجاوز مشاكل gunicorn
"""
import os
import sys
import subprocess
import time

def main():
    """تشغيل الخادم بطريقة مباشرة"""
    print("🚀 بدء تشغيل أداة استخراج المواقع...")
    
    # إضافة المسار الحالي
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # تشغيل working_extractor مباشرة
        print("📂 تحميل النظام الأساسي...")
        from working_extractor import main as extractor_main
        print("✅ تم تحميل النظام بنجاح")
        print("🌐 سيتم تشغيل الخادم على http://0.0.0.0:5000")
        print("💡 استخدم Ctrl+C للإيقاف")
        extractor_main()
        
    except ImportError as e:
        print(f"❌ فشل في تحميل working_extractor: {e}")
        print("🔄 محاولة تشغيل باستخدام subprocess...")
        
        try:
            # تشغيل كـ subprocess
            subprocess.run([sys.executable, "working_extractor.py"], 
                         cwd=current_dir, check=True)
        except Exception as e2:
            print(f"❌ فشل تشغيل subprocess: {e2}")
            print("🆘 تشغيل خادم أساسي...")
            
            # خادم HTTP بسيط كحل أخير
            import http.server
            import socketserver
            
            class BasicHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"status": "basic_server_running"}')
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        html = '''
                        <!DOCTYPE html>
                        <html lang="ar" dir="rtl">
                        <head>
                            <meta charset="UTF-8">
                            <title>أداة استخراج المواقع</title>
                        </head>
                        <body>
                            <h1>🌐 أداة استخراج المواقع</h1>
                            <p>الخادم الأساسي يعمل</p>
                            <p>للنظام الكامل، جرب: <code>python working_extractor.py</code></p>
                        </body>
                        </html>
                        '''
                        self.wfile.write(html.encode('utf-8'))
            
            with socketserver.TCPServer(("0.0.0.0", 5000), BasicHandler) as httpd:
                print("🌐 خادم أساسي يعمل على المنفذ 5000")
                httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == '__main__':
    main()