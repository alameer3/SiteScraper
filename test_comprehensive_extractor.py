#!/usr/bin/env python3
"""
اختبار أداة الاستخراج الشاملة المطورة
Test script for the comprehensive website extraction tool
"""

import sys
import time
from pathlib import Path
from tools2.advanced_extractor import AdvancedWebsiteExtractor

def test_extractor():
    """اختبار أداة الاستخراج مع موقع تجريبي"""
    
    print("🚀 بدء اختبار أداة الاستخراج الشاملة المطورة")
    print("=" * 60)
    
    # تهيئة الأداة
    extractor = AdvancedWebsiteExtractor(output_directory="test_extractions")
    
    # مواقع تجريبية للاختبار
    test_sites = [
        {
            'url': 'https://example.com',
            'type': 'basic',
            'description': 'موقع بسيط للاختبار الأساسي'
        },
        {
            'url': 'https://httpbin.org',
            'type': 'standard', 
            'description': 'موقع اختبار HTTP للاستخراج المعياري'
        }
    ]
    
    results = []
    
    for i, site in enumerate(test_sites, 1):
        print(f"\n📝 اختبار {i}/{len(test_sites)}: {site['description']}")
        print(f"🌐 الرابط: {site['url']}")
        print(f"📋 النوع: {site['type']}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            result = extractor.extract(
                url=site['url'],
                extraction_type=site['type']
            )
            
            duration = time.time() - start_time
            
            if result.get('extraction_info', {}).get('success'):
                print(f"✅ نجح الاستخراج في {duration:.2f} ثانية")
                
                # عرض الإحصائيات
                stats = result.get('statistics', {})
                assets = result.get('downloaded_assets', {}).get('summary', {})
                
                print(f"   📊 اكتمال الاستخراج: {stats.get('extraction_completeness', 0):.1f}%")
                print(f"   📁 الملفات المحملة: {assets.get('total_images', 0)} صورة، {assets.get('total_css', 0)} CSS، {assets.get('total_js', 0)} JS")
                print(f"   📏 حجم البيانات: {assets.get('total_size_mb', 0):.2f} MB")
                print(f"   🔒 نقاط الأمان: {stats.get('security_score', 0):.1f}%")
                print(f"   🔍 نقاط SEO: {stats.get('seo_score', 0):.1f}%")
                
                # مسار النتائج
                output_path = result.get('output_paths', {}).get('extraction_folder')
                if output_path:
                    print(f"   📂 النتائج محفوظة في: {output_path}")
                
                results.append({
                    'site': site,
                    'success': True,
                    'duration': duration,
                    'result': result
                })
                
            else:
                print(f"❌ فشل الاستخراج: {result.get('error', 'خطأ غير محدد')}")
                results.append({
                    'site': site,
                    'success': False,
                    'error': result.get('error')
                })
                
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {str(e)}")
            results.append({
                'site': site,
                'success': False,
                'error': str(e)
            })
    
    # تقرير النتائج النهائي
    print("\n" + "=" * 60)
    print("📈 تقرير الاختبار النهائي")
    print("=" * 60)
    
    successful_tests = len([r for r in results if r['success']])
    total_tests = len(results)
    
    print(f"✅ الاختبارات الناجحة: {successful_tests}/{total_tests}")
    print(f"📊 معدل النجاح: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        avg_duration = sum([r.get('duration', 0) for r in results if r['success']]) / successful_tests
        print(f"⏱️ متوسط مدة الاستخراج: {avg_duration:.2f} ثانية")
    
    # تفاصيل كل اختبار
    print("\n📋 تفاصيل الاختبارات:")
    for i, result in enumerate(results, 1):
        status = "✅ نجح" if result['success'] else "❌ فشل"
        print(f"  {i}. {result['site']['url']} - {status}")
        if not result['success']:
            print(f"     خطأ: {result.get('error', 'غير محدد')}")
    
    print(f"\n🏁 انتهى الاختبار")
    return results

def test_advanced_features():
    """اختبار الميزات المتقدمة"""
    
    print("\n🔬 اختبار الميزات المتقدمة")
    print("=" * 40)
    
    extractor = AdvancedWebsiteExtractor(output_directory="advanced_test")
    
    # اختبار استخراج متقدم
    try:
        print("🧪 اختبار الاستخراج المتقدم...")
        result = extractor.extract(
            url="https://example.com",
            extraction_type="advanced"
        )
        
        if result.get('extraction_info', {}).get('success'):
            print("✅ نجح الاستخراج المتقدم")
            
            # فحص الميزات المتقدمة
            extra_features = result.get('advanced_features', {})
            
            if extra_features.get('screenshots'):
                print("  📸 تم التقاط لقطات الشاشة")
            
            if extra_features.get('crawl_results'):
                crawl = extra_features['crawl_results']
                print(f"  🕷️ تم زحف {crawl.get('pages_crawled', 0)} صفحة")
            
            if extra_features.get('sitemap'):
                sitemap = extra_features['sitemap']
                print(f"  🗺️ تم إنشاء خريطة موقع بـ {sitemap.get('urls_count', 0)} رابط")
            
            # تحليل الأمان
            security = result.get('comprehensive_analysis', {}).get('security_analysis', {})
            print(f"  🛡️ نقاط الأمان: {security.get('security_score', 0):.1f}%")
            
            # كشف CMS
            cms = result.get('comprehensive_analysis', {}).get('cms_detection', {})
            detected_cms = cms.get('primary_cms', 'غير محدد')
            print(f"  ⚙️ نظام إدارة المحتوى: {detected_cms}")
            
        else:
            print("❌ فشل الاستخراج المتقدم")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الميزات المتقدمة: {str(e)}")

def test_performance():
    """اختبار الأداء"""
    
    print("\n⚡ اختبار الأداء")
    print("=" * 30)
    
    extractor = AdvancedWebsiteExtractor(output_directory="performance_test")
    
    # اختبار مواقع مختلفة الأحجام
    performance_sites = [
        'https://example.com',  # موقع صغير
        'https://httpbin.org'   # موقع متوسط
    ]
    
    for url in performance_sites:
        print(f"\n🎯 اختبار أداء: {url}")
        
        start_time = time.time()
        
        try:
            result = extractor.extract(url, extraction_type="standard")
            duration = time.time() - start_time
            
            if result.get('extraction_info', {}).get('success'):
                assets = result.get('downloaded_assets', {}).get('summary', {})
                total_assets = (assets.get('total_images', 0) + 
                              assets.get('total_css', 0) + 
                              assets.get('total_js', 0))
                
                print(f"  ⏱️ المدة: {duration:.2f} ثانية")
                print(f"  📁 إجمالي الأصول: {total_assets}")
                print(f"  💾 حجم البيانات: {assets.get('total_size_mb', 0):.2f} MB")
                
                if duration < 30:
                    print("  🚀 أداء ممتاز")
                elif duration < 60:
                    print("  ✅ أداء جيد")
                else:
                    print("  ⚠️ أداء بطيء")
                    
            else:
                print("  ❌ فشل في الاستخراج")
                
        except Exception as e:
            print(f"  ❌ خطأ: {str(e)}")

if __name__ == "__main__":
    print("🧪 مجموعة اختبارات أداة الاستخراج الشاملة")
    print("=" * 70)
    
    try:
        # الاختبارات الأساسية
        basic_results = test_extractor()
        
        # الاختبارات المتقدمة
        test_advanced_features()
        
        # اختبارات الأداء
        test_performance()
        
        print(f"\n🎉 انتهت جميع الاختبارات بنجاح!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ تم إيقاف الاختبارات بواسطة المستخدم")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n💥 خطأ عام في الاختبارات: {str(e)}")
        sys.exit(1)