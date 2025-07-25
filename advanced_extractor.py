"""
أداة الاستخراج المتقدمة - Advanced Website Extractor
استخراج المواقع بالكامل مع جميع الملفات والأصول
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
import time
import logging
import hashlib
import mimetypes
import json
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

class AdvancedExtractor:
    def __init__(self, base_url, output_dir="extracted_sites", max_depth=3, max_threads=5):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.max_threads = max_threads
        
        self.visited_urls = set()
        self.downloaded_files = set()
        self.stats = {
            'pages_downloaded': 0,
            'images_downloaded': 0,
            'css_files': 0,
            'js_files': 0,
            'other_files': 0,
            'total_size': 0,
            'errors': 0
        }
        
        # إعداد Session للطلبات
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # إنشاء مجلد الإخراج
        self.site_dir = self.output_dir / self._generate_site_id()
        self.site_dir.mkdir(parents=True, exist_ok=True)
        
        # مجلدات فرعية
        self.pages_dir = self.site_dir / "pages"
        self.assets_dir = self.site_dir / "assets"
        self.images_dir = self.assets_dir / "images"
        self.css_dir = self.assets_dir / "css"
        self.js_dir = self.assets_dir / "js"
        self.fonts_dir = self.assets_dir / "fonts"
        
        for dir_path in [self.pages_dir, self.images_dir, self.css_dir, self.js_dir, self.fonts_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _generate_site_id(self):
        """إنشاء معرف فريد للموقع"""
        site_hash = hashlib.md5(f"{self.base_url}_{time.time()}".encode()).hexdigest()[:12]
        return f"site_{site_hash}"

    def _get_safe_filename(self, url):
        """إنشاء اسم ملف آمن من الرابط"""
        parsed = urlparse(url)
        path = parsed.path
        
        if not path or path == '/':
            return 'index.html'
        
        # إزالة المعاملات
        path = path.split('?')[0]
        
        # تنظيف اسم الملف
        filename = unquote(path.split('/')[-1])
        if not filename:
            return 'index.html'
        
        # إضافة امتداد HTML إذا لم يكن موجود
        if not '.' in filename:
            filename += '.html'
        
        # تنظيف الأحرف غير الآمنة
        safe_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        filename = ''.join(c for c in filename if c in safe_chars)
        
        return filename[:100]  # تحديد طول الاسم

    def _download_file(self, url, file_path):
        """تحميل ملف من رابط"""
        try:
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = file_path.stat().st_size
            self.stats['total_size'] += file_size
            return True
            
        except Exception as e:
            logging.error(f"خطأ في تحميل {url}: {e}")
            self.stats['errors'] += 1
            return False

    def _process_html_content(self, html_content, base_url):
        """معالجة محتوى HTML وتحديث الروابط"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # معالجة الصور
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                img_url = urljoin(base_url, src)
                if self._is_same_domain(img_url):
                    local_path = self._download_asset(img_url, 'images')
                    if local_path:
                        img['src'] = f"../assets/images/{local_path.name}"

        # معالجة ملفات CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                css_url = urljoin(base_url, href)
                if self._is_same_domain(css_url):
                    local_path = self._download_asset(css_url, 'css')
                    if local_path:
                        link['href'] = f"../assets/css/{local_path.name}"

        # معالجة ملفات JavaScript
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                js_url = urljoin(base_url, src)
                if self._is_same_domain(js_url):
                    local_path = self._download_asset(js_url, 'js')
                    if local_path:
                        script['src'] = f"../assets/js/{local_path.name}"

        # معالجة الروابط الداخلية
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and not href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                full_url = urljoin(base_url, href)
                if self._is_same_domain(full_url):
                    filename = self._get_safe_filename(full_url)
                    a['href'] = filename

        return str(soup)

    def _download_asset(self, url, asset_type):
        """تحميل أصل معين (صورة، CSS، JS)"""
        if url in self.downloaded_files:
            return None
        
        try:
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1]
            
            if not filename:
                filename = f"asset_{len(self.downloaded_files)}"
            
            # تحديد الامتداد
            if not '.' in filename:
                content_type = self.session.head(url, timeout=5).headers.get('content-type', '')
                ext = mimetypes.guess_extension(content_type.split(';')[0])
                if ext:
                    filename += ext
            
            # مسار الملف المحلي
            if asset_type == 'images':
                local_path = self.images_dir / filename
            elif asset_type == 'css':
                local_path = self.css_dir / filename
            elif asset_type == 'js':
                local_path = self.js_dir / filename
            else:
                local_path = self.assets_dir / filename
            
            # تحميل الملف
            if self._download_file(url, local_path):
                self.downloaded_files.add(url)
                self.stats[f'{asset_type.rstrip("s")}_files' if asset_type.endswith('s') else f'{asset_type}_downloaded'] += 1
                return local_path
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الأصل {url}: {e}")
            self.stats['errors'] += 1
        
        return None

    def _is_same_domain(self, url):
        """فحص إذا كان الرابط من نفس النطاق"""
        try:
            return urlparse(url).netloc == self.domain
        except:
            return False

    def _extract_page(self, url, depth=0):
        """استخراج صفحة واحدة"""
        if url in self.visited_urls or depth > self.max_depth:
            return []
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            if 'text/html' not in response.headers.get('content-type', ''):
                return []
            
            # معالجة محتوى HTML
            processed_html = self._process_html_content(response.text, url)
            
            # حفظ الصفحة
            filename = self._get_safe_filename(url)
            page_path = self.pages_dir / filename
            
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(processed_html)
            
            self.stats['pages_downloaded'] += 1
            
            # استخراج الروابط للمستوى التالي
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href:
                    full_url = urljoin(url, href)
                    if self._is_same_domain(full_url) and full_url not in self.visited_urls:
                        links.append(full_url)
            
            return links[:10]  # حد أقصى 10 روابط لكل صفحة
            
        except Exception as e:
            logging.error(f"خطأ في استخراج {url}: {e}")
            self.stats['errors'] += 1
            return []

    def extract_complete_site(self):
        """استخراج الموقع بالكامل"""
        logging.info(f"بدء استخراج الموقع: {self.base_url}")
        
        # استخراج الصفحة الرئيسية
        urls_to_process = [self.base_url]
        
        for depth in range(self.max_depth + 1):
            if not urls_to_process:
                break
            
            logging.info(f"معالجة المستوى {depth}: {len(urls_to_process)} رابط")
            
            # معالجة متوازية للصفحات
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                future_to_url = {
                    executor.submit(self._extract_page, url, depth): url 
                    for url in urls_to_process
                }
                
                next_urls = []
                for future in as_completed(future_to_url):
                    try:
                        links = future.result()
                        next_urls.extend(links)
                    except Exception as e:
                        logging.error(f"خطأ في المعالجة المتوازية: {e}")
            
            urls_to_process = list(set(next_urls))
            time.sleep(0.5)  # تأخير بسيط
        
        # إنشاء ملف البداية
        self._create_start_file()
        
        # إنشاء تقرير الاستخراج
        self._create_extraction_report()
        
        logging.info(f"اكتمل الاستخراج: {self.stats}")
        return self.site_dir, self.stats

    def _create_start_file(self):
        """إنشاء ملف البداية للموقع المستخرج"""
        pages = list(self.pages_dir.glob("*.html"))
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الموقع المستخرج - {self.domain}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #ffd700;
        }}
        .pages-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .page-card {{
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }}
        .page-card:hover {{
            transform: translateY(-5px);
        }}
        .page-link {{
            color: #fff;
            text-decoration: none;
            font-weight: bold;
        }}
        .page-link:hover {{
            color: #ffd700;
        }}
        .launch-btn {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            border: none;
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
        }}
        .launch-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 الموقع المستخرج بنجاح</h1>
        <p style="text-align: center; font-size: 1.2rem; margin-bottom: 30px;">
            تم استخراج الموقع من: <strong>{self.base_url}</strong>
        </p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{self.stats['pages_downloaded']}</div>
                <div>صفحة</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['images_downloaded']}</div>
                <div>صورة</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['css_files']}</div>
                <div>ملف CSS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['js_files']}</div>
                <div>ملف JS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{round(self.stats['total_size']/1024/1024, 2)} MB</div>
                <div>الحجم الإجمالي</div>
            </div>
        </div>
        
        <div style="text-align: center; margin-bottom: 30px;">
            <button class="launch-btn" onclick="openMainPage()">
                🚀 فتح الصفحة الرئيسية
            </button>
            <button class="launch-btn" onclick="showAllPages()">
                📁 عرض جميع الصفحات
            </button>
        </div>
        
        <div class="pages-grid" id="pagesGrid">
