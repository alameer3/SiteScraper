#!/usr/bin/env python3
"""
نظام لقطات الشاشة البسيط باستخدام requests و HTML
"""
import os
import time
import json
import base64
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from io import BytesIO

class SimpleScreenshotEngine:
    """محرك لقطات الشاشة البسيط"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def capture_html_preview(self, url: str, screenshots_dir: Path) -> dict:
        """إنشاء معاينة HTML بدلاً من screenshot حقيقي"""
        
        try:
            # تحميل الصفحة
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # إنشاء ملف HTML للمعاينة
            preview_file = screenshots_dir / 'html_preview.html'
            
            html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>معاينة الموقع - {url}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            direction: rtl;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .info {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        .preview-frame {{
            width: 100%;
            height: 600px;
            border: none;
            background: white;
        }}
        .devices {{
            display: flex;
            gap: 10px;
            padding: 20px;
            justify-content: center;
            background: #f8f9fa;
        }}
        .device {{
            text-align: center;
            flex: 1;
        }}
        .device iframe {{
            border: 2px solid #ddd;
            border-radius: 5px;
            width: 100%;
        }}
        .desktop {{
            height: 400px;
        }}
        .tablet {{
            height: 300px;
            max-width: 768px;
        }}
        .mobile {{
            height: 250px;
            max-width: 375px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖼️ معاينة موقع الويب</h1>
            <p>{url}</p>
            <div class="timestamp">تم الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="info">
            <p><strong>الحالة:</strong> {response.status_code}</p>
            <p><strong>نوع المحتوى:</strong> {response.headers.get('content-type', 'غير معروف')}</p>
            <p><strong>حجم الصفحة:</strong> {len(response.content)} بايت</p>
            <p><strong>الخادم:</strong> {response.headers.get('server', 'غير معروف')}</p>
        </div>
        
        <div class="devices">
            <div class="device">
                <h3>🖥️ سطح المكتب</h3>
                <iframe src="{url}" class="desktop"></iframe>
            </div>
            <div class="device">
                <h3>📱 جهاز لوحي</h3>
                <iframe src="{url}" class="tablet"></iframe>
            </div>
            <div class="device">
                <h3>📱 هاتف</h3>
                <iframe src="{url}" class="mobile"></iframe>
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            with open(preview_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # إنشاء تقرير تفصيلي
            report = {
                'url': url,
                'method': 'html_preview',
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type'),
                'content_size': len(response.content),
                'server': response.headers.get('server'),
                'preview_file': str(preview_file.name),
                'timestamp': datetime.now().isoformat(),
                'note': 'تم إنشاء معاينة HTML تفاعلية للموقع',
                'features': {
                    'responsive_preview': True,
                    'multiple_devices': True,
                    'interactive_frames': True,
                    'real_time_loading': True
                },
                'devices_supported': ['desktop', 'tablet', 'mobile']
            }
            
            return report
            
        except Exception as e:
            return {
                'error': str(e),
                'method': 'failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def create_website_thumbnail(self, url: str, content: str, screenshots_dir: Path) -> dict:
        """إنشاء thumbnail نصي للموقع"""
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # استخراج معلومات الموقع
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'بدون عنوان'
            
            # البحث عن الصور
            images = soup.find_all('img')
            image_info = []
            for img in images[:5]:  # أول 5 صور فقط
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    image_info.append({'src': src, 'alt': alt})
            
            # إنشاء thumbnail HTML
            thumbnail_file = screenshots_dir / 'website_thumbnail.html'
            
            thumbnail_html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>thumbnail - {title_text}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            direction: rtl;
        }}
        .thumbnail {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        .site-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }}
        .site-url {{
            font-size: 16px;
            opacity: 0.8;
            text-align: center;
            margin-bottom: 20px;
        }}
        .images-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .image-card {{
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }}
        .image-card img {{
            max-width: 100%;
            max-height: 80px;
            border-radius: 5px;
            object-fit: cover;
        }}
        .image-alt {{
            font-size: 12px;
            margin-top: 5px;
            opacity: 0.8;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat {{
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 20px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 12px;
            opacity: 0.8;
        }}
        .timestamp {{
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="thumbnail">
        <div class="site-title">{title_text}</div>
        <div class="site-url">{url}</div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(images)}</div>
                <div class="stat-label">صورة</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(soup.find_all('a'))}</div>
                <div class="stat-label">رابط</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(soup.find_all(['script']))}</div>
                <div class="stat-label">سكريبت</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(content)} حرف</div>
                <div class="stat-label">المحتوى</div>
            </div>
        </div>
        
        {f'''
        <div class="images-grid">
            {''.join([f'<div class="image-card"><img src="{img["src"]}" alt="صورة"><div class="image-alt">{img["alt"][:50]}</div></div>' for img in image_info])}
        </div>
        ''' if image_info else ''}
        
        <div class="timestamp">تم الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
</body>
</html>
            """
            
            with open(thumbnail_file, 'w', encoding='utf-8') as f:
                f.write(thumbnail_html)
            
            return {
                'thumbnail_file': str(thumbnail_file.name),
                'images_found': len(images),
                'title': title_text,
                'method': 'html_thumbnail'
            }
            
        except Exception as e:
            return {'error': str(e)}