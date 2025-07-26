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

# استيراد النظام العامل
from working_extractor import WebsiteExtractor

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

# إنشاء مستخرج المواقع
extractor = WebsiteExtractor()

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    recent_results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_results=recent_results)

@app.route('/extract', methods=['POST'])
def extract():
    """استخراج موقع جديد"""
    url = request.form.get('url')
    extraction_type = request.form.get('extraction_type', 'basic')
    
    if not url:
        flash('يرجى إدخال رابط الموقع', 'error')
        return redirect(url_for('index'))
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # استخراج الموقع
        result = extractor.extract_website(url, extraction_type)
        
        # حفظ النتيجة
        extraction_result = ExtractionResult(
            url=url,
            title=result.get('title', 'No title'),
            extraction_type=extraction_type,
            result_data=json.dumps(result, ensure_ascii=False, indent=2)
        )
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
        result = extractor.extract_website(url, extraction_type)
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
    return jsonify({
        'status': 'healthy',
        'app': 'website-analyzer',
        'database': 'connected'
    })

# إنشاء الجداول
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)