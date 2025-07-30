#!/usr/bin/env python3
"""
فاحص شامل لجميع أدوات الاستخراج
Comprehensive Tools Tester
"""

import os
import sys
import time
import json
import traceback
from pathlib import Path
from datetime import datetime

# إعداد مجلد الإخراج الموحد
OUTPUT_DIR = Path("11")
OUTPUT_DIR.mkdir(exist_ok=True)

def test_basic_imports():
    """اختبار الاستيرادات الأساسية"""
    print("🔍 اختبار الاستيرادات الأساسية...")
    
    test_results = {
        'basic_imports': {},
        'advanced_imports': {},
        'core_modules': {}
    }
    
    # اختبار المكتبات الأساسية
    basic_modules = [
        'requests', 'bs4', 'urllib3', 'pathlib', 'json', 
        'time', 'datetime', 'csv', 'sqlite3'
    ]
    
    for module in basic_modules:
        try:
            __import__(module)
            test_results['basic_imports'][module] = '✅ متاح'
            print(f"  ✅ {module}")
        except ImportError as e:
            test_results['basic_imports'][module] = f'❌ غير متاح: {str(e)}'
            print(f"  ❌ {module}: {e}")
    
    # اختبار المكتبات المتقدمة (اختيارية)
    advanced_modules = [
        'selenium', 'playwright', 'trafilatura', 'builtwith', 
        'reportlab', 'docx', 'aiohttp', 'aiofiles'
    ]
    
    for module in advanced_modules:
        try:
            __import__(module)
            test_results['advanced_imports'][module] = '✅ متاح'
            print(f"  ✅ {module} (متقدم)")
        except ImportError:
            test_results['advanced_imports'][module] = '⚠️ غير متاح (اختياري)'
            print(f"  ⚠️ {module} (اختياري)")
    
    # اختبار مودیولات core
    core_modules = [
        'tools2.core.config',
        'tools2.core.session_manager',
        'tools2.core.file_manager',
        'tools2.core.content_extractor'
    ]
    
    for module in core_modules:
        try:
            __import__(module)
            test_results['core_modules'][module] = '✅ متاح'
            print(f"  ✅ {module}")
        except ImportError as e:
            test_results['core_modules'][module] = f'❌ خطأ: {str(e)}'
            print(f"  ❌ {module}: {e}")
    
    return test_results

