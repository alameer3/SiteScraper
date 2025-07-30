#!/usr/bin/env python3
"""
أداة استخراج مواقع بسيطة وموثوقة
Simple and Reliable Website Extractor
"""

import os
import json
import csv
import time
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import traceback

# تحديد مجلد الإخراج الموحد
OUTPUT_DIR = Path("11")
OUTPUT_DIR.mkdir(exist_ok=True)

class SimpleWebsiteExtractor:
    """أداة استخراج مواقع بسيطة وفعالة"""
    
    def __init__(self, output_dir="11"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = self._create_session()
        
    def _create_session(self):
        """إنشاء جلسة HTTP محسنة"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session
    
    def extract_website(self, url, extraction_type="basic"):
        """استخراج موقع كامل"""
        print(f"🚀 بدء استخراج الموقع: {url}")
        
        # إنشاء مجلد للاستخراج
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = urlparse(url).netloc.replace('.', '_')
        extraction_folder = self.output_dir / f"{domain}_{timestamp}"
        extraction_folder.mkdir(exist_ok=True)
        
        results = {
            'url': url,
            'extraction_type': extraction_type,
            'timestamp': timestamp,
            'extraction_folder': str(extraction_folder),
            'success': False,
            'error': None,
            'data': {}
        }
        
        try:
            # جلب الصفحة الرئيسية
            print(f"📡 جلب الصفحة الرئيسية...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # تحليل HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج المعلومات الأساسية
            basic_info = self._extract_basic_info(soup, url, response)
            results['data']['basic_info'] = basic_info
            
            # حفظ HTML الأصلي
            html_file = extraction_folder / 'index.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 تم حفظ HTML: {html_file}")
            
            # استخراج الروابط
            links = self._extract_links(soup, url)
            results['data']['links'] = links
            
            # استخراج الصور إذا طُلب ذلك
            if extraction_type in ['standard', 'advanced', 'complete']:
                images = self._extract_images(soup, url)
                results['data']['images'] = images
                
                # تحميل الصور
                images_folder = extraction_folder / 'images'
                images_folder.mkdir(exist_ok=True)
                downloaded_images = self._download_images(images, images_folder)
                results['data']['downloaded_images'] = downloaded_images
            
            # استخراج CSS و JS إذا طُلب ذلك
            if extraction_type in ['advanced', 'complete']:
                css_links = self._extract_css_links(soup, url)
                js_links = self._extract_js_links(soup, url)
                
                results['data']['css_links'] = css_links
                results['data']['js_links'] = js_links
                
                # تحميل الملفات
                assets_folder = extraction_folder / 'assets'
                assets_folder.mkdir(exist_ok=True)
                
                downloaded_css = self._download_assets(css_links, assets_folder / 'css')
                downloaded_js = self._download_assets(js_links, assets_folder / 'js')
                
                results['data']['downloaded_css'] = downloaded_css
                results['data']['downloaded_js'] = downloaded_js
            
            # حفظ النتائج بصيغة JSON
            json_file = extraction_folder / 'extraction_results.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results['data'], f, ensure_ascii=False, indent=2)
            
            # إنشاء تقرير HTML
            report_file = extraction_folder / 'report.html'
            self._create_html_report(results['data'], report_file)
            
            # إنشاء ملف CSV للروابط
            csv_file = extraction_folder / 'links.csv'
            self._create_csv_report(links, csv_file)
            
            results['success'] = True
            print(f"✅ تم الاستخراج بنجاح في: {extraction_folder}")
            
        except Exception as e:
            results['error'] = str(e)
            print(f"❌ خطأ في الاستخراج: {e}")
            
        return results
    
    def _extract_basic_info(self, soup, url, response):
        """استخراج المعلومات الأساسية"""
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "بدون عنوان"
        
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag.get('content', '') if description_tag else ''
        
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_tag.get('content', '') if keywords_tag else ''
        
        return {
            'title': title_text,
            'description': description,
            'keywords': keywords,
            'url': url,
            'status_code': response.status_code,
            'content_length': len(response.text),
            'headers': dict(response.headers),
            'extraction_time': datetime.now().isoformat()
        }
    
    def _extract_links(self, soup, base_url):
        """استخراج جميع الروابط"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            text = link.get_text().strip()
            
            links.append({
                'href': href,
                'absolute_url': absolute_url,
                'text': text,
                'is_internal': urlparse(absolute_url).netloc == urlparse(base_url).netloc
            })
        
        return links
    
    def _extract_images(self, soup, base_url):
        """استخراج جميع الصور"""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            alt = img.get('alt', '')
            
            images.append({
                'src': src,
                'absolute_url': absolute_url,
                'alt': alt
            })
        
        return images
    
    def _extract_css_links(self, soup, base_url):
        """استخراج روابط CSS"""
        css_links = []
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                css_links.append(absolute_url)
        
        return css_links
    
    def _extract_js_links(self, soup, base_url):
        """استخراج روابط JavaScript"""
        js_links = []
        
        for script in soup.find_all('script', src=True):
            src = script['src']
            absolute_url = urljoin(base_url, src)
            js_links.append(absolute_url)
        
        return js_links
    
    def _download_images(self, images, images_folder):
        """تحميل الصور"""
        images_folder.mkdir(exist_ok=True)
        downloaded = []
        
        for img in images[:10]:  # تحديد العدد لتجنب الإفراط
            try:
                response = self.session.get(img['absolute_url'], timeout=10)
                if response.status_code == 200:
                    filename = Path(img['absolute_url']).name or 'image.jpg'
                    file_path = images_folder / filename
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded.append({
                        'url': img['absolute_url'],
                        'file_path': str(file_path),
                        'size': len(response.content)
                    })
                    
            except Exception as e:
                print(f"فشل تحميل الصورة {img['absolute_url']}: {e}")
        
        return downloaded
    
    def _download_assets(self, urls, assets_folder):
        """تحميل ملفات CSS/JS"""
        assets_folder.mkdir(exist_ok=True, parents=True)
        downloaded = []
        
        for url in urls[:5]:  # تحديد العدد
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    filename = Path(url).name or 'asset.txt'
                    file_path = assets_folder / filename
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded.append({
                        'url': url,
                        'file_path': str(file_path),
                        'size': len(response.content)
                    })
                    
            except Exception as e:
                print(f"فشل تحميل الملف {url}: {e}")
        
        return downloaded
    
    def _create_html_report(self, data, report_file):
        """إنشاء تقرير HTML"""
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير استخراج الموقع</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }}
        .info {{ background: #f8f9fa; }}
        .links {{ background: #e9ecef; }}
        .images {{ background: #fff3cd; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; border: 1px solid #ddd; text-align: right; }}
        th {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>تقرير استخراج الموقع</h1>
    
    <div class="section info">
        <h2>المعلومات الأساسية</h2>
        <p><strong>العنوان:</strong> {data['basic_info'].get('title', 'غير محدد')}</p>
        <p><strong>الرابط:</strong> {data['basic_info'].get('url', 'غير محدد')}</p>
        <p><strong>الوصف:</strong> {data['basic_info'].get('description', 'غير محدد')}</p>
        <p><strong>حالة الاستجابة:</strong> {data['basic_info'].get('status_code', 'غير محدد')}</p>
        <p><strong>حجم المحتوى:</strong> {data['basic_info'].get('content_length', 0)} حرف</p>
    </div>
    
    <div class="section links">
        <h2>الروابط المستخرجة ({len(data.get('links', []))} رابط)</h2>
        <table>
            <tr><th>النص</th><th>الرابط</th><th>نوع الرابط</th></tr>
            {"".join(f"<tr><td>{link.get('text', '')[:50]}</td><td>{link.get('absolute_url', '')}</td><td>{'داخلي' if link.get('is_internal') else 'خارجي'}</td></tr>" for link in data.get('links', [])[:20])}
        </table>
    </div>
    
    {"<div class='section images'><h2>الصور المستخرجة (" + str(len(data.get('images', []))) + " صورة)</h2></div>" if 'images' in data else ""}
    
    <div class="section">
        <p><strong>تاريخ الاستخراج:</strong> {data['basic_info'].get('extraction_time', 'غير محدد')}</p>
    </div>
</body>
</html>
        """
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_csv_report(self, links, csv_file):
        """إنشاء تقرير CSV للروابط"""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'href', 'absolute_url', 'is_internal'])
            writer.writeheader()
            writer.writerows(links)

def main():
    """الوظيفة الرئيسية للاختبار"""
    extractor = SimpleWebsiteExtractor()
    
    # اختبار مواقع مختلفة
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    for url in test_urls:
        print(f"\n{'='*50}")
        print(f"اختبار الموقع: {url}")
        print('='*50)
        
        try:
            result = extractor.extract_website(url, "standard")
            
            if result['success']:
                print(f"✅ نجح الاستخراج")
                print(f"📁 مجلد النتائج: {result['extraction_folder']}")
                print(f"📄 العنوان: {result['data']['basic_info']['title']}")
                print(f"🔗 عدد الروابط: {len(result['data']['links'])}")
                if 'images' in result['data']:
                    print(f"🖼️ عدد الصور: {len(result['data']['images'])}")
            else:
                print(f"❌ فشل الاستخراج: {result['error']}")
                
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()