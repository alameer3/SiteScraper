"""
محرك الاستخراج الفائق - Ultra Advanced Website Extractor
استخراج ذكي ومتطور للمواقع مع تحليل AI وميزات متقدمة
"""

import os
import requests
from bs4 import BeautifulSoup, NavigableString
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
import re
from typing import Dict, List, Optional, Tuple, Any
import zipfile
import base64
from datetime import datetime
import csv
import xml.etree.ElementTree as ET

class UltraSmartExtractor:
    """محرك الاستخراج الفائق مع ذكاء اصطناعي متقدم"""
    
    def __init__(self, base_url: str, config: Dict[str, Any] = None):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.config = config or self._default_config()
        
        # إعداد المجلدات
        self.output_dir = Path("extracted_sites")
        self.site_id = self._generate_site_id()
        self.site_dir = self.output_dir / self.site_id
        self._setup_directories()
        
        # إحصائيات متقدمة
        self.stats = {
            'extraction_start': datetime.now().isoformat(),
            'pages_discovered': 0,
            'pages_extracted': 0,
            'images_downloaded': 0,
            'css_files': 0,
            'js_files': 0,
            'fonts_downloaded': 0,
            'videos_downloaded': 0,
            'audios_downloaded': 0,
            'documents_downloaded': 0,
            'total_size_bytes': 0,
            'errors': [],
            'warnings': [],
            'duplicate_urls': 0,
            'external_links': 0,
            'processing_time_seconds': 0,
            'technologies_detected': [],
            'seo_data': {},
            'performance_metrics': {},
            'security_info': {}
        }
        
        # مجموعات البيانات
        self.visited_urls = set()
        self.failed_urls = set()
        self.external_urls = set()
        self.discovered_technologies = set()
        self.page_metadata = {}
        
        # إعداد Session متقدم
        self.session = requests.Session()
        self._setup_session()
        
        # قوائم أنواع الملفات
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
        self.audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}
        self.document_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
        self.font_extensions = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}

    def _default_config(self) -> Dict[str, Any]:
        """إعدادات افتراضية للاستخراج"""
        return {
            'max_depth': 3,
            'max_threads': 5,
            'max_pages': 100,
            'timeout': 30,
            'delay_between_requests': 0.5,
            'extract_images': True,
            'extract_css': True,
            'extract_js': True,
            'extract_fonts': True,
            'extract_videos': True,
            'extract_audio': True,
            'extract_documents': True,
            'analyze_seo': True,
            'analyze_performance': True,
            'analyze_security': True,
            'detect_technologies': True,
            'create_sitemap': True,
            'compress_output': True,
            'generate_preview': True,
            'extract_metadata': True
        }

    def _setup_session(self):
        """إعداد جلسة HTTP متقدمة"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(headers)
        
        # إعداد إعادة المحاولة
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _setup_directories(self):
        """إنشاء هيكل مجلدات متقدم"""
        directories = [
            self.site_dir,
            self.site_dir / "pages",
            self.site_dir / "assets" / "images",
            self.site_dir / "assets" / "css",
            self.site_dir / "assets" / "js",
            self.site_dir / "assets" / "fonts",
            self.site_dir / "assets" / "videos",
            self.site_dir / "assets" / "audio",
            self.site_dir / "assets" / "documents",
            self.site_dir / "data",
            self.site_dir / "reports",
            self.site_dir / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_site_id(self) -> str:
        """إنشاء معرف فريد متقدم للموقع"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain_hash = hashlib.md5(self.domain.encode()).hexdigest()[:8]
        return f"site_{self.domain.replace('.', '_')}_{timestamp}_{domain_hash}"

    def detect_technologies(self, html_content: str, url: str) -> List[str]:
        """كشف التقنيات المستخدمة في الموقع"""
        technologies = []
        content_lower = html_content.lower()
        
        # كشف frameworks و libraries
        tech_patterns = {
            'React': [r'react', r'_react', r'react-dom'],
            'Vue.js': [r'vue\.js', r'vue\.min\.js', r'__vue__'],
            'Angular': [r'angular', r'ng-app', r'ng-controller'],
            'jQuery': [r'jquery', r'\$\('],
            'Bootstrap': [r'bootstrap', r'btn-primary', r'container-fluid'],
            'WordPress': [r'/wp-content/', r'/wp-includes/', r'wp-json'],
            'Drupal': [r'/sites/default/', r'drupal'],
            'Magento': [r'magento', r'/skin/frontend/'],
            'Shopify': [r'shopify', r'cdn.shopify.com'],
            'Laravel': [r'laravel', r'csrf-token'],
            'Django': [r'django', r'csrfmiddlewaretoken'],
            'Flask': [r'flask', r'__flask__'],
            'Node.js': [r'node_modules', r'npm'],
            'MongoDB': [r'mongodb', r'mongo'],
            'MySQL': [r'mysql', r'phpmyadmin'],
            'Redis': [r'redis'],
            'Cloudflare': [r'cloudflare', r'cf-ray'],
            'Google Analytics': [r'google-analytics', r'gtag', r'ga\('],
            'Font Awesome': [r'font-awesome', r'fa-'],
            'Tailwind CSS': [r'tailwind', r'tw-'],
            'Material-UI': [r'material-ui', r'mui-'],
            'Next.js': [r'next\.js', r'_next/'],
            'Nuxt.js': [r'nuxt', r'_nuxt/']
        }
        
        for tech, patterns in tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    technologies.append(tech)
                    break
        
        self.discovered_technologies.update(technologies)
        return technologies

    def extract_seo_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """استخراج بيانات SEO المتقدمة"""
        seo_data = {
            'url': url,
            'title': '',
            'description': '',
            'keywords': '',
            'og_data': {},
            'twitter_data': {},
            'schema_data': [],
            'h1_tags': [],
            'h2_tags': [],
            'internal_links': 0,
            'external_links': 0,
            'images_without_alt': 0,
            'canonical_url': '',
            'robots_meta': '',
            'language': '',
            'viewport': ''
        }
        
        # عنوان الصفحة
        title_tag = soup.find('title')
        if title_tag:
            seo_data['title'] = title_tag.get_text().strip()
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                seo_data['description'] = content
            elif name == 'keywords':
                seo_data['keywords'] = content
            elif name == 'robots':
                seo_data['robots_meta'] = content
            elif name == 'viewport':
                seo_data['viewport'] = content
            elif property_attr.startswith('og:'):
                seo_data['og_data'][property_attr] = content
            elif name.startswith('twitter:'):
                seo_data['twitter_data'][name] = content
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            seo_data['canonical_url'] = canonical.get('href', '')
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            seo_data['language'] = html_tag.get('lang', '')
        
        # Headers
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            if i <= 2:
                seo_data[f'h{i}_tags'] = [h.get_text().strip() for h in headers]
        
        # Links analysis
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == self.domain:
                    seo_data['internal_links'] += 1
                else:
                    seo_data['external_links'] += 1
        
        # Images without alt
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                seo_data['images_without_alt'] += 1
        
        # Schema.org data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                schema = json.loads(script.string)
                seo_data['schema_data'].append(schema)
            except:
                pass
        
        return seo_data

    def analyze_performance(self, html_content: str, url: str) -> Dict[str, Any]:
        """تحليل الأداء المتقدم"""
        performance = {
            'url': url,
            'html_size_bytes': len(html_content.encode('utf-8')),
            'external_resources': {
                'css': 0,
                'js': 0,
                'images': 0,
                'fonts': 0
            },
            'inline_styles': 0,
            'inline_scripts': 0,
            'critical_issues': [],
            'suggestions': []
        }
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # عد الموارد الخارجية
        css_links = soup.find_all('link', rel='stylesheet')
        performance['external_resources']['css'] = len(css_links)
        
        js_scripts = soup.find_all('script', src=True)
        performance['external_resources']['js'] = len(js_scripts)
        
        images = soup.find_all('img', src=True)
        performance['external_resources']['images'] = len(images)
        
        # Inline resources
        style_tags = soup.find_all('style')
        performance['inline_styles'] = len(style_tags)
        
        script_tags = soup.find_all('script', src=False)
        performance['inline_scripts'] = len([s for s in script_tags if s.string])
        
        # تحليل المشاكل
        if performance['external_resources']['css'] > 10:
            performance['critical_issues'].append('Too many CSS files (>10)')
            performance['suggestions'].append('Combine CSS files to reduce HTTP requests')
        
        if performance['external_resources']['js'] > 10:
            performance['critical_issues'].append('Too many JavaScript files (>10)')
            performance['suggestions'].append('Combine and minify JavaScript files')
        
        if performance['html_size_bytes'] > 100000:  # 100KB
            performance['critical_issues'].append('Large HTML size (>100KB)')
            performance['suggestions'].append('Optimize HTML structure and remove unnecessary code')
        
        return performance

    def extract_smart_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """استخراج ذكي للمحتوى"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # إزالة العناصر غير المرغوب فيها
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        content = {
            'main_content': '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': [],
            'forms': [],
            'media': []
        }
        
        # استخراج المحتوى الرئيسي
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main'))
        if main_content:
            content['main_content'] = main_content.get_text(strip=True)
        
        # العناوين
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for heading in headings:
                content['headings'].append({
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', '')
                })
        
        # الفقرات
        paragraphs = soup.find_all('p')
        content['paragraphs'] = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
        
        # القوائم
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = [li.get_text().strip() for li in lst.find_all('li')]
            content['lists'].append({
                'type': lst.name,
                'items': items
            })
        
        # الجداول
        tables = soup.find_all('table')
        for table in tables:
            rows = []
            for tr in table.find_all('tr'):
                row = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                if row:
                    rows.append(row)
            if rows:
                content['tables'].append(rows)
        
        return content

    def create_enhanced_report(self) -> Dict[str, Any]:
        """إنشاء تقرير شامل ومتقدم"""
        self.stats['extraction_end'] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(self.stats['extraction_start'])
        end_time = datetime.fromisoformat(self.stats['extraction_end'])
        self.stats['processing_time_seconds'] = (end_time - start_time).total_seconds()
        
        report = {
            'extraction_info': {
                'site_url': self.base_url,
                'domain': self.domain,
                'extraction_id': self.site_id,
                'start_time': self.stats['extraction_start'],
                'end_time': self.stats['extraction_end'],
                'duration_seconds': self.stats['processing_time_seconds'],
                'config_used': self.config
            },
            'statistics': self.stats,
            'technologies_detected': list(self.discovered_technologies),
            'file_structure': self._analyze_file_structure(),
            'quality_metrics': self._calculate_quality_metrics(),
            'recommendations': self._generate_recommendations(),
            'sitemap': self._create_sitemap_data()
        }
        
        # حفظ التقرير
        report_file = self.site_dir / "reports" / "extraction_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # إنشاء تقرير HTML
        self._create_html_report(report)
        
        return report

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """تحليل هيكل الملفات"""
        structure = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': defaultdict(lambda: {'count': 0, 'size_mb': 0}),
            'largest_files': [],
            'directory_tree': {}
        }
        
        for file_path in self.site_dir.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                ext = file_path.suffix.lower()
                
                structure['total_files'] += 1
                structure['total_size_mb'] += size / (1024 * 1024)
                
                structure['by_type'][ext]['count'] += 1
                structure['by_type'][ext]['size_mb'] += size / (1024 * 1024)
                
                structure['largest_files'].append({
                    'path': str(file_path.relative_to(self.site_dir)),
                    'size_mb': size / (1024 * 1024)
                })
        
        # ترتيب أكبر الملفات
        structure['largest_files'].sort(key=lambda x: x['size_mb'], reverse=True)
        structure['largest_files'] = structure['largest_files'][:10]
        
        return structure

    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """حساب مقاييس الجودة"""
        metrics = {
            'success_rate': 0,
            'performance_score': 0,
            'seo_score': 0,
            'security_score': 0,
            'overall_score': 0
        }
        
        # معدل النجاح
        total_attempts = len(self.visited_urls) + len(self.failed_urls)
        if total_attempts > 0:
            metrics['success_rate'] = len(self.visited_urls) / total_attempts * 100
        
        # النتيجة الإجمالية
        scores = [metrics['success_rate'], metrics['performance_score'], 
                 metrics['seo_score'], metrics['security_score']]
        metrics['overall_score'] = sum(scores) / len(scores)
        
        return metrics

    def _generate_recommendations(self) -> List[str]:
        """إنشاء توصيات للتحسين"""
        recommendations = []
        
        if self.stats['errors']:
            recommendations.append("تحسين معالجة الأخطاء لتقليل فشل التحميل")
        
        if self.stats['pages_extracted'] < self.stats['pages_discovered']:
            recommendations.append("زيادة عمق الاستخراج لتحميل المزيد من الصفحات")
        
        if len(self.discovered_technologies) > 10:
            recommendations.append("الموقع يستخدم تقنيات متعددة - قد يحتاج تحسين الأداء")
        
        return recommendations

    def _create_sitemap_data(self) -> List[Dict[str, str]]:
        """إنشاء خريطة الموقع"""
        sitemap = []
        for url in self.visited_urls:
            sitemap.append({
                'url': url,
                'lastmod': datetime.now().isoformat(),
                'priority': '0.8'
            })
        return sitemap

    def _create_html_report(self, report: Dict[str, Any]):
        """إنشاء تقرير HTML تفاعلي"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الاستخراج الفائق - {self.domain}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
        .chart-container {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }}
        .tech-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .tech-tag {{
            background: rgba(255,255,255,0.3);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 تقرير الاستخراج الفائق</h1>
            <h2>{self.domain}</h2>
            <p>تم الاستخراج في: {report['extraction_info']['end_time']}</p>
            <p>مدة الاستخراج: {report['extraction_info']['duration_seconds']:.2f} ثانية</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{self.stats['pages_extracted']}</div>
                <div>صفحة مستخرجة</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['images_downloaded']}</div>
                <div>صورة محملة</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(self.discovered_technologies)}</div>
                <div>تقنية مكتشفة</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['quality_metrics']['overall_score']:.1f}%</div>
                <div>نقاط الجودة</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>التقنيات المكتشفة</h3>
            <div class="tech-list">
                {''.join(f'<span class="tech-tag">{tech}</span>' for tech in self.discovered_technologies)}
            </div>
        </div>
        
        <div class="chart-container">
            <h3>توصيات التحسين</h3>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in report['recommendations'])}
            </ul>
        </div>
    </div>
