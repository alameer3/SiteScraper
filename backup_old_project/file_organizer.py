#!/usr/bin/env python3
"""
نظام تنظيم الملفات المستخرجة - File Organizer
ينظم جميع الملفات المستخرجة من الأدوات في مجلد extracted_files
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import zipfile
import hashlib

class FileOrganizer:
    """منظم الملفات المستخرجة"""
    
    def __init__(self, base_dir: str = "extracted_files"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # إنشاء المجلدات الرئيسية
        self.folders = {
            'websites': self.base_dir / 'websites',           # المواقع المستخرجة
            'cloner_pro': self.base_dir / 'cloner_pro',       # Website Cloner Pro
            'ai_analysis': self.base_dir / 'ai_analysis',     # تحليل AI
            'spider_crawl': self.base_dir / 'spider_crawl',   # Spider Engine
            'assets': self.base_dir / 'assets',               # الأصول المحملة
            'database_scans': self.base_dir / 'database_scans', # فحص قواعد البيانات
            'reports': self.base_dir / 'reports',             # التقارير
            'temp': self.base_dir / 'temp',                   # الملفات المؤقتة
            'archives': self.base_dir / 'archives'            # الأرشيف المضغوط
        }
        
        # إنشاء جميع المجلدات
        for folder in self.folders.values():
            folder.mkdir(exist_ok=True)
    
    def create_extraction_folder(self, tool_name: str, url: str, extraction_id: Optional[int] = None) -> Path:
        """إنشاء مجلد للاستخراج الجديد"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = self.extract_domain(url)
        
        if extraction_id:
            folder_name = f"{extraction_id}_{domain}_{timestamp}"
        else:
            folder_name = f"{domain}_{timestamp}"
        
        extraction_folder = self.folders[tool_name] / folder_name
        extraction_folder.mkdir(exist_ok=True)
        
        # إنشاء المجلدات الفرعية المعيارية
        subfolders = {
            'content': extraction_folder / '01_content',      # المحتوى المستخرج
            'assets': extraction_folder / '02_assets',        # الأصول (صور، CSS، JS)
            'structure': extraction_folder / '03_structure',  # هيكل الموقع
            'analysis': extraction_folder / '04_analysis',    # التحليل والتقارير
            'replicated': extraction_folder / '05_replicated', # النسخة المطابقة
            'exports': extraction_folder / '06_exports',      # التصديرات
            'logs': extraction_folder / '07_logs'             # سجلات العملية
        }
        
        for subfolder in subfolders.values():
            subfolder.mkdir(exist_ok=True)
        
        # إنشاء ملف المعلومات الأساسية
        info_file = extraction_folder / 'extraction_info.json'
        extraction_info = {
            'extraction_id': extraction_id,
            'tool_name': tool_name,
            'url': url,
            'domain': domain,
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'folder_structure': {name: str(path.relative_to(extraction_folder)) 
                               for name, path in subfolders.items()},
            'status': 'in_progress'
        }
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_info, f, ensure_ascii=False, indent=2)
        
        return extraction_folder
    
    def save_content(self, extraction_folder: Path, content_type: str, content: Any, filename: str = None) -> Path:
        """حفظ المحتوى في المجلد المناسب"""
        if filename is None:
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{content_type}_{timestamp}"
        
        # تحديد المجلد المناسب حسب نوع المحتوى
        if content_type in ['html', 'text', 'markdown']:
            target_folder = extraction_folder / '01_content'
            if not filename.endswith('.html') and content_type == 'html':
                filename += '.html'
            elif not filename.endswith('.txt') and content_type == 'text':
                filename += '.txt'
            elif not filename.endswith('.md') and content_type == 'markdown':
                filename += '.md'
                
        elif content_type in ['css', 'js', 'image', 'font', 'media']:
            target_folder = extraction_folder / '02_assets' / content_type
            target_folder.mkdir(exist_ok=True)
            
        elif content_type in ['structure', 'sitemap', 'navigation']:
            target_folder = extraction_folder / '03_structure'
            if not filename.endswith('.json'):
                filename += '.json'
                
        elif content_type in ['analysis', 'report', 'summary']:
            target_folder = extraction_folder / '04_analysis'
            if not filename.endswith('.json') and isinstance(content, dict):
                filename += '.json'
                
        elif content_type in ['replicated_site', 'clone']:
            target_folder = extraction_folder / '05_replicated'
            
        elif content_type in ['export', 'csv', 'xml', 'pdf']:
            target_folder = extraction_folder / '06_exports'
            
        else:
            target_folder = extraction_folder / '07_logs'
        
        file_path = target_folder / filename
        
        # حفظ المحتوى حسب نوعه
        if isinstance(content, dict) or isinstance(content, list):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        elif isinstance(content, str):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif isinstance(content, bytes):
            with open(file_path, 'wb') as f:
                f.write(content)
        else:
            # محاولة تحويل إلى JSON
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(str(content), f, ensure_ascii=False, indent=2)
            except:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(content))
        
        return file_path
    
    def save_assets_batch(self, extraction_folder: Path, assets: Dict[str, List[str]], downloaded_files: Dict[str, bytes] = None) -> Dict[str, List[Path]]:
        """حفظ مجموعة من الأصول"""
        saved_assets = {}
        assets_folder = extraction_folder / '02_assets'
        
        for asset_type, urls in assets.items():
            asset_type_folder = assets_folder / asset_type
            asset_type_folder.mkdir(exist_ok=True)
            saved_assets[asset_type] = []
            
            for i, url in enumerate(urls):
                # إنشاء اسم ملف آمن
                filename = self.safe_filename(url.split('/')[-1] or f"{asset_type}_{i+1}")
                file_path = asset_type_folder / filename
                
                # حفظ الملف إذا كان متوفراً
                if downloaded_files and url in downloaded_files:
                    with open(file_path, 'wb') as f:
                        f.write(downloaded_files[url])
                    saved_assets[asset_type].append(file_path)
                else:
                    # حفظ رابط فقط
                    link_file = asset_type_folder / f"{filename}.url"
                    with open(link_file, 'w', encoding='utf-8') as f:
                        f.write(url)
                    saved_assets[asset_type].append(link_file)
        
        return saved_assets
    
    def finalize_extraction(self, extraction_folder: Path, final_results: Dict[str, Any]) -> Path:
        """إنهاء عملية الاستخراج وإنشاء التقرير النهائي"""
        # تحديث معلومات الاستخراج
        info_file = extraction_folder / 'extraction_info.json'
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                extraction_info = json.load(f)
        else:
            extraction_info = {}
        
        extraction_info.update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'final_results': final_results,
            'file_count': self.count_files(extraction_folder),
            'total_size': self.get_folder_size(extraction_folder)
        })
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_info, f, ensure_ascii=False, indent=2)
        
        # إنشاء تقرير مفصل
        report_file = extraction_folder / '04_analysis' / 'final_report.json'
        detailed_report = {
            'extraction_summary': extraction_info,
            'results': final_results,
            'file_structure': self.get_folder_structure(extraction_folder),
            'statistics': {
                'total_files': extraction_info['file_count'],
                'total_size_mb': round(extraction_info['total_size'] / (1024*1024), 2),
                'processing_time': self.calculate_processing_time(extraction_info)
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)
        
        # إنشاء README باللغة العربية
        readme_file = extraction_folder / 'README.md'
        readme_content = self.generate_readme(extraction_info, detailed_report)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return report_file
    
    def create_archive(self, extraction_folder: Path) -> Path:
        """إنشاء أرشيف مضغوط للاستخراج"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{extraction_folder.name}_{timestamp}.zip"
        archive_path = self.folders['archives'] / archive_name
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in extraction_folder.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(extraction_folder)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """الحصول على ملخص جميع العمليات"""
        summary = {
            'total_extractions': 0,
            'by_tool': {},
            'recent_extractions': [],
            'total_size_mb': 0,
            'folder_structure': {}
        }
        
        for tool_name, folder in self.folders.items():
            if tool_name in ['temp', 'archives', 'reports']:
                continue
                
            tool_extractions = []
            if folder.exists():
                for extraction_folder in folder.iterdir():
                    if extraction_folder.is_dir():
                        info_file = extraction_folder / 'extraction_info.json'
                        if info_file.exists():
                            with open(info_file, 'r', encoding='utf-8') as f:
                                info = json.load(f)
                                tool_extractions.append(info)
                                summary['total_extractions'] += 1
                                
                                # إضافة إلى العمليات الحديثة
                                if len(summary['recent_extractions']) < 10:
                                    summary['recent_extractions'].append({
                                        'tool': tool_name,
                                        'url': info.get('url', ''),
                                        'timestamp': info.get('created_at', ''),
                                        'status': info.get('status', 'unknown')
                                    })
            
            summary['by_tool'][tool_name] = {
                'count': len(tool_extractions),
                'extractions': tool_extractions[:5]  # آخر 5 عمليات
            }
        
        # حساب الحجم الإجمالي
        summary['total_size_mb'] = round(self.get_folder_size(self.base_dir) / (1024*1024), 2)
        
        # ترتيب العمليات الحديثة حسب التاريخ
        summary['recent_extractions'].sort(
            key=lambda x: x['timestamp'], 
            reverse=True
        )
        
        return summary
    
    # Helper methods
    def extract_domain(self, url: str) -> str:
        """استخراج اسم النطاق من الرابط"""
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '') or 'unknown'
    
    def safe_filename(self, filename: str) -> str:
        """إنشاء اسم ملف آمن"""
        import re
        # إزالة الأحرف غير المسموحة
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return safe_name[:100]  # تحديد الطول
    
    def count_files(self, folder: Path) -> int:
        """عد الملفات في المجلد"""
        return len([f for f in folder.rglob('*') if f.is_file()])
    
    def get_folder_size(self, folder: Path) -> int:
        """حساب حجم المجلد بالبايت"""
        return sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
    
    def get_folder_structure(self, folder: Path) -> Dict[str, Any]:
        """الحصول على هيكل المجلد"""
        structure = {}
        for item in folder.iterdir():
            if item.is_dir():
                structure[item.name] = {
                    'type': 'directory',
                    'files_count': len([f for f in item.rglob('*') if f.is_file()]),
                    'size_mb': round(self.get_folder_size(item) / (1024*1024), 2)
                }
            else:
                structure[item.name] = {
                    'type': 'file',
                    'size_kb': round(item.stat().st_size / 1024, 2)
                }
        return structure
    
    def calculate_processing_time(self, extraction_info: Dict[str, Any]) -> str:
        """حساب وقت المعالجة"""
        try:
            start = datetime.fromisoformat(extraction_info['created_at'])
            end = datetime.fromisoformat(extraction_info.get('completed_at', datetime.now().isoformat()))
            duration = end - start
            return str(duration).split('.')[0]  # إزالة الميكروثواني
        except:
            return 'unknown'
    
    def generate_readme(self, extraction_info: Dict[str, Any], detailed_report: Dict[str, Any]) -> str:
        """إنشاء ملف README باللغة العربية"""
        readme = f"""# تقرير استخراج الموقع - {extraction_info.get('domain', 'unknown')}

## معلومات الاستخراج
- **الأداة المستخدمة**: {extraction_info.get('tool_name', 'unknown')}
- **الرابط**: {extraction_info.get('url', 'unknown')}
- **تاريخ البدء**: {extraction_info.get('created_at', 'unknown')}
- **تاريخ الانتهاء**: {extraction_info.get('completed_at', 'في المعالجة')}
- **الحالة**: {extraction_info.get('status', 'unknown')}

## الإحصائيات
- **إجمالي الملفات**: {detailed_report['statistics']['total_files']}
- **الحجم الإجمالي**: {detailed_report['statistics']['total_size_mb']} ميجابايت
- **وقت المعالجة**: {detailed_report['statistics']['processing_time']}

## هيكل المجلدات
- `01_content/` - المحتوى المستخرج (HTML, نصوص)
- `02_assets/` - الأصول (صور, CSS, JavaScript)
- `03_structure/` - هيكل الموقع وخرائط التنقل
- `04_analysis/` - التحليل والتقارير
- `05_replicated/` - النسخة المطابقة للموقع
- `06_exports/` - التصديرات (CSV, XML, PDF)
- `07_logs/` - سجلات العملية

## الملفات الرئيسية
- `extraction_info.json` - معلومات الاستخراج الأساسية
- `04_analysis/final_report.json` - التقرير النهائي المفصل
- `README.md` - هذا الملف

## كيفية الاستخدام
1. راجع `extraction_info.json` للمعلومات السريعة
2. اطلع على `04_analysis/final_report.json` للتفاصيل الكاملة
3. تجد المحتوى المستخرج في `01_content/`
4. الأصول المحملة في `02_assets/`
5. النسخة المطابقة في `05_replicated/`

---
تم إنشاء هذا التقرير تلقائياً بواسطة نظام تنظيم الملفات
"""
        return readme

# إنشاء منظم الملفات العام
file_organizer = FileOrganizer()