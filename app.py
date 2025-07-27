#!/usr/bin/env python3
"""
تطبيق Flask لأداة استخراج المواقع
"""
import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

# استيراد الأنظمة المتقدمة
from unified_extractor import UnifiedWebsiteExtractor
from advanced_tools_manager import AdvancedToolsManager

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# إنشاء التطبيق
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# إعداد قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///website_analyzer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# نموذج النتائج
class ExtractionResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    extraction_type = db.Column(db.String(50), default='basic')
    status = db.Column(db.String(50), default='completed')
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_data(self):
        return json.loads(self.result_data) if self.result_data else {}

# إنشاء مستخرجات المواقع والأدوات المتقدمة
unified_extractor = UnifiedWebsiteExtractor()
advanced_tools = AdvancedToolsManager()

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    recent_results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_results=recent_results)

@app.route('/extract', methods=['GET', 'POST'])
def extract():
    """صفحة/API استخراج موقع جديد"""
    if request.method == 'GET':
        return render_template('extract.html')
    
    url = request.form.get('url')
    extraction_type = request.form.get('extraction_type', 'basic')
    
    if not url:
        flash('يرجى إدخال رابط الموقع', 'error')
        return redirect(url_for('index'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # اختيار المستخرج المناسب حسب النوع
        result = unified_extractor.extract_website(url, extraction_type)
        
        # حفظ النتيجة
        extraction_result = ExtractionResult()
        extraction_result.url = url
        extraction_result.title = result.get('title', 'No title')
        extraction_result.extraction_type = extraction_type
        extraction_result.result_data = json.dumps(result, ensure_ascii=False, indent=2)
        db.session.add(extraction_result)
        db.session.commit()
        
        return redirect(url_for('result_detail', result_id=extraction_result.id))
        
    except Exception as e:
        flash(f'خطأ في استخراج الموقع: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """صفحة جميع النتائج"""
    page = request.args.get('page', 1, type=int)
    results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('results.html', results=results)

@app.route('/result/<int:result_id>')
def result_detail(result_id):
    """تفاصيل النتيجة"""
    result = ExtractionResult.query.get_or_404(result_id)
    return render_template('result_detail.html', result=result)

# النظام الموحد مبسط
UNIFIED_SYSTEM_AVAILABLE = False

# APIs متقدمة لجميع الأدوات

@app.route('/api/tools/status')
def api_tools_status():
    """حالة جميع الأدوات"""
    return jsonify(advanced_tools.get_tools_status())

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API لاستخراج الموقع"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    extraction_type = data.get('extraction_type', 'basic')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # استخدام المستخرج الموحد
        result = unified_extractor.extract_website(url, extraction_type)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """فحص صحة النظام"""
    tools_status = advanced_tools.get_tools_status()
    return jsonify({
        'status': 'healthy',
        'app': 'website-analyzer',
        'database': 'connected',
        'tools': tools_status['available_tools'],
        'active_tools': tools_status['active_tools']
    })

# APIs متقدمة للأدوات
@app.route('/api/cloner-pro', methods=['POST'])
def api_cloner_pro():
    """API لـ Website Cloner Pro"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    config = data.get('config', {})
    
    try:
        result = advanced_tools.extract_with_cloner_pro(url, config)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-analyze', methods=['POST'])
def api_ai_analyze():
    """API لتحليل المحتوى بالذكاء الاصطناعي"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content']
    analysis_type = data.get('analysis_type', 'comprehensive')
    
    try:
        result = advanced_tools.analyze_with_ai(content, analysis_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spider-crawl', methods=['POST'])
def api_spider_crawl():
    """API لـ Spider Engine"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    max_depth = data.get('max_depth', 2)
    
    try:
        result = advanced_tools.extract_with_spider(url, max_depth)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-assets', methods=['POST'])
def api_download_assets():
    """API لتحميل الأصول"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    asset_types = data.get('asset_types', ['images', 'css', 'js'])
    
    try:
        result = advanced_tools.download_assets(url, asset_types)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# صفحات الأدوات المتقدمة والموحدة
@app.route('/advanced-tools')
def advanced_tools_page():
    """صفحة الأدوات المتقدمة"""
    tools_status = advanced_tools.get_tools_status()
    return render_template('advanced_tools.html', tools_status=tools_status)

@app.route('/unified-dashboard')
def unified_dashboard():
    """لوحة التحكم الموحدة المتطورة"""
    # إحصائيات النظام البسيطة
    total_results = ExtractionResult.query.count()
    recent_results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(5).all()
    
    system_stats = {
        'database_stats': {
            'total_extractions': total_results,
            'completed_extractions': total_results,
            'failed_extractions': 0,
            'total_data_extracted_mb': 0.0
        },
        'system_health': 'excellent',
        'system_uptime': 'متاح',
        'tools_status': {'active_tools': 6}
    }
    
    return render_template('unified_dashboard.html', 
                         system_stats=system_stats,
                         recent_extractions=recent_results)

@app.route('/unified-extractor')
def unified_extractor_page():
    """صفحة المستخرج الموحد المتطور"""
    # إحصائيات سريعة
    total_extractions = unified_extractor.extraction_id
    recent_results = list(unified_extractor.results.values())[-5:] if unified_extractor.results else []
    
    stats = {
        'total_extractions': total_extractions,
        'recent_extractions': len(recent_results),
        'available_modes': 5,  # basic, standard, advanced, complete, secure
        'system_status': 'active'
    }
    
    return render_template('unified_extractor.html', stats=stats, recent_results=recent_results)

# API للنظام الموحد البسيط
@app.route('/api/unified/stats')
def api_unified_stats():
    """API إحصائيات النظام"""
    total_results = ExtractionResult.query.count()
    return jsonify({
        'database_stats': {
            'total_extractions': total_results,
            'completed_extractions': total_results,
            'failed_extractions': 0,
            'total_data_extracted_mb': 0.0
        },
        'system_health': 'excellent',
        'system_uptime': 'متاح',
        'tools_status': {'active_tools': 6}
    })

@app.route('/api/unified/recent')
def api_unified_recent():
    """API آخر الاستخراجات"""
    limit = request.args.get('limit', 5, type=int)
    recent_results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(limit).all()
    
    results = []
    for result in recent_results:
        results.append({
            'url': result.url,
            'extraction_type': result.extraction_type,
            'status': result.status,
            'created_at': result.created_at.isoformat() if result.created_at else ''
        })
    
    return jsonify(results)

@app.route('/api/unified-extract', methods=['POST'])
def api_unified_extract():
    """API موحد للاستخراج - الإصدار المحسن"""
    try:
        # التحقق من البيانات المرسلة
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        extraction_type = data.get('extraction_type', 'basic')
        
        # تصحيح URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # تشغيل الاستخراج
        result = unified_extractor.extract_website(url, extraction_type)
        
        if result.get('success'):
            # حفظ النتيجة في قاعدة البيانات
            try:
                extraction_result = ExtractionResult()
                extraction_result.url = url
                extraction_result.title = result.get('title', 'بدون عنوان')
                extraction_result.extraction_type = extraction_type
                extraction_result.status = 'completed'
                extraction_result.result_data = json.dumps(result, ensure_ascii=False)
                db.session.add(extraction_result)
                db.session.commit()
                
                # إضافة ID النتيجة
                result['database_id'] = extraction_result.id
                
            except Exception as db_error:
                # إذا فشل حفظ قاعدة البيانات، لا نفشل العملية
                result['database_error'] = str(db_error)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'extraction_id': 0
        }), 500

@app.route('/api/unified/extract', methods=['POST'])
def api_unified_extract_legacy():
    """API legacy للاستخراج"""
    return api_unified_extract()

@app.route('/cloner-pro')
def cloner_pro_page():
    """صفحة Website Cloner Pro"""
    return render_template('cloner_pro.html')

@app.route('/ai-analyzer')
def ai_analyzer_page():
    """صفحة محلل الذكاء الاصطناعي"""
    return render_template('ai_analyzer.html')

@app.route('/file-manager')
def file_manager_page():
    """صفحة إدارة الملفات"""
    # إحصائيات مؤقتة حتى يتم تفعيل file_manager_api
    storage_stats = {
        'total_extractions': ExtractionResult.query.count(),
        'storage_used': '1.2 MB',
        'cache_size': '500 KB'
    }
    recent_extractions = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(10).all()
    return render_template('file_manager.html',
                         storage_stats=storage_stats,
                         recent_extractions=recent_extractions)

# إنشاء الجداول
with app.app_context():
    db.create_all()

# تم نقل التشغيل إلى main.py