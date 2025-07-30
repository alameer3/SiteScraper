#!/usr/bin/env python3
"""
محلل المواقع المتطور - إصدار محسّن ومرتب
Website Analyzer Pro - Clean & Organized Edition
"""
import os
import json
import logging
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Base(DeclarativeBase):
    pass

# إنشاء التطبيق والقاعدة
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# التكوين الأساسي
app.secret_key = os.environ.get("SESSION_SECRET", "T3K-Z0hbqq9CCBS37Lb5HHzuXbgMuJuIuSYgvK8jB6g")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# إعداد قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///website_analyzer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# تهيئة قاعدة البيانات
db.init_app(app)

# استيراد النماذج والنظم الأساسية
from models import AnalysisResult
from core import WebsiteAnalyzer
from enhanced_crawler import enhanced_crawler
from optimized_extractor import optimized_extractor

# استيراد أنظمة الحماية والأمان
from ad_blocker import AdBlocker, ContentProtector, PrivacyFilter
from security_scanner import SecurityScanner, ThreatDetector

# استيراد النظام المطور
try:
    from tools2.advanced_extractor import AdvancedWebsiteExtractor
    ADVANCED_SYSTEM_AVAILABLE = True
    advanced_extractor = AdvancedWebsiteExtractor("extracted_files")
    logging.info("✅ تم دمج النظام المطور مع التطبيق الأساسي")
except ImportError as e:
    ADVANCED_SYSTEM_AVAILABLE = False
    advanced_extractor = None
    logging.warning(f"⚠️ النظام المطور غير متاح: {e}")

# تهيئة المحلل الرئيسي
analyzer = WebsiteAnalyzer()

