"""
إصلاحات LSP شاملة لجميع أدوات الاستخراج
هذا الملف يحتوي على إصلاحات جميع مشاكل الكود والأخطاء في النظام
"""

import logging
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
import asyncio
import aiohttp
import time
from pathlib import Path
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin, urlparse

# إصلاحات AssetDownloader
@dataclass
class FixedAssetDownloadConfig:
    """تكوين تحميل الأصول المُحسن"""
    max_file_size: int = 50 * 1024 * 1024
    timeout: int = 30
    max_concurrent_downloads: int = 10
    save_directory: str = "downloaded_assets"
    organize_by_type: bool = True
    verify_checksums: bool = True
    allowed_extensions: Set[str] = field(default_factory=lambda: {
        '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.webp', 
        '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot',
        '.mp4', '.mp3', '.wav', '.pdf', '.zip'
    })

# إصلاحات ComprehensiveExtractor
@dataclass  
class FixedComprehensiveExtractionConfig:
    """تكوين الاستخراج الشامل المُحسن"""
    extraction_mode: str = "comprehensive"
    target_url: str = ""
    max_extraction_time: int = 1800
    max_crawl_depth: int = 5
    max_pages: int = 100
    respect_robots_txt: bool = True
    extract_interface: bool = True
    extract_technical_structure: bool = True
    extract_features: bool = True
    extract_behavior: bool = True
    enable_ai_analysis: bool = True
    enable_smart_replication: bool = True
    enable_database_analysis: bool = False
    output_directory: str = "extracted_websites"
    export_formats: List[str] = field(default_factory=lambda: ["json", "html", "project"])

# إصلاحات BeautifulSoup Type Safety
def safe_get_text(element: Union[Tag, NavigableString, None]) -> str:
    """الحصول على النص بشكل آمن من عنصر BeautifulSoup"""
    if element is None:
        return ""
    if isinstance(element, NavigableString):
        return str(element)
    if isinstance(element, Tag):
        return element.get_text(strip=True)
    return str(element)

def safe_get_attribute(element: Union[Tag, None], attr: str, default: str = "") -> str:
    """الحصول على خاصية بشكل آمن من عنصر BeautifulSoup"""
    if element is None or not isinstance(element, Tag):
        return default
    
    attr_value = element.get(attr)
    if attr_value is None:
        return default
    
    # التعامل مع AttributeValueList
    if isinstance(attr_value, list):
        return " ".join(str(v) for v in attr_value)
    
    return str(attr_value)

def safe_find_elements(soup: BeautifulSoup, selector: str) -> List[Tag]:
    """البحث الآمن عن العناصر"""
    try:
        elements = soup.select(selector)
        return [el for el in elements if isinstance(el, Tag)]
    except Exception:
        return []

