#!/usr/bin/env python3
"""
محلل المواقع المتطور - إصدار محسّن ومرتب
Website Analyzer Pro - Clean & Organized Edition
"""
import os
import json
import logging
from datetime import datetime
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
        # تشغيل التحليل
        result = analyzer.analyze_website(url, analysis_type)
        
        # حفظ النتيجة
        analysis_result = AnalysisResult()
        analysis_result.url = url
        analysis_result.title = result.get('title', 'بدون عنوان')
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

@app.route('/api/extraction-presets')
def api_extraction_presets():
    """API للحصول على أنواع الاستخراج المتاحة"""
    if not ADVANCED_SYSTEM_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'النظام المطور غير متاح'
        }), 503
    
    try:
        presets = advanced_extractor.get_available_presets()
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
        'version': '2.0.0'
    })

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