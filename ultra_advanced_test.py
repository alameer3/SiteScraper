#!/usr/bin/env python3
"""
اختبار النظام المتطور جداً لحجب الإعلانات والمحتوى الضار
"""

from advanced_ad_blocker import AdvancedAdBlocker
from website_extractor import WebsiteExtractor
import json

def test_ultra_advanced_blocking():
    """اختبار شامل للنظام المتطور"""
    
    # HTML تجريبي شامل مع كل أنواع الإعلانات والتتبع المخفي
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>موقع تجريبي شامل</title>
        <!-- تتبع خفي وإعلانات متقدمة -->
        <meta name="google-adsense-account" content="ca-pub-123456789">
        <meta name="facebook-domain-verification" content="abc123">
        <meta property="fb:app_id" content="123456789">
        
        <!-- إعلانات Google متقدمة -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
        
        <!-- تتبع فيسبوك متقدم -->
        <script>
            !function(f,b,e,v,n,t,s)
            {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
            n.queue=[];t=b.createElement(e);t.async=!0;
            t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}(window, document,'script',
            'https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', '123456789');
            fbq('track', 'PageView');
        </script>
    </head>
    <body>
        <!-- المحتوى الرئيسي المفيد -->
        <main>
            <article>
                <h1>مقال تقني مفيد</h1>
                <p>هذا محتوى مفيد يجب الاحتفاظ به في التحليل. يحتوي على معلومات تقنية قيمة.</p>
                <section class="content">
                    <h2>قسم فرعي مهم</h2>
                    <p>معلومات تقنية تفصيلية هنا...</p>
                </section>
            </article>
        </main>
        
        <!-- إعلانات متقدمة ومخفية -->
        <div class="advertisement banner-ad" data-ad-unit="top-banner">
            <script>
                (adsbygoogle = window.adsbygoogle || []).push({
                    google_ad_client: "ca-pub-123456789",
                    enable_page_level_ads: true
                });
            </script>
        </div>
        
        <!-- تتبع خفي متطور -->
        <div style="display:none;width:1px;height:1px;">
            <img src="https://facebook.com/tr?id=123456789&ev=PageView&noscript=1" />
            <img src="https://googletagmanager.com/ns.html?id=GTM-XXXXXXX" />
            <script>
                gtag('config', 'GA_MEASUREMENT_ID', {
                    page_title: document.title,
                    page_location: window.location.href
                });
            </script>
        </div>
        
        <!-- إعلانات شبكات خارجية -->
        <div class="outbrain-widget" data-widget-id="AR_1">
            <script src="https://widgets.outbrain.com/outbrain.js"></script>
        </div>
        
        <div class="taboola-below-article">
            <script type="text/javascript">
                window._taboola = window._taboola || [];
                _taboola.push({mode: 'thumbnails-a', container: 'taboola-below-article'});
            </script>
        </div>
        
        <!-- محتوى ترويجي مخفي -->
        <div class="sponsored-content promotional" style="visibility:hidden;">
            <p>محتوى مُمول - عرض خاص لفترة محدودة!</p>
            <a href="https://affiliate.example.com/track?id=123">اشتري الآن بخصم 50%</a>
        </div>
        
        <!-- نماذج تسويقية -->
        <div class="newsletter-signup lead-gen">
            <form action="https://mailchimp.com/track/submit" method="post">
                <input type="email" name="email" placeholder="اشترك في النشرة الإخبارية">
                <button type="submit">اشتراك مجاني</button>
            </form>
        </div>
        
        <!-- iframe إعلاني -->
        <iframe src="https://doubleclick.net/ads/show?size=300x250" width="300" height="250" frameborder="0"></iframe>
        
        <!-- أزرار اجتماعية ترويجية -->
        <div class="social-widgets">
            <div class="fb-like" data-href="https://www.facebook.com/page" data-send="false"></div>
            <div class="twitter-follow-button" data-screen-name="example">تابعنا</div>
        </div>
        
        <!-- تحليلات متقدمة مخفية -->
        <script>
            // Google Analytics 4
            gtag('event', 'page_view', {
                page_title: 'Test Page',
                page_location: 'https://example.com/test'
            });
            
            // Hotjar
            (function(h,o,t,j,a,r){
                h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
                h._hjSettings={hjid:123456,hjsv:6};
                a=o.getElementsByTagName('head')[0];
                r=o.createElement('script');r.async=1;
                r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
                a.appendChild(r);
            })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
            
            // Mixpanel
            (function(c,a){if(!a.__SV){var b=window;try{var d,m,j,k=b.location,f=k.hash;d=function(a,b){return(m=a.match(RegExp(b+"=([^&]*)")))?m[1]:null};f&&d(f,"state")&&(j=JSON.parse(decodeURIComponent(d(f,"state"))),"mpeditor"===j.action&&(b.sessionStorage.setItem("_mpcehash",f),history.replaceState(j.desiredHash||"",c.title,k.pathname+k.search)))}catch(n){}var l,h;window.mixpanel=a;a._i=[];a.init=function(b,d,g){function c(b,i){var a=i.split(".");2==a.length&&(b=b[a[0]],i=a[1]);b[i]=function(){b.push([i].concat(Array.prototype.slice.call(arguments,0)))}}var e=a;"undefined"!==typeof g?e=a[g]=[]:g="mixpanel";e.people=e.people||[];e.toString=function(b){var a="mixpanel";"mixpanel"!==g&&(a+="."+g);b||(a+=" (stub)");return a};e.people.toString=function(){return e.toString(1)+".people (stub)"};l="disable time_event track track_pageview track_links track_forms register register_once alias unregister identify name_tag set_config reset opt_in_tracking opt_out_tracking has_opted_in_tracking has_opted_out_tracking clear_opt_in_out_tracking people.set people.set_once people.unset people.increment people.append people.union people.track_charge people.clear_charges people.delete_user".split(" ");for(h=0;h<l.length;h++)c(e,l[h]);a._i.push([b,d,g])};a.__SV=1.2;b=c.createElement("script");b.type="text/javascript";b.async=!0;b.src="undefined"!==typeof MIXPANEL_CUSTOM_LIB_URL?MIXPANEL_CUSTOM_LIB_URL:"file:"===c.location.protocol&&"//cdn4.mxpnl.com/libs/mixpanel-2-latest.min.js".match(/^\/\//)?  "https://cdn4.mxpnl.com/libs/mixpanel-2-latest.min.js":"//cdn4.mxpnl.com/libs/mixpanel-2-latest.min.js";d=c.getElementsByTagName("script")[0];d.parentNode.insertBefore(b,d)}})(document,window.mixpanel||[]);
            mixpanel.init("abc123");
            mixpanel.track("Page View");
        </script>
        
        <!-- محتوى مفيد إضافي -->
        <footer>
            <div class="useful-links">
                <a href="/about">حول الموقع</a>
                <a href="/contact">اتصل بنا</a>
                <a href="/privacy">سياسة الخصوصية</a>
            </div>
        </footer>
    </body>
    </html>
    """
    
    print("🔥 اختبار النظام المتطور جداً لحجب الإعلانات والتتبع")
    print("=" * 60)
    
    # إنشاء نسخة من حاجب الإعلانات المتطور
    ad_blocker = AdvancedAdBlocker()
    
    print("🔄 تحليل وتنظيف المحتوى الشامل...")
    cleaned_html, report = ad_blocker.clean_html_content(test_html)
    
    print("\n📊 تقرير التنظيف الشامل:")
    print(f"• العناصر الأصلية: {report['original_elements']}")
    print(f"• العناصر النهائية: {report['final_elements']}")
    print(f"• العناصر المحذوفة: {len(report['removed_elements'])}")
    print(f"• السكريپت المنظف: {report['cleaned_scripts']}")
    print(f"• الطلبات المحجوبة: {report['blocked_requests']}")
    
    # حساب النسب
    reduction_ratio = ((report['original_elements'] - report['final_elements']) / report['original_elements']) * 100
    size_reduction = ((len(test_html) - len(cleaned_html)) / len(test_html)) * 100
    
    print(f"• نسبة تقليل العناصر: {reduction_ratio:.1f}%")
    print(f"• نسبة تقليل الحجم: {size_reduction:.1f}%")
    
    print("\n🛡️ العناصر المحذوفة (عينة):")
    for i, element in enumerate(report['removed_elements'][:15]):
        print(f"  {i+1:2d}. {element}")
    
    if len(report['removed_elements']) > 15:
        print(f"  ... و {len(report['removed_elements']) - 15} عنصر آخر")
    
    # تقرير شامل للحجب
    blocking_report = ad_blocker.generate_blocking_report()
    
    print("\n📈 إحصائيات الحجب المتطورة:")
    for key, value in blocking_report['summary'].items():
        print(f"• {key}: {value}")
    
    print("\n🎯 الفئات المحجوبة:")
    for category, description in blocking_report['categories_blocked'].items():
        print(f"• {description}")
    
    print("\n🔒 ميزات الحماية المتطورة:")
    for feature in blocking_report['protection_features']:
        print(f"• {feature}")
    
    # تحليل جودة المحتوى المحفوظ
    useful_content_keywords = ["مقال تقني", "محتوى مفيد", "معلومات تقنية", "قسم فرعي"]
    harmful_content_keywords = ["advertisement", "sponsored", "google-ads", "facebook.com/tr", "mixpanel", "hotjar"]
    
    useful_preserved = sum(1 for keyword in useful_content_keywords if keyword in cleaned_html)
    harmful_removed = sum(1 for keyword in harmful_content_keywords if keyword not in cleaned_html.lower())
    
    print(f"\n🎯 تقييم جودة التنظيف:")
    print(f"• المحتوى المفيد محفوظ: {useful_preserved}/{len(useful_content_keywords)} ({'✅' if useful_preserved >= 3 else '⚠️'})")
    print(f"• المحتوى الضار محذوف: {harmful_removed}/{len(harmful_content_keywords)} ({'✅' if harmful_removed >= 5 else '⚠️'})")
    
    # حفظ النتائج المفصلة
    detailed_results = {
        'test_metadata': {
            'original_html_length': len(test_html),
            'cleaned_html_length': len(cleaned_html),
            'reduction_ratio': reduction_ratio,
            'size_reduction': size_reduction,
            'useful_content_preserved': useful_preserved,
            'harmful_content_removed': harmful_removed
        },
        'cleaning_report': report,
        'blocking_report': blocking_report,
        'cleaned_html_sample': cleaned_html[:500] + "..." if len(cleaned_html) > 500 else cleaned_html
    }
    
    with open('ultra_advanced_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم حفظ النتائج المفصلة في ultra_advanced_test_results.json")
    print(f"📏 تم تقليل حجم HTML من {len(test_html):,} إلى {len(cleaned_html):,} حرف")
    
    # تقييم الأداء العام
    overall_score = (
        (reduction_ratio * 0.3) +  # 30% للتقليل
        (size_reduction * 0.3) +   # 30% لتقليل الحجم  
        (useful_preserved / len(useful_content_keywords) * 100 * 0.2) +  # 20% للمحتوى المحفوظ
        (harmful_removed / len(harmful_content_keywords) * 100 * 0.2)    # 20% للمحتوى المحذوف
    )
    
    print(f"\n🏆 النتيجة الإجمالية: {overall_score:.1f}/100")
    
    if overall_score >= 90:
        print("🌟 ممتاز! النظام يعمل بأعلى مستوى من الكفاءة")
    elif overall_score >= 80:
        print("👍 جيد جداً! النظام يحقق أداءً عالياً")
    elif overall_score >= 70:
        print("👌 جيد! النظام يعمل بكفاءة مقبولة")
    else:
        print("⚠️ يحتاج تحسين في بعض الجوانب")
    
    return blocking_report, overall_score

if __name__ == "__main__":
    test_ultra_advanced_blocking()