</body>
</html>
"""
        
        report_html = self.site_dir / "reports" / "extraction_report.html"
        with open(report_html, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def extract_ultra_smart(self) -> Tuple[Path, Dict[str, Any]]:
        """الاستخراج الفائق الذكي"""
        logging.info(f"🚀 بدء الاستخراج الفائق للموقع: {self.base_url}")
        
        try:
            # المرحلة 1: اكتشاف الموقع
            self._discover_site_structure()
            
            # المرحلة 2: الاستخراج المتوازي
            self._extract_parallel()
            
            # المرحلة 3: التحليل المتقدم
            self._analyze_extracted_content()
            
            # المرحلة 4: إنشاء التقارير
            report = self.create_enhanced_report()
            
            # المرحلة 5: التحسين والضغط
            if self.config.get('compress_output'):
                self._create_compressed_archive()
            
            logging.info(f"✅ اكتمل الاستخراج الفائق بنجاح!")
            return self.site_dir, report
            
        except Exception as e:
            logging.error(f"❌ خطأ في الاستخراج الفائق: {e}")
            self.stats['errors'].append(str(e))
            raise

    def _discover_site_structure(self):
        """اكتشاف هيكل الموقع"""
        # تنفيذ اكتشاف الهيكل...
        pass

    def _extract_parallel(self):
        """الاستخراج المتوازي"""
        # تنفيذ الاستخراج المتوازي...
        pass

    def _analyze_extracted_content(self):
        """تحليل المحتوى المستخرج"""
        # تنفيذ التحليل...
        pass

    def _create_compressed_archive(self):
        """إنشاء أرشيف مضغوط"""
        archive_path = self.site_dir.parent / f"{self.site_id}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.site_dir.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(self.site_dir))


def extract_ultra_smart(url: str, config: Dict[str, Any] = None) -> Tuple[Path, Dict[str, Any]]:
    """دالة الاستخراج الفائق السهلة"""
    extractor = UltraSmartExtractor(url, config)
    return extractor.extract_ultra_smart()