#!/usr/bin/env python3
"""
تشغيل بسيط لاستخراج المواقع
"""
from unified_extractor import UnifiedWebsiteExtractor

# إنشاء المستخرج
extractor = UnifiedWebsiteExtractor()

# استخراج موقع
url = input("ادخل رابط الموقع: ")
result = extractor.extract_website(url, "basic")

print(f"\n✅ تم الاستخراج: {result['success']}")
print(f"📊 العنوان: {result.get('title', 'غير محدد')}")
print(f"🔗 الروابط: {result.get('links_count', 0)}")
print(f"🖼️ الصور: {result.get('images_count', 0)}")