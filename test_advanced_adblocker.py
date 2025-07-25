#!/usr/bin/env python3
"""
اختبار النظام المتطور لحجب الإعلانات
"""

from advanced_ad_blocker import AdvancedAdBlocker
import json

def test_ad_blocker():
    """اختبار نظام حجب الإعلانات المتطور"""
    
    # HTML تجريبي يحتوي على إعلانات
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>موقع تجريبي</title>
        <meta name="google-adsense-account" content="ca-pub-123456789">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    </head>
    <body>
        <div class="content">
            <h1>المحتوى الرئيسي</h1>
            <p>هذا نص عادي يجب أن يبقى.</p>
        </div>
        
        <!-- إعلانات يجب إزالتها -->
        <div class="advertisement">
            <p>إعلان مزعج!</p>
        </div>
        
        <div id="google-ads">
            <script>
                (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
        </div>
        
        <iframe src="https://doubleclick.net/ads" width="300" height="250"></iframe>
        
        <!-- تتبع يجب إزالته -->
        <script>
            gtag('config', 'GA_MEASUREMENT_ID');
        </script>
        
        <!-- محتوى مفيد -->
        <article>
            <h2>مقال مفيد</h2>
            <p>هذا محتوى مفيد يجب الاحتفاظ به.</p>
        </article>
        
        <!-- المزيد من الإعلانات -->
        <div class="sponsored-content">
            <p>محتوى مُمول</p>
        </div>
        
        <div style="display:none;">
            <img src="https://facebook.com/tr?id=123456789" />
        </div>
    </body>
    </html>
    """
    
    print("🧪 اختبار النظام المتطور لحجب الإعلانات")
    print("=" * 50)
    
    # إنشاء نسخة من حاجب الإعلانات
    ad_blocker = AdvancedAdBlocker()
    
    # تنظيف HTML
    print("🔄 تنظيف المحتوى...")
    cleaned_html, report = ad_blocker.clean_html_content(test_html)
    
    print("\n📊 تقرير التنظيف:")
    print(f"• العناصر الأصلية: {report['original_elements']}")
    print(f"• العناصر النهائية: {report['final_elements']}")
    print(f"• العناصر المحذوفة: {len(report['removed_elements'])}")
    print(f"• السكريپت المنظف: {report['cleaned_scripts']}")
    print(f"• الطلبات المحجوبة: {report['blocked_requests']}")
    
    print("\n🛡️ العناصر المحذوفة:")
    for element in report['removed_elements'][:10]:  # أول 10 عناصر
        print(f"  - {element}")
    
    if len(report['removed_elements']) > 10:
        print(f"  ... و {len(report['removed_elements']) - 10} عنصر آخر")
    
    # تقرير شامل للحجب
    blocking_report = ad_blocker.generate_blocking_report()
    
    print("\n📈 إحصائيات الحجب:")
    for key, value in blocking_report['summary'].items():
        print(f"• {key}: {value}")
    
    print("\n🎯 الفئات المحجوبة:")
    for category, description in blocking_report['categories_blocked'].items():
        print(f"• {description}")
    
    print("\n🔒 ميزات الحماية:")
    for feature in blocking_report['protection_features']:
        print(f"• {feature}")
    
    # حفظ النتائج للفحص
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'original_html_length': len(test_html),
            'cleaned_html_length': len(cleaned_html),
            'cleaning_report': report,
            'blocking_report': blocking_report
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم حفظ النتائج في test_results.json")
    print(f"📏 تم تقليل حجم HTML من {len(test_html)} إلى {len(cleaned_html)} حرف")
    
    # فحص ما إذا كان المحتوى المفيد محفوظ
    useful_content_preserved = "المحتوى الرئيسي" in cleaned_html and "مقال مفيد" in cleaned_html
    ads_removed = "advertisement" not in cleaned_html.lower() and "google-ads" not in cleaned_html
    
    print(f"\n🎯 تقييم الأداء:")
    print(f"• المحتوى المفيد محفوظ: {'✅' if useful_content_preserved else '❌'}")
    print(f"• الإعلانات محذوفة: {'✅' if ads_removed else '❌'}")
    
    return blocking_report

if __name__ == "__main__":
    test_ad_blocker()