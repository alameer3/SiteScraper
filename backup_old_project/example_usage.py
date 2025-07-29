#!/usr/bin/env python3
"""
أمثلة لتشغيل unified_extractor
"""

from unified_extractor import UnifiedWebsiteExtractor
import json

def main():
    # إنشاء instance من المستخرج
    extractor = UnifiedWebsiteExtractor()
    
    # مثال 1: استخراج أساسي
    print("🔍 استخراج أساسي...")
    result = extractor.extract_website("https://httpbin.org", "basic")
    print(f"النتيجة: {result['success']}")
    
    # مثال 2: استخراج متقدم
    print("\n🚀 استخراج متقدم...")
    result = extractor.extract_website("https://example.com", "advanced")
    
    # طباعة النتائج
    print(f"\n📊 نتائج الاستخراج:")
    print(f"- الموقع: {result.get('url', 'غير محدد')}")
    print(f"- النجاح: {result.get('success', False)}")
    print(f"- عدد الصفحات: {result.get('pages_analyzed', 0)}")
    
    # حفظ النتائج
    with open('extraction_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 تم حفظ النتائج في: extraction_results.json")

if __name__ == "__main__":
    main()