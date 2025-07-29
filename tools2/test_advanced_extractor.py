#!/usr/bin/env python3
"""
اختبار أداة الاستخراج المتطورة
Test for Advanced Website Extractor
"""

import sys
import time
from advanced_extractor import AdvancedWebsiteExtractor, quick_extract, extract_ai_powered

def test_basic_extraction():
    """اختبار الاستخراج الأساسي"""
    print("🧪 اختبار الاستخراج الأساسي...")
    
    try:
        # اختبار موقع بسيط
        result = quick_extract("https://example.com", "basic")
        
        print(f"✅ نجح الاستخراج!")
        print(f"📊 النتائج:")
        print(f"   - العنوان: {result.get('title', 'غير محدد')}")
        print(f"   - المجال: {result.get('domain', 'غير محدد')}")
        print(f"   - عدد الروابط: {result.get('links_count', 0)}")
        print(f"   - عدد الصور: {result.get('images_count', 0)}")
        print(f"   - التقنيات: {len(result.get('technologies', []))}")
        print(f"   - نسبة الاكتمال: {result.get('extraction_stats', {}).get('completeness_score', 0)}%")
        print(f"   - جودة الاستخراج: {result.get('extraction_stats', {}).get('extraction_quality', 'غير محدد')}")
        print(f"   - مدة الاستخراج: {result.get('duration', 0)} ثانية")
        
        return True
        
    except Exception as e:
        print(f"❌ فشل الاختبار: {str(e)}")
        return False

def test_advanced_extraction():
    """اختبار الاستخراج المتقدم"""
    print("\n🔬 اختبار الاستخراج المتقدم...")
    
    try:
        # إنشاء مستخرج متقدم
        extractor = AdvancedWebsiteExtractor("extracted_files/test")
        
        # اختبار الاستخراج المتقدم
        result = extractor.extract("https://example.com", "advanced")
        
        print(f"✅ نجح الاستخراج المتقدم!")
        print(f"📊 النتائج المتقدمة:")
        print(f"   - تحليل SEO: {'✅' if result.get('seo_analysis') else '❌'}")
        print(f"   - تحليل الأمان: {'✅' if result.get('security_analysis') else '❌'}")
        print(f"   - تحليل الهيكل: {'✅' if result.get('structure_analysis') else '❌'}")
        print(f"   - تحليل الروابط: {'✅' if result.get('links_analysis') else '❌'}")
        print(f"   - مجلد الاستخراج: {result.get('extraction_folder', 'غير محدد')}")
        
        return True
        
    except Exception as e:
        print(f"❌ فشل الاختبار المتقدم: {str(e)}")
        return False

def test_ai_powered_extraction():
    """اختبار الاستخراج بالذكاء الاصطناعي"""
    print("\n🤖 اختبار الاستخراج بالذكاء الاصطناعي...")
    
    try:
        # اختبار الاستخراج بـ AI
        result = extract_ai_powered("https://example.com")
        
        print(f"✅ نجح الاستخراج بالذكاء الاصطناعي!")
        print(f"📊 ميزات الذكاء الاصطناعي:")
        ai_features = result.get('ai_features', {})
        print(f"   - التحليل الذكي: {'✅' if ai_features.get('intelligent_analysis') else '❌'}")
        print(f"   - التعرف على الأنماط: {'✅' if ai_features.get('pattern_recognition') else '❌'}")
        print(f"   - النسخ الذكي: {'✅' if ai_features.get('smart_replication') else '❌'}")
        print(f"   - تقييم الجودة: {'✅' if ai_features.get('quality_assessment') else '❌'}")
        
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis and not ai_analysis.get('error'):
            print(f"   - تحليل المحتوى: ✅")
            print(f"   - تقييم الجودة: ✅")
            print(f"   - توصيات التحسين: {len(ai_analysis.get('recommendations', []))} توصية")
        
        return True
        
    except Exception as e:
        print(f"❌ فشل اختبار الذكاء الاصطناعي: {str(e)}")
        return False

def test_extractor_features():
    """اختبار ميزات المستخرج"""
    print("\n⚙️ اختبار ميزات المستخرج...")
    
    try:
        extractor = AdvancedWebsiteExtractor()
        
        # اختبار الأنواع المتاحة
        presets = extractor.get_available_presets()
        print(f"✅ الأنواع المتاحة: {presets}")
        
        # اختبار إنشاء إعدادات مخصصة
        custom_config = extractor.create_custom_config(
            extraction_type="standard",
            extract_assets=True,
            extract_images=True,
            capture_screenshots=True,
            analyze_security=True,
            analyze_seo=True,
            export_formats=['json', 'html', 'csv']
        )
        
        print(f"✅ تم إنشاء إعدادات مخصصة بنجاح")
        print(f"   - استخراج الأصول: {custom_config.get('extract_assets', False)}")
        print(f"   - تصدير JSON: {custom_config.get('export_json', False)}")
        print(f"   - تصدير HTML: {custom_config.get('export_html', False)}")
        print(f"   - تصدير CSV: {custom_config.get('export_csv', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ فشل اختبار الميزات: {str(e)}")
        return False

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار أداة الاستخراج المتطورة")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    start_time = time.time()
    
    # تشغيل الاختبارات
    if test_basic_extraction():
        tests_passed += 1
    
    if test_advanced_extraction():
        tests_passed += 1
    
    if test_ai_powered_extraction():
        tests_passed += 1
    
    if test_extractor_features():
        tests_passed += 1
    
    # تقرير النتائج
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    
    print("\n" + "=" * 50)
    print(f"📋 تقرير الاختبارات:")
    print(f"   - اجتازت: {tests_passed}/{total_tests}")
    print(f"   - نسبة النجاح: {int((tests_passed/total_tests)*100)}%")
    print(f"   - مدة الاختبار: {duration} ثانية")
    
    if tests_passed == total_tests:
        print("🎉 جميع الاختبارات نجحت!")
        return True
    else:
        print(f"⚠️  فشل {total_tests - tests_passed} اختبار")
        return False

if __name__ == "__main__":
    # تشغيل الاختبارات
    success = run_all_tests()
    
    # رمز الخروج
    sys.exit(0 if success else 1)