"""
        
        # إضافة بطاقات الصفحات
        for i, page in enumerate(pages[:12]):  # أول 12 صفحة
            html_content += f"""
            <div class="page-card">
                <h3>📄 صفحة {i+1}</h3>
                <a href="pages/{page.name}" target="_blank" class="page-link">
                    {page.name}
                </a>
            </div>
"""
        
        html_content += """
        </div>
    </div>
    
    <script>
        function openMainPage() {
            window.open('pages/index.html', '_blank');
        }
        
        function showAllPages() {
            const pages = """ + json.dumps([p.name for p in pages]) + """;
            let pagesList = 'الصفحات المتوفرة:\\n\\n';
            pages.forEach((page, index) => {
                pagesList += `${index + 1}. ${page}\\n`;
            });
            alert(pagesList);
        }
    </script>
</body>
</html>
"""
        
        start_file = self.site_dir / "index.html"
        with open(start_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _create_extraction_report(self):
        """إنشاء تقرير تفصيلي عن الاستخراج"""
        report = {
            'site_info': {
                'url': self.base_url,
                'domain': self.domain,
                'extraction_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'output_directory': str(self.site_dir)
            },
            'statistics': self.stats,
            'files': {
                'pages': [p.name for p in self.pages_dir.glob("*.html")],
                'images': [i.name for i in self.images_dir.glob("*")],
                'css': [c.name for c in self.css_dir.glob("*")],
                'js': [j.name for j in self.js_dir.glob("*")]
            }
        }
        
        report_file = self.site_dir / "extraction_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

def extract_website_advanced(url, max_depth=2, max_threads=3):
    """دالة سهلة لاستخراج موقع متقدم"""
    extractor = AdvancedExtractor(url, max_depth=max_depth, max_threads=max_threads)
    return extractor.extract_complete_site()