# إصلاحات Spider Engine
class FixedSpiderEngine:
    """محرك الزحف المُحسن مع إصلاح جميع مشاكل LSP"""
    
    def __init__(self, config=None):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.site_map: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
    
    def _analyze_page_safe(self, content: str, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """تحليل الصفحة بشكل آمن"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            analysis = {
                'title': safe_get_text(soup.find('title')),
                'meta_description': safe_get_attribute(soup.find('meta', attrs={'name': 'description'}), 'content'),
                'links': [],
                'images': [],
                'scripts': [],
                'stylesheets': []
            }
            
            # استخراج الروابط بشكل آمن
            for link in safe_find_elements(soup, 'a[href]'):
                href = safe_get_attribute(link, 'href')
                if href and href.startswith(('http', '/')):
                    analysis['links'].append({
                        'url': urljoin(url, href),
                        'text': safe_get_text(link),
                        'title': safe_get_attribute(link, 'title')
                    })
            
            # استخراج الصور بشكل آمن
            for img in safe_find_elements(soup, 'img[src]'):
                src = safe_get_attribute(img, 'src')
                if src:
                    analysis['images'].append({
                        'url': urljoin(url, src),
                        'alt': safe_get_attribute(img, 'alt'),
                        'title': safe_get_attribute(img, 'title')
                    })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الصفحة: {e}")
            return {'error': str(e)}

# إصلاحات Database Scanner
def fix_database_scanner_methods():
    """إصلاح مشاكل ماسح قاعدة البيانات"""
    
    def safe_form_analysis(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """تحليل النماذج بشكل آمن"""
        forms = []
        
        for form in safe_find_elements(soup, 'form'):
            form_data = {
                'action': safe_get_attribute(form, 'action'),
                'method': safe_get_attribute(form, 'method', 'get').lower(),
                'fields': []
            }
            
            # تحليل الحقول
            for field in safe_find_elements(form, 'input, textarea, select'):
                field_data = {
                    'name': safe_get_attribute(field, 'name'),
                    'type': safe_get_attribute(field, 'type', 'text'),
                    'required': field.has_attr('required')
                }
                form_data['fields'].append(field_data)
            
            forms.append(form_data)
        
        return forms
    
    return safe_form_analysis

# إصلاحات Code Analyzer
class FixedCodeAnalyzer:
    """محلل الكود المُحسن مع إصلاح جميع المشاكل"""
    
    def __init__(self, config=None):
        self.config = config
        self.analysis_results = {
            'javascript_analysis': {},
            'css_analysis': {},
            'html_structure': {},
            'frameworks_detected': [],
            'api_endpoints': [],
            'database_patterns': [],
            'functions_extracted': [],
            'security_analysis': {},
            'architecture_patterns': []
        }
        
    def _detect_database_patterns(self, content: str) -> List[Dict[str, Any]]:
        """كشف أنماط قاعدة البيانات بشكل آمن"""
        patterns = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # البحث عن أنماط قاعدة البيانات في JavaScript
            for script in safe_find_elements(soup, 'script'):
                script_content = safe_get_text(script)
                
                # البحث عن كلمات مفتاحية لقاعدة البيانات
                db_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 'mongodb', 'mysql', 'postgres']
                
                for keyword in db_keywords:
                    if keyword.lower() in script_content.lower():
                        patterns.append({
                            'type': 'database_operation',
                            'keyword': keyword,
                            'context': 'javascript'
                        })
            
            return patterns
            
        except Exception as e:
            logging.error(f"خطأ في كشف أنماط قاعدة البيانات: {e}")
            return []
    
    def _generate_basic_report(self) -> Dict[str, Any]:
        """إنشاء تقرير أساسي"""
        return {
            'total_frameworks': len(self.analysis_results.get('frameworks_detected', [])),
            'total_apis': len(self.analysis_results.get('api_endpoints', [])),
            'security_score': self._calculate_security_score(),
            'complexity_score': self._calculate_complexity_score()
        }
    
    def _calculate_security_score(self) -> int:
        """حساب نقاط الأمان"""
        security_analysis = self.analysis_results.get('security_analysis', {})
        
        score = 50  # نقطة البداية
        
        if security_analysis.get('https_enabled'):
            score += 20
        if security_analysis.get('csrf_protection'):
            score += 15
        if security_analysis.get('input_validation'):
            score += 15
        
        return min(score, 100)
    
    def _calculate_complexity_score(self) -> int:
        """حساب نقاط التعقيد"""
        js_analysis = self.analysis_results.get('javascript_analysis', {})
        
        functions_count = len(js_analysis.get('functions', []))
        apis_count = len(self.analysis_results.get('api_endpoints', []))
        
        # حساب نقاط التعقيد بناءً على عدد الوظائف والـ APIs
        complexity = (functions_count * 2) + (apis_count * 3)
        
        if complexity < 10:
            return 20  # بسيط
        elif complexity < 30:
            return 50  # متوسط
        elif complexity < 60:
            return 80  # معقد
        else:
            return 100  # معقد جداً

print("✅ تم تحميل جميع إصلاحات LSP بنجاح")