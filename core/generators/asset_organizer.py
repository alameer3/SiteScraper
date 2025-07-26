
"""
منظم الملفات والموارد - تنظيم الملفات المستخرجة في هيكل مشروع
"""

import os
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class OrganizationConfig:
    """إعدادات تنظيم الملفات"""
    output_directory: str = "organized_project"
    create_structure: bool = True
    group_by_type: bool = True
    minify_assets: bool = False
    optimize_images: bool = True

class AssetOrganizer:
    """منظم الملفات والموارد المتقدم"""
    
    def __init__(self, config: OrganizationConfig = None):
        self.config = config or OrganizationConfig()
        self.logger = logging.getLogger(__name__)
        
        # هيكل المشروع القياسي
        self.project_structure = {
            'assets': {
                'css': [],
                'js': [],
                'images': [],
                'fonts': [],
                'videos': [],
                'audio': []
            },
            'templates': [],
            'components': [],
            'pages': [],
            'api': [],
            'config': [],
            'docs': []
        }
    
    async def organize_extracted_assets(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تنظيم الملفات المستخرجة"""
        self.logger.info("بدء تنظيم الملفات المستخرجة...")
        
        organization_results = {
            'project_structure': {},
            'files_organized': 0,
            'folders_created': 0,
            'optimization_results': {},
            'manifest': {}
        }
        
        try:
            # إنشاء هيكل المشروع
            project_path = Path(self.config.output_directory)
            project_path.mkdir(parents=True, exist_ok=True)
            
            # تنظيم الملفات حسب النوع
            if 'assets' in extraction_data:
                await self._organize_assets(extraction_data['assets'], project_path)
            
            # تنظيم القوالب والمكونات
            if 'templates' in extraction_data:
                await self._organize_templates(extraction_data['templates'], project_path)
            
            # تنظيم الكود والوظائف
            if 'functions' in extraction_data:
                await self._organize_code(extraction_data['functions'], project_path)
            
            # إنشاء ملف التكوين
            await self._create_project_config(extraction_data, project_path)
            
            # إنشاء الوثائق
            await self._create_documentation(extraction_data, project_path)
            
            # إحصائيات التنظيم
            organization_results.update({
                'project_path': str(project_path),
                'files_organized': self._count_files(project_path),
                'folders_created': len(list(project_path.rglob('*/'))),
                'structure_created': self.project_structure
            })
            
        except Exception as e:
            self.logger.error(f"خطأ في تنظيم الملفات: {e}")
            organization_results['error'] = str(e)
        
        return organization_results
    
    async def _organize_assets(self, assets: Dict[str, Any], project_path: Path):
        """تنظيم ملفات الموارد"""
        assets_path = project_path / "assets"
        
        # CSS Files
        if 'css' in assets:
            css_path = assets_path / "css"
            css_path.mkdir(parents=True, exist_ok=True)
            for css_file in assets['css']:
                await self._save_css_file(css_file, css_path)
        
        # JavaScript Files
        if 'javascript' in assets:
            js_path = assets_path / "js"
            js_path.mkdir(parents=True, exist_ok=True)
            for js_file in assets['javascript']:
                await self._save_js_file(js_file, js_path)
        
        # Images
        if 'images' in assets:
            img_path = assets_path / "images"
            img_path.mkdir(parents=True, exist_ok=True)
            for img_file in assets['images']:
                await self._save_image_file(img_file, img_path)
        
        # Fonts
        if 'fonts' in assets:
            fonts_path = assets_path / "fonts"
            fonts_path.mkdir(parents=True, exist_ok=True)
            for font_file in assets['fonts']:
                await self._save_font_file(font_file, fonts_path)
    
    async def _organize_templates(self, templates: Dict[str, Any], project_path: Path):
        """تنظيم القوالب"""
        templates_path = project_path / "templates"
        templates_path.mkdir(parents=True, exist_ok=True)
        
        # صفحات رئيسية
        pages_path = templates_path / "pages"
        pages_path.mkdir(parents=True, exist_ok=True)
        
        # مكونات قابلة للإعادة الاستخدام
        components_path = templates_path / "components"
        components_path.mkdir(parents=True, exist_ok=True)
        
        # تخطيطات أساسية
        layouts_path = templates_path / "layouts"
        layouts_path.mkdir(parents=True, exist_ok=True)
    
    async def _organize_code(self, functions: Dict[str, Any], project_path: Path):
        """تنظيم الكود والوظائف"""
        code_path = project_path / "src"
        code_path.mkdir(parents=True, exist_ok=True)
        
        # APIs
        api_path = code_path / "api"
        api_path.mkdir(parents=True, exist_ok=True)
        
        # Utils
        utils_path = code_path / "utils"
        utils_path.mkdir(parents=True, exist_ok=True)
        
        # Components
        components_path = code_path / "components"
        components_path.mkdir(parents=True, exist_ok=True)
    
    async def _save_css_file(self, css_data: Dict[str, Any], css_path: Path):
        """حفظ ملف CSS"""
        filename = css_data.get('filename', 'style.css')
        content = css_data.get('content', '')
        
        file_path = css_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    async def _save_js_file(self, js_data: Dict[str, Any], js_path: Path):
        """حفظ ملف JavaScript"""
        filename = js_data.get('filename', 'script.js')
        content = js_data.get('content', '')
        
        file_path = js_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    async def _save_image_file(self, img_data: Dict[str, Any], img_path: Path):
        """حفظ ملف صورة"""
        filename = img_data.get('filename', 'image.png')
        content = img_data.get('content')
        
        if content:
            file_path = img_path / filename
            if isinstance(content, bytes):
                with open(file_path, 'wb') as f:
                    f.write(content)
            else:
                # إذا كان base64
                import base64
                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(content))
    
    async def _save_font_file(self, font_data: Dict[str, Any], fonts_path: Path):
        """حفظ ملف خط"""
        filename = font_data.get('filename', 'font.woff')
        content = font_data.get('content')
        
        if content:
            file_path = fonts_path / filename
            with open(file_path, 'wb') as f:
                f.write(content)
    
    async def _create_project_config(self, extraction_data: Dict[str, Any], project_path: Path):
        """إنشاء ملف تكوين المشروع"""
        config = {
            'project_name': extraction_data.get('metadata', {}).get('title', 'Extracted Website'),
            'source_url': extraction_data.get('url', ''),
            'extraction_date': extraction_data.get('timestamp', ''),
            'framework_detected': extraction_data.get('technical_analysis', {}).get('framework', 'Unknown'),
            'dependencies': extraction_data.get('dependencies', []),
            'structure': self.project_structure
        }
        
        config_path = project_path / "project.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    async def _create_documentation(self, extraction_data: Dict[str, Any], project_path: Path):
        """إنشاء الوثائق"""
        docs_path = project_path / "docs"
        docs_path.mkdir(parents=True, exist_ok=True)
        
        # README.md
        readme_content = f"""# {extraction_data.get('metadata', {}).get('title', 'Extracted Website')}

## معلومات المشروع
- **المصدر**: {extraction_data.get('url', '')}
- **تاريخ الاستخراج**: {extraction_data.get('timestamp', '')}
- **الإطار المكتشف**: {extraction_data.get('technical_analysis', {}).get('framework', 'Unknown')}

## هيكل المشروع
```
{self._generate_structure_tree()}
```

## التبعيات
{self._generate_dependencies_list(extraction_data.get('dependencies', []))}

## تعليمات التشغيل
1. تثبيت التبعيات
2. تشغيل الخادم المحلي
3. فتح المتصفح على الرابط المحدد
"""
        
        readme_path = docs_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _generate_structure_tree(self) -> str:
        """إنشاء شجرة هيكل المشروع"""
        return """project/
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
├── templates/
│   ├── pages/
│   ├── components/
│   └── layouts/
├── src/
│   ├── api/
│   ├── utils/
│   └── components/
├── docs/
└── project.json"""
    
    def _generate_dependencies_list(self, dependencies: List[str]) -> str:
        """إنشاء قائمة التبعيات"""
        if not dependencies:
            return "- لا توجد تبعيات مكتشفة"
        
        return "\n".join([f"- {dep}" for dep in dependencies])
    
    def _count_files(self, path: Path) -> int:
        """عد الملفات في المجلد"""
        return len([f for f in path.rglob('*') if f.is_file()])
