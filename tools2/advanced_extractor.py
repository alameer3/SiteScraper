"""
أداة الاستخراج المتطورة - الواجهة الرئيسية
Advanced Extractor Tool - Main Interface
"""

from .core import AdvancedExtractorEngine, ExtractionConfig, get_preset_config
from typing import Dict, Any, Optional


class AdvancedExtractor:
    """الواجهة الرئيسية لأداة الاستخراج المتطورة"""
    
    def __init__(self):
        """تهيئة أداة الاستخراج"""
        self.engine = None
        self.current_config = None
    
    def extract_website(self, 
                       url: str, 
                       extraction_type: str = "standard",
                       custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        استخراج موقع ويب بالإعدادات المحددة
        
        Args:
            url: رابط الموقع المراد استخراجه
            extraction_type: نوع الاستخراج (basic, standard, advanced, complete)
            custom_config: إعدادات مخصصة (اختيارية)
        
        Returns:
            نتائج الاستخراج مع جميع البيانات المُحللة
        """
        
        try:
            # إعداد التكوين
            if custom_config:
                config = ExtractionConfig.from_dict(custom_config)
            else:
                config = get_preset_config(extraction_type)
            
            config.target_url = url
            self.current_config = config
            
            # إنشاء محرك الاستخراج
            with AdvancedExtractorEngine(config) as engine:
                self.engine = engine
                result = engine.extract_website(url, extraction_type)
                
                # إضافة معلومات إضافية للنتيجة
                result['extractor_version'] = '1.0.0'
                result['config_used'] = config.to_dict()
                
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'extraction_type': extraction_type
            }
    
    def extract_basic(self, url: str) -> Dict[str, Any]:
        """استخراج أساسي سريع"""
        return self.extract_website(url, "basic")
    
    def extract_standard(self, url: str) -> Dict[str, Any]:
        """استخراج قياسي مع تحليلات متوسطة"""
        return self.extract_website(url, "standard")
    
    def extract_advanced(self, url: str) -> Dict[str, Any]:
        """استخراج متقدم مع تحليلات شاملة"""
        return self.extract_website(url, "advanced")
    
    def extract_complete(self, url: str) -> Dict[str, Any]:
        """استخراج كامل مع جميع الميزات"""
        return self.extract_website(url, "complete")
    
    def extract_with_custom_config(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج بإعدادات مخصصة"""
        return self.extract_website(url, custom_config=config)
    
    def get_available_extraction_types(self) -> Dict[str, str]:
        """قائمة أنواع الاستخراج المتاحة"""
        return {
            'basic': 'استخراج أساسي - معلومات عامة فقط',
            'standard': 'استخراج قياسي - تحليل متوسط مع الأصول',
            'advanced': 'استخراج متقدم - تحليل شامل مع الأمان',
            'complete': 'استخراج كامل - جميع الميزات مع الأرشيف'
        }
    
    def create_custom_config(self, 
                           extraction_type: str = "standard",
                           **kwargs) -> ExtractionConfig:
        """إنشاء إعدادات مخصصة"""
        
        config = get_preset_config(extraction_type)
        
        # تطبيق التخصيصات
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def get_statistics(self) -> Dict[str, Any]:
        """إحصائيات الاستخراج"""
        if self.engine:
            return self.engine.get_statistics()
        return {'message': 'لا توجد إحصائيات متاحة'}


def quick_extract(url: str, extraction_type: str = "standard") -> Dict[str, Any]:
    """وظيفة سريعة للاستخراج"""
    extractor = AdvancedExtractor()
    return extractor.extract_website(url, extraction_type)


def extract_multiple_urls(urls: list, extraction_type: str = "standard") -> Dict[str, Any]:
    """استخراج مواقع متعددة"""
    results = {}
    extractor = AdvancedExtractor()
    
    for i, url in enumerate(urls, 1):
        print(f"استخراج الموقع {i}/{len(urls)}: {url}")
        try:
            result = extractor.extract_website(url, extraction_type)
            results[url] = result
        except Exception as e:
            results[url] = {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    return {
        'total_urls': len(urls),
        'successful_extractions': sum(1 for r in results.values() if r.get('success', False)),
        'results': results
    }


# الكلاسات المُصدَّرة للاستيراد
__all__ = [
    'AdvancedExtractor',
    'quick_extract', 
    'extract_multiple_urls',
    'ExtractionConfig',
    'get_preset_config'
]


if __name__ == "__main__":
    # مثال على الاستخدام
    extractor = AdvancedExtractor()
    
    # اختبار الاستخراج الأساسي
    test_url = "https://example.com"
    print(f"اختبار استخراج: {test_url}")
    
    result = extractor.extract_basic(test_url)
    
    if result.get('success'):
        print("✅ نجح الاستخراج!")
        print(f"العنوان: {result.get('title', 'غير متوفر')}")
        print(f"النطاق: {result.get('domain', 'غير متوفر')}")
        print(f"عدد الروابط: {result.get('links_count', 0)}")
        print(f"عدد الصور: {result.get('images_count', 0)}")
        print(f"المدة: {result.get('duration', 0)} ثانية")
    else:
        print("❌ فشل الاستخراج:")
        print(result.get('error', 'خطأ غير معروف'))