# تهيئة أنظمة الحماية والأمان
ad_blocker = AdBlocker()
content_protector = ContentProtector()
privacy_filter = PrivacyFilter()
security_scanner = SecurityScanner()
threat_detector = ThreatDetector()

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    recent_results = AnalysisResult.query.order_by(
        AnalysisResult.created_at.desc()
    ).limit(5).all()
    
    stats = {
        'total_analyses': AnalysisResult.query.count(),
        'successful_analyses': AnalysisResult.query.filter_by(status='completed').count(),
        'recent_count': len(recent_results)
    }
    
    return render_template('index.html', recent_results=recent_results, stats=stats)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """تحليل موقع جديد"""
    if request.method == 'GET':
        return render_template('analyze.html')
    
    url = request.form.get('url', '').strip()
    analysis_type = request.form.get('analysis_type', 'standard')
    
    if not url:
        flash('يرجى إدخال رابط صحيح', 'error')
        return redirect(url_for('analyze'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # تشغيل النظام المحسن السريع أولاً
        optimized_result = optimized_extractor.extract_comprehensive_fast(url)
        
        if optimized_result['success']:
            # استخدام النتيجة المحسنة السريعة
            result = {
                'success': True,
                'data': optimized_result['data'],
                'execution_time': optimized_result['execution_time'],
                'method_used': optimized_result['method_used'],
                'optimized': True
            }
        else:
            # إذا فشل النظام المحسن، جرب النظام العادي
            app.logger.warning(f"فشل النظام المحسن: {optimized_result['error']}")
            try:
                enhanced_result = enhanced_crawler.analyze_website_enhanced(url)
                if enhanced_result['success']:
                    result = {
                        'success': True,
                        'data': enhanced_result['data'],
                        'execution_time': enhanced_result['execution_time'],
                        'method_used': enhanced_result['method_used'],
                        'enhanced': True
                    }
                else:
                    result = analyzer.analyze_website(url, analysis_type)
            except Exception as e:
                app.logger.error(f"خطأ في النظام الاحتياطي: {str(e)}")
                result = analyzer.analyze_website(url, analysis_type)
        
        # حفظ النتيجة
        analysis_result = AnalysisResult()
        analysis_result.url = url
        
        # استخراج العنوان من البيانات
        if result.get('optimized'):
            title = result['data']['basic_info'].get('title', 'بدون عنوان')
        elif result.get('enhanced'):
            title = result['data'].get('title', 'بدون عنوان')
        else:
            title = result.get('data', {}).get('title', 'بدون عنوان')
            
        analysis_result.title = title
        analysis_result.analysis_type = analysis_type
        analysis_result.status = 'completed'
        analysis_result.result_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        return redirect(url_for('result_detail', result_id=analysis_result.id))
        
    except Exception as e:
        app.logger.error(f"خطأ في تحليل الموقع {url}: {str(e)}")
        flash(f'خطأ في تحليل الموقع: {str(e)}', 'error')
        return redirect(url_for('analyze'))

@app.route('/results')
def results():
    """عرض جميع النتائج"""
    page = request.args.get('page', 1, type=int)
    results = AnalysisResult.query.order_by(
        AnalysisResult.created_at.desc()
    ).paginate(
        page=page, 
        per_page=10, 
        error_out=False
    )
    return render_template('results.html', results=results)

@app.route('/result/<int:result_id>')
def result_detail(result_id):
    """تفاصيل النتيجة"""
    result = AnalysisResult.query.get_or_404(result_id)
    return render_template('result_detail.html', result=result)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API لتحليل المواقع"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL مطلوب'
        }), 400
    
    url = data['url']
    analysis_type = data.get('analysis_type', 'standard')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        result = analyzer.analyze_website(url, analysis_type)
        
        # حفظ في قاعدة البيانات
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = result.get('title', 'بدون عنوان')
        analysis_result.analysis_type = analysis_type
        analysis_result.status = 'completed'
        analysis_result.result_data = json.dumps(result, ensure_ascii=False)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': result,
            'result_id': analysis_result.id
        })
        
    except Exception as e:
        app.logger.error(f"API تحليل خطأ: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== النظام المطور ====================

@app.route('/unified-extractor')
def unified_extractor():
    """صفحة نظام الاستخراج المتطور"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        flash('النظام المطور غير متاح حالياً', 'warning')
        return redirect(url_for('index'))
    
    return render_template('unified_extractor.html')

@app.route('/extract-advanced', methods=['POST'])
def extract_advanced():
    """تشغيل نظام الاستخراج المتطور"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        flash('النظام المطور غير متاح حالياً', 'error')
        return redirect(url_for('index'))
    
    url = request.form.get('url', '').strip()
    extraction_type = request.form.get('extraction_type', 'standard')
    
    if not url:
        flash('يرجى إدخال رابط صحيح', 'error')
        return redirect(url_for('unified_extractor'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # تشغيل الاستخراج المتطور
        if advanced_extractor is None:
            raise Exception("النظام المتطور غير متاح")
        result = advanced_extractor.extract(url, extraction_type)
        
        # حفظ النتيجة في قاعدة البيانات
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = result.get('title', 'بدون عنوان')
        analysis_result.analysis_type = f"advanced_{extraction_type}"
        analysis_result.status = 'completed' if result.get('success') else 'failed'
        analysis_result.result_data = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        flash(f'تم الاستخراج بنجاح! نوع الاستخراج: {extraction_type}', 'success')
        return redirect(url_for('result_detail', result_id=analysis_result.id))
        
    except Exception as e:
        app.logger.error(f"خطأ في نظام الاستخراج المتطور: {str(e)}")
        flash(f'خطأ في الاستخراج: {str(e)}', 'error')
        return redirect(url_for('unified_extractor'))

@app.route('/api/extract-advanced', methods=['POST'])
def api_extract_advanced():
    """API لنظام الاستخراج المتطور"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'النظام المطور غير متاح'
        }), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL مطلوب'
        }), 400
    
    url = data['url']
    extraction_type = data.get('extraction_type', 'standard')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        if advanced_extractor is None:
            raise Exception("النظام المتطور غير متاح")
        result = advanced_extractor.extract(url, extraction_type)
        
        # حفظ في قاعدة البيانات
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = result.get('title', 'بدون عنوان')
        analysis_result.analysis_type = f"advanced_{extraction_type}"
        analysis_result.status = 'completed' if result.get('success') else 'failed'
        analysis_result.result_data = json.dumps(result, ensure_ascii=False, default=str)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': result,
            'result_id': analysis_result.id,
            'extraction_folder': result.get('extraction_folder')
        })
        
    except Exception as e:
        app.logger.error(f"API استخراج متطور خطأ: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/comprehensive-extractor')
def comprehensive_extractor():
    """صفحة النظام الشامل - جميع المزايا المطلوبة حسب 11.txt"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        flash('النظام المطور غير متاح حالياً', 'warning')
        return redirect(url_for('index'))
    
    return render_template('comprehensive_extractor.html')

@app.route('/extract-comprehensive', methods=['POST'])
def extract_comprehensive():
    """تشغيل النظام الشامل مع جميع المزايا"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        flash('النظام المطور غير متاح حالياً', 'error')
        return redirect(url_for('index'))
    
    url = request.form.get('url', '').strip()
    extraction_type = request.form.get('extraction_type', 'complete')
    
    if not url:
        flash('يرجى إدخال رابط صحيح', 'error')
        return redirect(url_for('comprehensive_extractor'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # التحقق من المواقع المحظورة (استثناء ak.sv للاختبار)
    blocked_domains = [
        'localhost', '127.0.0.1',
        'github.com', 'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
        'google.com', 'amazon.com', 'ebay.com', 'paypal.com', 'netflix.com',
        'spotify.com', 'apple.com', 'microsoft.com', 'adobe.com', 'salesforce.com',
        'cloudflare.com', 'akamai.com', 'fastly.com', 'cnn.com', 'bbc.com'
    ]
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    
    if any(blocked_domain in domain for blocked_domain in blocked_domains):
        flash(f'⚠️ الموقع {domain} محمي ولا يمكن تحليله. استخدم المواقع المقترحة للاختبار.', 'warning')
        return redirect(url_for('comprehensive_extractor'))
    
    try:
        # تشغيل النظام الشامل مع حماية متطورة
        app.logger.info(f"🚀 بدء التحليل الشامل للموقع: {url}")
        if advanced_extractor is None:
            raise Exception("النظام الشامل غير متاح")
        
        # تطبيق أنظمة الحماية والتنظيف
        app.logger.info("🛡️ تطبيق أنظمة الحماية وتخطي الإعلانات...")
        
        # جلب المحتوى الأولي للفحص
        initial_response = analyzer.session.get(url, timeout=15)
        original_content = initial_response.text
        
        # فحص التهديدات قبل الاستخراج
        threats = threat_detector.detect_threats(original_content, url)
        app.logger.info(f"🔍 تم اكتشاف {len(threats.get('threats_found', []))} تهديد محتمل")
        
        # تنظيف المحتوى من الإعلانات والمتتبعات
        cleaned_content = ad_blocker.clean_html(original_content, url)
        cleaned_content = content_protector.remove_trackers(cleaned_content)
        cleaned_content = content_protector.sanitize_content(cleaned_content)
        
        # حساب إحصائيات التنظيف
        original_size = len(original_content)
        cleaned_size = len(cleaned_content)
        reduction_percentage = ((original_size - cleaned_size) / original_size) * 100 if original_size > 0 else 0
        
        app.logger.info(f"✅ تم تنظيف المحتوى بنسبة {reduction_percentage:.1f}%")
        
        # استخدام النظام المحسن السريع بدلاً من comprehensive download
        app.logger.info("🚀 تشغيل النظام المحسن السريع...")
        optimized_result = optimized_extractor.extract_comprehensive_fast(url)
        
        if optimized_result['success']:
            result = {
                'extraction_info': {
                    'success': True,
                    'duration': optimized_result['execution_time'],
                    'base_folder': f"النظام السريع - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                },
                'basic_content': {
                    'basic_info': optimized_result['data']['basic_info']
                },
                'optimized_extraction': True,
                'data': optimized_result['data']
            }
        else:
            # إذا فشل النظام المحسن، جرب النظام العادي
            app.logger.warning(f"فشل النظام المحسن: {optimized_result['error']}")
            result = {
                'extraction_info': {
                    'success': False,
                    'duration': 0,
                    'error': optimized_result['error']
                },
                'error': optimized_result['error']
            }
        
        # إضافة معلومات الحماية إلى النتائج
        if isinstance(result, dict):
            result['security_analysis'] = {
                'threats_detected': threats,
                'content_protection': {
                    'original_size': original_size,
                    'cleaned_size': cleaned_size,
                    'reduction_percentage': round(reduction_percentage, 2),
                    'ads_blocked': True,
                    'trackers_removed': True,
                    'content_sanitized': True
                },
                'ad_blocker_stats': ad_blocker.get_blocked_stats()
            }
        
        # حفظ النتيجة في قاعدة البيانات
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = result.get('basic_content', {}).get('basic_info', {}).get('title', 'بدون عنوان')
        analysis_result.analysis_type = f"comprehensive_{extraction_type}"
        analysis_result.status = 'completed' if result.get('extraction_info', {}).get('success') else 'failed'
        analysis_result.result_data = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        if result.get('extraction_info', {}).get('success'):
            flash(f'✅ تم التحليل الشامل بنجاح! المدة: {result["extraction_info"]["duration"]} ثانية', 'success')
            flash(f'📁 مجلد النتائج: {result["extraction_info"]["base_folder"]}', 'info')
            
            # رسائل حماية إضافية
            security_info = result.get('security_analysis', {})
            content_protection = security_info.get('content_protection', {})
            if content_protection.get('reduction_percentage', 0) > 5:
                flash(f'🛡️ تم تنظيف المحتوى وإزالة {content_protection["reduction_percentage"]:.1f}% من الإعلانات والمتتبعات', 'info')
            
            threats_count = len(security_info.get('threats_detected', {}).get('threats_found', []))
            if threats_count > 0:
                flash(f'⚠️ تم اكتشاف ومعالجة {threats_count} تهديد أمني', 'warning')
        else:
            flash(f'❌ فشل التحليل: {result.get("error", "خطأ غير معروف")}', 'error')
        
        return redirect(url_for('result_detail', result_id=analysis_result.id))
        
    except Exception as e:
        app.logger.error(f"خطأ في النظام الشامل: {str(e)}")
        flash(f'خطأ في التحليل الشامل: {str(e)}', 'error')
        return redirect(url_for('comprehensive_extractor'))

@app.route('/api/extract-comprehensive', methods=['POST'])
def api_extract_comprehensive():
    """API للنظام الشامل"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'النظام الشامل غير متاح'
        }), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL مطلوب'
        }), 400
    
    url = data['url']
    extraction_type = data.get('extraction_type', 'complete')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        if advanced_extractor is None:
            raise Exception("النظام الشامل غير متاح")
        
        # تطبيق حماية متطورة في API
        initial_response = analyzer.session.get(url, timeout=15)
        original_content = initial_response.text
        
        # فحص وتنظيف المحتوى
        threats = threat_detector.detect_threats(original_content, url)
        cleaned_content = ad_blocker.clean_html(original_content, url)
        cleaned_content = content_protector.remove_trackers(cleaned_content)
        cleaned_content = content_protector.sanitize_content(cleaned_content)
        
        # حساب إحصائيات
        original_size = len(original_content)
        cleaned_size = len(cleaned_content)
        reduction_percentage = ((original_size - cleaned_size) / original_size) * 100 if original_size > 0 else 0
        
        result = advanced_extractor.comprehensive_website_download(url, extraction_type)
        
        # إضافة معلومات الحماية
        if isinstance(result, dict):
            result['security_analysis'] = {
                'threats_detected': threats,
                'content_protection': {
                    'original_size': original_size,
                    'cleaned_size': cleaned_size,
                    'reduction_percentage': round(reduction_percentage, 2),
                    'protection_enabled': True
                },
                'ad_blocker_stats': ad_blocker.get_blocked_stats()
            }
        
        # حفظ في قاعدة البيانات
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = result.get('basic_content', {}).get('basic_info', {}).get('title', 'بدون عنوان')
        analysis_result.analysis_type = f"comprehensive_{extraction_type}"
        analysis_result.status = 'completed' if result.get('extraction_info', {}).get('success') else 'failed'
        analysis_result.result_data = json.dumps(result, ensure_ascii=False, default=str)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        # إحصائيات محسنة مع معلومات الحماية
        security_info = result.get('security_analysis', {})
        return jsonify({
            'success': True,
            'data': result,
            'result_id': analysis_result.id,
            'extraction_folder': result.get('extraction_info', {}).get('base_folder'),
            'duration': result.get('extraction_info', {}).get('duration'),
            'pages_crawled': result.get('crawl_results', {}).get('pages_crawled', 0),
            'assets_downloaded': result.get('assets_download', {}).get('summary', {}).get('total_downloaded', 0),
            'security_stats': {
                'threats_found': len(security_info.get('threats_detected', {}).get('threats_found', [])),
                'content_cleaned': security_info.get('content_protection', {}).get('reduction_percentage', 0),
                'protection_enabled': True
            }
        })
        
    except Exception as e:
        app.logger.error(f"API النظام الشامل خطأ: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/extraction-presets')
def api_extraction_presets():
    """API للحصول على أنواع الاستخراج المتاحة"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'النظام المطور غير متاح'
        }), 503
    
    try:
        if advanced_extractor is None:
            raise Exception("النظام المتطور غير متاح")
        # استخدام قائمة ثابتة للأنماط المتاحة بدلاً من get_available_presets
        presets = {
            'basic': 'استخراج أساسي - محتوى النص والروابط',
            'standard': 'استخراج قياسي - محتوى + صور + ملفات CSS/JS',
            'advanced': 'استخراج متقدم - تحليل شامل + أدوات متطورة',
            'complete': 'استخراج كامل - جميع المزايا + تحليل عميق',
            'ultra': 'استخراج فائق - نسخ كامل + ذكاء اصطناعي'
        }
        return jsonify({
            'success': True,
            'presets': presets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/results')
def api_results():
    """API لجلب النتائج"""
    limit = request.args.get('limit', 10, type=int)
    results = AnalysisResult.query.order_by(
        AnalysisResult.created_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        'id': r.id,
        'url': r.url,
        'title': r.title,
        'analysis_type': r.analysis_type,
        'status': r.status,
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in results])

@app.route('/health')
def health():
    """فحص صحة النظام"""
    return jsonify({
        'status': 'healthy',
        'app': 'website-analyzer-pro',
        'database': 'connected',
        'version': '2.0.0',
        'security_systems': {
            'ad_blocker': 'enabled',
            'content_protector': 'enabled',
            'privacy_filter': 'enabled',
            'security_scanner': 'enabled',
            'threat_detector': 'enabled'
        }
    })

# ==================== أنظمة الحماية والأمان ====================

@app.route('/security-scan')
def security_scan_page():
    """صفحة فحص الأمان"""
    return render_template('security_scan.html')

@app.route('/scan-security', methods=['POST'])
def scan_security():
    """تشغيل فحص أمني شامل"""
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('يرجى إدخال رابط صحيح للفحص', 'error')
        return redirect(url_for('security_scan_page'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # تشغيل الفحص الأمني الشامل
        scan_results = security_scanner.comprehensive_security_scan(url)
        
        # حفظ النتيجة في قاعدة البيانات
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = f"فحص أمني - {urlparse(url).netloc}"
        analysis_result.analysis_type = "security_scan"
        analysis_result.status = 'completed'
        analysis_result.result_data = json.dumps(scan_results, ensure_ascii=False, indent=2, default=str)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        # عرض النتائج
        security_score = scan_results.get('overall_security_score', 0)
        if security_score >= 80:
            flash(f'✅ الموقع آمن! نقاط الأمان: {security_score}/100', 'success')
        elif security_score >= 60:
            flash(f'⚠️ الموقع آمن نسبياً. نقاط الأمان: {security_score}/100', 'warning')
        else:
            flash(f'❌ تحذير أمني! نقاط الأمان: {security_score}/100', 'error')
        
        return redirect(url_for('result_detail', result_id=analysis_result.id))
        
    except Exception as e:
        app.logger.error(f"خطأ في الفحص الأمني: {str(e)}")
        flash(f'خطأ في الفحص الأمني: {str(e)}', 'error')
        return redirect(url_for('security_scan_page'))

@app.route('/ad-block-analysis')
def ad_block_analysis_page():
    """صفحة تحليل الإعلانات"""
    return render_template('ad_block_analysis.html')

@app.route('/analyze-ads', methods=['POST'])
def analyze_ads():
    """تحليل وإزالة الإعلانات"""
    url = request.form.get('url', '').strip()
    remove_ads = request.form.get('remove_ads', 'off') == 'on'
    
    if not url:
        flash('يرجى إدخال رابط صحيح', 'error')
        return redirect(url_for('ad_block_analysis_page'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # جلب محتوى الصفحة
        response = analyzer.session.get(url, timeout=15)
        original_content = response.text
        
        # كشف التهديدات
        threats = threat_detector.detect_threats(original_content, url)
        
        # تحليل البيانات الحساسة
        sensitive_data = privacy_filter.detect_sensitive_data(original_content)
        
        # تنظيف المحتوى إذا طُلب ذلك
        cleaned_content = original_content
        if remove_ads:
            # إزالة الإعلانات
            cleaned_content = ad_blocker.clean_html(cleaned_content, url)
            # إزالة المتتبعات
            cleaned_content = content_protector.remove_trackers(cleaned_content)
            # تعقيم المحتوى
            cleaned_content = content_protector.sanitize_content(cleaned_content)
            # إخفاء البيانات الحساسة
            cleaned_content = privacy_filter.mask_sensitive_data(cleaned_content)
        
        # إحصائيات التنظيف
        original_size = len(original_content)
        cleaned_size = len(cleaned_content)
        reduction_percentage = ((original_size - cleaned_size) / original_size) * 100 if original_size > 0 else 0
        
        analysis_results = {
            'url': url,
            'original_size': original_size,
            'cleaned_size': cleaned_size,
            'reduction_percentage': round(reduction_percentage, 2),
            'threats_detected': threats,
            'sensitive_data': sensitive_data,
            'ad_blocker_stats': ad_blocker.get_blocked_stats(),
            'content_cleaned': remove_ads,
            'cleaned_content': cleaned_content if remove_ads else None
        }
        
        # حفظ النتيجة
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = f"تحليل الإعلانات - {urlparse(url).netloc}"
        analysis_result.analysis_type = "ad_block_analysis"
        analysis_result.status = 'completed'
        analysis_result.result_data = json.dumps(analysis_results, ensure_ascii=False, indent=2, default=str)
        
        db.session.add(analysis_result)
        db.session.commit()
        
        # رسائل النتائج
        if threats['threat_score'] > 0:
            flash(f'⚠️ تم اكتشاف {len(threats["threats_found"])} تهديد محتمل', 'warning')
        
        if any(len(data) > 0 for data in sensitive_data.values()):
            flash('🔐 تم اكتشاف بيانات حساسة في الموقع', 'info')
        
        if remove_ads and reduction_percentage > 10:
            flash(f'✅ تم تنظيف المحتوى! تم تقليل الحجم بـ {reduction_percentage:.1f}%', 'success')
        
        return redirect(url_for('result_detail', result_id=analysis_result.id))
        
    except Exception as e:
        app.logger.error(f"خطأ في تحليل الإعلانات: {str(e)}")
        flash(f'خطأ في التحليل: {str(e)}', 'error')
        return redirect(url_for('ad_block_analysis_page'))

@app.route('/api/security-scan', methods=['POST'])
def api_security_scan():
    """API للفحص الأمني"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL مطلوب'
        }), 400
    
    url = data['url']
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        scan_results = security_scanner.comprehensive_security_scan(url)
        
        return jsonify({
            'success': True,
            'data': scan_results,
            'security_score': scan_results.get('overall_security_score', 0),
            'recommendations': scan_results.get('recommendations', [])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ad-block', methods=['POST'])
def api_ad_block():
    """API لتخطي الإعلانات"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL مطلوب'
        }), 400
    
    url = data['url']
    remove_ads = data.get('remove_ads', True)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # جلب المحتوى
        response = analyzer.session.get(url, timeout=15)
        content = response.text
        
        results = {
            'url': url,
            'original_size': len(content),
            'threats': threat_detector.detect_threats(content, url),
            'sensitive_data': privacy_filter.detect_sensitive_data(content)
        }
        
        if remove_ads:
            # تنظيف المحتوى
            cleaned = ad_blocker.clean_html(content, url)
            cleaned = content_protector.remove_trackers(cleaned)
            cleaned = content_protector.sanitize_content(cleaned)
            
            results.update({
                'cleaned_size': len(cleaned),
                'reduction_percentage': ((len(content) - len(cleaned)) / len(content)) * 100,
                'cleaned_content': cleaned
            })
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/threat-detection', methods=['POST'])
def api_threat_detection():
    """API لكشف التهديدات"""
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'بيانات مطلوبة'
        }), 400
    
    content = data.get('content', '')
    url = data.get('url', '')
    
    if not content and not url:
        return jsonify({
            'success': False,
            'error': 'محتوى أو رابط مطلوب'
        }), 400
    
    try:
        if url and not content:
            # جلب المحتوى من الرابط
            response = analyzer.session.get(url, timeout=15)
            content = response.text
        
        threats = threat_detector.detect_threats(content, url)
        
        return jsonify({
            'success': True,
            'threats': threats,
            'threat_level': threats.get('threat_level', 'Low'),
            'threat_score': threats.get('threat_score', 0)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# معالج الأخطاء
@app.errorhandler(404)
def not_found(error):
    """صفحة غير موجودة"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """خطأ خادم داخلي"""
    db.session.rollback()
    return render_template('500.html'), 500

# إنشاء الجداول
with app.app_context():
    db.create_all()
    app.logger.info("تم إنشاء قاعدة البيانات بنجاح")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)