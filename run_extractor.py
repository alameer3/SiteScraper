#!/usr/bin/env python3
"""
تشغيل المستخرج من Terminal مع معاملات
"""
import sys
import json
from unified_extractor import UnifiedWebsiteExtractor

def print_usage():
    print("""
🚀 استخدام unified_extractor:

python run_extractor.py <URL> [نوع_الاستخراج]

أنواع الاستخراج:
- basic: استخراج أساسي سريع
- advanced: استخراج متقدم مع تحليل
- complete: استخراج شامل بجميع الأدوات

أمثلة:
python run_extractor.py https://example.com
python run_extractor.py https://httpbin.org basic
python run_extractor.py https://github.com advanced
""")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    url = sys.argv[1]
    extraction_type = sys.argv[2] if len(sys.argv) > 2 else 'basic'
    
    print(f"🔍 استخراج {extraction_type} للموقع: {url}")
    
    extractor = UnifiedWebsiteExtractor()
    result = extractor.extract_website(url, extraction_type)
    
    print(f"\n✅ النتيجة: {result['success']}")
    if result['success']:
        print(f"📊 العنوان: {result.get('title', 'غير محدد')}")
        print(f"📝 الوصف: {result.get('description', 'غير متاح')[:100]}...")
        print(f"🔗 عدد الروابط: {result.get('links_count', 0)}")
        print(f"🖼️ عدد الصور: {result.get('images_count', 0)}")
        print(f"📄 حجم المحتوى: {result.get('content_length', 0)} bytes")
    else:
        print(f"❌ خطأ: {result.get('error', 'خطأ غير محدد')}")

if __name__ == "__main__":
    main()