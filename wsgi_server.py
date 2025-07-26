#!/usr/bin/env python3
"""
WSGI server alternative to gunicorn
"""
import sys
import os
from wsgiref.simple_server import make_server

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """تشغيل WSGI server"""
    try:
        # استيراد التطبيق من main.py
        from main import app as application
        
        # إنشاء الخادم
        port = 5000
        host = '0.0.0.0'
        
        print(f"Starting WSGI server on {host}:{port}")
        server = make_server(host, port, application)
        
        print(f"🚀 أداة استخراج المواقع تعمل على http://{host}:{port}")
        print("💡 استخدم Ctrl+C للإيقاف")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف الخادم")
            
    except ImportError as e:
        print(f"فشل في استيراد التطبيق: {e}")
        print("تشغيل working_extractor مباشرة...")
        
        # الانتقال إلى working_extractor
        from working_extractor import main as extractor_main
        extractor_main()
        
    except Exception as e:
        print(f"خطأ في تشغيل الخادم: {e}")

if __name__ == '__main__':
    main()