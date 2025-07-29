"""
مدير الملفات والمجلدات
File and Directory Manager
"""

import os
import json
import csv
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import zipfile
import tempfile


class FileManager:
    """مدير شامل للملفات والمجلدات"""
    
    def __init__(self, base_directory: str = "extracted_files"):
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(exist_ok=True)
        self._setup_directory_structure()
        
    def _setup_directory_structure(self):
        """إعداد هيكل المجلدات الأساسي"""
        directories = [
            'content',      # المحتوى المستخرج
            'assets',       # الأصول (صور، CSS، JS)
            'reports',      # التقارير والتحليلات
            'screenshots',  # لقطات الشاشة
            'exports',      # الملفات المُصدَّرة
            'temp',         # الملفات المؤقتة
            'archives'      # الأرشيف المضغوط
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(exist_ok=True)
    
    def create_extraction_folder(self, extraction_id: str, url: str = "") -> Path:
        """إنشاء مجلد جديد لعملية استخراج"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # تنظيف اسم المجلد من الأحرف غير المسموحة
        safe_url = self._sanitize_filename(url)
        folder_name = f"{extraction_id}_{timestamp}"
        if safe_url:
            folder_name += f"_{safe_url[:50]}"
        
        extraction_folder = self.base_dir / 'content' / folder_name
        extraction_folder.mkdir(parents=True, exist_ok=True)
        
        # إنشاء المجلدات الفرعية
        subfolders = ['html', 'assets', 'data', 'analysis', 'exports']
        for subfolder in subfolders:
            (extraction_folder / subfolder).mkdir(exist_ok=True)
        
        return extraction_folder
    
    def _sanitize_filename(self, filename: str) -> str:
        """تنظيف أسماء الملفات من الأحرف غير المسموحة"""
        if not filename:
            return ""
        
        # إزالة البروتوكول والأحرف الخاصة
        cleaned = filename.replace('https://', '').replace('http://', '')
        cleaned = cleaned.replace('www.', '')
        
        # استبدال الأحرف غير المسموحة
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
        
        # إزالة النقاط المتتالية والمسافات
        cleaned = cleaned.replace('..', '_').replace('  ', '_')
        cleaned = cleaned.strip('. _')
        
        return cleaned
    
    def save_html_content(self, content: str, extraction_folder: Path, filename: str = "page.html") -> Path:
        """حفظ محتوى HTML"""
        html_folder = extraction_folder / 'html'
        html_folder.mkdir(exist_ok=True)
        
        file_path = html_folder / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def save_json_data(self, data: Dict[str, Any], extraction_folder: Path, filename: str = "data.json") -> Path:
        """حفظ البيانات بصيغة JSON"""
        data_folder = extraction_folder / 'data'
        data_folder.mkdir(exist_ok=True)
        
        file_path = data_folder / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return file_path
    
    def save_csv_data(self, data: List[Dict], extraction_folder: Path, filename: str = "data.csv") -> Path:
        """حفظ البيانات بصيغة CSV"""
        if not data:
            return None
        
        exports_folder = extraction_folder / 'exports'
        exports_folder.mkdir(exist_ok=True)
        
        file_path = exports_folder / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        return file_path
    
    def save_asset_file(self, content: bytes, extraction_folder: Path, filename: str, asset_type: str = "general") -> Path:
        """حفظ ملف أصول (صور، CSS، JS)"""
        assets_folder = extraction_folder / 'assets' / asset_type
        assets_folder.mkdir(parents=True, exist_ok=True)
        
        # تنظيف اسم الملف
        safe_filename = self._sanitize_filename(filename)
        if not safe_filename:
            safe_filename = f"asset_{datetime.now().strftime('%H%M%S')}"
        
        file_path = assets_folder / safe_filename
        
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            return file_path
        except Exception as e:
            print(f"Error saving asset {filename}: {str(e)}")
            return None
    
    def generate_html_report(self, data: Dict[str, Any], extraction_folder: Path) -> Path:
        """إنشاء تقرير HTML"""
        exports_folder = extraction_folder / 'exports'
        exports_folder.mkdir(exist_ok=True)
        
        html_content = self._create_html_report_template(data)
        
        file_path = exports_folder / 'report.html'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def _create_html_report_template(self, data: Dict[str, Any]) -> str:
        """إنشاء قالب تقرير HTML"""
        return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير تحليل الموقع - {data.get('domain', 'غير محدد')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            direction: rtl;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .tech-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }}
        .tech-tag {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .metadata strong {{
            color: #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 تقرير تحليل الموقع</h1>
            <p>{data.get('url', 'غير محدد')}</p>
            <p>تم الإنشاء: {data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
        </div>
        
        <div class="section">
            <h2>📊 معلومات أساسية</h2>
            <div class="metadata">
                <p><strong>العنوان:</strong> {data.get('title', 'غير متوفر')}</p>
                <p><strong>الوصف:</strong> {data.get('description', 'غير متوفر')}</p>
                <p><strong>النطاق:</strong> {data.get('domain', 'غير محدد')}</p>
                <p><strong>حالة الاستجابة:</strong> {data.get('status_code', 'غير محدد')}</p>
                <p><strong>نوع المحتوى:</strong> {data.get('content_type', 'غير محدد')}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 إحصائيات سريعة</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{data.get('links_count', 0)}</div>
                    <div class="stat-label">روابط</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('images_count', 0)}</div>
                    <div class="stat-label">صور</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('scripts_count', 0)}</div>
                    <div class="stat-label">سكريبتات</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('stylesheets_count', 0)}</div>
                    <div class="stat-label">ملفات CSS</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🛠️ التقنيات المستخدمة</h2>
            <div class="tech-tags">
                {"".join(f'<span class="tech-tag">{tech}</span>' for tech in data.get('technologies', []))}
            </div>
        </div>
        
        <div class="section">
            <h2>⚡ تحليل الأداء</h2>
            <div class="metadata">
                <p><strong>وقت الاستجابة:</strong> {data.get('performance', {}).get('response_time', 'غير محدد')} ثانية</p>
                <p><strong>حجم المحتوى:</strong> {data.get('content_length', 0)} بايت</p>
                <p><strong>ضغط المحتوى:</strong> {"مفعل" if data.get('performance', {}).get('compression') else "غير مفعل"}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>تم إنشاء هذا التقرير بواسطة أداة الاستخراج المتطورة</p>
            <p>وقت المعالجة: {data.get('duration', 0)} ثانية</p>
        </div>
    </div>
</body>
</html>"""
    
    def create_archive(self, extraction_folder: Path, archive_name: str = None) -> Path:
        """إنشاء أرشيف مضغوط من مجلد الاستخراج"""
        archives_folder = self.base_dir / 'archives'
        archives_folder.mkdir(exist_ok=True)
        
        if not archive_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"extraction_{timestamp}.zip"
        
        archive_path = archives_folder / archive_name
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in extraction_folder.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(extraction_folder)
                        zipf.write(file_path, arcname)
            
            return archive_path
        except Exception as e:
            print(f"Error creating archive: {str(e)}")
            return None
    
    def get_folder_size(self, folder_path: Path) -> Dict[str, Union[int, str]]:
        """حساب حجم المجلد"""
        total_size = 0
        file_count = 0
        
        try:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'formatted_size': self._format_bytes(total_size)
            }
        except Exception as e:
            return {
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'file_count': 0,
                'formatted_size': '0 B',
                'error': str(e)
            }
    
    def _format_bytes(self, bytes_count: int) -> str:
        """تنسيق حجم البايتات إلى وحدة مناسبة"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"
    
    def cleanup_temp_files(self):
        """تنظيف الملفات المؤقتة"""
        temp_folder = self.base_dir / 'temp'
        if temp_folder.exists():
            try:
                shutil.rmtree(temp_folder)
                temp_folder.mkdir(exist_ok=True)
                return True
            except Exception as e:
                print(f"Error cleaning temp files: {str(e)}")
                return False
        return True
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """إحصائيات التخزين"""
        stats = {}
        
        for subfolder in ['content', 'assets', 'reports', 'screenshots', 'exports', 'archives']:
            folder_path = self.base_dir / subfolder
            if folder_path.exists():
                stats[subfolder] = self.get_folder_size(folder_path)
            else:
                stats[subfolder] = {'total_size_mb': 0, 'file_count': 0}
        
        # إجمالي الإحصائيات
        total_size = sum([stats[key]['total_size_bytes'] for key in stats if 'total_size_bytes' in stats[key]])
        total_files = sum([stats[key]['file_count'] for key in stats if 'file_count' in stats[key]])
        
        stats['total'] = {
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': total_files,
            'formatted_size': self._format_bytes(total_size)
        }
        
        return stats