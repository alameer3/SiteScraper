#!/usr/bin/env python3
"""
اختبار شامل لجميع وظائف النظام
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """اختبار حالة النظام"""
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(f"✅ حالة النظام: {data['status']} - الإصدار: {data['version']}")
    return response.status_code == 200

def test_basic_extraction():
    """اختبار الاستخراج الأساسي"""
    data = {
        "url": "https://httpbin.org/html",
        "extraction_type": "basic"
    }
    response = requests.post(f"{BASE_URL}/api/extract", json=data)
    result = response.json()
    print(f"✅ الاستخراج الأساسي: {result['title']} - المدة: {result['duration']}s")
    return result['success']

def test_advanced_extraction():
    """اختبار الاستخراج المتقدم"""
    data = {
        "url": "https://example.com",
        "extraction_type": "advanced"
    }
    response = requests.post(f"{BASE_URL}/api/extract", json=data)
    result = response.json()
    print(f"✅ الاستخراج المتقدم: {result['domain']} - الروابط: {result['links_found']}")
    return result['success']

def test_technology_detection():
    """اختبار اكتشاف التقنيات"""
    data = {
        "url": "https://react.dev",
        "extraction_type": "complete"
    }
    response = requests.post(f"{BASE_URL}/api/extract", json=data)
    result = response.json()
    print(f"✅ اكتشاف التقنيات: {result['technologies_detected']} في {result['title']}")
    return result['success']

def test_results_page():
    """اختبار صفحة النتائج"""
    response = requests.get(f"{BASE_URL}/results")
    success = "سجل الاستخراجات" in response.text
    print(f"✅ صفحة النتائج: {'تعمل' if success else 'لا تعمل'}")
    return success

def test_home_page():
    """اختبار الصفحة الرئيسية"""
    response = requests.get(f"{BASE_URL}/")
    success = "أداة استخراج المواقع" in response.text
    print(f"✅ الصفحة الرئيسية: {'تعمل' if success else 'لا تعمل'}")
    return success

def main():
    """تشغيل جميع الاختبارات"""
    print("🧪 بدء اختبار جميع وظائف النظام...")
    print("=" * 50)
    
    tests = [
        ("صحة النظام", test_health),
        ("الصفحة الرئيسية", test_home_page),
        ("الاستخراج الأساسي", test_basic_extraction),
        ("الاستخراج المتقدم", test_advanced_extraction),
        ("اكتشاف التقنيات", test_technology_detection),
        ("صفحة النتائج", test_results_page),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            print(f"   {'✅ نجح' if result else '❌ فشل'}: {test_name}")
        except Exception as e:
            print(f"   ❌ خطأ في {test_name}: {e}")
        
        time.sleep(0.5)  # فترة انتظار قصيرة بين الاختبارات
    
    print("=" * 50)
    print(f"📊 النتائج النهائية: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الوظائف تعمل بنجاح!")
    else:
        print(f"⚠️  {total - passed} وظائف تحتاج إصلاح")

if __name__ == '__main__':
    main()