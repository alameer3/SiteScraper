"""
إعدادات أداة الاستخراج المتطورة
Advanced Extraction Tool Configuration
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class ExtractionConfig:
    """إعدادات شاملة لعملية الاستخراج"""
    
    # إعدادات أساسية
    target_url: str = ""
    extraction_type: str = "standard"  # basic, standard, advanced, complete, ai_powered
    output_directory: str = "11"  # تم تغييره إلى مجلد 11
    
    # إعدادات الشبكة
    timeout: int = 30
    max_retries: int = 3
    delay_between_requests: float = 1.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    verify_ssl: bool = True
    
    # إعدادات الاستخراج
    max_depth: int = 3
    max_pages: int = 100
    max_file_size_mb: int = 50
    allowed_domains: List[str] = None
    
    # ميزات الاستخراج
    extract_content: bool = True
    extract_assets: bool = True
    extract_images: bool = True
    extract_css: bool = True
    extract_js: bool = True
    extract_links: bool = True
    extract_metadata: bool = True
    
    # ميزات متقدمة
    capture_screenshots: bool = False
    analyze_seo: bool = True
    analyze_performance: bool = True
    analyze_security: bool = True
    detect_technologies: bool = True
    
    # تصدير البيانات
    export_json: bool = True
    export_csv: bool = True
    export_html: bool = True
    export_pdf: bool = False
    
    def __post_init__(self):
        """التحقق من صحة الإعدادات بعد التهيئة"""
        if self.allowed_domains is None:
            self.allowed_domains = []
            
        if self.max_file_size_mb <= 0:
            self.max_file_size_mb = 50
            
        if self.timeout <= 0:
            self.timeout = 30
    
    def to_dict(self) -> Dict:
        """تحويل الإعدادات إلى قاموس"""
        return {
            'target_url': self.target_url,
            'extraction_type': self.extraction_type,
            'output_directory': self.output_directory,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'delay_between_requests': self.delay_between_requests,
            'verify_ssl': self.verify_ssl,
            'max_depth': self.max_depth,
            'max_pages': self.max_pages,
            'max_file_size_mb': self.max_file_size_mb,
            'features': {
                'extract_content': self.extract_content,
                'extract_assets': self.extract_assets,
                'extract_images': self.extract_images,
                'extract_css': self.extract_css,
                'extract_js': self.extract_js,
                'extract_links': self.extract_links,
                'extract_metadata': self.extract_metadata,
                'capture_screenshots': self.capture_screenshots,
                'analyze_seo': self.analyze_seo,
                'analyze_performance': self.analyze_performance,
                'analyze_security': self.analyze_security,
                'detect_technologies': self.detect_technologies
            },
            'exports': {
                'export_json': self.export_json,
                'export_csv': self.export_csv,
                'export_html': self.export_html,
                'export_pdf': self.export_pdf
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExtractionConfig':
        """إنشاء إعدادات من قاموس"""
        config = cls()
        
        # الإعدادات الأساسية
        config.target_url = data.get('target_url', '')
        config.extraction_type = data.get('extraction_type', 'standard')
        config.output_directory = data.get('output_directory', '11')
        config.timeout = data.get('timeout', 30)
        config.max_retries = data.get('max_retries', 3)
        config.delay_between_requests = data.get('delay_between_requests', 1.0)
        config.verify_ssl = data.get('verify_ssl', True)
        config.max_depth = data.get('max_depth', 3)
        config.max_pages = data.get('max_pages', 100)
        config.max_file_size_mb = data.get('max_file_size_mb', 50)
        
        # الميزات
        features = data.get('features', {})
        config.extract_content = features.get('extract_content', True)
        config.extract_assets = features.get('extract_assets', True)
        config.extract_images = features.get('extract_images', True)
        config.extract_css = features.get('extract_css', True)
        config.extract_js = features.get('extract_js', True)
        config.extract_links = features.get('extract_links', True)
        config.extract_metadata = features.get('extract_metadata', True)
        config.capture_screenshots = features.get('capture_screenshots', False)
        config.analyze_seo = features.get('analyze_seo', True)
        config.analyze_performance = features.get('analyze_performance', True)
        config.analyze_security = features.get('analyze_security', True)
        config.detect_technologies = features.get('detect_technologies', True)
        
        # التصدير
        exports = data.get('exports', {})
        config.export_json = exports.get('export_json', True)
        config.export_csv = exports.get('export_csv', True)
        config.export_html = exports.get('export_html', True)
        config.export_pdf = exports.get('export_pdf', False)
        
        return config


def get_preset_config(extraction_type: str) -> ExtractionConfig:
    """الحصول على إعدادات مُعرَّفة مسبقاً"""
    
    base_config = ExtractionConfig()
    base_config.extraction_type = extraction_type
    
    if extraction_type == "basic":
        base_config.extract_assets = False
        base_config.extract_images = False
        base_config.extract_css = False
        base_config.extract_js = False
        base_config.capture_screenshots = False
        base_config.analyze_seo = False
        base_config.analyze_performance = False
        base_config.analyze_security = False
        base_config.detect_technologies = False
        base_config.max_pages = 1
        
    elif extraction_type == "standard":
        base_config.extract_assets = True
        base_config.extract_images = True
        base_config.capture_screenshots = False
        base_config.analyze_seo = True
        base_config.analyze_performance = True
        base_config.analyze_security = False
        base_config.max_pages = 10
        
    elif extraction_type == "advanced":
        base_config.extract_assets = True
        base_config.extract_images = True
        base_config.extract_css = True
        base_config.extract_js = True
        base_config.capture_screenshots = True
        base_config.analyze_seo = True
        base_config.analyze_performance = True
        base_config.analyze_security = True
        base_config.detect_technologies = True
        base_config.max_pages = 50
        
    elif extraction_type == "complete":
        base_config.extract_assets = True
        base_config.extract_images = True
        base_config.extract_css = True
        base_config.extract_js = True
        base_config.capture_screenshots = True
        base_config.analyze_seo = True
        base_config.analyze_performance = True
        base_config.analyze_security = True
        base_config.detect_technologies = True
        base_config.export_pdf = True
        base_config.max_pages = 100
        base_config.max_depth = 5
    
    return base_config


# إعدادات افتراضية للاستخدام العام
DEFAULT_CONFIG = ExtractionConfig()