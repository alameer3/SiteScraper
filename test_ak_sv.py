#!/usr/bin/env python3
"""
اختبار شامل لموقع ak.sv
"""

import requests
import json
from pathlib import Path
from tools2.advanced_extractor import AdvancedWebsiteExtractor

def test_ak_sv():
    """اختبار تحليل موقع ak.sv"""
    url = "https://ak.sv/"
    
    print(f"🚀 بدء اختبار شامل لموقع: {url}")
    
    try:
        # إنشاء مستخرج متطور
        extractor = AdvancedWebsiteExtractor("test_ak_sv_output")
        
        # تشغيل الاستخراج الشامل
        print("📥 بدء الاستخراج الشامل...")
        result = extractor.comprehensive_website_download(url, "complete")
        
        # عرض النتائج
        if result and result.get('extraction_info', {}).get('success'):
            print("✅ نجح الاستخراج الشامل!")
            
            extraction_info = result.get('extraction_info', {})
            print(f"⏱️ المدة: {extraction_info.get('duration', 'غير محدد')} ثانية")
            print(f"📁 المجلد: {extraction_info.get('base_folder', 'غير محدد')}")
            
            # عرض المحتوى الأساسي
            basic_content = result.get('basic_content', {})
            if basic_content:
                basic_info = basic_content.get('basic_info', {})
                print(f"📄 العنوان: {basic_info.get('title', 'بدون عنوان')}")
                print(f"📏 حجم الصفحة: {basic_info.get('content_length', 0)} حرف")
                print(f"🔗 عدد الروابط: {basic_info.get('links_count', 0)}")
                print(f"🖼️ عدد الصور: {basic_info.get('images_count', 0)}")
            
            # عرض الأصول المحملة
            assets = result.get('assets', {})
            if assets:
                print("\n📦 الأصول المحملة:")
                for asset_type, files in assets.items():
                    if files:
                        print(f"  {asset_type}: {len(files)} ملف")
            
            # حفظ تقرير مفصل
            report_path = Path("test_ak_sv_output") / "test_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n📊 تم حفظ التقرير المفصل في: {report_path}")
            
        else:
            print("❌ فشل في الاستخراج الشامل")
            if result:
                print(f"🔍 السبب: {result.get('error', 'غير محدد')}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ak_sv()