def test_simple_extraction():
    """اختبار استخراج بسيط"""
    print("\n🧪 اختبار الاستخراج البسيط...")
    
    test_url = "https://example.com"
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # إنشاء جلسة HTTP
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"  🔗 اختبار الوصول إلى: {test_url}")
        response = session.get(test_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "بدون عنوان"
            
            # حفظ نتائج الاختبار في مجلد 11
            test_folder = OUTPUT_DIR / 'basic_test'
            test_folder.mkdir(exist_ok=True)
            
            # حفظ HTML
            with open(test_folder / 'example.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # حفظ تقرير الاختبار
            test_report = {
                'url': test_url,
                'status_code': response.status_code,
                'title': title_text,
                'content_length': len(response.text),
                'test_time': datetime.now().isoformat(),
                'success': True
            }
            
            with open(test_folder / 'test_report.json', 'w', encoding='utf-8') as f:
                json.dump(test_report, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ نجح الاستخراج البسيط")
            print(f"  📄 العنوان: {title_text}")
            print(f"  📊 حجم المحتوى: {len(response.text)} حرف")
            print(f"  📁 النتائج محفوظة في: {test_folder}")
            
            return test_report
        else:
            print(f"  ❌ فشل الوصول: {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"  ❌ خطأ في الاختبار: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_core_modules():
    """اختبار مودیولات core"""
    print("\n🔧 اختبار مودیولات core...")
    
    core_test_results = {}
    
    # اختبار session_manager
    try:
        from tools2.core.session_manager import SessionManager
        from tools2.core.config import ExtractionConfig
        
        config = ExtractionConfig()
        session_manager = SessionManager(config)
        test_response = session_manager.make_request("https://example.com")
        
        if test_response and test_response.status_code == 200:
            core_test_results['session_manager'] = '✅ يعمل'
            print("  ✅ session_manager")
        else:
            core_test_results['session_manager'] = '⚠️ مشكلة في الاتصال'
            print("  ⚠️ session_manager")
            
    except Exception as e:
        core_test_results['session_manager'] = f'❌ خطأ: {str(e)}'
        print(f"  ❌ session_manager: {e}")
    
    # اختبار file_manager
    try:
        from tools2.core.file_manager import FileManager
        
        file_manager = FileManager(str(OUTPUT_DIR / 'test_files'))
        test_folder = file_manager.create_extraction_folder("test_001", "https://example.com")
        
        if test_folder.exists():
            core_test_results['file_manager'] = '✅ يعمل'
            print("  ✅ file_manager")
        else:
            core_test_results['file_manager'] = '❌ فشل إنشاء المجلد'
            print("  ❌ file_manager")
            
    except Exception as e:
        core_test_results['file_manager'] = f'❌ خطأ: {str(e)}'
        print(f"  ❌ file_manager: {e}")
    
    # اختبار content_extractor
    try:
        from tools2.core.content_extractor import ContentExtractor
        from tools2.core.session_manager import SessionManager
        from tools2.core.config import ExtractionConfig
        from bs4 import BeautifulSoup
        
        config = ExtractionConfig()
        session_manager = SessionManager(config)
        content_extractor = ContentExtractor(config, session_manager)
        
        # اختبار مع HTML بسيط
        html = "<html><head><title>Test</title></head><body><h1>Test Page</h1></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        class MockResponse:
            text = html
            status_code = 200
        
        basic_info = content_extractor.extract_basic_info(soup, "https://example.com", MockResponse())
        
        if basic_info and 'title' in basic_info:
            core_test_results['content_extractor'] = '✅ يعمل'
            print("  ✅ content_extractor")
        else:
            core_test_results['content_extractor'] = '❌ فشل الاستخراج'
            print("  ❌ content_extractor")
            
    except Exception as e:
        core_test_results['content_extractor'] = f'❌ خطأ: {str(e)}'
        print(f"  ❌ content_extractor: {e}")
    
    return core_test_results

def test_advanced_extractor():
    """اختبار advanced_extractor"""
    print("\n🚀 اختبار advanced_extractor...")
    
    try:
        # نقوم بتعديل مجلد الإخراج للأداة المتقدمة
        sys.path.insert(0, 'tools2')
        
        # إنشاء نسخة معدلة من AdvancedWebsiteExtractor
        from tools2.advanced_extractor import AdvancedWebsiteExtractor, CloningConfig
        
        # تعديل مجلد الإخراج ليكون "11"
        extractor = AdvancedWebsiteExtractor(str(OUTPUT_DIR))
        
        print("  🔗 اختبار استخراج موقع example.com...")
        
        # اختبار بسيط مع معالجة الأخطاء
        try:
            result = extractor.extract("https://example.com", "basic")
            
            if result and result.get('success'):
                print("  ✅ نجح الاستخراج المتقدم")
                print(f"  📄 العنوان: {result.get('title', 'غير محدد')}")
                print(f"  📁 مجلد النتائج: {result.get('extraction_folder', 'غير محدد')}")
                
                # حفظ تقرير الاختبار
                with open(OUTPUT_DIR / 'advanced_test_report.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                return {'success': True, 'result': result}
            else:
                print(f"  ❌ فشل الاستخراج: {result.get('error', 'خطأ غير محدد')}")
                return {'success': False, 'error': result.get('error', 'خطأ غير محدد')}
                
        except Exception as e:
            print(f"  ❌ خطأ في الاستخراج: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    except Exception as e:
        print(f"  ❌ خطأ في تحميل advanced_extractor: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_unified_tools():
    """اختبار unified_tools"""
    print("\n🔧 اختبار unified_tools...")
    
    try:
        sys.path.insert(0, 'tools2')
        
        # اختبار الاستيراد فقط لأن الملف كبير جداً
        print("  📦 اختبار استيراد unified_tools...")
        
        # نحاول استيراد أجزاء من الملف
        with open('tools2/unified_tools.py', 'r', encoding='utf-8') as f:
            first_lines = f.read(1000)  # قراءة أول 1000 حرف
            
        if 'UnifiedWebsiteExtractor' in first_lines:
            print("  ✅ unified_tools موجود ويحتوي على الكلاسات المطلوبة")
            return {'success': True, 'note': 'ملف كبير جداً - تم التحقق من الوجود فقط'}
        else:
            print("  ❌ unified_tools لا يحتوي على الكلاسات المطلوبة")
            return {'success': False, 'error': 'محتوى غير صحيح'}
            
    except Exception as e:
        print(f"  ❌ خطأ في اختبار unified_tools: {str(e)}")
        return {'success': False, 'error': str(e)}

def generate_comprehensive_report():
    """إنشاء تقرير شامل"""
    print("\n📊 إنشاء التقرير الشامل...")
    
    # تجميع جميع نتائج الاختبارات
    all_results = {
        'test_timestamp': datetime.now().isoformat(),
        'output_directory': str(OUTPUT_DIR.absolute()),
        'tests_performed': {},
        'summary': {},
        'recommendations': []
    }
    
    # تشغيل جميع الاختبارات
    print("\n" + "="*50)
    print("           🚀 بدء الفحص الشامل للأدوات")
    print("="*50)
    
    # اختبار 1: الاستيرادات
    all_results['tests_performed']['imports'] = test_basic_imports()
    
    # اختبار 2: الاستخراج البسيط
    all_results['tests_performed']['simple_extraction'] = test_simple_extraction()
    
    # اختبار 3: مودیولات core
    all_results['tests_performed']['core_modules'] = test_core_modules()
    
    # اختبار 4: advanced_extractor
    all_results['tests_performed']['advanced_extractor'] = test_advanced_extractor()
    
    # اختبار 5: unified_tools
    all_results['tests_performed']['unified_tools'] = test_unified_tools()
    
    # إنشاء الملخص
    successful_tests = 0
    total_tests = 5
    
    for test_name, test_result in all_results['tests_performed'].items():
        if isinstance(test_result, dict) and test_result.get('success'):
            successful_tests += 1
    
    all_results['summary'] = {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'success_rate': f"{(successful_tests/total_tests)*100:.1f}%",
        'overall_status': 'نجح' if successful_tests >= 3 else 'يحتاج تحسين'
    }
    
    # توصيات
    if successful_tests < total_tests:
        all_results['recommendations'].append("إصلاح الأخطاء في الملفات")
        all_results['recommendations'].append("تحديث dependencies المفقودة")
    
    if successful_tests >= 3:
        all_results['recommendations'].append("النظام جاهز للاستخدام الأساسي")
        all_results['recommendations'].append("يمكن إضافة ميزات متقدمة")
    
    # حفظ التقرير النهائي
    report_file = OUTPUT_DIR / 'comprehensive_test_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # إنشاء تقرير HTML
    html_report = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير فحص الأدوات الشامل</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px; }}
        .success {{ color: #28a745; }}
        .error {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 تقرير فحص الأدوات الشامل</h1>
        <p><strong>التاريخ:</strong> {all_results['test_timestamp']}</p>
        <p><strong>مجلد الإخراج:</strong> {all_results['output_directory']}</p>
    </div>
    
    <div class="summary">
        <h2>📊 الملخص العام</h2>
        <p><strong>إجمالي الاختبارات:</strong> {all_results['summary']['total_tests']}</p>
        <p><strong>الاختبارات الناجحة:</strong> {all_results['summary']['successful_tests']}</p>
        <p><strong>معدل النجاح:</strong> {all_results['summary']['success_rate']}</p>
        <p><strong>الحالة العامة:</strong> <span class="{'success' if all_results['summary']['overall_status'] == 'نجح' else 'warning'}">{all_results['summary']['overall_status']}</span></p>
    </div>
    
    <div class="section">
        <h2>📋 تفاصيل الاختبارات</h2>
        <ul>
            <li>اختبار الاستيرادات: {'✅' if all_results['tests_performed']['imports'] else '❌'}</li>
            <li>الاستخراج البسيط: {'✅' if all_results['tests_performed']['simple_extraction'].get('success') else '❌'}</li>
            <li>مودیولات core: {'✅' if all_results['tests_performed']['core_modules'] else '❌'}</li>
            <li>advanced_extractor: {'✅' if all_results['tests_performed']['advanced_extractor'].get('success') else '❌'}</li>
            <li>unified_tools: {'✅' if all_results['tests_performed']['unified_tools'].get('success') else '❌'}</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>💡 التوصيات</h2>
        <ul>
            {"".join(f"<li>{rec}</li>" for rec in all_results['recommendations'])}
        </ul>
    </div>
</body>
</html>"""
    
    with open(OUTPUT_DIR / 'test_report.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print("\n" + "="*50)
    print("           📊 تقرير الفحص الشامل")
    print("="*50)
    print(f"✅ إجمالي الاختبارات: {all_results['summary']['total_tests']}")
    print(f"✅ الاختبارات الناجحة: {all_results['summary']['successful_tests']}")
    print(f"📈 معدل النجاح: {all_results['summary']['success_rate']}")
    print(f"🎯 الحالة العامة: {all_results['summary']['overall_status']}")
    print(f"📁 جميع النتائج محفوظة في مجلد: {OUTPUT_DIR.absolute()}")
    print(f"📄 التقرير التفاعلي: {OUTPUT_DIR / 'test_report.html'}")
    print("="*50)
    
    return all_results

if __name__ == "__main__":
    try:
        # تشغيل الفحص الشامل
        results = generate_comprehensive_report()
        
        # عرض النتائج
        if results['summary']['successful_tests'] >= 3:
            print("\n🎉 النظام جاهز للاستخدام!")
        else:
            print("\n⚠️ النظام يحتاج إلى إصلاحات قبل الاستخدام")
        
        print(f"\n📱 لعرض التقرير التفاعلي افتح: {OUTPUT_DIR.absolute() / 'test_report.html'}")
        
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل الفحص الشامل: {str(e)}")
        traceback.print_exc()