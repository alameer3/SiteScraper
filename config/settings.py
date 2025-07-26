"""
Application configuration and settings.
"""

import os
from typing import Dict, Any

class Config:
    """Main application configuration."""
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data/analyzer.db')
    
    # Security settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-key-change-in-production')
    
    # Cache settings
    CACHE_ENABLED = True
    CACHE_TIMEOUT_HOURS = 24
    CACHE_MAX_ENTRIES = 1000
    
    # Extraction settings
    DEFAULT_EXTRACTION_MODE = 'standard'
    MAX_CRAWL_DEPTH = 5
    REQUEST_TIMEOUT = 30
    CRAWL_DELAY = 1.0
    
    # Export settings
    EXPORT_FORMATS = ['json', 'csv', 'xml', 'html', 'pdf']
    MAX_EXPORT_SIZE_MB = 100
    
    # Analysis settings
    ENABLE_AI_ANALYSIS = True
    ENABLE_SECURITY_SCAN = True
    ENABLE_PERFORMANCE_ANALYSIS = True
    
    # Rate limiting
    REQUESTS_PER_MINUTE = 60
    BURST_REQUESTS = 10
    
    # File paths
    BASE_DATA_PATH = 'data'
    CACHE_PATH = 'data/cache'
    EXPORTS_PATH = 'data/exports'
    REPORTS_PATH = 'data/reports'
    
    @classmethod
    def get_extraction_config(cls, mode: str) -> Dict[str, Any]:
        """Get extraction configuration for specified mode."""
        configs = {
            'basic': {
                'depth': 1,
                'include_assets': False,
                'include_links': True,
                'timeout': 15
            },
            'standard': {
                'depth': 2,
                'include_assets': True,
                'include_links': True,
                'timeout': 30
            },
            'advanced': {
                'depth': 3,
                'include_assets': True,
                'include_links': True,
                'include_seo': True,
                'timeout': 60
            },
            'ultra': {
                'depth': 5,
                'include_assets': True,
                'include_links': True,
                'include_seo': True,
                'include_security': True,
                'include_ai_analysis': True,
                'timeout': 120
            },
            'secure': {
                'depth': 2,
                'include_assets': False,
                'include_links': False,
                'security_focused': True,
                'timeout': 45
            }
        }
        
        return configs.get(mode, configs['standard'])

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    
class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    
    # Enhanced security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Environment-based configuration selection
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(env, DevelopmentConfig)()