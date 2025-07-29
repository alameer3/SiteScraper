"""
واجهة الاستخراج المتطورة الموحدة
Unified Advanced Extraction Interface
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from .core.extractor_engine import AdvancedExtractorEngine
from .core.config import ExtractionConfig, get_preset_config


class AdvancedWebsiteExtractor:
    """واجهة مبسطة لاستخدام محرك الاستخراج المتطور"""
    
    def __init__(self, output_directory: str = "extracted_files"):
        """تهيئة أداة الاستخراج"""
        self.output_directory = output_directory
        self.engine = None
        
    def extract(self, url: str, extraction_type: str = "standard", custom_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        استخراج شامل للموقع
        
        Args:
            url: رابط الموقع المراد استخراجه
            extraction_type: نوع الاستخراج (basic, standard, advanced, complete)
            custom_config: إعدادات مخصصة اختيارية
            
        Returns:
            Dict: نتائج الاستخراج الشاملة
        """
        
        # إعداد التكوين
        if custom_config:
            config = ExtractionConfig.from_dict(custom_config)
        else:
            config = get_preset_config(extraction_type)
        
        config.target_url = url
        config.output_directory = self.output_directory
        
        # تهيئة المحرك
        self.engine = AdvancedExtractorEngine(config)
        result = self.engine.extract_website(url, extraction_type)
            
        return result
    
    def extract_basic(self, url: str) -> Dict[str, Any]:
        """استخراج أساسي سريع"""
        return self.extract(url, "basic")
    
    def extract_standard(self, url: str) -> Dict[str, Any]:
        """استخراج قياسي مع تحليلات متقدمة"""
        return self.extract(url, "standard")
    
    def extract_advanced(self, url: str) -> Dict[str, Any]:
        """استخراج متقدم مع تحميل الأصول"""
        return self.extract(url, "advanced")
    
    def extract_complete(self, url: str) -> Dict[str, Any]:
        """استخراج شامل مع جميع الميزات"""
        return self.extract(url, "complete")
    
    def extract_with_custom_config(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج مع إعدادات مخصصة"""
        return self.extract(url, "custom", config)
    
    def get_available_presets(self) -> List[str]:
        """الحصول على أنواع الاستخراج المتاحة"""
        return ["basic", "standard", "advanced", "complete"]
    
    def create_custom_config(self, 
                           extraction_type: str = "standard",
                           extract_assets: bool = True,
                           extract_images: bool = True,
                           capture_screenshots: bool = False,
                           analyze_security: bool = True,
                           analyze_seo: bool = True,
                           export_formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        إنشاء إعدادات مخصصة
        
        Args:
            extraction_type: نوع الاستخراج الأساسي
            extract_assets: تحميل الأصول
            extract_images: تحليل الصور
            capture_screenshots: التقاط لقطات الشاشة
            analyze_security: تحليل الأمان
            analyze_seo: تحليل SEO
            export_formats: صيغ التصدير ['json', 'csv', 'html', 'pdf']
            
        Returns:
            Dict: إعدادات مخصصة
        """
        
        if export_formats is None:
            export_formats = ['json', 'html']
        
        config = get_preset_config(extraction_type)
        
        # تحديث الإعدادات المخصصة
        config.extract_assets = extract_assets
        config.extract_images = extract_images
        config.capture_screenshots = capture_screenshots
        config.analyze_security = analyze_security
        config.analyze_seo = analyze_seo
        
        # إعدادات التصدير
        config.export_json = 'json' in export_formats
        config.export_csv = 'csv' in export_formats
        config.export_html = 'html' in export_formats
        config.export_pdf = 'pdf' in export_formats
        
        return config.to_dict()


# دوال مساعدة للاستخدام السريع
def quick_extract(url: str, extraction_type: str = "standard") -> Dict[str, Any]:
    """استخراج سريع بإعدادات افتراضية"""
    extractor = AdvancedWebsiteExtractor()
    return extractor.extract(url, extraction_type)


def extract_basic_info(url: str) -> Dict[str, Any]:
    """استخراج المعلومات الأساسية فقط"""
    return quick_extract(url, "basic")


def extract_with_assets(url: str) -> Dict[str, Any]:
    """استخراج مع تحميل جميع الأصول"""
    return quick_extract(url, "advanced")


def extract_complete_analysis(url: str) -> Dict[str, Any]:
    """تحليل شامل مع جميع الميزات"""
    return quick_extract(url, "complete")


def batch_extract(urls: List[str], extraction_type: str = "standard") -> Dict[str, Any]:
    """
    استخراج متعدد المواقع
    
    Args:
        urls: قائمة بروابط المواقع
        extraction_type: نوع الاستخراج
        
    Returns:
        Dict: نتائج الاستخراج لجميع المواقع
    """
    
    extractor = AdvancedWebsiteExtractor()
    results = {}
    
    for i, url in enumerate(urls):
        print(f"استخراج الموقع {i+1}/{len(urls)}: {url}")
        try:
            result = extractor.extract(url, extraction_type)
            results[url] = result
        except Exception as e:
            results[url] = {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    return {
        'total_sites': len(urls),
        'successful_extractions': sum(1 for r in results.values() if r.get('success', False)),
        'failed_extractions': sum(1 for r in results.values() if not r.get('success', False)),
        'results': results
    }


# مثال للاستخدام
if __name__ == "__main__":
    # استخراج أساسي
    result = extract_basic_info("https://example.com")
    print(f"استخراج أساسي: {result.get('title', 'غير متوفر')}")
    
    # استخراج متقدم
    result = extract_with_assets("https://example.com")
    print(f"عدد الأصول المحملة: {len(result.get('assets', {}).get('images', []))}")
    
    # استخراج مخصص
    extractor = AdvancedWebsiteExtractor()
    custom_config = extractor.create_custom_config(
        extraction_type="advanced",
        capture_screenshots=True,
        export_formats=['json', 'html', 'csv']
    )
    
    result = extractor.extract_with_custom_config("https://example.com", custom_config)
    print(f"استخراج مخصص مكتمل: {result.get('success', False)}")