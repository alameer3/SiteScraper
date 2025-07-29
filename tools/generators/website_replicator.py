"""
Website Replicator - محرك إنشاء المواقع المطابقة
إنشاء مواقع مطابقة بناءً على الاستخراج
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

class WebsiteReplicator:
    """محرك إنشاء المواقع المطابقة"""
    
    def __init__(self, output_directory: str = "replicated_sites"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def replicate_website(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء موقع مطابق بناءً على بيانات الاستخراج"""
        try:
            url = extraction_data.get('url', '')
            domain = urlparse(url).netloc.replace(':', '_')
            
            # إنشاء مجلد المشروع
            project_dir = self.output_directory / f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # إنشاء بنية المشروع
            self._create_project_structure(project_dir)
            
            # إنشاء ملف HTML الرئيسي
            main_html = self._generate_main_html(extraction_data, project_dir)
            
            # إنشاء ملفات CSS
            css_files = self._generate_css_files(extraction_data, project_dir)
            
            # إنشاء ملفات JavaScript
            js_files = self._generate_js_files(extraction_data, project_dir)
            
            # نسخ الأصول المحملة
            assets_info = self._copy_downloaded_assets(extraction_data, project_dir)
            
            # إنشاء ملف معلومات المشروع
            project_info = self._create_project_info(extraction_data, project_dir)
            
            return {
                'status': 'success',
                'project_directory': str(project_dir),
                'files_created': {
                    'html': main_html,
                    'css': css_files,
                    'js': js_files,
                    'assets': assets_info,
                    'project_info': project_info
                },
                'url': url,
                'domain': domain
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء الموقع المطابق: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _create_project_structure(self, project_dir: Path):
        """إنشاء بنية المشروع الأساسية"""
        directories = [
            'css',
            'js',
            'images',
            'fonts',
            'assets',
            'docs'
        ]
        
        for directory in directories:
            (project_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_main_html(self, extraction_data: Dict[str, Any], project_dir: Path) -> str:
        """إنشاء ملف HTML الرئيسي"""
        content = extraction_data.get('content', {})
        metadata = extraction_data.get('metadata', {})
        assets = extraction_data.get('assets', {})
        
        title = content.get('title', 'Replicated Website')
        
        html_template = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- Generated CSS -->
    <link rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" href="css/layout.css">
    <link rel="stylesheet" href="css/components.css">
    
    <!-- Meta Tags -->
    <meta name="description" content="{metadata.get('basic', {}).get('description', '')}">
    <meta name="keywords" content="{metadata.get('basic', {}).get('keywords', '')}">
    <meta name="author" content="Website Replicator">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{metadata.get('social', {}).get('description', '')}">
    <meta property="og:type" content="website">
</head>
<body>
    <div class="container">
        <header class="main-header">
            <h1>{title}</h1>
        </header>
        
        <main class="main-content">
            {self._generate_content_sections(content)}
        </main>
        
        <footer class="main-footer">
            <p>تم إنشاء هذا الموقع بواسطة محرك النسخ الذكي</p>
            <p>تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
    
    <!-- Generated JavaScript -->
    <script src="js/main.js"></script>
    <script src="js/components.js"></script>
</body>
</html>"""
        
        html_path = project_dir / 'index.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return str(html_path)
    
    def _generate_content_sections(self, content: Dict[str, Any]) -> str:
        """إنشاء أقسام المحتوى"""
        sections_html = ""
        
        # العناوين
        headings = content.get('headings', {})
        for level, heading_list in headings.items():
            if heading_list:
                sections_html += f'<section class="headings-section">\n'
                for heading in heading_list:
                    sections_html += f'<{level} class="heading">{heading}</{level}>\n'
                sections_html += '</section>\n'
        
        # الفقرات
        paragraphs = content.get('paragraphs', [])
        if paragraphs:
            sections_html += '<section class="paragraphs-section">\n'
            for paragraph in paragraphs[:10]:  # أول 10 فقرات
                sections_html += f'<p class="paragraph">{paragraph}</p>\n'
            sections_html += '</section>\n'
        
        # المحتوى النصي
        text_content = content.get('text_content', '')
        if text_content and len(text_content) > 100:
            sections_html += f'''
            <section class="text-content-section">
                <h2>المحتوى الرئيسي</h2>
                <div class="text-content">
                    {text_content[:1000]}...
                </div>
            </section>
            '''
        
        return sections_html
    
    def _generate_css_files(self, extraction_data: Dict[str, Any], project_dir: Path) -> List[str]:
        """إنشاء ملفات CSS"""
        css_files = []
        
        # ملف CSS الرئيسي
        main_css = """
/* ملف CSS الرئيسي للموقع المطابق */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', 'Tahoma', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    direction: rtl;
    text-align: right;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.main-header {
    background-color: #2c3e50;
    color: white;
    padding: 2rem;
    text-align: center;
    border-radius: 8px;
    margin-bottom: 2rem;
}

.main-content {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.headings-section {
    margin-bottom: 2rem;
}

.heading {
    margin-bottom: 1rem;
    color: #2c3e50;
}

.paragraphs-section {
    margin-bottom: 2rem;
}

.paragraph {
    margin-bottom: 1rem;
    line-height: 1.8;
}

.text-content-section {
    margin-bottom: 2rem;
}

.text-content {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 6px;
    border-right: 4px solid #007bff;
}

.main-footer {
    background-color: #34495e;
    color: white;
    padding: 1rem;
    text-align: center;
    border-radius: 8px;
    font-size: 0.9rem;
}

/* تصميم متجاوب */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .main-header,
    .main-content {
        padding: 1rem;
    }
}
"""
        
        main_css_path = project_dir / 'css' / 'main.css'
        with open(main_css_path, 'w', encoding='utf-8') as f:
            f.write(main_css)
        css_files.append(str(main_css_path))
        
        # ملف تخطيط
        layout_css = """
/* تخطيط الموقع */

.layout-grid {
    display: grid;
    grid-template-columns: 1fr 3fr 1fr;
    gap: 2rem;
}

.sidebar {
    background-color: #ecf0f1;
    padding: 1rem;
    border-radius: 6px;
}

.content-area {
    background-color: white;
    padding: 2rem;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
    .layout-grid {
        grid-template-columns: 1fr;
    }
}
"""
        
        layout_css_path = project_dir / 'css' / 'layout.css'
        with open(layout_css_path, 'w', encoding='utf-8') as f:
            f.write(layout_css)
        css_files.append(str(layout_css_path))
        
        return css_files
    
    def _generate_js_files(self, extraction_data: Dict[str, Any], project_dir: Path) -> List[str]:
        """إنشاء ملفات JavaScript"""
        js_files = []
        
        # ملف JavaScript الرئيسي
        main_js = """
// ملف JavaScript الرئيسي للموقع المطابق

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل الموقع المطابق بنجاح');
    
    // إضافة تفاعلات أساسية
    initializeBasicInteractions();
    
    // تحسين الأداء
    optimizePerformance();
});

