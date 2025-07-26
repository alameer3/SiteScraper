#!/usr/bin/env python3
"""
أداة استخراج المواقع العاملة - بدون مكتبات خارجية معقدة
"""
import os
import sys
import json
import time
import threading
from datetime import datetime
from urllib.parse import urlparse, urljoin
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import ssl
import re

# استيراد منظم الملفات
try:
    from file_organizer import file_organizer
except ImportError:
    file_organizer = None

class WebsiteExtractor:
    """مستخرج المواقع البسيط"""
    
    def __init__(self):
        self.results = {}
        self.extraction_id = 0
    
    def extract_website(self, url, extraction_type='basic'):
        """استخراج أساسي للموقع مع حفظ منظم"""
        self.extraction_id += 1
        extraction_id = self.extraction_id
        
        start_time = time.time()
        
        # إنشاء مجلد الاستخراج
        extraction_folder = None
        if file_organizer:
            try:
                extraction_folder = file_organizer.create_extraction_folder('websites', url, extraction_id)
            except Exception as e:
                print(f"تحذير: فشل في إنشاء مجلد منظم: {e}")
        
        try:
            # إعداد SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # تحضير الطلب
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            
            # تحميل الصفحة
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                status_code = response.getcode()
                content_type = response.getheader('Content-Type', '')
            
            # تحليل بسيط للمحتوى
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else 'No title'
            
            # عد العناصر
            links = len(re.findall(r'<a[^>]+href', content, re.IGNORECASE))
            images = len(re.findall(r'<img[^>]+src', content, re.IGNORECASE))
            scripts = len(re.findall(r'<script', content, re.IGNORECASE))
            stylesheets = len(re.findall(r'<link[^>]+stylesheet', content, re.IGNORECASE))
            
            # اكتشاف التقنيات
            technologies = []
            if 'react' in content.lower():
                technologies.append('React')
            if 'vue' in content.lower():
                technologies.append('Vue.js')
            if 'angular' in content.lower():
                technologies.append('Angular')
            if 'jquery' in content.lower():
                technologies.append('jQuery')
            if 'bootstrap' in content.lower():
                technologies.append('Bootstrap')
            
            duration = time.time() - start_time
            
            result = {
                'extraction_id': extraction_id,
                'url': url,
                'extraction_type': extraction_type,
                'success': True,
                'status_code': status_code,
                'content_type': content_type,
                'title': title,
                'content_length': len(content),
                'links_found': links,
                'images_found': images,
                'scripts_found': scripts,
                'stylesheets_found': stylesheets,
                'technologies_detected': technologies,
                'duration': round(duration, 2),
                'timestamp': datetime.now().isoformat(),
                'domain': urlparse(url).netloc
            }
            
            # حفظ الملفات في النظام المنظم
            if extraction_folder and file_organizer:
                try:
                    # حفظ المحتوى الأساسي
                    file_organizer.save_content(extraction_folder, 'html', content, 'index.html')
                    
                    # حفظ النتائج
                    file_organizer.save_content(extraction_folder, 'analysis', result, 'extraction_results.json')
                    
                    # حفظ قائمة التقنيات
                    if technologies:
                        file_organizer.save_content(extraction_folder, 'analysis', {'technologies': technologies}, 'technologies_detected.json')
                    
                    # إنهاء عملية الاستخراج
                    file_organizer.finalize_extraction(extraction_folder, result)
                    
                    # إضافة مسار المجلد للنتيجة
                    result['extraction_folder'] = str(extraction_folder)
                    
                except Exception as e:
                    print(f"تحذير: فشل في حفظ الملفات: {e}")
            
            # حفظ النتيجة
            self.results[extraction_id] = result
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_result = {
                'extraction_id': extraction_id,
                'url': url,
                'extraction_type': extraction_type,
                'success': False,
                'error': str(e),
                'duration': round(duration, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results[extraction_id] = error_result
            return error_result
    
    def get_results(self):
        """الحصول على جميع النتائج"""
        return list(self.results.values())
    
    def get_result(self, extraction_id):
        """الحصول على نتيجة محددة"""
        return self.results.get(extraction_id)

class ExtractorHTTPHandler(BaseHTTPRequestHandler):
    """معالج HTTP للخادم"""
    
    extractor = WebsiteExtractor()
    
    def do_GET(self):
        """معالجة طلبات GET"""
        if self.path == '/':
            self.serve_index()
        elif self.path == '/advanced-tools':
            self.serve_advanced_tools()
        elif self.path == '/health':
            self.serve_health()
        elif self.path == '/results':
            self.serve_results()
        elif self.path.startswith('/result/'):
            result_id = int(self.path.split('/')[-1])
            self.serve_result(result_id)
        else:
            self.send_error(404)
    
    def do_POST(self):
        """معالجة طلبات POST"""
        if self.path == '/api/extract':
            self.handle_extract_api()
        else:
            self.send_error(404)
    
    def serve_index(self):
        """صفحة الرئيسية"""
        html = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>أداة استخراج المواقع</title>
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container { max-width: 800px; margin: 0 auto; }
                .card { 
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                    backdrop-filter: blur(10px);
                }
                h1 { color: #333; text-align: center; margin-bottom: 30px; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, select { 
                    width: 100%; 
                    padding: 12px; 
                    border: 1px solid #ddd; 
                    border-radius: 8px;
                    font-size: 16px;
                }
                button { 
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white; 
                    padding: 12px 30px; 
                    border: none; 
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    width: 100%;
                }
                button:hover { opacity: 0.9; }
                .result { 
                    margin-top: 20px; 
                    padding: 15px; 
                    border-radius: 8px;
                    display: none;
                }
                .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
                .loading { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
                .nav { text-align: center; margin-bottom: 20px; }
                .nav a { 
                    color: white; 
                    text-decoration: none; 
                    margin: 0 15px; 
                    padding: 8px 15px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">الرئيسية</a>
                    <a href="/results">النتائج</a>
                    <a href="/health">الحالة</a>
                </div>
                
                <div class="card">
                    <h1>🌐 أداة استخراج المواقع المتقدمة</h1>
                    
                    <form id="extractForm">
                        <div class="form-group">
                            <label for="url">رابط الموقع:</label>
                            <input type="url" id="url" required placeholder="https://example.com">
                        </div>
                        
                        <div class="form-group">
                            <label for="extraction_type">نوع الاستخراج:</label>
                            <select id="extraction_type">
                                <option value="basic">أساسي - سريع</option>
                                <option value="advanced">متقدم - تفصيلي</option>
                                <option value="complete">شامل - كامل</option>
                            </select>
                        </div>
                        
                        <button type="submit">🚀 بدء الاستخراج</button>
                    </form>
                    
                    <div id="result" class="result"></div>
                </div>
            </div>
            
            <script>
            document.getElementById('extractForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const url = document.getElementById('url').value;
                const type = document.getElementById('extraction_type').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.className = 'result loading';
                resultDiv.innerHTML = '⏳ جاري الاستخراج...';
                resultDiv.style.display = 'block';
                
                fetch('/api/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, extraction_type: type })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>✅ تم الاستخراج بنجاح!</h3>
                            <p><strong>العنوان:</strong> ${data.title}</p>
                            <p><strong>المجال:</strong> ${data.domain}</p>
                            <p><strong>الروابط:</strong> ${data.links_found}</p>
                            <p><strong>الصور:</strong> ${data.images_found}</p>
                            <p><strong>التقنيات:</strong> ${data.technologies_detected.join(', ') || 'غير محدد'}</p>
                            <p><strong>المدة:</strong> ${data.duration} ثانية</p>
                            <p><strong>ID:</strong> <a href="/result/${data.extraction_id}">${data.extraction_id}</a></p>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `❌ خطأ: ${data.error}`;
                    }
                })
                .catch(error => {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `❌ خطأ في الاتصال: ${error.message}`;
                });
            });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_health(self):
        """صحة النظام"""
        health_data = {
            'status': 'healthy',
            'app': 'website-extractor',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'total_extractions': len(self.extractor.results)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health_data, ensure_ascii=False).encode('utf-8'))
    
    def serve_results(self):
        """قائمة النتائج"""
        results = self.extractor.get_results()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>النتائج</title>
            <style>
                body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                table {{ width: 100%; border-collapse: collapse; background: white; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; }}
                th {{ background: #667eea; color: white; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                a {{ color: #667eea; text-decoration: none; }}
                .nav {{ margin-bottom: 20px; }}
                .nav a {{ margin: 0 10px; padding: 8px 15px; background: #667eea; color: white; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">الرئيسية</a>
                    <a href="/results">النتائج</a>
                    <a href="/health">الحالة</a>
                </div>
                
                <h1>📊 سجل الاستخراجات ({len(results)})</h1>
                
                <table>
                    <tr>
                        <th>ID</th>
                        <th>الرابط</th>
                        <th>النوع</th>
                        <th>الحالة</th>
                        <th>العنوان</th>
                        <th>المدة</th>
                        <th>التاريخ</th>
                    </tr>
        """
        
        for result in reversed(results):
            status_class = 'success' if result['success'] else 'error'
            status_text = 'نجح' if result['success'] else 'فشل'
            title = result.get('title', 'خطأ')[:50]
            
            html += f"""
                    <tr>
                        <td><a href="/result/{result['extraction_id']}">{result['extraction_id']}</a></td>
                        <td>{result['url'][:50]}...</td>
                        <td>{result['extraction_type']}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{title}</td>
                        <td>{result['duration']}s</td>
                        <td>{result['timestamp'][:19]}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_result(self, result_id):
        """تفاصيل نتيجة محددة"""
        result = self.extractor.get_result(result_id)
        
        if not result:
            self.send_error(404)
            return
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تفاصيل النتيجة {result_id}</title>
            <style>
                body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .nav {{ margin-bottom: 20px; }}
                .nav a {{ margin: 0 10px; padding: 8px 15px; background: #667eea; color: white; border-radius: 5px; text-decoration: none; }}
                .field {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #333; }}
                .value {{ color: #666; }}
                pre {{ background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">الرئيسية</a>
                    <a href="/results">النتائج</a>
                    <a href="/health">الحالة</a>
                </div>
                
                <h1>📋 تفاصيل الاستخراج #{result_id}</h1>
                
                <div class="field">
                    <span class="label">الرابط:</span>
                    <span class="value">{result['url']}</span>
                </div>
                
                <div class="field">
                    <span class="label">النوع:</span>
                    <span class="value">{result['extraction_type']}</span>
                </div>
                
                <div class="field">
                    <span class="label">الحالة:</span>
                    <span class="value">{'نجح' if result['success'] else 'فشل'}</span>
                </div>
                
                <h3>📊 البيانات الكاملة:</h3>
                <pre>{json.dumps(result, ensure_ascii=False, indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_extract_api(self):
        """معالجة API الاستخراج"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            url = data.get('url')
            extraction_type = data.get('extraction_type', 'basic')
            
            if not url:
                self.send_error(400, 'URL required')
                return
            
            # تشغيل الاستخراج في thread منفصل للحصول على استجابة سريعة
            result = self.extractor.extract_website(url, extraction_type)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """تسجيل الرسائل"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def main():
    """تشغيل الخادم"""
    port = 5000
    server_address = ('0.0.0.0', port)
    
    try:
        httpd = HTTPServer(server_address, ExtractorHTTPHandler)
        print(f"🚀 تشغيل أداة استخراج المواقع على المنفذ {port}")
        print(f"🌐 الرابط: http://localhost:{port}")
        print(f"💡 استخدم Ctrl+C للإيقاف")
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")

if __name__ == '__main__':
    main()