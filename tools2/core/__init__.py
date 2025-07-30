"""
مجلد core - المكونات الأساسية لأدوات الاستخراج
Core Components for Website Extraction Tools
"""

# استيراد المكونات الأساسية
try:
    from .config import ExtractionConfig, get_preset_config
    from .session_manager import SessionManager
    from .file_manager import FileManager
    from .content_extractor import ContentExtractor
    from .security_analyzer import SecurityAnalyzer
    from .asset_downloader import AssetDownloader
    from .ai_analyzer import BasicAIAnalyzer
    from .spider_engine import AdvancedSpiderEngine, SpiderConfig
    from .extractor_engine import AdvancedExtractorEngine
    
    __all__ = [
        'ExtractionConfig',
        'get_preset_config', 
        'SessionManager',
        'FileManager',
        'ContentExtractor',
        'SecurityAnalyzer',
        'AssetDownloader',
        'BasicAIAnalyzer',
        'AdvancedSpiderEngine',
        'SpiderConfig',
        'AdvancedExtractorEngine'
    ]
    
except ImportError as e:
    print(f"تحذير: لا يمكن استيراد بعض المكونات: {e}")
    __all__ = []

__version__ = "1.0.0"
__author__ = "Advanced Extraction Team"