function initializeBasicInteractions() {
    // إضافة تأثيرات للعناصر
    const headings = document.querySelectorAll('.heading');
    headings.forEach(heading => {
        heading.addEventListener('mouseover', function() {
            this.style.color = '#007bff';
        });
        
        heading.addEventListener('mouseout', function() {
            this.style.color = '#2c3e50';
        });
    });
    
    // تحسين التمرير
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.main-header');
        if (window.scrollY > 100) {
            header.style.position = 'fixed';
            header.style.top = '0';
            header.style.width = '100%';
            header.style.zIndex = '1000';
        } else {
            header.style.position = 'static';
        }
    });
}

function optimizePerformance() {
    // تحسين تحميل الصور
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.loading = 'lazy';
    });
    
    // إضافة مؤشر التحميل
    const loadingIndicator = document.createElement('div');
    loadingIndicator.innerHTML = 'جاري التحميل...';
    loadingIndicator.style.display = 'none';
    document.body.appendChild(loadingIndicator);
}

// وظائف مساعدة
function showLoading() {
    document.querySelector('div[innerHTML*="جاري التحميل"]').style.display = 'block';
}

function hideLoading() {
    document.querySelector('div[innerHTML*="جاري التحميل"]').style.display = 'none';
}
"""
        
        main_js_path = project_dir / 'js' / 'main.js'
        with open(main_js_path, 'w', encoding='utf-8') as f:
            f.write(main_js)
        js_files.append(str(main_js_path))
        
        return js_files
    
    def _copy_downloaded_assets(self, extraction_data: Dict[str, Any], project_dir: Path) -> Dict[str, Any]:
        """نسخ الأصول المحملة إلى المشروع"""
        assets_info = {
            'copied_files': [],
            'failed_copies': [],
            'total_size': 0
        }
        
        assets = extraction_data.get('assets', {})
        download_info = assets.get('download_info', {})
        
        if download_info.get('status') == 'completed':
            downloaded_assets = download_info.get('downloaded_assets', {})
            
            for url, file_path in downloaded_assets.items():
                try:
                    source_path = Path(file_path)
                    if source_path.exists():
                        # تحديد المجلد المناسب
                        file_ext = source_path.suffix.lower()
                        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                            dest_dir = project_dir / 'images'
                        elif file_ext in ['.css']:
                            dest_dir = project_dir / 'css'
                        elif file_ext in ['.js']:
                            dest_dir = project_dir / 'js'
                        elif file_ext in ['.woff', '.woff2', '.ttf']:
                            dest_dir = project_dir / 'fonts'
                        else:
                            dest_dir = project_dir / 'assets'
                        
                        dest_path = dest_dir / source_path.name
                        
                        # نسخ الملف
                        import shutil
                        shutil.copy2(source_path, dest_path)
                        
                        assets_info['copied_files'].append(str(dest_path))
                        assets_info['total_size'] += source_path.stat().st_size
                        
                except Exception as e:
                    assets_info['failed_copies'].append(f"{url}: {str(e)}")
                    self.logger.warning(f"فشل نسخ {url}: {e}")
        
        return assets_info
    
    def _create_project_info(self, extraction_data: Dict[str, Any], project_dir: Path) -> str:
        """إنشاء ملف معلومات المشروع"""
        project_info = {
            'project_name': f"Replicated Website - {urlparse(extraction_data.get('url', '')).netloc}",
            'creation_date': datetime.now().isoformat(),
            'source_url': extraction_data.get('url', ''),
            'extraction_mode': extraction_data.get('mode', 'unknown'),
            'statistics': extraction_data.get('statistics', {}),
            'structure': {
                'html_files': ['index.html'],
                'css_files': ['css/main.css', 'css/layout.css'],
                'js_files': ['js/main.js'],
                'directories': ['css', 'js', 'images', 'fonts', 'assets', 'docs']
            },
            'features': [
                'Responsive Design',
                'RTL Support',
                'Basic Interactions',
                'Performance Optimized',
                'SEO Ready'
            ],
            'instructions': {
                'arabic': 'افتح ملف index.html في المتصفح لعرض الموقع المطابق',
                'english': 'Open index.html in browser to view the replicated website'
            }
        }
        
        info_path = project_dir / 'project_info.json'
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
        
        # إنشاء ملف README
        readme_content = f"""# {project_info['project_name']}

