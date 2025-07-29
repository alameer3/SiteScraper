"""
مدير الأدوات الرئيسي - Main Tools Manager
"""
import os
import sys
from pathlib import Path

# إضافة مسار tools إلى Python path
tools_path = Path(__file__).parent
sys.path.insert(0, str(tools_path))

class ToolsManager:
    """مدير شامل لجميع الأدوات المتخصصة"""
    
    def __init__(self):
        self.available_tools = self._scan_available_tools()
        
    def _scan_available_tools(self):
        """فحص الأدوات المتاحة"""
        tools = {
            'extractors': [],
            'analyzers': [],
            'cloners': [],
            'scrapers': [],
            'ai': [],
            'generators': []
        }
        
        try:
            # فحص مجلد extractors
            extractors_path = tools_path / 'extractors'
            if extractors_path.exists():
                for file in extractors_path.glob('*.py'):
                    if file.name != '__init__.py':
                        tools['extractors'].append(file.stem)
            
            # فحص مجلد analyzers
            analyzers_path = tools_path / 'analyzers'
            if analyzers_path.exists():
                for file in analyzers_path.glob('*.py'):
                    if file.name != '__init__.py':
                        tools['analyzers'].append(file.stem)
            
            # فحص مجلد cloners
            cloners_path = tools_path / 'cloners'
            if cloners_path.exists():
                for file in cloners_path.glob('*.py'):
                    if file.name != '__init__.py':
                        tools['cloners'].append(file.stem)
            
            # فحص مجلد scrapers
            scrapers_path = tools_path / 'scrapers'
            if scrapers_path.exists():
                for file in scrapers_path.glob('*.py'):
                    if file.name != '__init__.py':
                        tools['scrapers'].append(file.stem)
                        
        except Exception as e:
            print(f"خطأ في فحص الأدوات: {e}")
            
        return tools
        
    def get_available_tools(self):
        """الحصول على قائمة الأدوات المتاحة"""
        return self.available_tools
        
    def get_tool_info(self, tool_category, tool_name):
        """الحصول على معلومات أداة محددة"""
        if tool_category in self.available_tools:
            if tool_name in self.available_tools[tool_category]:
                return f"الأداة {tool_name} متاحة في فئة {tool_category}"
        return f"الأداة {tool_name} غير متاحة"