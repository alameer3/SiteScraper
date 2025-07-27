#!/usr/bin/env python3
"""
اختبار شامل لجميع الوظائف المطورة
"""
import sys
from pathlib import Path

def test_all_systems():
    """اختبار جميع النظم المطورة"""
    
    print("🧪 بدء اختبار شامل لجميع النظم المطورة...")
    print("=" * 60)
    
    # 1. اختبار unified_extractor
    print("\n1. اختبار نظام الاستخراج الموحد:")
    try:
        from unified_extractor import UnifiedWebsiteExtractor
        extractor = UnifiedWebsiteExtractor()
        print("✅ تم تحميل UnifiedWebsiteExtractor بنجاح")
    except Exception as e:
        print(f"❌ فشل تحميل UnifiedWebsiteExtractor: {e}")
    
    # 2. اختبار نظام Screenshots
    print("\n2. اختبار نظام لقطات الشاشة:")
    try:
        from simple_screenshot import SimpleScreenshotEngine
        screenshot_engine = SimpleScreenshotEngine()
        print("✅ تم تحميل SimpleScreenshotEngine بنجاح")
    except Exception as e:
        print(f"❌ فشل تحميل SimpleScreenshotEngine: {e}")
    
    # 3. اختبار نظام CMS Detection
    print("\n3. اختبار نظام كشف CMS:")
    try:
        from cms_detector import CMSDetector
        cms_detector = CMSDetector()
        print("✅ تم تحميل CMSDetector بنجاح")
        
        # اختبار سريع
        test_result = cms_detector.detect_cms("https://example.com")
        print(f"✅ اختبار سريع نجح: {len(test_result)} مفتاح في النتيجة")
    except Exception as e:
        print(f"❌ فشل تحميل CMSDetector: {e}")
    
    # 4. اختبار نظام Sitemap Generator
    print("\n4. اختبار مولد خرائط المواقع:")
    try:
        from sitemap_generator import SitemapGenerator
        sitemap_gen = SitemapGenerator()
        print("✅ تم تحميل SitemapGenerator بنجاح")
    except Exception as e:
        print(f"❌ فشل تحميل SitemapGenerator: {e}")
    
    # 5. اختبار نظام Security Scanner
    print("\n5. اختبار نظام فحص الأمان:")
    try:
        from security_scanner import SecurityScanner
        security_scanner = SecurityScanner()
        print("✅ تم تحميل SecurityScanner بنجاح")
    except Exception as e:
        print(f"❌ فشل تحميل SecurityScanner: {e}")
    
    # 6. اختبار Advanced Tools Manager
    print("\n6. اختبار مدير الأدوات المتقدمة:")
    try:
        from advanced_tools_manager import AdvancedToolsManager
        tools_manager = AdvancedToolsManager()
        print("✅ تم تحميل AdvancedToolsManager بنجاح")
        
        # فحص الأدوات المتاحة
        available_tools = []
        if tools_manager.cms_detector:
            available_tools.append("CMS Detection")
        if tools_manager.sitemap_generator:
            available_tools.append("Sitemap Generation")
        if tools_manager.security_scanner:
            available_tools.append("Security Scanner")
        if tools_manager.screenshot_engine:
            available_tools.append("Screenshot Engine")
        
        print(f"✅ الأدوات المتاحة: {', '.join(available_tools)}")
        
    except Exception as e:
        print(f"❌ فشل تحميل AdvancedToolsManager: {e}")
    
    # 7. فحص ملفات الاستخراج الموجودة
    print("\n7. فحص ملفات الاستخراج:")
    extracted_dir = Path("extracted_files/websites")
    if extracted_dir.exists():
        websites = list(extracted_dir.glob("*"))
        print(f"✅ عدد المواقع المستخرجة: {len(websites)}")
        
        # فحص آخر استخراج
        if websites:
            latest = max(websites, key=lambda x: x.stat().st_mtime)
            print(f"✅ آخر استخراج: {latest.name}")
            
            # فحص مجلدات فرعية
            subdirs = [d.name for d in latest.iterdir() if d.is_dir()]
            print(f"✅ المجلدات الفرعية: {', '.join(subdirs)}")
            
            # فحص ملفات Screenshots
            screenshots_dir = latest / "05_screenshots"
            if screenshots_dir.exists():
                screenshot_files = list(screenshots_dir.glob("*.html"))
                print(f"✅ ملفات Screenshots: {len(screenshot_files)}")
                for file in screenshot_files:
                    size_kb = file.stat().st_size / 1024
                    print(f"   📁 {file.name}: {size_kb:.1f} KB")
    else:
        print("❌ مجلد extracted_files غير موجود")
    
    # 8. فحص Flask API
    print("\n8. فحص Flask API:")
    try:
        import requests
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask API يعمل بنجاح")
        else:
            print(f"⚠️ Flask API يعمل لكن حالة غير متوقعة: {response.status_code}")
    except Exception as e:
        print(f"❌ فشل الاتصال بـ Flask API: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 انتهى الاختبار الشامل")

if __name__ == "__main__":
    test_all_systems()