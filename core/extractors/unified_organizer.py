"""
نظام تنظيم موحد لجميع البيانات والملفات المستخرجة
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urlparse
import logging

class UnifiedOrganizer:
    """منظم موحد لجميع البيانات والملفات المستخرجة"""
    
    def __init__(self, base_directory: str = "extracted_data"):
        self.base_directory = base_directory
        self.logger = logging.getLogger(__name__)
        self._ensure_base_structure()
    
    def _ensure_base_structure(self):
        """إنشاء البنية الأساسية للمجلدات"""
        directories = [
            self.base_directory,
            os.path.join(self.base_directory, "websites"),
            os.path.join(self.base_directory, "assets"),
            os.path.join(self.base_directory, "reports"),
            os.path.join(self.base_directory, "exports"),
            os.path.join(self.base_directory, "replicated_sites")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def organize_extraction_data(self, url: str, extraction_result: Dict[str, Any]) -> str:
        """تنظيم جميع بيانات الاستخراج في مجلد واحد مرتب"""
        
        # إنشاء اسم المجلد بناءً على URL والتاريخ
        domain = urlparse(url).netloc.replace('www.', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_folder = f"{domain}_{timestamp}"
        site_path = os.path.join(self.base_directory, "websites", site_folder)
        
        # إنشاء البنية المنظمة
        self._create_organized_structure(site_path, url, extraction_result)
        
        return site_path
    
    def _create_organized_structure(self, site_path: str, url: str, extraction_result: Dict[str, Any]):
        """إنشاء البنية المنظمة للموقع"""
        
        # إنشاء المجلدات الرئيسية
        folders = {
            'content': os.path.join(site_path, '01_content'),
            'assets': os.path.join(site_path, '02_assets'),
            'structure': os.path.join(site_path, '03_structure'),
            'analysis': os.path.join(site_path, '04_analysis'),
            'replicated': os.path.join(site_path, '05_replicated_site'),
            'exports': os.path.join(site_path, '06_exports')
        }
        
        for folder in folders.values():
            os.makedirs(folder, exist_ok=True)
        
        # تنظيم المحتوى النصي
        self._organize_content(folders['content'], extraction_result)
        
        # تنظيم الأصول (صور، CSS، JS)
        self._organize_assets(folders['assets'], extraction_result)
        
        # تنظيم بيانات البنية
        self._organize_structure_data(folders['structure'], extraction_result)
        
        # تنظيم التحليل والتقارير
        self._organize_analysis(folders['analysis'], extraction_result)
        
        # نسخ الموقع المطابق إذا وُجد
        self._organize_replicated_site(folders['replicated'], extraction_result)
        
        # إنشاء ملفات التصدير
        self._create_export_files(folders['exports'], url, extraction_result)
        
        # إنشاء ملف الفهرس الرئيسي
        self._create_index_file(site_path, url, extraction_result)
    
    def _organize_content(self, content_path: str, extraction_result: Dict[str, Any]):
        """تنظيم المحتوى النصي"""
        
        # المحتوى الرئيسي
        if 'content' in extraction_result:
            content = extraction_result['content']
            
            # النص الخام
            with open(os.path.join(content_path, 'raw_text.txt'), 'w', encoding='utf-8') as f:
                f.write(content.get('text', ''))
            
            # العناوين
            with open(os.path.join(content_path, 'headings.json'), 'w', encoding='utf-8') as f:
                json.dump(content.get('headings', []), f, ensure_ascii=False, indent=2)
            
            # الروابط
            with open(os.path.join(content_path, 'links.json'), 'w', encoding='utf-8') as f:
                json.dump(content.get('links', []), f, ensure_ascii=False, indent=2)
            
            # الفقرات
            with open(os.path.join(content_path, 'paragraphs.txt'), 'w', encoding='utf-8') as f:
                for p in content.get('paragraphs', []):
                    f.write(f"{p}\n\n")
    
    def _organize_assets(self, assets_path: str, extraction_result: Dict[str, Any]):
        """تنظيم الأصول (صور، CSS، JS)"""
        
        # إنشاء مجلدات فرعية للأصول
        asset_folders = {
            'images': os.path.join(assets_path, 'images'),
            'styles': os.path.join(assets_path, 'styles'),
            'scripts': os.path.join(assets_path, 'scripts'),
            'fonts': os.path.join(assets_path, 'fonts'),
            'documents': os.path.join(assets_path, 'documents'),
            'media': os.path.join(assets_path, 'media')
        }
        
        for folder in asset_folders.values():
            os.makedirs(folder, exist_ok=True)
        
        # نسخ الأصول من المجلدات المتناثرة
        self._copy_downloaded_assets(asset_folders, extraction_result)
        
        # إنشاء فهرس الأصول
        self._create_assets_index(assets_path, asset_folders)
    
    def _copy_downloaded_assets(self, asset_folders: Dict[str, str], extraction_result: Dict[str, Any]):
        """نسخ الأصول المُحملة من المجلدات المتناثرة"""
        
        # البحث عن الأصول في downloaded_assets
        downloaded_assets_path = "downloaded_assets"
        if os.path.exists(downloaded_assets_path):
            for site_folder in os.listdir(downloaded_assets_path):
                site_assets_path = os.path.join(downloaded_assets_path, site_folder)
                if os.path.isdir(site_assets_path):
                    
                    # نسخ الصور
                    images_src = os.path.join(site_assets_path, "images")
                    if os.path.exists(images_src):
                        self._copy_files(images_src, asset_folders['images'])
                    
                    # نسخ CSS
                    styles_src = os.path.join(site_assets_path, "styles")
                    if os.path.exists(styles_src):
                        self._copy_files(styles_src, asset_folders['styles'])
                    
                    # نسخ JavaScript
                    scripts_src = os.path.join(site_assets_path, "scripts")
                    if os.path.exists(scripts_src):
                        self._copy_files(scripts_src, asset_folders['scripts'])
    
    def _copy_files(self, src_dir: str, dest_dir: str):
        """نسخ الملفات من مجلد إلى آخر"""
        if os.path.exists(src_dir):
            for file_name in os.listdir(src_dir):
                src_file = os.path.join(src_dir, file_name)
                dest_file = os.path.join(dest_dir, file_name)
                if os.path.isfile(src_file):
                    try:
                        shutil.copy2(src_file, dest_file)
                        self.logger.info(f"تم نسخ الملف: {file_name}")
                    except Exception as e:
                        self.logger.error(f"خطأ في نسخ {file_name}: {e}")
    
    def _organize_structure_data(self, structure_path: str, extraction_result: Dict[str, Any]):
        """تنظيم بيانات البنية"""
        
        structure_data = {
            'html_structure': extraction_result.get('structure', {}),
            'technology_stack': extraction_result.get('technology', {}),
            'seo_data': extraction_result.get('seo', {}),
            'performance_data': extraction_result.get('performance', {}),
            'navigation': extraction_result.get('navigation', {})
        }
        
        for data_type, data in structure_data.items():
            with open(os.path.join(structure_path, f'{data_type}.json'), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _organize_analysis(self, analysis_path: str, extraction_result: Dict[str, Any]):
        """تنظيم التحليل والتقارير"""
        
        # إحصائيات عامة
        stats = extraction_result.get('stats', {})
        with open(os.path.join(analysis_path, 'statistics.json'), 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        # تقرير HTML مفصل
        self._create_detailed_report(analysis_path, extraction_result)
    
    def _organize_replicated_site(self, replicated_path: str, extraction_result: Dict[str, Any]):
        """تنظيم الموقع المطابق"""
        
        # البحث عن المواقع المطابقة في replicated_sites
        replicated_sites_path = "replicated_sites"
        if os.path.exists(replicated_sites_path):
            sites = os.listdir(replicated_sites_path)
            if sites:
                # نسخ أحدث موقع مطابق
                latest_site = max(sites, key=lambda x: os.path.getctime(os.path.join(replicated_sites_path, x)))
                src_path = os.path.join(replicated_sites_path, latest_site)
                
                if os.path.isdir(src_path):
                    try:
                        shutil.copytree(src_path, replicated_path, dirs_exist_ok=True)
                        self.logger.info(f"تم نسخ الموقع المطابق: {latest_site}")
                    except Exception as e:
                        self.logger.error(f"خطأ في نسخ الموقع المطابق: {e}")
    
    def _create_export_files(self, exports_path: str, url: str, extraction_result: Dict[str, Any]):
        """إنشاء ملفات التصدير بصيغ مختلفة"""
        
        # JSON كامل
        with open(os.path.join(exports_path, 'complete_data.json'), 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, ensure_ascii=False, indent=2)
        
        # CSV للروابط
        import csv
        links = extraction_result.get('content', {}).get('links', [])
        with open(os.path.join(exports_path, 'links.csv'), 'w', newline='', encoding='utf-8') as f:
            if links:
                writer = csv.DictWriter(f, fieldnames=links[0].keys())
                writer.writeheader()
                writer.writerows(links)
        
        # ملف نصي للمحتوى
        content_text = extraction_result.get('content', {}).get('text', '')
        with open(os.path.join(exports_path, 'content.txt'), 'w', encoding='utf-8') as f:
            f.write(content_text)
    
    def _create_assets_index(self, assets_path: str, asset_folders: Dict[str, str]):
        """إنشاء فهرس الأصول"""
        
        index_data = {}
        
        for category, folder_path in asset_folders.items():
            files = []
            if os.path.exists(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        files.append({
                            'name': file_name,
                            'size': file_size,
                            'size_mb': round(file_size / 1024 / 1024, 2)
                        })
            
            index_data[category] = {
                'count': len(files),
                'total_size_mb': round(sum(f['size'] for f in files) / 1024 / 1024, 2),
                'files': files
            }
        
        with open(os.path.join(assets_path, 'assets_index.json'), 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def _create_detailed_report(self, analysis_path: str, extraction_result: Dict[str, Any]):
        """إنشاء تقرير HTML مفصل"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الاستخراج المفصل</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .file-list {{ columns: 2; column-gap: 20px; }}
        .file-item {{ break-inside: avoid; margin: 5px 0; padding: 5px; background: #f8f9fa; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 تقرير الاستخراج المفصل</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{extraction_result.get('stats', {}).get('total_files', 0)}</div>
                <div>إجمالي الملفات</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{extraction_result.get('stats', {}).get('images_count', 0)}</div>
                <div>الصور</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{extraction_result.get('stats', {}).get('css_files', 0)}</div>
                <div>ملفات CSS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{extraction_result.get('stats', {}).get('js_files', 0)}</div>
                <div>ملفات JavaScript</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📁 هيكل المجلدات</h2>
            <ul>
                <li><strong>01_content/</strong> - المحتوى النصي والروابط</li>
                <li><strong>02_assets/</strong> - جميع الأصول (صور، CSS، JS)</li>
                <li><strong>03_structure/</strong> - بيانات البنية والتقنيات</li>
                <li><strong>04_analysis/</strong> - التحليل والإحصائيات</li>
                <li><strong>05_replicated_site/</strong> - الموقع المطابق الكامل</li>
                <li><strong>06_exports/</strong> - ملفات التصدير (JSON, CSV, TXT)</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📈 الإحصائيات التفصيلية</h2>
            <pre>{json.dumps(extraction_result.get('stats', {}), ensure_ascii=False, indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>🔗 ملخص المحتوى</h2>
            <p><strong>عدد الكلمات:</strong> {len(extraction_result.get('content', {}).get('text', '').split())}</p>
            <p><strong>عدد الروابط:</strong> {len(extraction_result.get('content', {}).get('links', []))}</p>
            <p><strong>عدد العناوين:</strong> {len(extraction_result.get('content', {}).get('headings', []))}</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(os.path.join(analysis_path, 'detailed_report.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_index_file(self, site_path: str, url: str, extraction_result: Dict[str, Any]):
        """إنشاء ملف الفهرس الرئيسي"""
        
        index_data = {
            'extraction_info': {
                'url': url,
                'extraction_date': datetime.now().isoformat(),
                'total_size_mb': self._calculate_total_size(site_path)
            },
            'folder_structure': {
                '01_content': 'المحتوى النصي والروابط والفقرات',
                '02_assets': 'جميع الأصول (صور، CSS، JavaScript، خطوط)',
                '03_structure': 'بيانات البنية والتقنيات المستخدمة',
                '04_analysis': 'التحليل والتقارير والإحصائيات',
                '05_replicated_site': 'الموقع المطابق الكامل القابل للتشغيل',
                '06_exports': 'ملفات التصدير بصيغ مختلفة (JSON, CSV, TXT)'
            },
            'statistics': extraction_result.get('stats', {}),
            'instructions': {
                'arabic': [
                    'تصفح مجلد 01_content للحصول على النصوص والروابط',
                    'تصفح مجلد 02_assets لعرض جميع الصور والملفات المحملة',
                    'افتح 05_replicated_site/index.html لعرض الموقع المطابق',
                    'استخدم ملفات 06_exports للحصول على البيانات بصيغ مختلفة',
                    'اقرأ 04_analysis/detailed_report.html للحصول على تقرير شامل'
                ],
                'english': [
                    'Browse 01_content folder for texts and links',
                    'Browse 02_assets folder for all downloaded images and files',
                    'Open 05_replicated_site/index.html to view the replicated website',
                    'Use 06_exports files to get data in different formats',
                    'Read 04_analysis/detailed_report.html for comprehensive report'
                ]
            }
        }
        
        # ملف JSON
        with open(os.path.join(site_path, 'README.json'), 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        # ملف README نصي
        readme_content = f"""
# تقرير الاستخراج - {urlparse(url).netloc}

## معلومات الاستخراج
- الرابط: {url}
- تاريخ الاستخراج: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- الحجم الإجمالي: {index_data['extraction_info']['total_size_mb']} ميجابايت

## هيكل المجلدات
- **01_content/** - المحتوى النصي والروابط والفقرات
- **02_assets/** - جميع الأصول (صور، CSS، JavaScript، خطوط)
- **03_structure/** - بيانات البنية والتقنيات المستخدمة
- **04_analysis/** - التحليل والتقارير والإحصائيات
- **05_replicated_site/** - الموقع المطابق الكامل القابل للتشغيل
- **06_exports/** - ملفات التصدير بصيغ مختلفة (JSON, CSV, TXT)

## التعليمات
1. تصفح مجلد 01_content للحصول على النصوص والروابط
2. تصفح مجلد 02_assets لعرض جميع الصور والملفات المحملة
3. افتح 05_replicated_site/index.html لعرض الموقع المطابق
4. استخدم ملفات 06_exports للحصول على البيانات بصيغ مختلفة
5. اقرأ 04_analysis/detailed_report.html للحصول على تقرير شامل

## الإحصائيات
{json.dumps(extraction_result.get('stats', {}), ensure_ascii=False, indent=2)}
        """
        
        with open(os.path.join(site_path, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _calculate_total_size(self, folder_path: str) -> float:
        """حساب الحجم الإجمالي للمجلد بالميجابايت"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass
        return round(total_size / 1024 / 1024, 2)
    
    def get_extraction_summary(self, site_path: str) -> Dict[str, Any]:
        """الحصول على ملخص الاستخراج"""
        
        summary = {
            'path': site_path,
            'folders': [],
            'total_files': 0,
            'total_size_mb': 0
        }
        
        if os.path.exists(site_path):
            summary['total_size_mb'] = self._calculate_total_size(site_path)
            
            for item in os.listdir(site_path):
                item_path = os.path.join(site_path, item)
                if os.path.isdir(item_path):
                    file_count = sum(len(files) for _, _, files in os.walk(item_path))
                    summary['folders'].append({
                        'name': item,
                        'file_count': file_count
                    })
                    summary['total_files'] += file_count
        
        return summary