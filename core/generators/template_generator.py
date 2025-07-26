
"""
مولد القوالب المتطور - Template Generator
المرحلة الثانية: إنشاء قوالب مطابقة للتصميم المستخرج
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, Template
import logging

@dataclass
class TemplateConfig:
    """إعدادات مولد القوالب"""
    framework: str = "flask"  # flask, django, fastapi, vanilla
    css_framework: str = "bootstrap"  # bootstrap, tailwind, bulma, vanilla
    js_framework: str = "vanilla"  # vanilla, react, vue, angular
    include_responsive: bool = True
    include_animations: bool = True
    include_interactions: bool = True
    preserve_structure: bool = True
    optimize_code: bool = True
    output_directory: str = "generated_templates"

class TemplateGenerator:
    """مولد القوالب الذكي لإعادة إنشاء التصاميم"""
    
    def __init__(self, config: Optional[TemplateConfig] = None):
        self.config = config or TemplateConfig()
        self.templates_env = None
        self.generated_templates = {}
        self.style_patterns = {}
        self.component_library = {}
        
        # إعداد البيئة
        self._setup_environment()
        
        # أنماط التصميم الشائعة
        self.layout_patterns = {
            'header_nav_footer': {
                'structure': ['header', 'nav', 'main', 'footer'],
                'css_classes': ['header', 'navbar', 'main-content', 'footer']
            },
            'sidebar_layout': {
                'structure': ['header', 'div.container', 'aside.sidebar', 'main.content', 'footer'],
                'css_classes': ['header', 'container', 'sidebar', 'content', 'footer']
            },
            'card_grid': {
                'structure': ['div.container', 'div.row', 'div.col'],
                'css_classes': ['container', 'row', 'col', 'card']
            },
            'hero_section': {
                'structure': ['section.hero', 'div.hero-content', 'h1', 'p', 'button'],
                'css_classes': ['hero', 'hero-content', 'hero-title', 'hero-text', 'btn-primary']
            }
        }
        
        # مكتبة المكونات
        self.component_templates = {
            'navigation': {
                'bootstrap': '''
<nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">{{brand_name}}</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                {% for item in nav_items %}
                <li class="nav-item">
                    <a class="nav-link" href="{{item.href}}">{{item.text}}</a>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
</nav>''',
                'tailwind': '''
<nav class="bg-white shadow-lg">
    <div class="max-w-6xl mx-auto px-4">
        <div class="flex justify-between">
            <div class="flex space-x-7">
                <div>
                    <a href="#" class="flex items-center py-4 px-2">
                        <span class="font-semibold text-gray-500 text-lg">{{brand_name}}</span>
                    </a>
                </div>
            </div>
            <div class="hidden md:flex items-center space-x-3">
                {% for item in nav_items %}
                <a href="{{item.href}}" class="py-4 px-2 text-gray-500 hover:text-green-500 transition duration-300">{{item.text}}</a>
                {% endfor %}
            </div>
        </div>
    </div>
</nav>'''
            },
            'hero_section': {
                'bootstrap': '''
<section class="hero bg-primary text-white">
    <div class="container">
        <div class="row align-items-center min-vh-100">
            <div class="col-lg-6">
                <h1 class="display-4 fw-bold">{{hero_title}}</h1>
                <p class="lead">{{hero_description}}</p>
                <a href="{{cta_link}}" class="btn btn-light btn-lg">{{cta_text}}</a>
            </div>
            {% if hero_image %}
            <div class="col-lg-6">
                <img src="{{hero_image}}" class="img-fluid" alt="{{hero_title}}">
            </div>
            {% endif %}
        </div>
    </div>
</section>''',
                'tailwind': '''
<section class="bg-blue-600 text-white">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center min-h-screen">
            <div class="w-full lg:w-1/2">
                <h1 class="text-4xl lg:text-6xl font-bold leading-tight">{{hero_title}}</h1>
                <p class="text-xl lg:text-2xl mt-6 mb-8">{{hero_description}}</p>
                <a href="{{cta_link}}" class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition duration-300">{{cta_text}}</a>
            </div>
            {% if hero_image %}
            <div class="hidden lg:block lg:w-1/2">
                <img src="{{hero_image}}" class="w-full h-auto" alt="{{hero_title}}">
            </div>
            {% endif %}
        </div>
    </div>
</section>'''
            },
            'card_grid': {
                'bootstrap': '''
<div class="container my-5">
    <div class="row">
        {% for item in items %}
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                {% if item.image %}
                <img src="{{item.image}}" class="card-img-top" alt="{{item.title}}">
                {% endif %}
                <div class="card-body">
                    <h5 class="card-title">{{item.title}}</h5>
                    <p class="card-text">{{item.description}}</p>
                    {% if item.link %}
                    <a href="{{item.link}}" class="btn btn-primary">{{item.link_text or 'اقرأ المزيد'}}</a>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>''',
                'tailwind': '''
<div class="max-w-6xl mx-auto px-4 py-12">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for item in items %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
            {% if item.image %}
            <img src="{{item.image}}" class="w-full h-48 object-cover" alt="{{item.title}}">
            {% endif %}
            <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">{{item.title}}</h3>
                <p class="text-gray-600 mb-4">{{item.description}}</p>
                {% if item.link %}
                <a href="{{item.link}}" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition duration-300">{{item.link_text or 'اقرأ المزيد'}}</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
</div>'''
            }
        }
    
    def _setup_environment(self):
        """إعداد بيئة القوالب"""
        # إعداد مجلد الإخراج
        self.output_path = Path(self.config.output_directory)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # إعداد Jinja2
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        self.templates_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def generate_templates_from_extraction(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء قوالب من البيانات المستخرجة"""
        logging.info("بدء إنشاء القوالب من البيانات المستخرجة...")
        
        generation_results = {
            'templates_generated': {},
            'styles_generated': {},
            'scripts_generated': {},
            'components_created': {},
            'layouts_created': {},
            'generation_statistics': {}
        }
        
        try:
            # تحليل البنية المستخرجة
            structure_analysis = await self._analyze_extracted_structure(extraction_data)
            
            # إنشاء القوالب الأساسية
            generation_results['templates_generated'] = await self._generate_base_templates(structure_analysis)
            
            # إنشاء المكونات
            generation_results['components_created'] = await self._generate_components(structure_analysis)
            
            # إنشاء التخطيطات
            generation_results['layouts_created'] = await self._generate_layouts(structure_analysis)
            
            # إنشاء الأنماط
            generation_results['styles_generated'] = await self._generate_styles(structure_analysis)
            
            # إنشاء السكريبت
            generation_results['scripts_generated'] = await self._generate_scripts(structure_analysis)
            
            # حفظ الملفات
            await self._save_generated_files(generation_results)
            
            # إحصائيات الإنتاج
            generation_results['generation_statistics'] = self._calculate_generation_stats(generation_results)
            
        except Exception as e:
            logging.error(f"خطأ في إنتاج القوالب: {e}")
            generation_results['error'] = str(e)
        
        return generation_results
    
    async def _analyze_extracted_structure(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل البنية المستخرجة"""
        structure = {
            'layout_type': 'unknown',
            'components_detected': [],
            'navigation_structure': {},
            'content_sections': [],
            'interactive_elements': [],
            'style_patterns': {},
            'responsive_breakpoints': []
        }
        
        # تحليل البنية HTML
        if 'interface_extraction' in extraction_data:
            interface_data = extraction_data['interface_extraction']
            
            # تحليل HTML
            if 'html_files' in interface_data:
                structure['layout_type'] = self._detect_layout_type(interface_data['html_files'])
                structure['components_detected'] = self._detect_components(interface_data['html_files'])
            
            # تحليل CSS
            if 'css_files' in interface_data:
                structure['style_patterns'] = self._analyze_css_patterns(interface_data['css_files'])
                structure['responsive_breakpoints'] = self._extract_responsive_breakpoints(interface_data['css_files'])
        
        # تحليل البنية التقنية
        if 'technical_structure' in extraction_data:
            tech_data = extraction_data['technical_structure']
            
            if 'interactive_components' in tech_data:
                structure['interactive_elements'] = tech_data['interactive_components']
            
            if 'routing_system' in tech_data:
                structure['navigation_structure'] = self._analyze_navigation_structure(tech_data['routing_system'])
        
        return structure
    
    def _detect_layout_type(self, html_files: Dict) -> str:
        """كشف نوع التخطيط"""
        layout_indicators = {
            'header_nav_footer': 0,
            'sidebar_layout': 0,
            'single_page': 0,
            'multi_column': 0,
            'grid_layout': 0
        }
        
        for filename, file_data in html_files.items():
            content = file_data.get('content', '').lower()
            
            # فحص header/nav/footer
            if '<header' in content and '<nav' in content and '<footer' in content:
                layout_indicators['header_nav_footer'] += 3
            
            # فحص sidebar
            if 'sidebar' in content or 'aside' in content:
                layout_indicators['sidebar_layout'] += 2
            
            # فحص grid
            if 'grid' in content or 'row' in content or 'col-' in content:
                layout_indicators['grid_layout'] += 2
            
            # فحص multi-column
            if content.count('col-') > 3:
                layout_indicators['multi_column'] += 1
        
        # إرجاع النوع الأكثر احتمالاً
        return max(layout_indicators.items(), key=lambda x: x[1])[0]
    
    def _detect_components(self, html_files: Dict) -> List[str]:
        """كشف المكونات الموجودة"""
        components = set()
        
        component_patterns = {
            'navigation': ['<nav', 'navbar', 'menu'],
            'hero_section': ['hero', 'jumbotron', 'banner'],
            'card_grid': ['card', 'grid', 'row'],
            'carousel': ['carousel', 'slider', 'swiper'],
            'modal': ['modal', 'dialog', 'popup'],
            'accordion': ['accordion', 'collapse'],
            'tabs': ['tab', 'nav-tabs'],
            'form': ['<form', 'input', 'textarea'],
            'footer': ['<footer', 'footer'],
            'breadcrumb': ['breadcrumb', 'navigation']
        }
        
        for filename, file_data in html_files.items():
            content = file_data.get('content', '').lower()
            
            for component, patterns in component_patterns.items():
                if any(pattern in content for pattern in patterns):
                    components.add(component)
        
        return list(components)
    
    def _analyze_css_patterns(self, css_files: Dict) -> Dict[str, Any]:
        """تحليل أنماط CSS"""
        patterns = {
            'color_scheme': {},
            'typography': {},
            'spacing': {},
            'layout_methods': [],
            'animations': []
        }
        
        for filename, file_data in css_files.items():
            content = file_data.get('content', '')
            
            # استخراج الألوان
            color_matches = re.findall(r'color:\s*([^;]+);', content)
            bg_color_matches = re.findall(r'background-color:\s*([^;]+);', content)
            
            # استخراج الخطوط
            font_matches = re.findall(r'font-family:\s*([^;]+);', content)
            
            # كشف طرق التخطيط
            if 'display: grid' in content:
                patterns['layout_methods'].append('css_grid')
            if 'display: flex' in content:
                patterns['layout_methods'].append('flexbox')
            
            # كشف الحركات
            if '@keyframes' in content or 'animation:' in content:
                patterns['animations'].append('css_animations')
        
        return patterns
    
    def _extract_responsive_breakpoints(self, css_files: Dict) -> List[str]:
        """استخراج نقاط الكسر المتجاوبة"""
        breakpoints = set()
        
        for filename, file_data in css_files.items():
            content = file_data.get('content', '')
            
            # البحث عن media queries
            media_queries = re.findall(r'@media[^{]+\(([^)]+)\)', content)
            for query in media_queries:
                if 'max-width' in query or 'min-width' in query:
                    breakpoints.add(query.strip())
        
        return list(breakpoints)
    
    def _analyze_navigation_structure(self, routing_data: Dict) -> Dict[str, Any]:
        """تحليل بنية التنقل"""
        nav_structure = {
            'primary_links': [],
            'secondary_links': [],
            'breadcrumbs': False,
            'pagination': False
        }
        
        if 'internal_links' in routing_data:
            # تصنيف الروابط
            for link in routing_data['internal_links']:
                if len(link.get('text', '')) > 0:
                    if any(word in link['text'].lower() for word in ['home', 'about', 'contact', 'services']):
                        nav_structure['primary_links'].append(link)
                    else:
                        nav_structure['secondary_links'].append(link)
        
        return nav_structure
    
    async def _generate_base_templates(self, structure: Dict[str, Any]) -> Dict[str, str]:
        """إنشاء القوالب الأساسية"""
        templates = {}
        
        # قالب أساسي
        base_template = self._create_base_template(structure)
        templates['base.html'] = base_template
        
        # قالب الصفحة الرئيسية
        index_template = self._create_index_template(structure)
        templates['index.html'] = index_template
        
        # قوالب إضافية حسب النوع
        layout_type = structure.get('layout_type', 'header_nav_footer')
        if layout_type == 'sidebar_layout':
            sidebar_template = self._create_sidebar_template(structure)
            templates['sidebar_layout.html'] = sidebar_template
        
        return templates
    
    def _create_base_template(self, structure: Dict[str, Any]) -> str:
        """إنشاء القالب الأساسي"""
        css_framework = self.config.css_framework
        
        # روابط CSS حسب الإطار
        css_links = {
            'bootstrap': '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">',
            'tailwind': '<script src="https://cdn.tailwindcss.com"></script>',
            'bulma': '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">',
            'vanilla': '<link rel="stylesheet" href="/static/css/style.css">'
        }
        
        # سكريبت JS حسب الإطار
        js_scripts = {
            'bootstrap': '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>',
            'tailwind': '',
            'bulma': '',
            'vanilla': '<script src="/static/js/main.js"></script>'
        }
        
        base_template = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title or 'موقع مُنشأ تلقائياً' }}}}</title>
    
    {css_links.get(css_framework, css_links['vanilla'])}
    
    {{% if config.include_responsive %}}
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    {{% endif %}}
    
    <style>
        /* أنماط مخصصة */
        body {{
            font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        {{% if config.include_animations %}}
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        {{% endif %}}
    </style>
    
    {{{{ extra_head | safe }}}}
</head>
<body>
    {{{{ content | safe }}}}
    
    {js_scripts.get(css_framework, js_scripts['vanilla'])}
    
    {% if self.config.include_interactions %}
    <script>
        // تفعيل التفاعلات
        document.addEventListener('DOMContentLoaded', function() {{
            // إضافة تأثيرات الحركة
            const elements = document.querySelectorAll('[data-animate]');
            elements.forEach(el => {{
                el.classList.add('fade-in');
            }});
        }});
    </script>
    {% endif %}
    
    {{{{ extra_scripts | safe }}}}
</body>
</html>'''
        
        return base_template
    
    def _create_index_template(self, structure: Dict[str, Any]) -> str:
        """إنشاء قالب الصفحة الرئيسية"""
        components = structure.get('components_detected', [])
        css_framework = self.config.css_framework
        
        # بناء المحتوى حسب المكونات المكتشفة
        content_sections = []
        
        # إضافة التنقل
        if 'navigation' in components:
            nav_template = self.component_templates['navigation'][css_framework]
            content_sections.append(nav_template)
        
        # إضافة Hero Section
        if 'hero_section' in components:
            hero_template = self.component_templates['hero_section'][css_framework]
            content_sections.append(hero_template)
        
        # إضافة Card Grid
        if 'card_grid' in components:
            card_template = self.component_templates['card_grid'][css_framework]
            content_sections.append(card_template)
        
        # دمج المحتوى
        content = '\n\n'.join(content_sections)
        
        index_template = f'''{{{{ extends "base.html" }}}}

{{{{ block content }}}}
{content}
{{{{ endblock }}}}'''
        
        return index_template
    
    async def _generate_components(self, structure: Dict[str, Any]) -> Dict[str, str]:
        """إنشاء المكونات المنفصلة"""
        components = {}
        detected_components = structure.get('components_detected', [])
        css_framework = self.config.css_framework
        
        for component in detected_components:
            if component in self.component_templates:
                template_content = self.component_templates[component][css_framework]
                components[f"{component}.html"] = template_content
        
        return components
    
    async def _generate_layouts(self, structure: Dict[str, Any]) -> Dict[str, str]:
        """إنشاء تخطيطات مختلفة"""
        layouts = {}
        layout_type = structure.get('layout_type', 'header_nav_footer')
        
        if layout_type == 'sidebar_layout':
            layouts['sidebar_layout.html'] = self._create_sidebar_layout()
        elif layout_type == 'grid_layout':
            layouts['grid_layout.html'] = self._create_grid_layout()
        
        return layouts
    
    def _create_sidebar_layout(self) -> str:
        """إنشاء تخطيط الشريط الجانبي"""
        css_framework = self.config.css_framework
        
        if css_framework == 'bootstrap':
            return '''
<div class="container-fluid">
    <div class="row">
        <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
            <div class="sidebar-sticky">
                <ul class="nav flex-column">
                    {% for item in sidebar_items %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{item.href}}">{{item.text}}</a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </nav>
        
        <main class="col-md-9 ml-sm-auto col-lg-10 px-md-4">
            {{ content | safe }}
        </main>
    </div>
</div>'''
        else:  # Tailwind
            return '''
<div class="flex">
    <nav class="bg-gray-800 text-white w-64 min-h-screen p-4">
        <ul class="space-y-2">
            {% for item in sidebar_items %}
            <li>
                <a href="{{item.href}}" class="block py-2 px-4 rounded hover:bg-gray-700">{{item.text}}</a>
            </li>
            {% endfor %}
        </ul>
    </nav>
    
    <main class="flex-1 p-6">
        {{ content | safe }}
    </main>
</div>'''
    
    def _create_grid_layout(self) -> str:
        """إنشاء تخطيط الشبكة"""
        css_framework = self.config.css_framework
        
        if css_framework == 'bootstrap':
            return '''
<div class="container">
    <div class="row">
        {% for item in grid_items %}
        <div class="col-lg-{{item.size or 4}} col-md-6 mb-4">
            <div class="card">
                <div class="card-body">
                    {{ item.content | safe }}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>'''
        else:  # Tailwind
            return '''
<div class="max-w-6xl mx-auto px-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for item in grid_items %}
        <div class="bg-white rounded-lg shadow-md p-6">
            {{ item.content | safe }}
        </div>
        {% endfor %}
    </div>
</div>'''
    
    async def _generate_styles(self, structure: Dict[str, Any]) -> Dict[str, str]:
        """إنشاء ملفات الأنماط"""
        styles = {}
        
        # CSS مخصص
        custom_css = self._generate_custom_css(structure)
        styles['custom.css'] = custom_css
        
        # CSS متجاوب
        if self.config.include_responsive:
            responsive_css = self._generate_responsive_css(structure)
            styles['responsive.css'] = responsive_css
        
        return styles
    
    def _generate_custom_css(self, structure: Dict[str, Any]) -> str:
        """إنشاء CSS مخصص"""
        style_patterns = structure.get('style_patterns', {})
        
        css = '''/* أنماط مخصصة مُنشأة تلقائياً */

:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
}

body {
    font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--dark-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* مكونات مخصصة */
.btn {
    display: inline-block;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 5px;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
}

.card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
}'''

        if self.config.include_animations:
            css += '''

/* حركات مخصصة */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
}

.fade-in {
    animation: fadeIn 0.6s ease-out;
}

.slide-in {
    animation: slideIn 0.6s ease-out;
}'''

        return css
    
    def _generate_responsive_css(self, structure: Dict[str, Any]) -> str:
        """إنشاء CSS متجاوب"""
        breakpoints = structure.get('responsive_breakpoints', [])
        
        css = '''/* تصميم متجاوب */

/* الهواتف الصغيرة */
@media (max-width: 576px) {
    .container {
        padding: 0 10px;
    }
    
    .btn {
        width: 100%;
        margin-bottom: 10px;
    }
    
    .card {
        margin-bottom: 20px;
    }
}

/* الأجهزة اللوحية */
@media (min-width: 768px) and (max-width: 991px) {
    .container {
        max-width: 750px;
    }
}

/* أجهزة سطح المكتب */
@media (min-width: 992px) {
    .container {
        max-width: 970px;
    }
}

/* الشاشات الكبيرة */
@media (min-width: 1200px) {
    .container {
        max-width: 1170px;
    }
}'''
        
        return css
    
    async def _generate_scripts(self, structure: Dict[str, Any]) -> Dict[str, str]:
        """إنشاء ملفات JavaScript"""
        scripts = {}
        
        # سكريبت أساسي
        main_js = self._generate_main_js(structure)
        scripts['main.js'] = main_js
        
        # سكريبت التفاعلات
        if self.config.include_interactions:
            interactions_js = self._generate_interactions_js(structure)
            scripts['interactions.js'] = interactions_js
        
        return scripts
    
    def _generate_main_js(self, structure: Dict[str, Any]) -> str:
        """إنشاء JavaScript أساسي"""
        js = '''// سكريبت رئيسي مُنشأ تلقائياً

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل الموقع بنجاح');
    
    // تفعيل الحركات
    animateElements();
    
    // تفعيل التنقل
    initNavigation();
    
    // تفعيل النماذج
    initForms();
});

function animateElements() {
    const elements = document.querySelectorAll('[data-animate]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    elements.forEach(el => observer.observe(el));
}

function initNavigation() {
    // تفعيل التنقل المحمول
    const toggleBtn = document.querySelector('.navbar-toggler');
    const navMenu = document.querySelector('.navbar-collapse');
    
    if (toggleBtn && navMenu) {
        toggleBtn.addEventListener('click', () => {
            navMenu.classList.toggle('show');
        });
    }
}

function initForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}'''
        
        return js
    
    def _generate_interactions_js(self, structure: Dict[str, Any]) -> str:
        """إنشاء JavaScript للتفاعلات"""
        interactive_elements = structure.get('interactive_elements', {})
        
        js = '''// تفاعلات متقدمة

// Modal handling
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                modal.style.display = 'block';
                modal.classList.add('show');
            }
        });
    });
    
    // إغلاق المودال
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-close') || e.target.classList.contains('modal-backdrop')) {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                modal.style.display = 'none';
                modal.classList.remove('show');
            });
        }
    });
}

// Carousel handling
function initCarousels() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
        const slides = carousel.querySelectorAll('.slide');
        const prevBtn = carousel.querySelector('.prev');
        const nextBtn = carousel.querySelector('.next');
        let currentSlide = 0;
        
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.style.display = i === index ? 'block' : 'none';
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                currentSlide = currentSlide > 0 ? currentSlide - 1 : slides.length - 1;
                showSlide(currentSlide);
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                currentSlide = currentSlide < slides.length - 1 ? currentSlide + 1 : 0;
                showSlide(currentSlide);
            });
        }
        
        // عرض الشريحة الأولى
        showSlide(0);
    });
}

// تفعيل جميع التفاعلات
document.addEventListener('DOMContentLoaded', function() {
    initModals();
    initCarousels();
});'''
        
        return js
    
    async def _save_generated_files(self, generation_results: Dict[str, Any]):
        """حفظ الملفات المُنشأة"""
        # حفظ القوالب
        templates_dir = self.output_path / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        for filename, content in generation_results['templates_generated'].items():
            file_path = templates_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # حفظ المكونات
        components_dir = self.output_path / 'components'
        components_dir.mkdir(exist_ok=True)
        
        for filename, content in generation_results['components_created'].items():
            file_path = components_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # حفظ الأنماط
        css_dir = self.output_path / 'static' / 'css'
        css_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in generation_results['styles_generated'].items():
            file_path = css_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # حفظ السكريبت
        js_dir = self.output_path / 'static' / 'js'
        js_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in generation_results['scripts_generated'].items():
            file_path = js_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _calculate_generation_stats(self, generation_results: Dict[str, Any]) -> Dict[str, int]:
        """حساب إحصائيات الإنتاج"""
        return {
            'templates_count': len(generation_results['templates_generated']),
            'components_count': len(generation_results['components_created']),
            'layouts_count': len(generation_results['layouts_created']),
            'css_files_count': len(generation_results['styles_generated']),
            'js_files_count': len(generation_results['scripts_generated']),
            'total_files': sum([
                len(generation_results['templates_generated']),
                len(generation_results['components_created']),
                len(generation_results['layouts_created']),
                len(generation_results['styles_generated']),
                len(generation_results['scripts_generated'])
            ])
        }
