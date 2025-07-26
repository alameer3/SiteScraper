#!/usr/bin/env python3
"""
مثال على تشغيل أداة Website Cloner Pro
"""

import asyncio
from website_cloner_pro import CloningConfig, WebsiteClonerPro

async def test_website_cloning():
    """اختبار أداة النسخ"""
    
    # إعداد التكوين
    config = CloningConfig(
        target_url="https://example.com",  # الموقع المراد نسخه
        max_depth=2,                       # عمق الاستخراج
        max_pages=10,                      # عدد الصفحات القصوى
        extract_all_content=True,          # استخراج جميع المحتوى
        analyze_with_ai=True,              # تحليل بالذكاء الاصطناعي
        generate_reports=True,             # إنشاء التقارير
        extract_assets=True,               # تحميل الأصول
        follow_robots_txt=True             # احترام robots.txt
    )
    
    print("🚀 بدء عملية استنساخ الموقع...")
    print(f"🎯 الموقع المستهدف: {config.target_url}")
    
    try:
        # إنشاء مثيل الأداة
        cloner = WebsiteClonerPro(config)
        
        # تشغيل عملية النسخ
        result = await cloner.clone_website()
        
        # عرض النتائج
        if result.success:
            print("\n✅ تم استنساخ الموقع بنجاح!")
            print(f"📁 مجلد النتائج: {result.output_path}")
            print(f"📊 صفحات مستخرجة: {result.pages_extracted}")
            print(f"🎯 أصول محملة: {result.assets_downloaded}")
            print(f"⏱️ المدة الزمنية: {result.duration:.2f} ثانية")
            print(f"💾 الحجم الإجمالي: {result.total_size:,} بايت")
            
            # عرض التقنيات المكتشفة
            if result.technologies_detected:
                print(f"🔧 التقنيات المكتشفة: {len(result.technologies_detected)} تقنية")
            
            # عرض التوصيات
            if result.recommendations:
                print(f"💡 التوصيات: {len(result.recommendations)} توصية")
                
        else:
            print("\n❌ فشل في استنساخ الموقع")
            print(f"🔍 عدد الأخطاء: {len(result.error_log)}")
            for error in result.error_log[:5]:  # عرض أول 5 أخطاء
                print(f"  - {error}")
                
    except Exception as e:
        print(f"\n💥 خطأ في التشغيل: {e}")

if __name__ == "__main__":
    # تشغيل الاختبار
    asyncio.run(test_website_cloning())