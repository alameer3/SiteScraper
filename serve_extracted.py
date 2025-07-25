#!/usr/bin/env python3
"""
خادم بسيط لعرض المواقع المستخرجة
"""

import os
import http.server
import socketserver
import webbrowser
from pathlib import Path
import argparse

class ExtractedSiteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)
    
    def end_headers(self):
        # إضافة headers للدعم الأفضل للملفات العربية
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()

def serve_extracted_site(site_path, port=8080):
    """تشغيل خادم لعرض الموقع المستخرج"""
    
    if not os.path.exists(site_path):
        print(f"❌ المسار غير موجود: {site_path}")
        return
    
    print(f"🚀 بدء تشغيل الخادم للموقع المستخرج...")
    print(f"📁 المسار: {site_path}")
    print(f"🌐 المنفذ: {port}")
    print(f"🔗 الرابط: http://localhost:{port}")
    print("=" * 50)
    
    # تغيير المجلد الحالي
    os.chdir(site_path)
    
    try:
        with socketserver.TCPServer(("", port), ExtractedSiteHandler) as httpd:
            print(f"✅ الخادم يعمل على المنفذ {port}")
            print("اضغط Ctrl+C لإيقاف الخادم")
            
            # فتح المتصفح تلقائياً
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("🌐 تم فتح المتصفح تلقائياً")
            except:
                print("💡 افتح المتصفح يدوياً وانتقل إلى http://localhost:{port}")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الخادم")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ المنفذ {port} قيد الاستخدام. جرب منفذ آخر:")
            print(f"python serve_extracted.py --port {port + 1}")
        else:
            print(f"❌ خطأ: {e}")

def main():
    parser = argparse.ArgumentParser(description='خادم لعرض المواقع المستخرجة')
    parser.add_argument('--path', '-p', 
                       default='extracted_sites', 
                       help='مسار المجلد المحتوي على المواقع المستخرجة')
    parser.add_argument('--port', '-P', 
                       type=int, 
                       default=8080, 
                       help='رقم المنفذ (افتراضي: 8080)')
    parser.add_argument('--site', '-s',
                       help='اسم الموقع المحدد للعرض')
    
    args = parser.parse_args()
    
    base_path = Path(args.path)
    
    if not base_path.exists():
        print(f"❌ المجلد غير موجود: {base_path}")
        return
    
    # إذا تم تحديد موقع معين
    if args.site:
        site_path = base_path / args.site
        if not site_path.exists():
            print(f"❌ الموقع غير موجود: {site_path}")
            print("المواقع المتاحة:")
            for site in base_path.iterdir():
                if site.is_dir():
                    print(f"  - {site.name}")
            return
        serve_extracted_site(str(site_path), args.port)
    else:
        # عرض قائمة المواقع المتاحة
        sites = [d for d in base_path.iterdir() if d.is_dir()]
        
        if not sites:
            print("❌ لا توجد مواقع مستخرجة")
            return
        
        if len(sites) == 1:
            # موقع واحد فقط، عرضه مباشرة
            serve_extracted_site(str(sites[0]), args.port)
        else:
            # عدة مواقع، اعرض القائمة
            print("المواقع المتاحة:")
            for i, site in enumerate(sites, 1):
                print(f"  {i}. {site.name}")
            
            try:
                choice = int(input("\nاختر رقم الموقع: ")) - 1
                if 0 <= choice < len(sites):
                    serve_extracted_site(str(sites[choice]), args.port)
                else:
                    print("❌ اختيار غير صحيح")
            except ValueError:
                print("❌ يرجى إدخال رقم صحيح")

if __name__ == "__main__":
    main()