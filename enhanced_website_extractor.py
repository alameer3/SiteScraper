"""
أداة استخراج المواقع المتطورة والآمنة
Enhanced and Secure Website Extractor
- نظام تحكم متقدم مع موافقات المستخدم
- استخراج آمن ومسؤول للمحتوى
- تحليل شامل قبل الاستخراج
- خيارات متقدمة للتخصيص
"""

import os
import re
import json
import requests
import time
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup, Tag
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# تكوين المسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtractionLevel(Enum):
    """مستويات الاستخراج المختلفة"""
    BASIC = "basic"           # HTML ونصوص أساسية فقط
    STANDARD = "standard"     # HTML، CSS، وصور أساسية
    ADVANCED = "advanced"     # جميع الأصول مع JavaScript
    COMPLETE = "complete"     # استخراج شامل مع جميع الملفات

class PermissionType(Enum):
    """أنواع الأذونات المطلوبة"""
    READ_CONTENT = "read_content"
    DOWNLOAD_IMAGES = "download_images"
    EXTRACT_CSS = "extract_css"
    EXTRACT_JS = "extract_js"
    MODIFY_CODE = "modify_code"
    REMOVE_ADS = "remove_ads"
    SAVE_TO_DISK = "save_to_disk"

@dataclass
class ExtractionConfig:
    """إعدادات الاستخراج"""
    url: str
    extraction_level: ExtractionLevel = ExtractionLevel.STANDARD
    max_pages: int = 5
    max_depth: int = 2
    include_external_assets: bool = False
    remove_ads: bool = True
    respect_robots_txt: bool = True
    delay_between_requests: float = 1.0
    user_permissions: Dict[PermissionType, bool] = None
    output_directory: str = "extracted_website"
    preview_before_extraction: bool = True
    
    def __post_init__(self):
        if self.user_permissions is None:
            self.user_permissions = {perm: False for perm in PermissionType}

@dataclass
class ExtractionPreview:
    """معاينة ما سيتم استخراجه"""
    target_url: str
    estimated_pages: int
    estimated_images: int
    estimated_css_files: int
    estimated_js_files: int
    estimated_size_mb: float
    detected_technologies: List[str]
    potential_issues: List[str]
    required_permissions: List[PermissionType]
    extraction_time_estimate: int  # بالثواني