## معلومات المشروع
- **الموقع المصدر**: {extraction_data.get('url', '')}
- **تاريخ الإنشاء**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **وضع الاستخراج**: {extraction_data.get('mode', 'غير محدد')}

## بنية المشروع
```
{project_dir.name}/
├── index.html          # الصفحة الرئيسية
├── css/               # ملفات التصميم
│   ├── main.css       # التصميم الرئيسي
│   └── layout.css     # تخطيط الصفحة
├── js/                # ملفات JavaScript
│   └── main.js        # الوظائف الرئيسية
├── images/            # الصور المحملة
├── fonts/             # الخطوط
├── assets/            # الملفات الأخرى
└── docs/              # الوثائق

```

## كيفية الاستخدام
1. افتح ملف `index.html` في المتصفح
2. يمكنك تعديل ملفات CSS في مجلد `css/`
3. يمكنك إضافة وظائف جديدة في مجلد `js/`

## الميزات المضمنة
- تصميم متجاوب (Responsive)
- دعم العربية (RTL)
- تفاعلات أساسية
- محسن للأداء
- جاهز لمحركات البحث

## ملاحظات
تم إنشاء هذا الموقع تلقائياً بواسطة محرك النسخ الذكي.
يمكنك تخصيصه وتطويره حسب احتياجاتك.
"""
        
        readme_path = project_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return str(info_path)