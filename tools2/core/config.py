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
    output_directory: str = "extracted_files"
    
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
            
        # لا نتطلب target_url عند الإنشاء لأنه قد يتم تعيينه لاحقاً
        # if not self.target_url:
        #     raise ValueError("target_url is required")
            
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
        config.output_directory = data.get('output_directory', 'extracted_files')
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


# إعدادات مُعرَّفة مسبقاً
PRESET_CONFIGS = {
    'basic': ExtractionConfig(
        extraction_type='basic',
        max_depth=1,
        max_pages=10,
        extract_assets=False,
        capture_screenshots=False,
        analyze_seo=False,
        analyze_performance=False,
        analyze_security=False
    ),
    
    'standard': ExtractionConfig(
        extraction_type='standard',
        max_depth=2,
        max_pages=50,
        extract_assets=True,
        capture_screenshots=False,
        analyze_seo=True,
        analyze_performance=True,
        analyze_security=True
    ),
    
    'advanced': ExtractionConfig(
        extraction_type='advanced',
        max_depth=3,
        max_pages=100,
        extract_assets=True,
        capture_screenshots=True,
        analyze_seo=True,
        analyze_performance=True,
        analyze_security=True,
        export_pdf=True
    ),
    
    'complete': ExtractionConfig(
        extraction_type='complete',
        max_depth=5,
        max_pages=500,
        extract_assets=True,
        capture_screenshots=True,
        analyze_seo=True,
        analyze_performance=True,
        analyze_security=True,
        export_pdf=True
    ),
    
    'ai_powered': ExtractionConfig(
        extraction_type='ai_powered',
        max_depth=5,
        max_pages=1000,
        extract_assets=True,
        capture_screenshots=True,
        analyze_seo=True,
        analyze_performance=True,
        analyze_security=True,
        export_pdf=True
    )
}


def get_preset_config(preset_name: str) -> ExtractionConfig:
    """الحصول على إعدادات مُعرَّفة مسبقاً"""
    if preset_name not in PRESET_CONFIGS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESET_CONFIGS.keys())}")
    
    return PRESET_CONFIGS[preset_name]