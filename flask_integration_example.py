#!/usr/bin/env python3
"""
مثال على دمج أداة Website Cloner Pro مع Flask
"""

from flask import Flask, request, jsonify, render_template_string
import asyncio
import threading
from website_cloner_pro import create_cloner_instance
import os
import json

app = Flask(__name__)

# HTML Template لواجهة بسيطة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أداة نسخ المواقع</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="url"], input[type="number"], select { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 5px;
            font-size: 16px;
        }
        button { 
            background: #007bff; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
        .result { 
            margin-top: 20px; 
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .loading { 
            color: #007bff; 
            font-style: italic; 
        }
        .success { 
            color: #28a745; 
            font-weight: bold; 
        }
        .error { 
            color: #dc3545; 
            font-weight: bold; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 أداة نسخ المواقع الاحترافية</h1>
        <p>أدخل رابط الموقع المراد نسخه وتحليله</p>
        
        <form id="cloneForm">
            <div class="form-group">
                <label for="url">رابط الموقع:</label>
                <input type="url" id="url" name="url" placeholder="https://example.com" required>
            </div>
            
            <div class="form-group">
                <label for="max_pages">عدد الصفحات القصوى:</label>
                <input type="number" id="max_pages" name="max_pages" value="10" min="1" max="100">
            </div>
            
            <div class="form-group">
                <label for="max_depth">عمق الاستخراج:</label>
                <select id="max_depth" name="max_depth">
                    <option value="1">سطحي (1 مستوى)</option>
                    <option value="2" selected>متوسط (2 مستوى)</option>
                    <option value="3">عميق (3 مستوى)</option>
                </select>
            </div>
            
            <button type="submit">🚀 بدء النسخ والتحليل</button>
        </form>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('cloneForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading">⏳ جاري معالجة الموقع... قد يستغرق الأمر بضع دقائق</div>';
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/clone', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div class="success">✅ تم نسخ الموقع بنجاح!</div>
                        <strong>📁 مجلد النتائج:</strong> ${result.output_path}
                        <strong>📊 الصفحات المستخرجة:</strong> ${result.pages_extracted}
                        <strong>🎯 الأصول المحملة:</strong> ${result.assets_downloaded}
                        <strong>⏱️ المدة:</strong> ${result.duration} ثانية
                        <strong>💾 الحجم:</strong> ${result.total_size} بايت
                        
                        ${result.technologies_detected ? '<strong>🔧 التقنيات المكتشفة:</strong> ' + result.technologies_detected.length + ' تقنية' : ''}
                        ${result.recommendations ? '<strong>💡 التوصيات:</strong> ' + result.recommendations.length + ' توصية' : ''}
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="error">❌ فشل في نسخ الموقع</div>
                        <strong>الأخطاء:</strong>
                        ${result.errors.map(error => `- ${error}`).join('\\n')}
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ خطأ في الاتصال: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
"""

def run_cloning_task(config_data):
    """تشغيل مهمة النسخ في thread منفصل"""
    async def clone_task():
        try:
            cloner = create_cloner_instance(
                target_url=config_data['url'],
                max_pages=int(config_data.get('max_pages', 10)),
                max_depth=int(config_data.get('max_depth', 2)),
                extract_all_content=True,
                analyze_with_ai=True,
                generate_reports=True
            )
            
            result = await cloner.clone_website()
            return result
            
        except Exception as e:
            # إنشاء نتيجة خطأ
            from website_cloner_pro import ExtractionResult
            error_result = ExtractionResult()
            error_result.success = False
            error_result.error_log = [str(e)]
            return error_result
    
    # تشغيل العملية غير المتزامنة
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(clone_task())
    loop.close()
    return result

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/clone', methods=['POST'])
def clone_website():
    """API endpoint لنسخ الموقع"""
    try:
        data = request.get_json()
        
        if not data or not data.get('url'):
            return jsonify({
                'success': False,
                'error': 'رابط الموقع مطلوب'
            }), 400
        
        # تشغيل النسخ في thread منفصل لتجنب blocking
        result = run_cloning_task(data)
        
        if result.success:
            return jsonify({
                'success': True,
                'output_path': result.output_path,
                'pages_extracted': result.pages_extracted,
                'assets_downloaded': result.assets_downloaded,
                'duration': f"{result.duration:.2f}",
                'total_size': f"{result.total_size:,}",
                'technologies_detected': result.technologies_detected,
                'recommendations': result.recommendations
            })
        else:
            return jsonify({
                'success': False,
                'errors': result.error_log
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """فحص حالة الخدمة"""
    return jsonify({
        'status': 'healthy',
        'service': 'Website Cloner Pro',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🌐 تشغيل خادم نسخ المواقع...")
    print("📱 الواجهة متاحة على: http://localhost:5000")
    print("🔗 API متاح على: http://localhost:5000/clone")
    app.run(host='0.0.0.0', port=5000, debug=True)