#!/usr/bin/env python3
"""
اختبار النظام المحسن للتأكد من عمله
Test Enhanced System Functionality
"""

from enhanced_crawler import enhanced_crawler
import json

def test_safe_sites():
    """اختبار المواقع الآمنة"""
    test_sites = [
        'https://httpbin.org/',
        'https://example.com/',
        'https://jsonplaceholder.typicode.com/'
    ]
    
    results = {}
    
    for site in test_sites:
        print(f"\n🔍 اختبار الموقع: {site}")
        result = enhanced_crawler.analyze_website_enhanced(site)
        
        print(f"✅ النجاح: {result['success']}")
        if result['success']:
            print(f"📊 العنوان: {result['data'].get('title', 'غير متوفر')}")
            print(f"⚡ الطريقة: {result['method_used']}")
            print(f"⏱️ الوقت: {result['execution_time']} ثانية")
            print(f"🔗 الروابط: {result['data']['elements']['links']}")
            print(f"🖼️ الصور: {result['data']['elements']['images']}")
        else:
            print(f"❌ الخطأ: {result['error']}")
        
        results[site] = result
    
    return results

if __name__ == "__main__":
    print("🚀 اختبار النظام المحسن للاستخراج")
    print("=" * 50)
    
    results = test_safe_sites()
    
    print("\n📊 ملخص النتائج:")
    print("-" * 30)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"✅ نجح: {successful}/{total}")
    print(f"❌ فشل: {total - successful}/{total}")
    
    if successful > 0:
        print("\n🎉 النظام يعمل بنجاح!")
    else:
        print("\n⚠️ النظام يحتاج إلى إصلاحات")