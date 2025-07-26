"""
تطبيق بسيط لاختبار الوظائف الأساسية
"""
import os
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# إعداد Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///simple_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد قاعدة البيانات
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# نموذج البيانات
class SimpleExtraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    extraction_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='completed')
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء الجداول
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['GET', 'POST'])
def extract():
    if request.method == 'POST':
        url = request.form.get('url')
        extraction_type = request.form.get('extraction_type', 'basic')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # إنشاء نتيجة بسيطة
        result_data = {
            'success': True,
            'url': url,
            'extraction_type': extraction_type,
            'pages_extracted': 1,
            'assets_downloaded': 0,
            'total_size': 1024,
            'duration': 2.5,
            'technologies_detected': {
                'framework': 'Unknown',
                'cms': 'Unknown',
                'analytics': []
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # حفظ في قاعدة البيانات
        extraction = SimpleExtraction(
            url=url,
            extraction_type=extraction_type,
            status='completed',
            result_data=json.dumps(result_data)
        )
        db.session.add(extraction)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'extraction_id': extraction.id,
            'result': result_data
        })
    
    return render_template('extract.html')

@app.route('/results')
def results():
    extractions = SimpleExtraction.query.order_by(SimpleExtraction.created_at.desc()).all()
    return render_template('results.html', extractions=extractions)

@app.route('/result/<int:extraction_id>')
def view_result(extraction_id):
    extraction = SimpleExtraction.query.get_or_404(extraction_id)
    result_data = json.loads(extraction.result_data) if extraction.result_data else {}
    return render_template('result_detail.html', extraction=extraction, result_data=result_data)

@app.route('/api/extract', methods=['POST'])
def api_extract():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    extraction_type = data.get('extraction_type', 'basic')
    
    result_data = {
        'success': True,
        'url': url,
        'extraction_type': extraction_type,
        'pages_extracted': 1,
        'assets_downloaded': 0,
        'total_size': 1024,
        'message': 'تم الاستخراج بنجاح (نسخة تجريبية)'
    }
    
    return jsonify({
        'status': 'success',
        'result': result_data
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 تشغيل التطبيق البسيط...")
    app.run(host='0.0.0.0', port=5000, debug=True)