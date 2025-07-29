#!/usr/bin/env python3
"""
واجهة إدارة الملفات المستخرجة - File Manager API
تسمح بعرض وإدارة جميع الملفات المستخرجة من الأدوات
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, render_template_string, request, send_file
import zipfile
import shutil

class ExtractedFilesManager:
    """مدير الملفات المستخرجة"""
    
    def __init__(self, base_dir: str = "extracted_files"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def get_all_extractions(self) -> Dict[str, Any]:
        """الحصول على جميع عمليات الاستخراج"""
        extractions = {
            'total_count': 0,
            'by_tool': {},
            'recent_extractions': [],
            'total_size_mb': 0,
            'folder_structure': {}
        }
        
        for tool_folder in self.base_dir.iterdir():
            if tool_folder.is_dir() and not tool_folder.name.startswith('.'):
                tool_name = tool_folder.name
                tool_extractions = []
                
                for extraction_folder in tool_folder.iterdir():
                    if extraction_folder.is_dir():
                        info_file = extraction_folder / 'extraction_info.json'
                        if info_file.exists():
                            try:
                                with open(info_file, 'r', encoding='utf-8') as f:
                                    info = json.load(f)
                                    tool_extractions.append({
                                        'extraction_id': info.get('extraction_id'),
                                        'url': info.get('url', ''),
                                        'domain': info.get('domain', ''),
                                        'created_at': info.get('created_at', ''),
                                        'status': info.get('status', 'unknown'),
                                        'folder_path': str(extraction_folder),
                                        'folder_name': extraction_folder.name,
                                        'file_count': len(list(extraction_folder.rglob('*'))),
                                        'size_mb': round(self._get_folder_size(extraction_folder) / (1024*1024), 2)
                                    })
                                    extractions['total_count'] += 1
                            except Exception as e:
                                print(f"خطأ في قراءة {info_file}: {e}")
                
                extractions['by_tool'][tool_name] = {
                    'count': len(tool_extractions),
                    'extractions': sorted(tool_extractions, key=lambda x: x['created_at'], reverse=True)
                }
                
                # إضافة للعمليات الحديثة
                for extraction in tool_extractions[:3]:  # آخر 3 من كل أداة
                    extraction['tool'] = tool_name
                    extractions['recent_extractions'].append(extraction)
        
        # ترتيب العمليات الحديثة
        extractions['recent_extractions'].sort(key=lambda x: x['created_at'], reverse=True)
        extractions['recent_extractions'] = extractions['recent_extractions'][:20]
        
        # حساب الحجم الإجمالي
        extractions['total_size_mb'] = round(self._get_folder_size(self.base_dir) / (1024*1024), 2)
        
        return extractions
    
    def get_extraction_details(self, tool_name: str, extraction_folder: str) -> Dict[str, Any]:
        """الحصول على تفاصيل استخراج محدد"""
        folder_path = self.base_dir / tool_name / extraction_folder
        
        if not folder_path.exists():
            return {'error': 'Extraction not found'}
        
        # قراءة معلومات الاستخراج
        info_file = folder_path / 'extraction_info.json'
        extraction_info = {}
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                extraction_info = json.load(f)
        
        # قراءة التقرير النهائي
        report_file = folder_path / '04_analysis' / 'final_report.json'
        final_report = {}
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                final_report = json.load(f)
        
        # هيكل الملفات
        file_structure = self._get_detailed_structure(folder_path)
        
        return {
            'extraction_info': extraction_info,
            'final_report': final_report,
            'file_structure': file_structure,
            'folder_path': str(folder_path),
            'total_files': len(list(folder_path.rglob('*'))),
            'total_size_mb': round(self._get_folder_size(folder_path) / (1024*1024), 2)
        }
    
    def create_archive(self, tool_name: str, extraction_folder: str) -> Optional[Path]:
        """إنشاء أرشيف مضغوط لاستخراج محدد"""
        folder_path = self.base_dir / tool_name / extraction_folder
        
        if not folder_path.exists():
            return None
        
        archives_dir = self.base_dir / 'archives'
        archives_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{extraction_folder}_{timestamp}.zip"
        archive_path = archives_dir / archive_name
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(folder_path)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    def delete_extraction(self, tool_name: str, extraction_folder: str) -> bool:
        """حذف استخراج محدد"""
        folder_path = self.base_dir / tool_name / extraction_folder
        
        if folder_path.exists():
            try:
                shutil.rmtree(folder_path)
                return True
            except Exception as e:
                print(f"خطأ في حذف {folder_path}: {e}")
                return False
        return False
    
    def clean_old_extractions(self, days_old: int = 30) -> Dict[str, Any]:
        """تنظيف العمليات القديمة"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        freed_space_mb = 0
        
        for tool_folder in self.base_dir.iterdir():
            if tool_folder.is_dir():
                for extraction_folder in tool_folder.iterdir():
                    if extraction_folder.is_dir():
                        info_file = extraction_folder / 'extraction_info.json'
                        if info_file.exists():
                            try:
                                with open(info_file, 'r', encoding='utf-8') as f:
                                    info = json.load(f)
                                    created_at = datetime.fromisoformat(info.get('created_at', ''))
                                    
                                    if created_at < cutoff_date:
                                        size_mb = self._get_folder_size(extraction_folder) / (1024*1024)
                                        shutil.rmtree(extraction_folder)
                                        deleted_count += 1
                                        freed_space_mb += size_mb
                            except Exception as e:
                                print(f"خطأ في معالجة {extraction_folder}: {e}")
        
        return {
            'deleted_count': deleted_count,
            'freed_space_mb': round(freed_space_mb, 2),
            'cutoff_date': cutoff_date.isoformat()
        }
    
    def get_file_content(self, tool_name: str, extraction_folder: str, file_path: str) -> Optional[str]:
        """قراءة محتوى ملف محدد"""
        full_path = self.base_dir / tool_name / extraction_folder / file_path
        
        if full_path.exists() and full_path.is_file():
            try:
                # تحديد نوع الملف
                if full_path.suffix.lower() in ['.txt', '.html', '.css', '.js', '.json', '.md']:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    return f"Binary file: {full_path.name}"
            except Exception as e:
                return f"Error reading file: {e}"
        
        return None
    
    def _get_folder_size(self, folder: Path) -> int:
        """حساب حجم المجلد بالبايت"""
        return sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
    
    def _get_detailed_structure(self, folder: Path) -> Dict[str, Any]:
        """الحصول على هيكل مفصل للمجلد"""
        structure = {}
        
        for item in folder.iterdir():
            if item.is_dir():
                # مجلد فرعي
                subfolder_files = list(item.rglob('*'))
                structure[item.name] = {
                    'type': 'directory',
                    'files_count': len([f for f in subfolder_files if f.is_file()]),
                    'size_mb': round(self._get_folder_size(item) / (1024*1024), 2),
                    'files': [f.name for f in item.iterdir() if f.is_file()][:10]  # أول 10 ملفات
                }
            else:
                # ملف
                structure[item.name] = {
                    'type': 'file',
                    'size_kb': round(item.stat().st_size / 1024, 2),
                    'extension': item.suffix,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
        
        return structure

# إنشاء مدير الملفات
files_manager = ExtractedFilesManager()

# واجهة Flask لإدارة الملفات
def create_file_manager_app():
    """إنشاء تطبيق Flask لإدارة الملفات"""
    app = Flask(__name__)
    
    FILE_MANAGER_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>إدارة الملفات المستخرجة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/feather-icons@4.28.0/dist/feather.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                margin-bottom: 2rem;
            }
            .stats-card {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
            }
            .extraction-card {
                transition: transform 0.3s ease;
                cursor: pointer;
                margin-bottom: 1rem;
            }
            .extraction-card:hover {
                transform: translateY(-2px);
            }
            .tool-badge {
                border-radius: 20px;
                font-size: 0.8rem;
            }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <div class="text-center mb-5">
                <h1 class="text-white mb-3">
                    <i data-feather="folder" class="me-2"></i>
                    إدارة الملفات المستخرجة
                </h1>
                <p class="text-white">جميع الملفات والمجلدات المستخرجة من الأدوات المختلفة</p>
            </div>

            <!-- الإحصائيات العامة -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i data-feather="database" style="width: 2rem; height: 2rem;"></i>
                            <h4>{{ extractions.total_count }}</h4>
                            <small>إجمالي العمليات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i data-feather="hard-drive" style="width: 2rem; height: 2rem;"></i>
                            <h4>{{ extractions.total_size_mb }}MB</h4>
                            <small>الحجم الإجمالي</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i data-feather="tool" style="width: 2rem; height: 2rem;"></i>
                            <h4>{{ extractions.by_tool|length }}</h4>
                            <small>أدوات مختلفة</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i data-feather="clock" style="width: 2rem; height: 2rem;"></i>
                            <h4>{{ extractions.recent_extractions|length }}</h4>
                            <small>عمليات حديثة</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- العمليات الحديثة -->
            <div class="card">
                <div class="card-header">
                    <h5><i data-feather="clock" class="me-2"></i>العمليات الحديثة</h5>
                </div>
                <div class="card-body">
                    {% for extraction in extractions.recent_extractions[:10] %}
                    <div class="extraction-card card mb-2" onclick="viewExtraction('{{ extraction.tool }}', '{{ extraction.folder_name }}')">
                        <div class="card-body py-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>{{ extraction.domain or extraction.url[:50] }}</strong>
                                    <br>
                                    <small class="text-muted">{{ extraction.created_at[:19] }}</small>
                                </div>
                                <div>
                                    <span class="badge bg-primary tool-badge">{{ extraction.tool }}</span>
                                    <span class="badge bg-success">{{ extraction.file_count }} ملف</span>
                                    <span class="badge bg-info">{{ extraction.size_mb }}MB</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- عمليات حسب الأداة -->
            {% for tool_name, tool_data in extractions.by_tool.items() %}
            <div class="card">
                <div class="card-header">
                    <h5>
                        <i data-feather="tool" class="me-2"></i>
                        {{ tool_name }} 
                        <span class="badge bg-primary">{{ tool_data.count }} عملية</span>
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        {% for extraction in tool_data.extractions[:6] %}
                        <div class="col-md-6 mb-2">
                            <div class="extraction-card card" onclick="viewExtraction('{{ tool_name }}', '{{ extraction.folder_name }}')">
                                <div class="card-body py-2">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <strong>{{ extraction.domain or 'غير محدد' }}</strong>
                                            <br>
                                            <small class="text-muted">{{ extraction.created_at[:16] }}</small>
                                        </div>
                                        <div>
                                            <span class="badge bg-success">{{ extraction.file_count }} ملف</span>
                                            <span class="badge bg-info">{{ extraction.size_mb }}MB</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endfor %}

            <!-- أدوات الإدارة -->
            <div class="card">
                <div class="card-header">
                    <h5><i data-feather="settings" class="me-2"></i>أدوات الإدارة</h5>
                </div>
                <div class="card-body text-center">
                    <button class="btn btn-warning me-2" onclick="cleanOldFiles()">
                        <i data-feather="trash-2" class="me-1"></i>تنظيف الملفات القديمة
                    </button>
                    <button class="btn btn-info me-2" onclick="createBackup()">
                        <i data-feather="archive" class="me-1"></i>إنشاء نسخة احتياطية
                    </button>
                    <button class="btn btn-success" onclick="location.reload()">
                        <i data-feather="refresh-cw" class="me-1"></i>تحديث البيانات
                    </button>
                </div>
            </div>

            <!-- العودة للصفحة الرئيسية -->
            <div class="text-center mt-4">
                <a href="/" class="btn btn-outline-light">
                    <i data-feather="home" class="me-1"></i>العودة للصفحة الرئيسية
                </a>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js"></script>
        <script>
            feather.replace();

            function viewExtraction(toolName, folderName) {
                window.open(`/file-manager/extraction/${toolName}/${folderName}`, '_blank');
            }

            function cleanOldFiles() {
                if (confirm('هل تريد حذف الملفات الأقدم من 30 يوماً؟')) {
                    fetch('/api/files/clean', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            alert(`تم حذف ${data.deleted_count} عملية وتحرير ${data.freed_space_mb}MB`);
                            location.reload();
                        });
                }
            }

            function createBackup() {
                alert('سيتم تنفيذ هذه الميزة قريباً');
            }
        </script>
    </body>
    </html>
    """
    
    @app.route('/file-manager')
    def file_manager_home():
        """الصفحة الرئيسية لإدارة الملفات"""
        extractions = files_manager.get_all_extractions()
        return render_template_string(FILE_MANAGER_TEMPLATE, extractions=extractions)
    
    @app.route('/api/files/all')
    def api_all_files():
        """API للحصول على جميع الملفات"""
        return jsonify(files_manager.get_all_extractions())
    
    @app.route('/api/files/extraction/<tool_name>/<extraction_folder>')
    def api_extraction_details(tool_name, extraction_folder):
        """API لتفاصيل استخراج محدد"""
        return jsonify(files_manager.get_extraction_details(tool_name, extraction_folder))
    
    @app.route('/api/files/clean', methods=['POST'])
    def api_clean_old_files():
        """API لتنظيف الملفات القديمة"""
        days = request.json.get('days', 30) if request.json else 30
        result = files_manager.clean_old_extractions(days)
        return jsonify(result)
    
    @app.route('/api/files/archive/<tool_name>/<extraction_folder>')
    def api_create_archive(tool_name, extraction_folder):
        """API لإنشاء أرشيف"""
        archive_path = files_manager.create_archive(tool_name, extraction_folder)
        if archive_path:
            return send_file(archive_path, as_attachment=True)
        else:
            return jsonify({'error': 'Archive creation failed'}), 500
    
    return app

if __name__ == '__main__':
    app = create_file_manager_app()
    app.run(host='0.0.0.0', port=5001, debug=True)