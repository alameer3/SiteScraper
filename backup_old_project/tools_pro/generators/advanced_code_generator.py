
"""
Advanced Code Generator - مولد الكود المتقدم
ينشئ كود مطابق للموقع المستخرج بناء على التحليل العميق
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import re
from jinja2 import Environment, FileSystemLoader, Template

class AdvancedCodeGenerator:
    """مولد الكود المتقدم"""

    def __init__(self, output_directory: str = "generated_code"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # إعداد محرك القوالب
        self.template_env = Environment(
            loader=FileSystemLoader('templates/code_templates'),
            autoescape=True
        )
        
        # قوالب الكود الافتراضية
        self.code_templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, str]:
        """تهيئة قوالب الكود"""
        return {
            'html_template': '''<!DOCTYPE html>
<html lang="{{ language }}">
<head>
    <meta charset="{{ charset }}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    {% for css_file in css_files %}
    <link rel="stylesheet" href="{{ css_file }}">
    {% endfor %}
</head>
<body>
    {{ body_content }}
    
    {% for js_file in js_files %}
    <script src="{{ js_file }}"></script>
    {% endfor %}
</body>
</html>''',

            'react_component': '''import React{% if has_state %}, { useState, useEffect }{% endif %} from 'react';
{% for import_statement in imports %}
{{ import_statement }}
{% endfor %}

const {{ component_name }} = ({% if props %}{ {{ props|join(', ') }} }{% endif %}) => {
    {% if state_variables %}
    {% for state_var in state_variables %}
    const [{{ state_var.name }}, set{{ state_var.name|title }}] = useState({{ state_var.initial_value }});
    {% endfor %}
    {% endif %}
    
    {% if effects %}
    {% for effect in effects %}
    useEffect(() => {
        {{ effect.code }}
    }, [{{ effect.dependencies|join(', ') }}]);
    {% endfor %}
    {% endif %}
    
    {% if functions %}
    {% for function in functions %}
    const {{ function.name }} = ({{ function.parameters|join(', ') }}) => {
        {{ function.body }}
    };
    {% endfor %}
    {% endif %}
    
    return (
        {{ jsx_content }}
    );
};

export default {{ component_name }};''',

            'vue_component': '''<template>
    {{ template_content }}
</template>

<script>
{% if composition_api %}
import { ref, reactive, computed, onMounted } from 'vue';

export default {
    name: '{{ component_name }}',
    setup(props) {
        {% for data_item in data %}
        const {{ data_item.name }} = ref({{ data_item.initial_value }});
        {% endfor %}
        
        {% for computed_prop in computed_properties %}
        const {{ computed_prop.name }} = computed(() => {
            {{ computed_prop.logic }}
        });
        {% endfor %}
        
        {% for method in methods %}
        const {{ method.name }} = ({{ method.parameters|join(', ') }}) => {
            {{ method.body }}
        };
        {% endfor %}
        
        onMounted(() => {
            {{ mounted_logic }}
        });
        
        return {
            {% for item in return_items %}
            {{ item }},
            {% endfor %}
        };
    }
};
{% else %}
export default {
    name: '{{ component_name }}',
    props: {{ props }},
    data() {
        return {{ data }};
    },
    computed: {{ computed }},
    methods: {{ methods }},
    mounted() {
        {{ mounted }}
    }
};
{% endif %}
</script>

<style scoped>
{{ styles }}
</style>''',

            'flask_route': '''from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models import {{ models|join(', ') }}
{% for import_statement in additional_imports %}
{{ import_statement }}
{% endfor %}

{{ blueprint_name }}_bp = Blueprint('{{ blueprint_name }}', __name__{% if url_prefix %}, url_prefix='{{ url_prefix }}'{% endif %})

{% for route in routes %}
@{{ blueprint_name }}_bp.route('{{ route.path }}'{% if route.methods %}, methods={{ route.methods }}{% endif %})
def {{ route.function_name }}({% if route.parameters %}{{ route.parameters|join(', ') }}{% endif %}):
    """{{ route.description }}"""
    try:
        {% if route.logic %}
        {{ route.logic }}
        {% else %}
        # Add your logic here
        pass
        {% endif %}
        
        {% if route.template %}
        return render_template('{{ route.template }}', **locals())
        {% elif route.returns_json %}
        return jsonify({'success': True, 'data': data})
        {% else %}
        return redirect(url_for('{{ route.redirect_to }}'))
        {% endif %}
    except Exception as e:
        {% if route.returns_json %}
        return jsonify({'success': False, 'error': str(e)}), 500
        {% else %}
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('{{ route.error_redirect }}'))
        {% endif %}

{% endfor %}''',

            'css_styles': ''':root {
    {% for var in css_variables %}
    {{ var.name }}: {{ var.value }};
    {% endfor %}
}

{% for selector in selectors %}
{{ selector.name }} {
    {% for property in selector.properties %}
    {{ property.name }}: {{ property.value }};
    {% endfor %}
}

{% endfor %}

/* Media Queries */
{% for breakpoint in media_queries %}
@media {{ breakpoint.condition }} {
    {% for selector in breakpoint.selectors %}
    {{ selector.name }} {
        {% for property in selector.properties %}
        {{ property.name }}: {{ property.value }};
        {% endfor %}
    }
    {% endfor %}
}
{% endfor %}''',

            'javascript_module': '''{% if is_module %}
// ES6 Module
{% for import_statement in imports %}
{{ import_statement }}
{% endfor %}
{% endif %}

{% if class_definition %}
class {{ class_name }} {
    constructor({{ constructor_params|join(', ') }}) {
        {{ constructor_body }}
    }
    
    {% for method in methods %}
    {{ method.name }}({{ method.parameters|join(', ') }}) {
        {{ method.body }}
    }
    {% endfor %}
}
{% endif %}

{% for function in functions %}
{% if function.is_async %}async {% endif %}function {{ function.name }}({{ function.parameters|join(', ') }}) {
    {{ function.body }}
}
{% endfor %}

{% if event_listeners %}
// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    {% for listener in event_listeners %}
    {{ listener.element }}.addEventListener('{{ listener.event }}', {{ listener.handler }});
    {% endfor %}
});
{% endif %}

{% if is_module %}
// Exports
export {% if default_export %}default {% endif %}{ {{ exports|join(', ') }} };
{% endif %}'''
        }

    async def generate_complete_website(self, extraction_data: Dict[str, Any], 
                                      framework: str = 'html', 
                                      target_directory: Optional[str] = None) -> Dict[str, Any]:
        """إنشاء موقع كامل من البيانات المستخرجة"""
        self.logger.info(f"إنشاء موقع كامل باستخدام {framework}")
        
        if target_directory:
            output_path = Path(target_directory)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_directory / f"generated_site_{timestamp}"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        generation_result = {
            'output_directory': str(output_path),
            'generated_files': [],
            'framework_used': framework,
            'generation_summary': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            # تحليل البيانات المستخرجة
            analysis = self._analyze_extraction_data(extraction_data)
            
            if framework.lower() == 'react':
                result = await self._generate_react_app(analysis, output_path)
            elif framework.lower() == 'vue':
                result = await self._generate_vue_app(analysis, output_path)
            elif framework.lower() == 'flask':
                result = await self._generate_flask_app(analysis, output_path)
            else:
                result = await self._generate_html_website(analysis, output_path)
            
            generation_result.update(result)
            
            # إنشاء ملف README
            await self._generate_readme(analysis, output_path)
            
            self.logger.info(f"تم إنشاء الموقع بنجاح في {output_path}")
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء الموقع: {e}")
            generation_result['errors'].append(str(e))
        
        return generation_result

    def _analyze_extraction_data(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل البيانات المستخرجة لتحديد بنية الموقع"""
        analysis = {
            'pages': [],
            'components': [],
            'styles': {},
            'scripts': {},
            'assets': {},
            'routing': {},
            'database_schema': {},
            'api_endpoints': []
        }
        
        # تحليل الواجهة
        interface_data = extraction_data.get('interface_extraction', {})
        
        # تحليل HTML
        html_files = interface_data.get('html_files', {})
        for filename, file_data in html_files.items():
            page_analysis = self._analyze_html_structure(file_data.get('content', ''))
            analysis['pages'].append({
                'filename': filename,
                'title': page_analysis.get('title', ''),
                'components': page_analysis.get('components', []),
                'forms': page_analysis.get('forms', []),
                'navigation': page_analysis.get('navigation', {})
            })
        
        # تحليل CSS
        css_files = interface_data.get('css_files', {})
        for filename, file_data in css_files.items():
            css_analysis = self._analyze_css_structure(file_data.get('content', ''))
            analysis['styles'][filename] = css_analysis
        
        # تحليل JavaScript
        js_files = interface_data.get('javascript_files', {})
        for filename, file_data in js_files.items():
            js_analysis = self._analyze_js_structure(file_data.get('content', ''))
            analysis['scripts'][filename] = js_analysis
        
        # تحليل APIs
        technical_data = extraction_data.get('technical_structure', {})
        analysis['api_endpoints'] = technical_data.get('api_endpoints', [])
        
        return analysis

    def _analyze_html_structure(self, html_content: str) -> Dict[str, Any]:
        """تحليل بنية HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        return {
            'title': soup.find('title').get_text() if soup.find('title') else '',
            'components': self._extract_html_components(soup),
            'forms': self._extract_forms_data(soup),
            'navigation': self._extract_navigation_data(soup)
        }

    def _extract_html_components(self, soup) -> List[Dict]:
        """استخراج مكونات HTML"""
        components = []
        
        # Header
        header = soup.find('header')
        if header:
            components.append({
                'type': 'header',
                'content': str(header),
                'classes': header.get('class', [])
            })
        
        # Navigation
        nav = soup.find('nav')
        if nav:
            components.append({
                'type': 'navigation',
                'content': str(nav),
                'classes': nav.get('class', [])
            })
        
        # Main content
        main = soup.find('main') or soup.find('div', class_='main')
        if main:
            components.append({
                'type': 'main',
                'content': str(main),
                'classes': main.get('class', [])
            })
        
        # Footer
        footer = soup.find('footer')
        if footer:
            components.append({
                'type': 'footer',
                'content': str(footer),
                'classes': footer.get('class', [])
            })
        
        return components

    def _extract_forms_data(self, soup) -> List[Dict]:
        """استخراج بيانات النماذج"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'fields': []
            }
            
            for field in form.find_all(['input', 'textarea', 'select']):
                form_data['fields'].append({
                    'tag': field.name,
                    'type': field.get('type', ''),
                    'name': field.get('name', ''),
                    'placeholder': field.get('placeholder', ''),
                    'required': field.has_attr('required')
                })
            
            forms.append(form_data)
        
        return forms

    def _extract_navigation_data(self, soup) -> Dict:
        """استخراج بيانات التنقل"""
        nav_data = {'links': []}
        
        nav = soup.find('nav')
        if nav:
            for link in nav.find_all('a'):
                nav_data['links'].append({
                    'text': link.get_text().strip(),
                    'href': link.get('href', ''),
                    'classes': link.get('class', [])
                })
        
        return nav_data

    def _analyze_css_structure(self, css_content: str) -> Dict[str, Any]:
        """تحليل بنية CSS"""
        analysis = {
            'selectors': [],
            'variables': [],
            'media_queries': [],
            'keyframes': []
        }
        
        # استخراج المتغيرات
        var_pattern = re.compile(r'--([^:]+):\s*([^;]+);')
        for match in var_pattern.finditer(css_content):
            analysis['variables'].append({
                'name': f'--{match.group(1).strip()}',
                'value': match.group(2).strip()
            })
        
        # استخراج الـ selectors
        selector_pattern = re.compile(r'([^{]+)\s*{([^}]+)}')
        for match in selector_pattern.finditer(css_content):
            selector_name = match.group(1).strip()
            properties_text = match.group(2).strip()
            
            properties = []
            for prop_line in properties_text.split(';'):
                if ':' in prop_line:
                    prop_parts = prop_line.split(':', 1)
                    properties.append({
                        'name': prop_parts[0].strip(),
                        'value': prop_parts[1].strip()
                    })
            
            analysis['selectors'].append({
                'name': selector_name,
                'properties': properties
            })
        
        return analysis

    def _analyze_js_structure(self, js_content: str) -> Dict[str, Any]:
        """تحليل بنية JavaScript"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'event_listeners': []
        }
        
        # استخراج الدوال
        function_pattern = re.compile(r'function\s+(\w+)\s*\(([^)]*)\)\s*{', re.MULTILINE)
        for match in function_pattern.finditer(js_content):
            analysis['functions'].append({
                'name': match.group(1),
                'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                'is_async': False
            })
        
        # استخراج Arrow Functions
        arrow_pattern = re.compile(r'(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', re.MULTILINE)
        for match in arrow_pattern.finditer(js_content):
            analysis['functions'].append({
                'name': match.group(1),
                'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                'is_async': 'async' in js_content[max(0, match.start()-10):match.start()]
            })
        
        # استخراج الكلاسات
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{', re.MULTILINE)
        for match in class_pattern.finditer(js_content):
            analysis['classes'].append({
                'name': match.group(1),
                'extends': match.group(2) if match.group(2) else None
            })
        
        return analysis

    async def _generate_react_app(self, analysis: Dict, output_path: Path) -> Dict[str, Any]:
        """إنشاء تطبيق React"""
        result = {
            'generated_files': [],
            'generation_summary': {'framework': 'React', 'components': 0, 'pages': 0}
        }
        
        # إنشاء بنية المجلدات
        (output_path / 'src' / 'components').mkdir(parents=True, exist_ok=True)
        (output_path / 'src' / 'pages').mkdir(parents=True, exist_ok=True)
        (output_path / 'src' / 'styles').mkdir(parents=True, exist_ok=True)
        (output_path / 'public').mkdir(parents=True, exist_ok=True)
        
        # إنشاء package.json
        package_json = {
            "name": "generated-react-app",
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "react-router-dom": "^6.0.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            }
        }
        
        with open(output_path / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        result['generated_files'].append('package.json')
        
        # إنشاء App.js الرئيسي
        app_js_content = '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/App.css';

// Import components
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';

function App() {
    return (
        <Router>
            <div className="App">
                <Header />
                <main>
                    <Routes>
                        <Route path="/" element={<Home />} />
                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    );
}

export default App;'''
        
        with open(output_path / 'src' / 'App.js', 'w') as f:
            f.write(app_js_content)
        result['generated_files'].append('src/App.js')
        
        # إنشاء مكونات من التحليل
        for page in analysis['pages']:
            components = page.get('components', [])
            
            for component in components:
                component_name = component['type'].title()
                component_content = self._generate_react_component(component_name, component)
                
                component_file = output_path / 'src' / 'components' / f'{component_name}.js'
                with open(component_file, 'w') as f:
                    f.write(component_content)
                result['generated_files'].append(f'src/components/{component_name}.js')
                result['generation_summary']['components'] += 1
        
        # إنشاء صفحة Home
        home_content = '''import React from 'react';

const Home = () => {
    return (
        <div className="home-page">
            <h1>مرحباً بك في الموقع المُنشأ</h1>
            <p>تم إنشاء هذا الموقع باستخدام محرك النسخ الذكي</p>
        </div>
    );
};

export default Home;'''
        
        with open(output_path / 'src' / 'pages' / 'Home.js', 'w') as f:
            f.write(home_content)
        result['generated_files'].append('src/pages/Home.js')
        result['generation_summary']['pages'] += 1
        
        return result

    def _generate_react_component(self, component_name: str, component_data: Dict) -> str:
        """إنشاء مكون React"""
        template = Template(self.code_templates['react_component'])
        
        return template.render(
            component_name=component_name,
            has_state=False,
            imports=[],
            props=[],
            state_variables=[],
            effects=[],
            functions=[],
            jsx_content=f'<div className="{component_name.lower()}">\n            {component_data.get("content", "")}\n        </div>'
        )

    async def _generate_vue_app(self, analysis: Dict, output_path: Path) -> Dict[str, Any]:
        """إنشاء تطبيق Vue"""
        result = {
            'generated_files': [],
            'generation_summary': {'framework': 'Vue.js', 'components': 0, 'pages': 0}
        }
        
        # إنشاء بنية المجلدات
        (output_path / 'src' / 'components').mkdir(parents=True, exist_ok=True)
        (output_path / 'src' / 'views').mkdir(parents=True, exist_ok=True)
        (output_path / 'src' / 'router').mkdir(parents=True, exist_ok=True)
        (output_path / 'public').mkdir(parents=True, exist_ok=True)
        
        # إنشاء package.json
        package_json = {
            "name": "generated-vue-app",
            "version": "1.0.0",
            "scripts": {
                "serve": "vue-cli-service serve",
                "build": "vue-cli-service build"
            },
            "dependencies": {
                "vue": "^3.0.0",
                "vue-router": "^4.0.0"
            }
        }
        
        with open(output_path / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        result['generated_files'].append('package.json')
        
        return result

    async def _generate_flask_app(self, analysis: Dict, output_path: Path) -> Dict[str, Any]:
        """إنشاء تطبيق Flask"""
        result = {
            'generated_files': [],
            'generation_summary': {'framework': 'Flask', 'routes': 0, 'templates': 0}
        }
        
        # إنشاء بنية المجلدات
        (output_path / 'templates').mkdir(parents=True, exist_ok=True)
        (output_path / 'static' / 'css').mkdir(parents=True, exist_ok=True)
        (output_path / 'static' / 'js').mkdir(parents=True, exist_ok=True)
        
        # إنشاء app.py
        app_py_content = '''from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)'''
        
        with open(output_path / 'app.py', 'w') as f:
            f.write(app_py_content)
        result['generated_files'].append('app.py')
        
        # إنشاء requirements.txt
        requirements = '''Flask==2.3.3
Jinja2==3.1.2'''
        
        with open(output_path / 'requirements.txt', 'w') as f:
            f.write(requirements)
        result['generated_files'].append('requirements.txt')
        
        return result

    async def _generate_html_website(self, analysis: Dict, output_path: Path) -> Dict[str, Any]:
        """إنشاء موقع HTML تقليدي"""
        result = {
            'generated_files': [],
            'generation_summary': {'framework': 'HTML/CSS/JS', 'pages': 0, 'assets': 0}
        }
        
        # إنشاء بنية المجلدات
        (output_path / 'css').mkdir(parents=True, exist_ok=True)
        (output_path / 'js').mkdir(parents=True, exist_ok=True)
        (output_path / 'images').mkdir(parents=True, exist_ok=True)
        
        # إنشاء صفحة index.html
        template = Template(self.code_templates['html_template'])
        
        html_content = template.render(
            language='ar',
            charset='UTF-8',
            title='الموقع المُنشأ',
            css_files=['css/style.css'],
            js_files=['js/main.js'],
            body_content='<h1>مرحباً بك في الموقع المُنشأ</h1>'
        )
        
        with open(output_path / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        result['generated_files'].append('index.html')
        result['generation_summary']['pages'] += 1
        
        # إنشاء ملف CSS أساسي
        css_content = '''/* الأنماط الأساسية */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    direction: rtl;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: #333;
    color: white;
    padding: 1rem 0;
}

main {
    padding: 2rem 0;
    min-height: 70vh;
}

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 1rem 0;
}'''
        
        with open(output_path / 'css' / 'style.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        result['generated_files'].append('css/style.css')
        
        # إنشاء ملف JavaScript أساسي
        js_content = '''// JavaScript أساسي
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل الموقع بنجاح');
    
    // إضافة تفاعلات أساسية
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('تم النقر على الزر');
        });
    });
});'''
        
        with open(output_path / 'js' / 'main.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        result['generated_files'].append('js/main.js')
        
        return result

    async def _generate_readme(self, analysis: Dict, output_path: Path):
        """إنشاء ملف README"""
        readme_content = f"""# الموقع المُنشأ

تم إنشاء هذا الموقع باستخدام محرك النسخ الذكي المتطور.

## معلومات المشروع

- تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- عدد الصفحات المحللة: {len(analysis.get('pages', []))}
- عدد المكونات: {len(analysis.get('components', []))}

## بنية المشروع

```
{output_path.name}/
├── src/          # الكود المصدري
├── public/       # الملفات العامة
├── styles/       # ملفات الأنماط
└── README.md     # هذا الملف
```

## تشغيل المشروع

### متطلبات النظام
- Node.js (للمشاريع React/Vue)
- Python (لمشاريع Flask)

### خطوات التشغيل
1. تثبيت المتطلبات
2. تشغيل الخادم المحلي
3. فتح المتصفح

## الميزات المُنشأة

- ✅ تصميم متجاوب
- ✅ تنقل سهل
- ✅ أكواد منظمة
- ✅ تعليقات توضيحية

## التطوير

يمكنك تطوير هذا المشروع بإضافة:
- المزيد من الصفحات
- وظائف تفاعلية
- ربط قاعدة بيانات
- نظام مصادقة

---
تم الإنشاء بواسطة محرك النسخ الذكي
"""
        
        with open(output_path / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
