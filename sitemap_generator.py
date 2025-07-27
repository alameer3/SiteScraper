#!/usr/bin/env python3
"""
مولد خرائط المواقع (Sitemap Generator)
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Optional, Any
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

class SitemapGenerator:
    """مولد خرائط المواقع التلقائي"""
    
    def __init__(self, max_depth: int = 3, max_pages: int = 100):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SitemapBot/1.0)'
        })
        self.visited_urls: Set[str] = set()
        self.found_urls: List[Dict[str, Any]] = []
        self.base_domain = ""
        
    def generate_sitemap(self, start_url: str, output_dir: Path) -> Dict[str, Any]:
        """إنشاء خريطة موقع شاملة"""
        
        self.base_domain = urlparse(start_url).netloc
        
        results = {
            'start_url': start_url,
            'total_pages_found': 0,
            'pages_crawled': 0,
            'max_depth_reached': 0,
            'sitemap_files': [],
            'errors': [],
            'crawl_duration': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # بدء الزحف
            self._crawl_website(start_url, 0)
            
            # إنشاء ملفات Sitemap
            sitemap_files = self._create_sitemap_files(output_dir)
            results['sitemap_files'] = sitemap_files
            
            # إنشاء تقرير HTML
            html_report = self._create_html_sitemap(output_dir)
            results['html_report'] = html_report
            
            # احصائيات نهائية
            results['total_pages_found'] = len(self.found_urls)
            results['pages_crawled'] = len(self.visited_urls)
            results['max_depth_reached'] = max([url['depth'] for url in self.found_urls] + [0])
            results['crawl_duration'] = round(time.time() - start_time, 2)
            
        except Exception as e:
            results['errors'].append(str(e))
        
        return results
    
    def _crawl_website(self, url: str, depth: int) -> None:
        """زحف موقع الويب بعمق محدد"""
        
        if (depth > self.max_depth or 
            len(self.visited_urls) >= self.max_pages or 
            url in self.visited_urls):
            return
        
        try:
            # تحميل الصفحة
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            
            # تحليل الصفحة
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # حفظ معلومات الصفحة
            page_info = {
                'url': url,
                'title': self._get_page_title(soup),
                'depth': depth,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'last_modified': response.headers.get('last-modified', ''),
                'content_length': len(response.content),
                'meta_description': self._get_meta_description(soup),
                'h1_tags': [h1.get_text().strip() for h1 in soup.find_all('h1')],
                'images_count': len(soup.find_all('img')),
                'links_count': len(soup.find_all('a')),
                'discovery_time': datetime.now().isoformat()
            }
            
            self.found_urls.append(page_info)
            
            # البحث عن روابط جديدة
            if depth < self.max_depth:
                links = self._extract_links(soup, url)
                for link in links[:20]:  # حد أقصى 20 رابط لكل صفحة
                    if self._should_crawl_url(link):
                        time.sleep(0.5)  # تأخير مهذب
                        self._crawl_website(link, depth + 1)
                        
        except Exception as e:
            self.found_urls.append({
                'url': url,
                'depth': depth,
                'error': str(e),
                'discovery_time': datetime.now().isoformat()
            })
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """استخراج الروابط من الصفحة"""
        
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # تنظيف الرابط
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin(base_url, href)
            
            # إزالة fragments
            if '#' in full_url:
                full_url = full_url.split('#')[0]
            
            # إزالة query parameters غير المهمة
            if '?' in full_url:
                url_parts = full_url.split('?')
                query = url_parts[1]
                # الاحتفاظ بـ query parameters مهمة فقط
                if not any(param in query for param in ['p=', 'page=', 'id=']):
                    full_url = url_parts[0]
            
            if full_url and full_url not in links:
                links.append(full_url)
        
        return links
    
    def _should_crawl_url(self, url: str) -> bool:
        """تحديد ما إذا كان يجب زحف الرابط"""
        
        parsed_url = urlparse(url)
        
        # فقط نفس النطاق
        if parsed_url.netloc != self.base_domain:
            return False
        
        # تجاهل أنواع ملفات معينة
        excluded_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg',
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv',
            '.css', '.js', '.xml', '.txt'
        ]
        
        path = parsed_url.path.lower()
        if any(path.endswith(ext) for ext in excluded_extensions):
            return False
        
        # تجاهل مسارات إدارية
        excluded_paths = [
            '/admin', '/wp-admin', '/administrator',
            '/login', '/register', '/logout',
            '/api/', '/ajax/', '/cgi-bin/',
            '/error', '/404', '/403'
        ]
        
        if any(excluded_path in path for excluded_path in excluded_paths):
            return False
        
        return True
    
    def _get_page_title(self, soup: BeautifulSoup) -> str:
        """الحصول على عنوان الصفحة"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else 'بدون عنوان'
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """الحصول على وصف meta"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc and meta_desc.get('content') else ''
    
    def _create_sitemap_files(self, output_dir: Path) -> List[str]:
        """إنشاء ملفات Sitemap بصيغة XML"""
        
        sitemap_files = []
        
        # إنشاء sitemap.xml أساسي
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        for page in self.found_urls:
            if 'error' not in page:
                url_element = ET.SubElement(root, "url")
                
                loc = ET.SubElement(url_element, "loc")
                loc.text = page['url']
                
                lastmod = ET.SubElement(url_element, "lastmod")
                lastmod.text = datetime.now().strftime('%Y-%m-%d')
                
                changefreq = ET.SubElement(url_element, "changefreq")
                changefreq.text = self._determine_change_frequency(page)
                
                priority = ET.SubElement(url_element, "priority")
                priority.text = self._calculate_priority(page)
        
        # حفظ sitemap.xml
        tree = ET.ElementTree(root)
        sitemap_file = output_dir / 'sitemap.xml'
        tree.write(sitemap_file, encoding='utf-8', xml_declaration=True)
        sitemap_files.append(str(sitemap_file.name))
        
        # إنشاء sitemap مفصل بصيغة JSON
        detailed_sitemap = {
            'sitemap_info': {
                'generated_at': datetime.now().isoformat(),
                'base_url': f"https://{self.base_domain}",
                'total_pages': len([p for p in self.found_urls if 'error' not in p]),
                'max_depth': max([p['depth'] for p in self.found_urls] + [0]),
                'crawl_summary': self._generate_crawl_summary()
            },
            'pages': self.found_urls
        }
        
        detailed_file = output_dir / 'detailed_sitemap.json'
        import json
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_sitemap, f, ensure_ascii=False, indent=2)
        sitemap_files.append(str(detailed_file.name))
        
        return sitemap_files
    
    def _create_html_sitemap(self, output_dir: Path) -> str:
        """إنشاء خريطة موقع HTML للعرض"""
        
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خريطة الموقع - {self.base_domain}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            direction: rtl;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat {{
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        .pages-list {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
        }}
        .page-item {{
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }}
        .page-item:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(-5px);
        }}
        .page-url {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .page-title {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .page-meta {{
            font-size: 12px;
            opacity: 0.7;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .depth-0 {{ border-left: 4px solid #4CAF50; }}
        .depth-1 {{ border-left: 4px solid #2196F3; }}
        .depth-2 {{ border-left: 4px solid #FF9800; }}
        .depth-3 {{ border-left: 4px solid #F44336; }}
        .error {{ border-left: 4px solid #f44336; background: rgba(244,67,54,0.2); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ خريطة الموقع</h1>
            <h2>{self.base_domain}</h2>
            <p>تم الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len([p for p in self.found_urls if 'error' not in p])}</div>
                <div class="stat-label">صفحة مكتشفة</div>
            </div>
            <div class="stat">
                <div class="stat-number">{max([p['depth'] for p in self.found_urls] + [0])}</div>
                <div class="stat-label">أقصى عمق</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len([p for p in self.found_urls if 'error' in p])}</div>
                <div class="stat-label">أخطاء</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(self.visited_urls)}</div>
                <div class="stat-label">صفحة تم زحفها</div>
            </div>
        </div>
        
        <div class="pages-list">
            <h3>📄 قائمة الصفحات</h3>
            {''.join([self._format_page_item(page) for page in sorted(self.found_urls, key=lambda x: x['depth'])])}
        </div>
    </div>
</body>
</html>
        """
        
        html_file = output_dir / 'sitemap.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_file.name)
    
    def _format_page_item(self, page: Dict[str, Any]) -> str:
        """تنسيق عنصر صفحة في HTML"""
        
        if 'error' in page:
            return f"""
            <div class="page-item error">
                <div class="page-url">❌ {page['url']}</div>
                <div class="page-meta">
                    <span>العمق: {page['depth']}</span>
                    <span>خطأ: {page['error']}</span>
                </div>
            </div>
            """
        
        depth_class = f"depth-{min(page['depth'], 3)}"
        
        return f"""
        <div class="page-item {depth_class}">
            <div class="page-url">🔗 <a href="{page['url']}" target="_blank" style="color: inherit; text-decoration: none;">{page['url']}</a></div>
            <div class="page-title">📝 {page.get('title', 'بدون عنوان')}</div>
            <div class="page-meta">
                <span>العمق: {page['depth']}</span>
                <span>الحالة: {page.get('status_code', 'غير معروف')}</span>
                <span>الصور: {page.get('images_count', 0)}</span>
                <span>الروابط: {page.get('links_count', 0)}</span>
                <span>الحجم: {page.get('content_length', 0)} بايت</span>
            </div>
        </div>
        """
    
    def _determine_change_frequency(self, page: Dict[str, Any]) -> str:
        """تحديد تكرار التغيير للصفحة"""
        url = page['url'].lower()
        
        if any(keyword in url for keyword in ['news', 'blog', 'article']):
            return 'daily'
        elif any(keyword in url for keyword in ['product', 'shop', 'store']):
            return 'weekly'
        elif page['depth'] == 0:  # الصفحة الرئيسية
            return 'daily'
        else:
            return 'monthly'
    
    def _calculate_priority(self, page: Dict[str, Any]) -> str:
        """حساب أولوية الصفحة"""
        if page['depth'] == 0:
            return '1.0'
        elif page['depth'] == 1:
            return '0.8'
        elif page['depth'] == 2:
            return '0.6'
        else:
            return '0.4'
    
    def _generate_crawl_summary(self) -> Dict[str, Any]:
        """إنشاء ملخص الزحف"""
        
        pages_by_depth = {}
        content_types = {}
        errors = []
        
        for page in self.found_urls:
            depth = page['depth']
            pages_by_depth[depth] = pages_by_depth.get(depth, 0) + 1
            
            if 'error' in page:
                errors.append(page['error'])
            else:
                content_type = page.get('content_type', '').split(';')[0]
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return {
            'pages_by_depth': pages_by_depth,
            'content_types': content_types,
            'total_errors': len(errors),
            'unique_errors': list(set(errors))
        }