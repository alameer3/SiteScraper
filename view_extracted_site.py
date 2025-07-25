#!/usr/bin/env python3
"""
عارض بسيط للمواقع المستخرجة
"""

from flask import Flask, send_from_directory, render_template_string, jsonify
import os
from pathlib import Path
import json

app = Flask(__name__)

# مسار المواقع المستخرجة
EXTRACTED_SITES_PATH = Path("extracted_sites")

# قالب HTML لعرض قائمة المواقع
SITE_LIST_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>المواقع المستخرجة</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5;
            direction: rtl;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            text-align: center; 
            margin-bottom: 30px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
        }
        .site-card { 
            border: 1px solid #ddd; 
            margin: 20px 0; 
            padding: 20px; 
            border-radius: 8px; 
            background: #fafafa;
            transition: all 0.3s ease;
        }
        .site-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .site-name { 
            font-size: 1.5em; 
            color: #007bff; 
            margin-bottom: 10px;
            font-weight: bold;
        }
        .site-info { 
            color: #666; 
            margin: 10px 0; 
        }
        .btn { 
            display: inline-block; 
            padding: 10px 20px; 
            background: #007bff; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 5px;
            transition: background 0.3s ease;
        }
        .btn:hover { 
            background: #0056b3; 
        }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #1e7e34; }
        .btn-info { background: #17a2b8; }
        .btn-info:hover { background: #117a8b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 المواقع المستخرجة</h1>
        
        {% for site in sites %}
        <div class="site-card">
            <div class="site-name">{{ site.name }}</div>
            <div class="site-info">
                <strong>الرابط الأصلي:</strong> {{ site.original_url }}<br>
                <strong>عدد الصفحات:</strong> {{ site.pages_count }}<br>
                <strong>تاريخ الاستخراج:</strong> {{ site.extraction_date }}
            </div>
            <div>
                <a href="/site/{{ site.id }}" class="btn">عرض الفهرس</a>
                <a href="/site/{{ site.id }}/pages" class="btn btn-success">تصفح الصفحات</a>
                <a href="/site/{{ site.id }}/assets" class="btn btn-info">عرض الملفات</a>
            </div>
        </div>
        {% endfor %}
        
        {% if not sites %}
        <div style="text-align: center; color: #666; padding: 50px;">
            <h3>لا توجد مواقع مستخرجة حالياً</h3>
            <p>استخدم أداة الاستخراج لاستخراج موقع جديد</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """عرض قائمة المواقع المستخرجة"""
    sites = []
    
    if EXTRACTED_SITES_PATH.exists():
        for site_dir in EXTRACTED_SITES_PATH.iterdir():
            if site_dir.is_dir():
                # قراءة تقرير الاستخراج
                report_file = site_dir / "extraction_report.json"
                if report_file.exists():
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report = json.load(f)
                        
                        sites.append({
                            'id': site_dir.name,
                            'name': report.get('url', site_dir.name),
                            'original_url': report.get('url', 'غير معروف'),
                            'pages_count': len(report.get('pages', [])),
                            'extraction_date': report.get('start_time', 'غير معروف')
                        })
                    except:
                        sites.append({
                            'id': site_dir.name,
                            'name': site_dir.name,
                            'original_url': 'غير معروف',
                            'pages_count': 'غير معروف',
                            'extraction_date': 'غير معروف'
                        })
    
    return render_template_string(SITE_LIST_TEMPLATE, sites=sites)

@app.route('/site/<site_id>')
def view_site_index(site_id):
    """عرض فهرس الموقع"""
    site_path = EXTRACTED_SITES_PATH / site_id
    index_file = site_path / "index.html"
    
    if index_file.exists():
        return send_from_directory(str(site_path), "index.html")
    else:
        return f"<h1>موقع غير موجود: {site_id}</h1>", 404

@app.route('/site/<site_id>/<path:filename>')
def serve_site_file(site_id, filename):
    """تقديم ملفات الموقع"""
    site_path = EXTRACTED_SITES_PATH / site_id
    return send_from_directory(str(site_path), filename)

@app.route('/site/<site_id>/pages')
def list_pages(site_id):
    """عرض قائمة صفحات الموقع"""
    site_path = EXTRACTED_SITES_PATH / site_id
    pages_path = site_path / "pages"
    
    pages = []
    if pages_path.exists():
        for page_file in pages_path.glob("*.html"):
            pages.append({
                'name': page_file.name,
                'url': f'/site/{site_id}/pages/{page_file.name}'
            })
    
    pages_html = f"""
    <h1>صفحات الموقع: {site_id}</h1>
    <ul>
    """
    
    for page in pages:
        pages_html += f'<li><a href="{page["url"]}" target="_blank">{page["name"]}</a></li>'
    
    pages_html += "</ul>"
    return pages_html

if __name__ == '__main__':
    print("🚀 بدء تشغيل عارض المواقع المستخرجة...")
    print("🔗 افتح المتصفح وانتقل إلى: http://localhost:8082")
    app.run(host='0.0.0.0', port=8082, debug=True)