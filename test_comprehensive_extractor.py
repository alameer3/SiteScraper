#!/usr/bin/env python3
"""
اختبار شامل للنظام مع مواقع آمنة مختلفة
"""

from tools2.advanced_extractor import AdvancedWebsiteExtractor
import json
from pathlib import Path

def test_safe_websites():
    """اختبار النظام مع مواقع آمنة ومختلفة"""
    
    # قائمة المواقع الآمنة للاختبار
    test_sites = [
        {
            'url': 'https://example.com',
            'name': 'Example.com - موقع اختبار كلاسيكي',
            'expected': 'موقع بسيط مع محتوى أساسي'
        },
        {
            'url': 'https://httpbin.org',
            'name': 'HTTPBin - أدوات اختبار HTTP',
            'expected': 'موقع مع APIs وأدوات متنوعة'
        },
        {
            'url': 'https://jsonplaceholder.typicode.com',
            'name': 'JSONPlaceholder - API وهمي',
            'expected': 'موقع API مع بيانات تجريبية'
        }
    ]
    
    print("🚀 بدء اختبار النظام الشامل مع مواقع آمنة متنوعة")
    print("=" * 60)
    
    results = []
    
    for i, site in enumerate(test_sites, 1):
        print(f"\n{i}️⃣ اختبار: {site['name']}")
        print(f"🔗 الرابط: {site['url']}")
        print(f"📝 المتوقع: {site['expected']}")
        print("-" * 40)
        
        try:
            # إنشاء مجلد منفصل لكل موقع
            site_name = site['url'].replace('https://', '').replace('/', '_').replace('.', '_')
            output_dir = f"test_extractions/site_{i}_{site_name}"
            
            # إنشاء مستخرج
            extractor = AdvancedWebsiteExtractor(output_dir)
            
            # تشغيل الاستخراج الشامل
            result = extractor.comprehensive_website_download(site['url'], 'standard')
            
            if result and result.get('extraction_info', {}).get('success'):
                print("✅ نجح الاستخراج!")
                
                extraction_info = result.get('extraction_info', {})
                basic_content = result.get('basic_content', {})
                basic_info = basic_content.get('basic_info', {}) if basic_content else {}
                
                print(f"⏱️ المدة: {extraction_info.get('duration', 'غير محدد')} ثانية")
                print(f"📄 العنوان: {basic_info.get('title', 'بدون عنوان')}")
                print(f"🔗 عدد الروابط: {basic_info.get('links_count', 0)}")
                print(f"🖼️ عدد الصور: {basic_info.get('images_count', 0)}")
                
                # عرض الأصول المحملة
                assets = result.get('assets', {})
                total_assets = sum(len(files) for files in assets.values() if files)
                print(f"📦 إجمالي الأصول: {total_assets}")
                
                results.append({
                    'site': site,
                    'success': True,
                    'result': result,
                    'output_dir': output_dir
                })
                
            else:
                print("❌ فشل في الاستخراج")
                error_msg = result.get('error', 'خطأ غير محدد') if result else 'لا توجد نتيجة'
                print(f"🔍 السبب: {error_msg}")
                
                results.append({
                    'site': site,
                    'success': False,
                    'error': error_msg,
                    'output_dir': output_dir
                })
                
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {str(e)}")
            results.append({
                'site': site,
                'success': False,
                'error': str(e),
                'output_dir': None
            })
    
    # تلخيص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص نتائج الاختبار:")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ نجح: {successful}/{total} مواقع")
    print(f"❌ فشل: {total - successful}/{total} مواقع")
    
    for i, result in enumerate(results, 1):
        status = "✅ نجح" if result['success'] else "❌ فشل"
        print(f"{i}. {result['site']['name']}: {status}")
        if result['success'] and result['output_dir']:
            print(f"   📁 المجلد: {result['output_dir']}")
    
    # حفظ تقرير شامل
    report_path = Path("test_extractions") / "comprehensive_test_report.json"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📋 تم حفظ التقرير الشامل في: {report_path}")
    
    return results

if __name__ == "__main__":
    test_safe_websites()