class EnhancedWebsiteExtractor:
    """أداة استخراج المواقع المتطورة والآمنة"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.domain = urlparse(config.url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Website-Analyzer-Tool) Respectful-Crawler/1.0'
        })
        
        # إحصائيات العمليات
        self.stats = {
            'start_time': None,
            'end_time': None,
            'pages_analyzed': 0,
            'files_downloaded': 0,
            'errors_encountered': 0,
            'user_approvals_requested': 0,
            'permissions_granted': 0
        }
        
        # قائمة العمليات المعلقة للموافقة
        self.pending_operations = []
        
    def request_permission(self, permission: PermissionType, details: str = "") -> bool:
        """طلب إذن من المستخدم لعملية معينة"""
        if self.config.user_permissions.get(permission, False):
            return True
            
        self.stats['user_approvals_requested'] += 1
        
        permission_messages = {
            PermissionType.READ_CONTENT: f"قراءة محتوى الموقع: {details}",
            PermissionType.DOWNLOAD_IMAGES: f"تحميل الصور: {details}",
            PermissionType.EXTRACT_CSS: f"استخراج ملفات CSS: {details}",
            PermissionType.EXTRACT_JS: f"استخراج ملفات JavaScript: {details}",
            PermissionType.MODIFY_CODE: f"تعديل الكود لإزالة العناصر غير المرغوبة: {details}",
            PermissionType.REMOVE_ADS: f"إزالة الإعلانات والمتتبعات: {details}",
            PermissionType.SAVE_TO_DISK: f"حفظ الملفات على القرص: {details}"
        }
        
        message = permission_messages.get(permission, f"عملية {permission.value}: {details}")
        
        # في بيئة حقيقية، هذا سيكون واجهة تفاعلية
        logger.warning(f"إذن مطلوب: {message}")
        
        # حالياً نفترض الموافقة للاختبار، لكن في التطبيق الحقيقي سيتم انتظار موافقة المستخدم
        return self._simulate_user_approval(permission, message)
    
    def _simulate_user_approval(self, permission: PermissionType, message: str) -> bool:
        """محاكاة موافقة المستخدم (في التطبيق الحقيقي ستكون واجهة تفاعلية)"""
        # هنا يمكن إضافة منطق متقدم لاتخاذ القرار
        safe_permissions = [PermissionType.READ_CONTENT, PermissionType.REMOVE_ADS]
        
        if permission in safe_permissions:
            self.config.user_permissions[permission] = True
            self.stats['permissions_granted'] += 1
            return True
        
        # للعمليات الأكثر تطفلاً، نحتاج موافقة صريحة
        logger.info(f"في انتظار موافقة المستخدم على: {message}")
        return False
    
    def analyze_website_preview(self) -> ExtractionPreview:
        """تحليل أولي للموقع لإنشاء معاينة"""
        logger.info(f"تحليل أولي للموقع: {self.config.url}")
        
        if not self.request_permission(PermissionType.READ_CONTENT, "للتحليل الأولي"):
            raise PermissionError("لم يتم منح إذن قراءة المحتوى")
        
        try:
            response = self.session.get(self.config.url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحليل المحتوى
            images = soup.find_all('img')
            css_links = soup.find_all('link', rel='stylesheet')
            js_scripts = soup.find_all('script', src=True)
            internal_links = self._find_internal_links(soup)
            
            # تقدير الحجم
            estimated_size = len(response.content) / (1024 * 1024)  # MB
            for img in images[:10]:  # عينة من الصور
                if isinstance(img, Tag) and img.get('src'):
                    try:
                        img_url = urljoin(self.config.url, img.get('src'))
                        head_response = self.session.head(img_url, timeout=5)
                        if 'content-length' in head_response.headers:
                            estimated_size += int(head_response.headers['content-length']) / (1024 * 1024)
                    except:
                        estimated_size += 0.1  # تقدير افتراضي
            
            # كشف التقنيات
            technologies = self._detect_technologies(soup, response)
            
            # تحديد المشاكل المحتملة
            issues = self._identify_potential_issues(soup, response)
            
            # تحديد الأذونات المطلوبة
            required_permissions = self._determine_required_permissions()
            
            preview = ExtractionPreview(
                target_url=self.config.url,
                estimated_pages=min(len(internal_links), self.config.max_pages),
                estimated_images=len(images),
                estimated_css_files=len(css_links),
                estimated_js_files=len(js_scripts),
                estimated_size_mb=round(estimated_size, 2),
                detected_technologies=technologies,
                potential_issues=issues,
                required_permissions=required_permissions,
                extraction_time_estimate=self._estimate_extraction_time(len(images), len(internal_links))
            )
            
            return preview
            
        except Exception as e:
            logger.error(f"خطأ في التحليل الأولي: {e}")
            raise
    
    def _find_internal_links(self, soup: BeautifulSoup) -> List[str]:
        """العثور على الروابط الداخلية"""
        internal_links = []
        for link in soup.find_all('a', href=True):
            if isinstance(link, Tag):
                href = link.get('href')
                if href:
                    full_url = urljoin(self.config.url, href)
                    if urlparse(full_url).netloc == self.domain:
                        internal_links.append(full_url)
        return list(set(internal_links))
    
    def _detect_technologies(self, soup: BeautifulSoup, response: requests.Response) -> List[str]:
        """كشف التقنيات المستخدمة"""
        technologies = []
        content = response.text.lower()
        
        # كشف التقنيات الشائعة
        tech_patterns = {
            'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
            'React': ['react', 'reactdom', 'jsx'],
            'Vue.js': ['vue.js', 'vuejs', 'v-if'],
            'Angular': ['angular', 'ng-app'],
            'jQuery': ['jquery', '$('],
            'Bootstrap': ['bootstrap', 'btn-'],
            'Font Awesome': ['font-awesome', 'fa-'],
            'Google Analytics': ['google-analytics', 'gtag'],
            'Shopify': ['shopify', 'shop.js']
        }
        
        for tech, patterns in tech_patterns.items():
            if any(pattern in content for pattern in patterns):
                technologies.append(tech)
        
        # فحص الخادم
        if 'server' in response.headers:
            technologies.append(f"Server: {response.headers['server']}")
        
        return technologies
    
    def _identify_potential_issues(self, soup: BeautifulSoup, response: requests.Response) -> List[str]:
        """تحديد المشاكل المحتملة"""
        issues = []
        
        # فحص حماية المحتوى
        if soup.find(attrs={'oncontextmenu': True}):
            issues.append("الموقع يحتوي على حماية ضد النسخ")
        
        # فحص الإعلانات
        ad_indicators = soup.find_all(class_=re.compile(r'ad|advertisement|banner', re.I))
        if ad_indicators:
            issues.append(f"تم اكتشاف {len(ad_indicators)} عنصر إعلاني محتمل")
        
        # فحص المحتوى الديناميكي
        if soup.find_all('script', src=True):
            issues.append("الموقع يحتوي على محتوى ديناميكي قد يتطلب JavaScript")
        
        # فحص حجم المحتوى
        if len(response.content) > 5 * 1024 * 1024:  # 5MB
            issues.append("الصفحة كبيرة الحجم قد تستغرق وقتاً أطول")
        
        return issues
    
    def _determine_required_permissions(self) -> List[PermissionType]:
        """تحديد الأذونات المطلوبة بناء على الإعدادات"""
        permissions = [PermissionType.READ_CONTENT]
        
        if self.config.extraction_level in [ExtractionLevel.STANDARD, ExtractionLevel.ADVANCED, ExtractionLevel.COMPLETE]:
            permissions.extend([
                PermissionType.DOWNLOAD_IMAGES,
                PermissionType.EXTRACT_CSS,
                PermissionType.SAVE_TO_DISK
            ])
        
        if self.config.extraction_level in [ExtractionLevel.ADVANCED, ExtractionLevel.COMPLETE]:
            permissions.append(PermissionType.EXTRACT_JS)
        
        if self.config.remove_ads:
            permissions.extend([
                PermissionType.REMOVE_ADS,
                PermissionType.MODIFY_CODE
            ])
        
        return permissions
    
    def _estimate_extraction_time(self, num_images: int, num_pages: int) -> int:
        """تقدير وقت الاستخراج بالثواني"""
        base_time = 30  # ثواني أساسية
        image_time = num_images * 2  # ثانيتان لكل صورة
        page_time = num_pages * 5  # 5 ثواني لكل صفحة
        return base_time + image_time + page_time
    
    def start_extraction(self, user_confirmed: bool = False) -> Dict[str, Any]:
        """بدء عملية الاستخراج مع التحكم الكامل"""
        if not user_confirmed:
            preview = self.analyze_website_preview()
            return {
                'status': 'preview_ready',
                'preview': asdict(preview),
                'message': 'يرجى مراجعة المعاينة والموافقة على الاستخراج'
            }
        
        logger.info("بدء عملية الاستخراج المتطورة")
        self.stats['start_time'] = datetime.now()
        
        try:
            # التحقق من جميع الأذونات المطلوبة
            required_permissions = self._determine_required_permissions()
            for permission in required_permissions:
                if not self.request_permission(permission, f"مطلوب للاستخراج من {self.config.url}"):
                    return {
                        'status': 'permission_denied',
                        'denied_permission': permission.value,
                        'message': f'تم رفض الإذن: {permission.value}'
                    }
            
            # إنشاء دليل الإخراج
            output_path = Path(self.config.output_directory)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            
            # بدء عملية الاستخراج الفعلية
            extraction_results = self._perform_extraction()
            
            self.stats['end_time'] = datetime.now()
            extraction_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            return {
                'status': 'completed',
                'results': extraction_results,
                'stats': self.stats,
                'extraction_time': extraction_time,
                'output_directory': str(output_path.absolute())
            }
            
        except Exception as e:
            logger.error(f"خطأ في عملية الاستخراج: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'stats': self.stats
            }
    
    def _perform_extraction(self) -> Dict[str, Any]:
        """تنفيذ عملية الاستخراج الفعلية"""
        results = {
            'pages_extracted': [],
            'assets_downloaded': [],
            'modifications_made': [],
            'errors': []
        }
        
        try:
            # استخراج الصفحة الرئيسية
            main_page_result = self._extract_single_page(self.config.url)
            results['pages_extracted'].append(main_page_result)
            self.stats['pages_analyzed'] += 1
            
            # معالجة الصفحات الإضافية إذا كان مسموحاً
            if self.config.max_pages > 1:
                additional_pages = self._extract_additional_pages()
                results['pages_extracted'].extend(additional_pages)
            
            logger.info(f"تم استخراج {len(results['pages_extracted'])} صفحة بنجاح")
            
        except Exception as e:
            results['errors'].append(f"خطأ في الاستخراج: {str(e)}")
            self.stats['errors_encountered'] += 1
        
        return results
    
    def _extract_single_page(self, url: str) -> Dict[str, Any]:
        """استخراج صفحة واحدة"""
        logger.info(f"استخراج الصفحة: {url}")
        
        response = self.session.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        page_result = {
            'url': url,
            'title': soup.title.string if soup.title else 'بدون عنوان',
            'content_extracted': True,
            'modifications': []
        }
        
        # إزالة الإعلانات إذا كان مطلوباً ومسموحاً
        if self.config.remove_ads and self.config.user_permissions.get(PermissionType.REMOVE_ADS):
            ads_removed = self._remove_advertisements(soup)
            page_result['modifications'].append(f"تم إزالة {ads_removed} عنصر إعلاني")
        
        # حفظ المحتوى المنظف
        if self.config.user_permissions.get(PermissionType.SAVE_TO_DISK):
            self._save_cleaned_html(soup, url)
            page_result['saved_to_disk'] = True
        
        return page_result
    
    def _extract_additional_pages(self) -> List[Dict[str, Any]]:
        """استخراج صفحات إضافية"""
        additional_results = []
        # تنفيذ منطق استخراج الصفحات الإضافية
        # هذا سيكون مشابهاً لـ _extract_single_page لكن مع تحكم في العدد والعمق
        return additional_results
    
    def _remove_advertisements(self, soup: BeautifulSoup) -> int:
        """إزالة الإعلانات من المحتوى"""
        ads_removed = 0
        
        # قائمة محسنة من selectors للإعلانات
        ad_selectors = [
            '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
            '[class*="banner"]', '[class*="popup"]', '[data-ad]',
            '.google-ads', '.adsense', '[class*="sponsor"]'
        ]
        
        for selector in ad_selectors:
            ad_elements = soup.select(selector)
            for element in ad_elements:
                element.decompose()
                ads_removed += 1
        
        return ads_removed
    
    def _save_cleaned_html(self, soup: BeautifulSoup, url: str):
        """حفظ HTML المنظف"""
        filename = self._generate_filename(url) + '.html'
        output_path = Path(self.config.output_directory) / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        self.stats['files_downloaded'] += 1
        logger.info(f"تم حفظ الملف: {output_path}")
    
    def _generate_filename(self, url: str) -> str:
        """إنشاء اسم ملف آمن من URL"""
        parsed = urlparse(url)
        path = parsed.path.strip('/') or 'index'
        # تنظيف اسم الملف من الأحرف غير المقبولة
        safe_name = re.sub(r'[^\w\-_.]', '_', path)
        return safe_name[:50]  # تحديد طول اسم الملف
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """ملخص شامل لعملية الاستخراج"""
        return {
            'configuration': asdict(self.config),
            'statistics': self.stats,
            'permissions_status': {
                perm.value: granted 
                for perm, granted in self.config.user_permissions.items()
            }
        }

# دالة مساعدة لإنشاء إعدادات الاستخراج
def create_extraction_config(
    url: str, 
    level: str = "standard",
    max_pages: int = 5,
    remove_ads: bool = True,
    preview: bool = True
) -> ExtractionConfig:
    """إنشاء إعدادات الاستخراج بسهولة"""
    
    level_map = {
        "basic": ExtractionLevel.BASIC,
        "standard": ExtractionLevel.STANDARD,
        "advanced": ExtractionLevel.ADVANCED,
        "complete": ExtractionLevel.COMPLETE
    }
    
    return ExtractionConfig(
        url=url,
        extraction_level=level_map.get(level, ExtractionLevel.STANDARD),
        max_pages=max_pages,
        remove_ads=remove_ads,
        preview_before_extraction=preview
    )