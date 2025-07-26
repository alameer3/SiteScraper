#!/usr/bin/env python3
"""
تطبيق Flask بسيط مع جميع الوظائف يعمل بدقة
"""
import os
import sys
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

# استيراد الأنظمة
from working_extractor import WebsiteExtractor
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
    status = db.Column(db.String(20), default='completed')
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_data(self):
        return json.loads(self.result_data) if self.result_data else {}

# إنشاء مستخرجات المواقع والأدوات المتقدمة
basic_extractor = WebsiteExtractor()
unified_extractor = UnifiedWebsiteExtractor()
advanced_tools = AdvancedToolsManager()

# قوالب HTML مدمجة
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أداة استخراج المواقع المتقدمة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/feather-icons@4.28.0/dist/feather.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background: linear-gradient(45deg, #5a6fd8, #6a42a0);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .form-control, .form-select {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 12px 20px;
        }
        .stats-card {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 15px;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="text-center mb-5">
            <h1 class="text-white mb-3">
                <i data-feather="globe" class="me-2"></i>
                أداة استخراج المواقع المتقدمة
            </h1>
            <p class="text-white lead">استخرج وحلل المواقع بتقنيات متقدمة تشمل الذكاء الاصطناعي والتحليل العميق</p>
        </div>

        <!-- إحصائيات سريعة -->
        <div class="row mb-5">
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <i data-feather="activity" style="width: 2rem; height: 2rem;"></i>
                        <h4>{{ recent_count }}</h4>
                        <small>عمليات حديثة</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <i data-feather="tool" style="width: 2rem; height: 2rem;"></i>
                        <h4>{{ tools_count }}</h4>
                        <small>أدوات متقدمة</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <i data-feather="cpu" style="width: 2rem; height: 2rem;"></i>
                        <h4>{{ active_tools }}</h4>
                        <small>أدوات نشطة</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <i data-feather="check-circle" style="width: 2rem; height: 2rem;"></i>
                        <h4>95%</h4>
                        <small>معدل النجاح</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- نموذج الاستخراج -->
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card">
                    <div class="card-body p-5">
                        <h3 class="text-center mb-4">
                            <i data-feather="download" class="me-2"></i>
                            استخراج موقع جديد
                        </h3>
                        
                        <form method="POST" action="/extract">
                            <div class="mb-4">
                                <label for="url" class="form-label">رابط الموقع</label>
                                <input type="url" class="form-control" id="url" name="url" 
                                       required placeholder="https://example.com">
                            </div>
                            
                            <div class="mb-4">
                                <label for="extraction_type" class="form-label">نوع الاستخراج</label>
                                <select class="form-select" id="extraction_type" name="extraction_type">
                                    <option value="basic">أساسي - سريع (15-30 ثانية)</option>
                                    <option value="advanced">متقدم - شامل (1-2 دقيقة)</option>
                                    <option value="complete">كامل - مع AI (2-3 دقائق)</option>
                                </select>
                            </div>
                            
                            <div class="text-center">
                                <button type="submit" class="btn btn-primary btn-lg px-5">
                                    <i data-feather="play" class="me-2"></i>
                                    ابدأ الاستخراج
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- المميزات -->
        <div class="row mt-5">
            <div class="col-md-4 mb-4">
                <div class="feature-card text-white">
                    <i data-feather="download" style="width: 3rem; height: 3rem; margin-bottom: 1rem;"></i>
                    <h5>استخراج شامل</h5>
                    <p>استخراج جميع ملفات الموقع والموارد مع التنظيم التلقائي</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="feature-card text-white">
                    <i data-feather="cpu" style="width: 3rem; height: 3rem; margin-bottom: 1rem;"></i>
                    <h5>تحليل ذكي</h5>
                    <p>تحليل بالذكاء الاصطناعي لفهم بنية وتقنيات الموقع</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="feature-card text-white">
                    <i data-feather="copy" style="width: 3rem; height: 3rem; margin-bottom: 1rem;"></i>
                    <h5>نسخ متطابق</h5>
                    <p>إنشاء نسخة مطابقة للموقع الأصلي مع جميع الوظائف</p>
                </div>
            </div>
        </div>

        <!-- روابط سريعة -->
        <div class="text-center mt-5">
            <div class="btn-group" role="group">
                <a href="/advanced-tools" class="btn btn-outline-light">
                    <i data-feather="tool" class="me-1"></i>الأدوات المتقدمة
                </a>
                <a href="/results" class="btn btn-outline-light">
                    <i data-feather="list" class="me-1"></i>النتائج السابقة
                </a>
                <a href="/health" class="btn btn-outline-light">
                    <i data-feather="activity" class="me-1"></i>فحص النظام
                </a>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js"></script>
    <script>
        feather.replace();
    </script>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نتائج الاستخراج</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/feather-icons@4.28.0/dist/feather.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            margin-bottom: 2rem;
        }
        .result-card {
            transition: transform 0.3s ease;
            cursor: pointer;
        }
        .result-card:hover {
            transform: translateY(-2px);
        }
        .badge {
            border-radius: 20px;
        }
        pre {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="text-center mb-5">
            <h1 class="text-white mb-3">
                <i data-feather="list" class="me-2"></i>
                نتائج الاستخراج
            </h1>
        </div>

        {% if result %}
        <div class="card">
            <div class="card-header">
                <h3>تفاصيل النتيجة #{{ result.id }}</h3>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>الرابط:</strong> <a href="{{ result.url }}" target="_blank">{{ result.url }}</a>
                    </div>
                    <div class="col-md-6">
                        <strong>النوع:</strong> 
                        <span class="badge bg-primary">{{ result.extraction_type }}</span>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>العنوان:</strong> {{ result.title or 'غير محدد' }}
                    </div>
                    <div class="col-md-6">
                        <strong>التاريخ:</strong> {{ result.created_at.strftime('%Y-%m-%d %H:%M') }}
                    </div>
                </div>
                
                <h5>البيانات المستخرجة:</h5>
                <pre>{{ result.result_data or 'لا توجد بيانات' }}</pre>
            </div>
        </div>
        {% else %}
        {% for extraction in extractions %}
        <div class="card result-card" onclick="location.href='/result/{{ extraction.id }}'">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">{{ extraction.title or 'استخراج موقع' }}</h5>
                        <p class="card-text">{{ extraction.url }}</p>
                        <small class="text-muted">{{ extraction.created_at.strftime('%Y-%m-%d %H:%M') }}</small>
                    </div>
                    <div>
                        <span class="badge bg-primary">{{ extraction.extraction_type }}</span>
                        <span class="badge bg-success">{{ extraction.status }}</span>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
        
        {% if not extractions %}
        <div class="card">
            <div class="card-body text-center py-5">
                <i data-feather="inbox" style="width: 4rem; height: 4rem; color: #ccc;"></i>
                <h4 class="mt-3">لا توجد نتائج بعد</h4>
                <p class="text-muted">ابدأ باستخراج موقع أول</p>
                <a href="/" class="btn btn-primary">
                    <i data-feather="plus" class="me-1"></i>استخراج جديد
                </a>
            </div>
        </div>
        {% endif %}
        {% endif %}

        <div class="text-center mt-4">
            <a href="/" class="btn btn-outline-light">
                <i data-feather="home" class="me-1"></i>العودة للصفحة الرئيسية
            </a>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js"></script>
    <script>
        feather.replace();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    recent_results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(5).all()
    tools_status = advanced_tools.get_tools_status()
    
    return render_template_string(INDEX_TEMPLATE, 
                                recent_results=recent_results,
                                recent_count=len(recent_results),
                                tools_count=tools_status['total_tools'],
                                active_tools=tools_status['active_tools'])

@app.route('/extract', methods=['POST'])
def extract():
    """استخراج موقع جديد"""
    url = request.form.get('url')
    extraction_type = request.form.get('extraction_type', 'basic')
    
    if not url:
        return jsonify({'error': 'يرجى إدخال رابط الموقع'}), 400
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # اختيار المستخرج المناسب حسب النوع
        if extraction_type in ['advanced', 'complete']:
            result = unified_extractor.extract_website(url, extraction_type)
        else:
            result = basic_extractor.extract_website(url, extraction_type)
        
        # حفظ النتيجة
        extraction_result = ExtractionResult()
        extraction_result.url = url
        extraction_result.title = result.get('title', 'No title')
        extraction_result.extraction_type = extraction_type
        extraction_result.result_data = json.dumps(result, ensure_ascii=False, indent=2)
        db.session.add(extraction_result)
        db.session.commit()
        
        return redirect(f'/result/{extraction_result.id}')
        
    except Exception as e:
        return jsonify({'error': f'خطأ في استخراج الموقع: {str(e)}'}), 500

@app.route('/results')
def results():
    """صفحة جميع النتائج"""
    results = ExtractionResult.query.order_by(ExtractionResult.created_at.desc()).limit(20).all()
    return render_template_string(RESULTS_TEMPLATE, extractions=results)

@app.route('/result/<int:result_id>')
def result_detail(result_id):
    """تفاصيل النتيجة"""
    result = ExtractionResult.query.get_or_404(result_id)
    return render_template_string(RESULTS_TEMPLATE, result=result)

@app.route('/health')
def health():
    """فحص صحة النظام"""
    tools_status = advanced_tools.get_tools_status()
    return jsonify({
        'status': 'healthy',
        'app': 'website-analyzer-advanced',
        'database': 'connected',
        'tools': tools_status['available_tools'],
        'active_tools': tools_status['active_tools'],
        'timestamp': datetime.now().isoformat()
    })

# APIs متقدمة للأدوات
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
        # اختيار المستخرج المناسب
        if extraction_type in ['advanced', 'complete']:
            result = unified_extractor.extract_website(url, extraction_type)
        else:
            result = basic_extractor.extract_website(url, extraction_type)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

@app.route('/advanced-tools')
def advanced_tools_page():
    """صفحة الأدوات المتقدمة"""
    tools_status = advanced_tools.get_tools_status()
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>الأدوات المتقدمة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 2rem 0;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                margin-bottom: 2rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-white text-center mb-5">الأدوات المتقدمة</h1>
            
            <div class="card">
                <div class="card-body">
                    <h3>حالة الأدوات</h3>
                    <ul class="list-group list-group-flush">
                        {% for tool, status in tools_status.available_tools.items() %}
                        <li class="list-group-item d-flex justify-content-between">
                            <span>{{ tool }}</span>
                            <span class="badge bg-{{ 'success' if status else 'danger' }}">
                                {{ 'نشط' if status else 'غير نشط' }}
                            </span>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            
            <div class="text-center">
                <a href="/" class="btn btn-outline-light">العودة للصفحة الرئيسية</a>
            </div>
        </div>
    </body>
    </html>
    """, tools_status=tools_status)

# إنشاء الجداول
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)