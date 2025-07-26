"""
API مبسط للاستخراج الشامل - يعمل فوراً بدون async
Simple Comprehensive Extraction API - Works immediately
"""

from flask import Blueprint, request, jsonify
import logging
import json
import time
from datetime import datetime
from urllib.parse import urlparse

# Import existing working extractors
from core.extractors.advanced_extractor import AdvancedExtractor
from core.scrapers.smart_scraper import SmartScraper
from data.manager import DataManager

# Create Blueprint
simple_comprehensive_bp = Blueprint('simple_comprehensive', __name__)

@simple_comprehensive_bp.route('/simple-comprehensive-extraction', methods=['POST'])
def simple_comprehensive_extraction():
    """الاستخراج الشامل المبسط - يعمل فوراً"""
    try:
        data = request.get_json()
        target_url = data.get('url', '').strip()
        
        if not target_url:
            return jsonify({'error': 'رابط الموقع مطلوب'}), 400
        
        # التحقق من صحة الرابط
        try:
            parsed_url = urlparse(target_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return jsonify({'error': 'رابط الموقع غير صحيح'}), 400
        except Exception:
            return jsonify({'error': 'رابط الموقع غير صحيح'}), 400
        
        extraction_mode = data.get('mode', 'comprehensive')
        
        # بدء الاستخراج الشامل المبسط
        start_time = datetime.now()
        
        # 1. استخراج البيانات الأساسية
        advanced_extractor = AdvancedExtractor()
        basic_result = advanced_extractor.extract_with_mode(target_url, 'advanced')
        
        if 'error' in basic_result:
            return jsonify({
                'success': False,
                'error': f'فشل في الاستخراج الأساسي: {basic_result["error"]}'
            }), 500
        
        # 2. استخراج البيانات المتقدمة
        comprehensive_result = {
            'extraction_id': f"simple_comp_{int(time.time())}",
            'target_url': target_url,
            'extraction_mode': extraction_mode,
            'start_time': start_time.isoformat(),
            'status': 'completed',
            
            # استخراج الواجهة
            'interface_extraction': {
                'html_structure': basic_result.get('structure', {}),
                'css_files': basic_result.get('assets', {}).get('stylesheets', []),
                'javascript_files': basic_result.get('assets', {}).get('scripts', []),
                'images': basic_result.get('assets', {}).get('images', []),
                'media_files': basic_result.get('assets', {}).get('media', []),
                'total_assets': len(basic_result.get('assets', {}).get('all_assets', []))
            },
            
            # البنية التقنية
            'technical_structure': {
                'frameworks_detected': basic_result.get('technologies', []),
                'meta_tags': basic_result.get('metadata', {}),
                'headers_analysis': basic_result.get('security', {}),
                'performance_metrics': basic_result.get('performance', {})
            },
            
            # الوظائف والميزات
            'features_extraction': {
                'forms_detected': basic_result.get('forms', []),
                'interactive_elements': basic_result.get('interactive_elements', []),
                'navigation_structure': basic_result.get('navigation', {}),
                'content_sections': basic_result.get('content_sections', [])
            },
            
            # تحليل السلوك
            'behavior_analysis': {
                'responsive_design': basic_result.get('responsive', {}),
                'javascript_interactions': basic_result.get('javascript_analysis', {}),
                'loading_behavior': basic_result.get('loading_analysis', {}),
                'user_experience': basic_result.get('ux_analysis', {})
            },
            
            # البيانات الكاملة
            'raw_data': basic_result
        }
        
        # 3. إحصائيات الاستخراج
        end_time = datetime.now()
        extraction_time = (end_time - start_time).total_seconds()
        
        comprehensive_result['statistics'] = {
            'extraction_time': extraction_time,
            'pages_analyzed': 1,
            'assets_found': len(basic_result.get('assets', {}).get('all_assets', [])),
            'forms_detected': len(basic_result.get('forms', [])),
            'technologies_detected': len(basic_result.get('technologies', [])),
            'images_found': len(basic_result.get('assets', {}).get('images', [])),
            'scripts_found': len(basic_result.get('assets', {}).get('scripts', [])),
            'stylesheets_found': len(basic_result.get('assets', {}).get('stylesheets', []))
        }
        
        comprehensive_result['end_time'] = end_time.isoformat()
        
        # 4. حفظ النتائج
        data_manager = DataManager()
        domain = urlparse(target_url).netloc
        report_path = data_manager.save_report(
            f"comprehensive_{domain}", 
            comprehensive_result, 
            'comprehensive_extraction'
        )
        
        # 5. إنشاء تقرير HTML مبسط
        html_report = generate_simple_html_report(comprehensive_result)
        html_path = report_path.replace('.json', '.html')
        
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
        except Exception as e:
            logging.warning(f"فشل في حفظ تقرير HTML: {e}")
        
        return jsonify({
            'success': True,
            'message': 'تم الاستخراج الشامل بنجاح',
            'extraction_id': comprehensive_result['extraction_id'],
            'url': target_url,
            'statistics': comprehensive_result['statistics'],
            'result': comprehensive_result,
            'download_links': {
                'json': f'/download-report/{report_path.split("/")[-1]}',
                'html': f'/download-report/{html_path.split("/")[-1]}' if 'html_path' in locals() else None
            }
        })
        
    except Exception as e:
        logging.error(f"خطأ في الاستخراج الشامل المبسط: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الاستخراج: {str(e)}'
        }), 500

def generate_simple_html_report(result):
    """إنشاء تقرير HTML مبسط"""
    stats = result.get('statistics', {})
    interface = result.get('interface_extraction', {})
    technical = result.get('technical_structure', {})
    features = result.get('features_extraction', {})
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تقرير الاستخراج الشامل</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; }}
            .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; margin: 10px; border-radius: 10px; text-align: center; }}
            .stat-number {{ font-size: 2rem; font-weight: bold; color: #007bff; }}
            pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>تقرير الاستخراج الشامل</h1>
            <p>الموقع: {result.get('target_url', 'غير محدد')}</p>
            <p>وقت الاستخراج: {result.get('start_time', 'غير محدد')}</p>
        </div>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('assets_found', 0)}</div>
                        <div>ملفات وأصول</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('forms_detected', 0)}</div>
                        <div>نماذج مكتشفة</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('technologies_detected', 0)}</div>
                        <div>تقنيات مكتشفة</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('extraction_time', 0):.1f}s</div>
                        <div>وقت الاستخراج</div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <ul class="nav nav-tabs" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" data-bs-toggle="tab" href="#interface">الواجهة</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-bs-toggle="tab" href="#technical">البنية التقنية</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-bs-toggle="tab" href="#features">الوظائف</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-bs-toggle="tab" href="#raw">البيانات الخام</a>
                        </li>
                    </ul>
                    
                    <div class="tab-content mt-3">
                        <div class="tab-pane active" id="interface">
                            <h4>استخراج الواجهة</h4>
                            <pre>{json.dumps(interface, ensure_ascii=False, indent=2)}</pre>
                        </div>
                        <div class="tab-pane" id="technical">
                            <h4>البنية التقنية</h4>
                            <pre>{json.dumps(technical, ensure_ascii=False, indent=2)}</pre>
                        </div>
                        <div class="tab-pane" id="features">
                            <h4>الوظائف والميزات</h4>
                            <pre>{json.dumps(features, ensure_ascii=False, indent=2)}</pre>
                        </div>
                        <div class="tab-pane" id="raw">
                            <h4>البيانات الخام</h4>
                            <pre>{json.dumps(result.get('raw_data', {}), ensure_ascii=False, indent=2)}</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return html_template