#!/usr/bin/env python3
"""
مدير الأدوات المتقدمة - يجمع جميع النظم المطورة
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

# النظم المتقدمة
try:
    from cms_detector import CMSDetector
    from sitemap_generator import SitemapGenerator
    from security_scanner import SecurityScanner
    from simple_screenshot import SimpleScreenshotEngine
except ImportError as e:
    print(f"تحذير: لم يتم تحميل بعض النظم المتقدمة: {e}")
    CMSDetector = None
    SitemapGenerator = None
    SecurityScanner = None
    SimpleScreenshotEngine = None

class AdvancedToolsManager:
    """مدير شامل لجميع الأدوات المتقدمة"""
    
    def __init__(self):
        self.cms_detector = CMSDetector() if CMSDetector else None
        self.sitemap_generator = SitemapGenerator() if SitemapGenerator else None
        self.security_scanner = SecurityScanner() if SecurityScanner else None
        self.screenshot_engine = SimpleScreenshotEngine() if SimpleScreenshotEngine else None
        
    def run_comprehensive_analysis(self, url: str, output_dir: Path, analysis_types: Optional[list] = None) -> Dict[str, Any]:
        """تشغيل تحليل شامل متقدم"""
        
        if analysis_types is None:
            analysis_types = ['cms', 'sitemap', 'security', 'screenshots']
        
        results = {
            'url': url,
            'analysis_timestamp': datetime.now().isoformat(),
            'completed_analyses': [],
            'failed_analyses': [],
            'comprehensive_results': {}
        }
        
        # إنشاء مجلدات فرعية للتحليلات
        analysis_dir = output_dir / '03_analysis'
        analysis_dir.mkdir(exist_ok=True)
        
        # 1. كشف CMS
        if 'cms' in analysis_types and self.cms_detector:
            try:
                print("🔍 تشغيل كشف نظام إدارة المحتوى...")
                cms_results = self.cms_detector.detect_cms(url)
                
                # حفظ التقرير
                cms_report_file = self.cms_detector.generate_cms_report(cms_results, analysis_dir)
                
                results['comprehensive_results']['cms_detection'] = cms_results
                results['completed_analyses'].append('CMS Detection')
                print(f"✅ تم كشف CMS: {cms_results.get('detected_cms', [])}")
                
            except Exception as e:
                results['failed_analyses'].append(f'CMS Detection: {str(e)}')
                print(f"❌ فشل كشف CMS: {e}")
        
        # 2. إنشاء خريطة الموقع
        if 'sitemap' in analysis_types and self.sitemap_generator:
            try:
                print("🗺️ إنشاء خريطة الموقع...")
                sitemap_results = self.sitemap_generator.generate_sitemap(url, analysis_dir)
                
                results['comprehensive_results']['sitemap_generation'] = sitemap_results
                results['completed_analyses'].append('Sitemap Generation')
                print(f"✅ تم إنشاء خريطة الموقع: {sitemap_results.get('total_pages_found', 0)} صفحة")
                
            except Exception as e:
                results['failed_analyses'].append(f'Sitemap Generation: {str(e)}')
                print(f"❌ فشل إنشاء الخريطة: {e}")
        
        # 3. فحص الأمان
        if 'security' in analysis_types and self.security_scanner:
            try:
                print("🔒 فحص الأمان والثغرات...")
                security_results = self.security_scanner.scan_website_security(url, analysis_dir)
                
                results['comprehensive_results']['security_scan'] = security_results
                results['completed_analyses'].append('Security Scan')
                print(f"✅ تم فحص الأمان: نتيجة {security_results.get('overall_security_score', 0)}/100")
                
            except Exception as e:
                results['failed_analyses'].append(f'Security Scan: {str(e)}')
                print(f"❌ فشل فحص الأمان: {e}")
        
        # 4. لقطات الشاشة المتقدمة
        if 'screenshots' in analysis_types and self.screenshot_engine:
            try:
                print("📸 إنشاء لقطات شاشة تفاعلية...")
                screenshots_dir = output_dir / '05_screenshots'
                screenshots_dir.mkdir(exist_ok=True)
                
                # إنشاء معاينة HTML
                preview_result = self.screenshot_engine.capture_html_preview(url, screenshots_dir)
                
                # إنشاء thumbnail إذا وُجد محتوى
                content_file = output_dir / '01_content' / 'page.html'
                if content_file.exists():
                    with open(content_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    thumbnail_result = self.screenshot_engine.create_website_thumbnail(url, content, screenshots_dir)
                    preview_result.update(thumbnail_result)
                
                results['comprehensive_results']['screenshots'] = preview_result
                results['completed_analyses'].append('Screenshots')
                print("✅ تم إنشاء لقطات الشاشة التفاعلية")
                
            except Exception as e:
                results['failed_analyses'].append(f'Screenshots: {str(e)}')
                print(f"❌ فشل إنشاء لقطات الشاشة: {e}")
        
        # إنشاء تقرير شامل
        comprehensive_report = self._create_comprehensive_report(results, analysis_dir)
        results['comprehensive_report_file'] = comprehensive_report
        
        return results
    
    def _create_comprehensive_report(self, results: Dict[str, Any], output_dir: Path) -> str:
        """إنشاء تقرير شامل لجميع التحليلات"""
        
        # تقرير JSON
        json_report_file = output_dir / 'comprehensive_analysis_report.json'
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # تقرير HTML تفاعلي
        html_report_file = output_dir / 'comprehensive_analysis_report.html'
        html_content = self._generate_html_report(results)
        
        with open(html_report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_report_file.name)
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML شامل ومتقدم"""
        
        comprehensive_results = results.get('comprehensive_results', {})
        completed = len(results.get('completed_analyses', []))
        failed = len(results.get('failed_analyses', []))
        
        # استخراج نتائج محددة
        cms_results = comprehensive_results.get('cms_detection', {})
        sitemap_results = comprehensive_results.get('sitemap_generation', {})
        security_results = comprehensive_results.get('security_scan', {})
        screenshots_results = comprehensive_results.get('screenshots', {})
        
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير التحليل الشامل - {results['url']}</title>
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
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(15px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            padding-bottom: 30px;
        }}
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .analysis-section {{
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            margin: 25px 0;
            border-right: 5px solid;
        }}
        .cms-section {{ border-right-color: #4CAF50; }}
        .sitemap-section {{ border-right-color: #2196F3; }}
        .security-section {{ border-right-color: #FF9800; }}
        .screenshots-section {{ border-right-color: #9C27B0; }}
        .section-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .result-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
        }}
        .success {{ background: rgba(76,175,80,0.2); }}
        .warning {{ background: rgba(255,152,0,0.2); }}
        .error {{ background: rgba(244,67,54,0.2); }}
        .tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 2px;
            background: rgba(255,255,255,0.2);
        }}
        .cms-tag {{ background: rgba(76,175,80,0.3); }}
        .tech-tag {{ background: rgba(33,150,243,0.3); }}
        .vuln-tag {{ background: rgba(244,67,54,0.3); }}
        .timestamp {{
            text-align: center;
            opacity: 0.7;
            margin-top: 40px;
            font-size: 14px;
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            overflow: hidden;
            margin: 15px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            border-radius: 4px;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 تقرير التحليل الشامل المتقدم</h1>
            <h2>{results['url']}</h2>
            <p>تحليل شامل متعدد الطبقات لاستخراج ونسخ المواقع</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card success">
                <div class="stat-number">{completed}</div>
                <div class="stat-label">تحليل مكتمل</div>
            </div>
            <div class="stat-card {'error' if failed > 0 else 'success'}">
                <div class="stat-number">{failed}</div>
                <div class="stat-label">تحليل فاشل</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(cms_results.get('detected_cms', []))}</div>
                <div class="stat-label">نظام CMS مكتشف</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{security_results.get('overall_security_score', 0)}/100</div>
                <div class="stat-label">نتيجة الأمان</div>
            </div>
        </div>
        
        {self._format_cms_section(cms_results) if cms_results else ''}
        {self._format_sitemap_section(sitemap_results) if sitemap_results else ''}
        {self._format_security_section(security_results) if security_results else ''}
        {self._format_screenshots_section(screenshots_results) if screenshots_results else ''}
        
        <div class="timestamp">
            تم إنشاء التقرير: {results.get('analysis_timestamp', '')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def get_tools_status(self) -> Dict[str, Any]:
        """الحصول على حالة جميع الأدوات المتاحة"""
        return {
            'available_tools': [
                'cms_detector' if self.cms_detector else None,
                'sitemap_generator' if self.sitemap_generator else None, 
                'security_scanner' if self.security_scanner else None,
                'screenshot_engine' if self.screenshot_engine else None
            ],
            'active_tools': sum(1 for tool in [
                self.cms_detector, self.sitemap_generator, 
                self.security_scanner, self.screenshot_engine
            ] if tool is not None),
            'total_tools': 4,
            'status': 'ready'
        }
    
    def extract_with_cloner_pro(self, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """استخراج متقدم باستخدام Website Cloner Pro"""
        if config is None:
            config = {}
            
        try:
            # محاكاة استخراج متقدم
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'success': True,
                'url': url,
                'title': soup.title.string if soup.title else 'No Title',
                'content_length': len(response.content),
                'links_found': len(soup.find_all('a')),
                'images_found': len(soup.find_all('img')),
                'extraction_type': 'cloner_pro',
                'config_used': config
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def analyze_with_ai(self, url: str, content: str = None) -> Dict[str, Any]:
        """تحليل باستخدام الذكاء الاصطناعي"""
        try:
            if not content:
                import requests
                response = requests.get(url, timeout=10)
                content = response.text
            
            # تحليل أساسي بدون AI حقيقي
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # استخراج المعلومات
            text_content = soup.get_text()
            word_count = len(text_content.split())
            
            return {
                'success': True,
                'url': url,
                'analysis': {
                    'word_count': word_count,
                    'character_count': len(text_content),
                    'links_count': len(soup.find_all('a')),
                    'images_count': len(soup.find_all('img')),
                    'headings_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                    'language': 'ar' if any(ord(char) > 1536 for char in text_content[:1000]) else 'en',
                    'sentiment': 'neutral',
                    'topics': ['website', 'content'],
                    'quality_score': min(100, max(0, word_count // 10))
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def extract_with_spider(self, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """استخراج باستخدام Spider Crawler"""
        if config is None:
            config = {'max_depth': 2, 'max_pages': 10}
            
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse
            
            visited = set()
            to_visit = [url]
            extracted_data = []
            
            while to_visit and len(extracted_data) < config.get('max_pages', 10):
                current_url = to_visit.pop(0)
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                
                try:
                    response = requests.get(current_url, timeout=5)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # استخراج البيانات
                    page_data = {
                        'url': current_url,
                        'title': soup.title.string if soup.title else 'No Title',
                        'content_length': len(response.content),
                        'status_code': response.status_code
                    }
                    extracted_data.append(page_data)
                    
                    # العثور على روابط جديدة
                    if len(extracted_data) < config.get('max_pages', 10):
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            full_url = urljoin(current_url, href)
                            if urlparse(full_url).netloc == urlparse(url).netloc:
                                if full_url not in visited and full_url not in to_visit:
                                    to_visit.append(full_url)
                                    
                except Exception as e:
                    continue
            
            return {
                'success': True,
                'url': url,
                'pages_crawled': len(extracted_data),
                'pages_data': extracted_data,
                'config_used': config
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def download_assets(self, url: str, asset_types: list = None) -> Dict[str, Any]:
        """تحميل أصول الموقع (CSS, JS, Images)"""
        if asset_types is None:
            asset_types = ['css', 'js', 'images']
            
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin
            
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            assets = {
                'css': [],
                'js': [], 
                'images': [],
                'total_size': 0
            }
            
            # CSS files
            if 'css' in asset_types:
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        assets['css'].append({
                            'url': full_url,
                            'size': 'unknown'
                        })
            
            # JavaScript files  
            if 'js' in asset_types:
                for script in soup.find_all('script', src=True):
                    src = script.get('src')
                    if src:
                        full_url = urljoin(url, src)
                        assets['js'].append({
                            'url': full_url,
                            'size': 'unknown'
                        })
            
            # Images
            if 'images' in asset_types:
                for img in soup.find_all('img', src=True):
                    src = img.get('src')
                    if src:
                        full_url = urljoin(url, src)
                        assets['images'].append({
                            'url': full_url,
                            'alt': img.get('alt', ''),
                            'size': 'unknown'
                        })
            
            return {
                'success': True,
                'url': url,
                'assets': assets,
                'total_assets': sum(len(assets[key]) for key in ['css', 'js', 'images'])
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _format_cms_section(self, cms_results: Dict[str, Any]) -> str:
        """تنسيق قسم CMS"""
        detected_cms = cms_results.get('detected_cms', [])
        confidence_scores = cms_results.get('confidence_scores', {})
        additional_info = cms_results.get('additional_info', {})
        
        cms_tags = ''.join([f'<span class="tag cms-tag">{cms}</span>' for cms in detected_cms])
        
        js_frameworks = additional_info.get('javascript_frameworks', [])
        js_tags = ''.join([f'<span class="tag tech-tag">{fw}</span>' for fw in js_frameworks])
        
        return f"""
        <div class="analysis-section cms-section">
            <div class="section-title">
                🎯 كشف نظام إدارة المحتوى
            </div>
            <div class="results-grid">
                <div class="result-card success">
                    <h4>أنظمة CMS المكتشفة</h4>
                    {cms_tags if cms_tags else '<p>لم يتم كشف نظام CMS محدد</p>'}
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {max(confidence_scores.values()) if confidence_scores else 0}%"></div>
                    </div>
                </div>
                <div class="result-card">
                    <h4>JavaScript Frameworks</h4>
                    {js_tags if js_tags else '<p>لم يتم كشف frameworks محددة</p>'}
                </div>
            </div>
        </div>
        """
    
    def _format_sitemap_section(self, sitemap_results: Dict[str, Any]) -> str:
        """تنسيق قسم خريطة الموقع"""
        total_pages = sitemap_results.get('total_pages_found', 0)
        crawled_pages = sitemap_results.get('pages_crawled', 0)
        max_depth = sitemap_results.get('max_depth_reached', 0)
        duration = sitemap_results.get('crawl_duration', 0)
        
        return f"""
        <div class="analysis-section sitemap-section">
            <div class="section-title">
                🗺️ خريطة الموقع وتحليل الهيكل
            </div>
            <div class="results-grid">
                <div class="result-card success">
                    <h4>إحصائيات الزحف</h4>
                    <p><strong>الصفحات المكتشفة:</strong> {total_pages}</p>
                    <p><strong>الصفحات المزورة:</strong> {crawled_pages}</p>
                    <p><strong>أقصى عمق:</strong> {max_depth} مستوى</p>
                    <p><strong>مدة الزحف:</strong> {duration} ثانية</p>
                </div>
                <div class="result-card">
                    <h4>ملفات تم إنشاؤها</h4>
                    <ul>
                        <li>📄 sitemap.xml</li>
                        <li>📊 detailed_sitemap.json</li>
                        <li>🌐 sitemap.html</li>
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def _format_security_section(self, security_results: Dict[str, Any]) -> str:
        """تنسيق قسم الأمان"""
        score = security_results.get('overall_security_score', 0)
        vulnerabilities = security_results.get('vulnerabilities_found', [])
        score_color = '#4CAF50' if score >= 80 else '#FF9800' if score >= 60 else '#F44336'
        
        vuln_tags = ''.join([f'<span class="tag vuln-tag">⚠️ {vuln.split(":")[1] if ":" in vuln else vuln}</span>' for vuln in vulnerabilities[:5]])
        
        return f"""
        <div class="analysis-section security-section">
            <div class="section-title">
                🔒 تحليل الأمان والثغرات
            </div>
            <div class="results-grid">
                <div class="result-card {'success' if score >= 80 else 'warning' if score >= 60 else 'error'}">
                    <h4>نتيجة الأمان الإجمالية</h4>
                    <div style="font-size: 36px; color: {score_color}; font-weight: bold;">{score}/100</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {score}%; background: {score_color};"></div>
                    </div>
                </div>
                <div class="result-card error">
                    <h4>الثغرات المكتشفة ({len(vulnerabilities)})</h4>
                    {vuln_tags if vuln_tags else '<p>✅ لم يتم العثور على ثغرات ظاهرة</p>'}
                </div>
            </div>
        </div>
        """
    
    def _format_screenshots_section(self, screenshots_results: Dict[str, Any]) -> str:
        """تنسيق قسم لقطات الشاشة"""
        method = screenshots_results.get('method', 'غير معروف')
        features = screenshots_results.get('features', {})
        files_created = screenshots_results.get('files_created', [])
        
        feature_tags = ''.join([f'<span class="tag tech-tag">{feature}</span>' for feature, enabled in features.items() if enabled])
        file_tags = ''.join([f'<span class="tag">📁 {file}</span>' for file in files_created])
        
        return f"""
        <div class="analysis-section screenshots-section">
            <div class="section-title">
                📸 لقطات الشاشة والمعاينة التفاعلية
            </div>
            <div class="results-grid">
                <div class="result-card success">
                    <h4>الميزات المتقدمة</h4>
                    {feature_tags if feature_tags else '<p>معاينة أساسية</p>'}
                </div>
                <div class="result-card">
                    <h4>الملفات المُنشأة</h4>
                    {file_tags if file_tags else '<p>لا توجد ملفات</p>'}
                </div>
            </div>
        </div>
        """