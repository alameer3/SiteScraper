"""
مدير الأدوات الموحد - Unified Tools Manager
==========================================

إدارة وتنسيق جميع أدوات الاستخراج والتحليل والنسخ
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .website_cloner_pro import WebsiteClonerPro, CloningConfig

class UnifiedToolsManager:
    """مدير شامل لجميع الأدوات المتقدمة"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools_registry = {}
        self.active_operations = {}
        
    def register_tool(self, tool_name: str, tool_instance: Any):
        """تسجيل أداة في المدير"""
        self.tools_registry[tool_name] = tool_instance
        self.logger.info(f"تم تسجيل الأداة: {tool_name}")
        
    async def run_comprehensive_analysis(self, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """تشغيل تحليل شامل باستخدام جميع الأدوات"""
        
        # إعداد التكوين
        cloning_config = CloningConfig(
            target_url=url,
            extract_all_content=True,
            extract_hidden_content=True,
            extract_dynamic_content=True,
            extract_apis=True,
            extract_database_structure=True,
            analyze_with_ai=True,
            create_identical_copy=True,
            bypass_protection=True
        )
        
        if config:
            for key, value in config.items():
                if hasattr(cloning_config, key):
                    setattr(cloning_config, key, value)
        
        # تشغيل Website Cloner Pro
        cloner = WebsiteClonerPro(cloning_config)
        
        try:
            result = await cloner.clone_website()
            
            # إضافة معلومات إضافية
            result.metadata = {
                'analysis_timestamp': datetime.now().isoformat(),
                'tools_used': list(self.tools_registry.keys()),
                'comprehensive_mode': True,
                'manager_version': '2.0.0'
            }
            
            return result.to_dict()
            
        except Exception as e:
            self.logger.error(f"خطأ في التحليل الشامل: {e}")
            raise
        finally:
            await cloner.cleanup()
            
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """الحصول على قائمة الأدوات المتاحة"""
        tools_info = []
        
        for tool_name, tool_instance in self.tools_registry.items():
            tool_info = {
                'name': tool_name,
                'type': type(tool_instance).__name__,
                'capabilities': getattr(tool_instance, 'capabilities', []),
                'status': 'active'
            }
            tools_info.append(tool_info)
            
        return tools_info
        
    async def export_results(self, results: Dict[str, Any], format: str = 'json') -> str:
        """تصدير النتائج بصيغ مختلفة"""
        output_dir = Path("tools_pro/exports")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == 'json':
            filename = f"comprehensive_analysis_{timestamp}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
        elif format.lower() == 'html':
            filename = f"comprehensive_report_{timestamp}.html"
            filepath = output_dir / filename
            
            html_content = self._generate_html_report(results)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        return str(filepath)
        
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML"""
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير التحليل الشامل</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 20px; direction: rtl; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 تقرير التحليل الشامل للموقع</h1>
                <p>الموقع المحلل: {results.get('target_url', 'غير محدد')}</p>
                <p>وقت التحليل: {results.get('metadata', {}).get('analysis_timestamp', 'غير محدد')}</p>
            </div>
            
            <div class="section">
                <h2>📊 إحصائيات سريعة</h2>
                <div class="metric success">الصفحات المستخرجة: {results.get('pages_extracted', 0)}</div>
                <div class="metric success">الأصول المحملة: {results.get('assets_downloaded', 0)}</div>
                <div class="metric success">حجم البيانات: {results.get('total_size', 0):,} بايت</div>
            </div>
            
            <div class="section">
                <h2>🤖 نتائج الذكاء الاصطناعي</h2>
                <p>تم تحليل الموقع باستخدام محرك الذكاء الاصطناعي المتقدم</p>
                <div class="metric">التقنيات المكتشفة: {len(results.get('technologies_detected', {}))}</div>
                <div class="metric">الأمان: {'آمن' if results.get('security_analysis', {}).get('ssl_analysis', {}).get('enabled', False) else 'يحتاج تحسين'}</div>
            </div>
            
            <div class="section">
                <h2>📁 الملفات المُنشأة</h2>
                <p>تم إنشاء نسخة كاملة من الموقع في مجلد الإخراج</p>
                <ul>
                    <li>المحتوى المستخرج: 01_extracted_content/</li>
                    <li>الأصول والملفات: 02_assets/</li>
                    <li>الكود المصدري: 03_source_code/</li>
                    <li>التحليل والتقارير: 04_analysis/</li>
                    <li>الموقع المُنشأ: 05_replicated_site/</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>✅ حالة العملية</h2>
                <p class="success">تم إكمال التحليل والاستخراج بنجاح!</p>
                <p>الأدوات المستخدمة: {', '.join(results.get('metadata', {}).get('tools_used', []))}</p>
            </div>
        </body>
        </html>
        """
        return html

# إنشاء مثيل عام للمدير
tools_manager = UnifiedToolsManager()