#!/usr/bin/env python3
"""
اختبار شامل لجميع الأدوات مع التوجيه لمجلد 11
Comprehensive Tools Test with Output to Folder 11
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import traceback

# إعداد مجلد الإخراج الموحد
OUTPUT_DIR = Path("11")
OUTPUT_DIR.mkdir(exist_ok=True)

class ToolsTester:
    """فاحص شامل لجميع الأدوات"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.results = {
            'test_timestamp': datetime.now().isoformat(),
            'output_directory': str(self.output_dir.absolute()),
            'tools_tested': {},
            'summary': {}
        }
    
    def test_simple_extractor(self):
        """اختبار أداة الاستخراج البسيطة"""
        print("🧪 اختبار أداة الاستخراج البسيطة...")
        
        try:
            from simple_extractor import SimpleWebsiteExtractor
            
            extractor = SimpleWebsiteExtractor(str(self.output_dir))
            
            # اختبار استخراج موقع example.com
            result = extractor.extract_website("https://example.com", "standard")
            
            if result['success']:
                self.results['tools_tested']['simple_extractor'] = {
                    'status': 'نجح',
                    'extraction_folder': result['extraction_folder'],
                    'title': result['data']['basic_info']['title'],
                    'links_count': len(result['data']['links']),
                    'images_count': len(result['data'].get('images', [])),
                    'test_time': datetime.now().isoformat()
                }
                print(f"  ✅ نجح الاستخراج: {result['extraction_folder']}")
                return True
            else:
                self.results['tools_tested']['simple_extractor'] = {
                    'status': 'فشل',
                    'error': result['error'],
                    'test_time': datetime.now().isoformat()
                }
                print(f"  ❌ فشل الاستخراج: {result['error']}")
                return False
                
        except Exception as e:
            self.results['tools_tested']['simple_extractor'] = {
                'status': 'خطأ',
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }
            print(f"  ❌ خطأ في الاختبار: {e}")
            return False
    
    def test_core_modules(self):
        """اختبار مودیولات core"""
        print("🔧 اختبار مودیولات core...")
        
        core_results = {}
        
        # اختبار config
        try:
            from tools2.core.config import ExtractionConfig, get_preset_config
            config = ExtractionConfig()
            config.output_directory = str(self.output_dir)
            
            preset_config = get_preset_config("standard")
            preset_config.output_directory = str(self.output_dir)
            
            core_results['config'] = 'نجح'
            print("  ✅ config")
        except Exception as e:
            core_results['config'] = f'فشل: {str(e)}'
            print(f"  ❌ config: {e}")
        
        # اختبار session_manager
        try:
            from tools2.core.session_manager import SessionManager
            from tools2.core.config import ExtractionConfig
            
            config = ExtractionConfig()
            session_manager = SessionManager(config)
            
            # اختبار طلب بسيط
            response = session_manager.make_request("https://example.com")
            if response and response.status_code == 200:
                core_results['session_manager'] = 'نجح'
                print("  ✅ session_manager")
            else:
                core_results['session_manager'] = 'فشل في الاتصال'
                print("  ⚠️ session_manager: فشل في الاتصال")
                
        except Exception as e:
            core_results['session_manager'] = f'فشل: {str(e)}'
            print(f"  ❌ session_manager: {e}")
        
        # اختبار file_manager
        try:
            from tools2.core.file_manager import FileManager
            
            file_manager = FileManager(str(self.output_dir / 'test_core'))
            test_folder = file_manager.create_extraction_folder("test_core", "https://example.com")
            
            if test_folder.exists():
                core_results['file_manager'] = 'نجح'
                print("  ✅ file_manager")
            else:
                core_results['file_manager'] = 'فشل في إنشاء المجلد'
                print("  ❌ file_manager")
                
        except Exception as e:
            core_results['file_manager'] = f'فشل: {str(e)}'
            print(f"  ❌ file_manager: {e}")
        
        self.results['tools_tested']['core_modules'] = core_results
        successful_core = len([v for v in core_results.values() if v == 'نجح'])
        total_core = len(core_results)
        
        return successful_core == total_core
    
    def test_advanced_extractor_basic(self):
        """اختبار أساسي لـ advanced_extractor"""
        print("🚀 اختبار أساسي لـ advanced_extractor...")
        
        try:
            # استيراد الملف والتحقق من الكلاسات
            sys.path.insert(0, 'tools2')
            
            with open('tools2/advanced_extractor.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # التحقق من وجود الكلاسات المطلوبة
            required_classes = [
                'AdvancedWebsiteExtractor',
                'CloningConfig',
                'ExtractionResult'
            ]
            
            found_classes = []
            for cls in required_classes:
                if f'class {cls}' in content:
                    found_classes.append(cls)
            
            if len(found_classes) >= 2:
                self.results['tools_tested']['advanced_extractor'] = {
                    'status': 'موجود (يحتاج إصلاح)',
                    'found_classes': found_classes,
                    'file_size': len(content),
                    'test_time': datetime.now().isoformat()
                }
                print(f"  ⚠️ الملف موجود ولكن يحتاج إصلاح ({len(found_classes)} كلاس)")
                return False
            else:
                self.results['tools_tested']['advanced_extractor'] = {
                    'status': 'غير مكتمل',
                    'found_classes': found_classes,
                    'test_time': datetime.now().isoformat()
                }
                print("  ❌ الملف غير مكتمل")
                return False
                
        except Exception as e:
            self.results['tools_tested']['advanced_extractor'] = {
                'status': 'خطأ',
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }
            print(f"  ❌ خطأ في الاختبار: {e}")
            return False
    
    def test_flask_app(self):
        """اختبار تطبيق Flask"""
        print("🌐 اختبار تطبيق Flask...")
        
        try:
            import requests
            
            # اختبار الوصول إلى الصفحة الرئيسية
            response = requests.get("http://localhost:5000", timeout=5)
            
            if response.status_code == 200:
                self.results['tools_tested']['flask_app'] = {
                    'status': 'يعمل',
                    'status_code': response.status_code,
                    'response_length': len(response.text),
                    'test_time': datetime.now().isoformat()
                }
                print("  ✅ تطبيق Flask يعمل")
                return True
            else:
                self.results['tools_tested']['flask_app'] = {
                    'status': 'مشكلة',
                    'status_code': response.status_code,
                    'test_time': datetime.now().isoformat()
                }
                print(f"  ⚠️ تطبيق Flask: حالة {response.status_code}")
                return False
                
        except Exception as e:
            self.results['tools_tested']['flask_app'] = {
                'status': 'غير متاح',
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }
            print(f"  ❌ تطبيق Flask غير متاح: {e}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("\n" + "="*60)
        print("           🚀 اختبار شامل لجميع الأدوات")
        print("="*60)
        
        tests = [
            ('simple_extractor', self.test_simple_extractor),
            ('core_modules', self.test_core_modules),
            ('advanced_extractor', self.test_advanced_extractor_basic),
            ('flask_app', self.test_flask_app)
        ]
        
        successful_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 اختبار: {test_name}")
            try:
                success = test_func()
                if success:
                    successful_tests += 1
            except Exception as e:
                print(f"  ❌ خطأ غير متوقع في {test_name}: {e}")
                traceback.print_exc()
        
        # إنشاء الملخص
        self.results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': f"{(successful_tests/total_tests)*100:.1f}%",
            'overall_status': 'ممتاز' if successful_tests >= 3 else 'جيد' if successful_tests >= 2 else 'يحتاج تحسين'
        }
        
        # حفظ التقرير
        report_file = self.output_dir / 'comprehensive_tools_test.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # إنشاء تقرير HTML مفصل
        self._create_detailed_html_report()
        
        # عرض النتائج
        print("\n" + "="*60)
        print("           📊 نتائج الاختبار الشامل")
        print("="*60)
        print(f"✅ إجمالي الاختبارات: {total_tests}")
        print(f"✅ الاختبارات الناجحة: {successful_tests}")
        print(f"📈 معدل النجاح: {self.results['summary']['success_rate']}")
        print(f"🎯 التقييم العام: {self.results['summary']['overall_status']}")
        print(f"📁 التقرير محفوظ في: {report_file}")
        print(f"📄 التقرير التفاعلي: {self.output_dir / 'detailed_test_report.html'}")
        print("="*60)
        
        return self.results
    
    def _create_detailed_html_report(self):
        """إنشاء تقرير HTML مفصل"""
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير الاختبار الشامل للأدوات</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Arial, sans-serif; margin: 0; padding: 20px; direction: rtl; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px 15px 0 0; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .summary {{ padding: 30px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #495057; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .tests-section {{ padding: 30px; }}
        .test-item {{ margin: 20px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 10px; }}
        .test-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .test-title {{ font-size: 1.3em; font-weight: bold; }}
        .status-badge {{ padding: 5px 15px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }}
        .status-success {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        .test-details {{ margin-top: 15px; }}
        .detail-item {{ margin: 5px 0; padding: 8px; background: #f8f9fa; border-radius: 5px; }}
        .footer {{ padding: 20px 30px; background: #f8f9fa; border-radius: 0 0 15px 15px; text-align: center; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 تقرير الاختبار الشامل للأدوات</h1>
            <p>تاريخ الاختبار: {self.results['test_timestamp']}</p>
            <p>مجلد الإخراج: {self.results['output_directory']}</p>
        </div>
        
        <div class="summary">
            <h2>📊 الملخص التنفيذي</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>إجمالي الاختبارات</h3>
                    <div class="value">{self.results['summary']['total_tests']}</div>
                </div>
                <div class="summary-card">
                    <h3>الاختبارات الناجحة</h3>
                    <div class="value success">{self.results['summary']['successful_tests']}</div>
                </div>
                <div class="summary-card">
                    <h3>معدل النجاح</h3>
                    <div class="value {'success' if float(self.results['summary']['success_rate'].rstrip('%')) >= 75 else 'warning' if float(self.results['summary']['success_rate'].rstrip('%')) >= 50 else 'error'}">{self.results['summary']['success_rate']}</div>
                </div>
                <div class="summary-card">
                    <h3>التقييم العام</h3>
                    <div class="value {'success' if self.results['summary']['overall_status'] == 'ممتاز' else 'warning' if self.results['summary']['overall_status'] == 'جيد' else 'error'}">{self.results['summary']['overall_status']}</div>
                </div>
            </div>
        </div>
        
        <div class="tests-section">
            <h2>🔍 تفاصيل الاختبارات</h2>
        """
        
        # إضافة تفاصيل كل اختبار
        for tool_name, tool_result in self.results['tools_tested'].items():
            status = tool_result.get('status', 'غير محدد')
            status_class = 'success' if status == 'نجح' or status == 'يعمل' else 'warning' if 'يحتاج' in status or status == 'مشكلة' else 'error'
            
            html_content += f"""
            <div class="test-item">
                <div class="test-header">
                    <div class="test-title">🔧 {tool_name}</div>
                    <div class="status-badge status-{status_class}">{status}</div>
                </div>
                <div class="test-details">
            """
            
            # إضافة تفاصيل الاختبار
            for key, value in tool_result.items():
                if key != 'status':
                    if isinstance(value, dict):
                        html_content += f"<div class='detail-item'><strong>{key}:</strong><br>"
                        for sub_key, sub_value in value.items():
                            html_content += f"&nbsp;&nbsp;• {sub_key}: {sub_value}<br>"
                        html_content += "</div>"
                    elif isinstance(value, list):
                        html_content += f"<div class='detail-item'><strong>{key}:</strong> {', '.join(str(v) for v in value)}</div>"
                    else:
                        html_content += f"<div class='detail-item'><strong>{key}:</strong> {value}</div>"
            
            html_content += """
                </div>
            </div>
            """
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>تم إنشاء هذا التقرير تلقائياً بواسطة نظام الاختبار الشامل</p>
            <p>جميع الملفات والنتائج محفوظة في مجلد: {self.output_dir.absolute()}</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(self.output_dir / 'detailed_test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

def main():
    """تشغيل الاختبار الشامل"""
    tester = ToolsTester()
    results = tester.run_comprehensive_test()
    
    # عرض ملخص سريع
    if results['summary']['successful_tests'] >= 3:
        print("\n🎉 حالة النظام: ممتاز - جاهز للاستخدام!")
    elif results['summary']['successful_tests'] >= 2:
        print("\n✅ حالة النظام: جيد - يعمل مع بعض التحسينات المطلوبة")
    else:
        print("\n⚠️ حالة النظام: يحتاج تحسين - بعض الأدوات تحتاج إصلاح")
    
    print(f"\n📱 لعرض التقرير التفصيلي: {OUTPUT_DIR.absolute() / 'detailed_test_report.html'}")

if __name__ == "__main__":
    main()