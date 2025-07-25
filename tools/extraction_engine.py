"""
محرك الاستخراج الشامل - Comprehensive Extraction Engine
دمج جميع أدوات الاستخراج في ملف واحد متطور
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
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from bs4 import BeautifulSoup, Tag, NavigableString
import logging
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
import shutil
import zipfile
import base64
import csv
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ExtractionLevel(Enum):
    """مستويات الاستخراج المختلفة"""
    BASIC = "basic"           # HTML ونصوص أساسية فقط
    STANDARD = "standard"     # HTML، CSS، وصور أساسية
    ADVANCED = "advanced"     # جميع الأصول مع JavaScript
    COMPLETE = "complete"     # استخراج شامل مع جميع الملفات
    ULTRA = "ultra"          # استخراج فائق مع AI

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
    respect_robots: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    delay_between_requests: float = 1.0
    timeout: int = 30
    permissions: Dict[str, bool] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = {perm.value: True for perm in PermissionType}

class SimpleWebsiteExtractor:
    """أداة الاستخراج البسيطة"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.base_url = config.url
        self.domain = urlparse(config.url).netloc
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.user_agent})
        
        # إعداد المجلدات
        self.output_dir = Path("extracted_sites")
        self.site_id = self._generate_site_id()
        self.site_dir = self.output_dir / self.site_id
        self._setup_directories()
        
        # إحصائيات
        self.stats = {
            'pages_extracted': 0,
            'images_downloaded': 0,
            'css_files': 0,
            'js_files': 0,
            'total_size_bytes': 0,
            'extraction_start': datetime.now().isoformat(),
            'errors': []
        }

    def _generate_site_id(self) -> str:
        """توليد معرف فريد للموقع"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain_hash = hashlib.md5(self.domain.encode()).hexdigest()[:8]
        return f"{self.domain}_{timestamp}_{domain_hash}"

    def _setup_directories(self):
        """إعداد مجلدات الاستخراج"""
        dirs = ['html', 'css', 'js', 'images', 'fonts', 'videos', 'documents']
        for dir_name in dirs:
            (self.site_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def extract_website(self) -> Tuple[Path, Dict[str, Any]]:
        """استخراج الموقع الأساسي"""
        try:
            # تحميل الصفحة الرئيسية
            response = self.session.get(self.base_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج الأصول حسب المستوى
            if self.config.extraction_level in [ExtractionLevel.STANDARD, ExtractionLevel.ADVANCED, ExtractionLevel.COMPLETE]:
                self._extract_css_files(soup)
                self._extract_images(soup)
                
            if self.config.extraction_level in [ExtractionLevel.ADVANCED, ExtractionLevel.COMPLETE]:
                self._extract_js_files(soup)
                
            # حفظ HTML الرئيسي
            self._save_html(soup, 'index.html')
            self.stats['pages_extracted'] += 1
            
            # إنشاء تقرير الاستخراج
            self._generate_report()
            
            return self.site_dir, self.stats
            
        except Exception as e:
            self.stats['errors'].append(f"خطأ في الاستخراج: {str(e)}")
            logger.error(f"خطأ في استخراج الموقع: {e}")
            raise

    def _extract_css_files(self, soup: BeautifulSoup):
        """استخراج ملفات CSS"""
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        
        for link in css_links:
            href = link.get('href')
            if href:
                css_url = urljoin(self.base_url, href)
                self._download_asset(css_url, 'css')
                self.stats['css_files'] += 1

    def _extract_js_files(self, soup: BeautifulSoup):
        """استخراج ملفات JavaScript"""
        js_scripts = soup.find_all('script', src=True)
        
        for script in js_scripts:
            src = script.get('src')
            if src:
                js_url = urljoin(self.base_url, src)
                self._download_asset(js_url, 'js')
                self.stats['js_files'] += 1

    def _extract_images(self, soup: BeautifulSoup):
        """استخراج الصور"""
        images = soup.find_all('img', src=True)
        
        for img in images:
            src = img.get('src')
            if src:
                img_url = urljoin(self.base_url, src)
                self._download_asset(img_url, 'images')
                self.stats['images_downloaded'] += 1

    def _download_asset(self, url: str, asset_type: str):
        """تحميل الأصول"""
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            # تحديد اسم الملف
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or 'index'
            
            if not os.path.splitext(filename)[1]:
                # إضافة امتداد مناسب
                content_type = response.headers.get('content-type', '')
                ext = mimetypes.guess_extension(content_type.split(';')[0])
                if ext:
                    filename += ext
            
            # حفظ الملف
            file_path = self.site_dir / asset_type / filename
            file_path.write_bytes(response.content)
            self.stats['total_size_bytes'] += len(response.content)
            
            time.sleep(self.config.delay_between_requests)
            
        except Exception as e:
            self.stats['errors'].append(f"فشل تحميل {url}: {str(e)}")
            logger.warning(f"فشل تحميل الأصل {url}: {e}")

    def _save_html(self, soup: BeautifulSoup, filename: str):
        """حفظ HTML مع التعديلات"""
        # تحديث الروابط لتصبح محلية
        self._update_local_links(soup)
        
        html_path = self.site_dir / 'html' / filename
        html_path.write_text(str(soup), encoding='utf-8')

    def _update_local_links(self, soup: BeautifulSoup):
        """تحديث الروابط لتصبح محلية"""
        # تحديث CSS links
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            href = link.get('href')
            if href:
                filename = os.path.basename(urlparse(href).path)
                link['href'] = f'../css/{filename}'
        
        # تحديث JS links
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                filename = os.path.basename(urlparse(src).path)
                script['src'] = f'../js/{filename}'
        
        # تحديث الصور
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                filename = os.path.basename(urlparse(src).path)
                img['src'] = f'../images/{filename}'

    def _generate_report(self):
        """إنشاء تقرير الاستخراج"""
        report = {
            'extraction_info': {
                'url': self.base_url,
                'domain': self.domain,
                'extraction_level': self.config.extraction_level.value,
                'timestamp': datetime.now().isoformat()
            },
            'statistics': self.stats,
            'config': asdict(self.config)
        }
        
        report_path = self.site_dir / 'extraction_report.json'
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

class UltraWebsiteExtractor(SimpleWebsiteExtractor):
    """أداة الاستخراج الفائقة مع ميزات AI متقدمة"""
    
    def __init__(self, config: ExtractionConfig):
        super().__init__(config)
        self.ai_analysis = {
            'content_classification': {},
            'seo_analysis': {},
            'performance_metrics': {},
            'security_assessment': {}
        }

    def extract_ultra_smart(self) -> Tuple[Path, Dict[str, Any]]:
        """استخراج فائق مع تحليل AI"""
        try:
            # تحميل الصفحة الرئيسية
            response = self.session.get(self.base_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحليل AI للمحتوى
            self._analyze_content_structure(soup)
            self._extract_seo_data(soup)
            self._analyze_performance_metrics(response)
            
            # استخراج الأصول مع معالجة ذكية
            self._smart_asset_extraction(soup)
            
            # معالجة متقدمة للمحتوى
            processed_soup = self._process_content_intelligently(soup)
            
            # حفظ النتائج
            self._save_html(processed_soup, 'index.html')
            self._save_ai_analysis()
            
            self.stats['ai_analysis'] = self.ai_analysis
            self.stats['pages_extracted'] += 1
            
            return self.site_dir, self.stats
            
        except Exception as e:
            self.stats['errors'].append(f"خطأ في الاستخراج الفائق: {str(e)}")
            logger.error(f"خطأ في الاستخراج الفائق: {e}")
            raise

    def _analyze_content_structure(self, soup: BeautifulSoup):
        """تحليل بنية المحتوى بذكاء اصطناعي"""
        self.ai_analysis['content_classification'] = {
            'main_content_areas': self._identify_content_areas(soup),
            'navigation_structure': self._analyze_navigation(soup),
            'media_content': self._classify_media_content(soup),
            'interactive_elements': self._find_interactive_elements(soup)
        }

    def _identify_content_areas(self, soup: BeautifulSoup) -> List[Dict]:
        """تحديد مناطق المحتوى الرئيسية"""
        content_areas = []
        
        # البحث عن المناطق الرئيسية
        main_selectors = ['main', 'article', '[role="main"]', '.main-content', '#main']
        
        for selector in main_selectors:
            elements = soup.select(selector)
            for element in elements:
                if element and len(element.get_text().strip()) > 100:
                    content_areas.append({
                        'type': 'main_content',
                        'selector': selector,
                        'text_length': len(element.get_text()),
                        'has_images': bool(element.find_all('img')),
                        'has_links': bool(element.find_all('a'))
                    })
        
        return content_areas

    def _analyze_navigation(self, soup: BeautifulSoup) -> Dict:
        """تحليل بنية التنقل"""
        nav_elements = soup.find_all('nav') + soup.select('[role="navigation"]')
        
        navigation = {
            'nav_count': len(nav_elements),
            'menu_items': [],
            'breadcrumbs': bool(soup.select('.breadcrumb, .breadcrumbs')),
            'search_form': bool(soup.find('form', {'role': 'search'}))
        }
        
        for nav in nav_elements:
            links = nav.find_all('a')
            navigation['menu_items'].extend([{
                'text': link.get_text().strip(),
                'href': link.get('href', ''),
                'is_external': self._is_external_link(link.get('href', ''))
            } for link in links if link.get_text().strip()])
        
        return navigation

    def _classify_media_content(self, soup: BeautifulSoup) -> Dict:
        """تصنيف المحتوى الإعلامي"""
        return {
            'images': {
                'total': len(soup.find_all('img')),
                'with_alt': len(soup.find_all('img', alt=True)),
                'types': self._classify_image_types(soup)
            },
            'videos': {
                'total': len(soup.find_all('video')),
                'embedded': len(soup.select('iframe[src*="youtube"], iframe[src*="vimeo"]'))
            },
            'audio': len(soup.find_all('audio'))
        }

    def _classify_image_types(self, soup: BeautifulSoup) -> Dict:
        """تصنيف أنواع الصور"""
        images = soup.find_all('img')
        types = {'logos': 0, 'content': 0, 'decorative': 0, 'avatars': 0}
        
        for img in images:
            src = img.get('src', '').lower()
            alt = img.get('alt', '').lower()
            class_name = ' '.join(img.get('class', [])).lower()
            
            if any(word in src or word in alt or word in class_name 
                   for word in ['logo', 'brand']):
                types['logos'] += 1
            elif any(word in src or word in alt or word in class_name 
                     for word in ['avatar', 'profile', 'user']):
                types['avatars'] += 1
            elif any(word in src or word in alt or word in class_name 
                     for word in ['icon', 'decoration', 'bg']):
                types['decorative'] += 1
            else:
                types['content'] += 1
        
        return types

    def _find_interactive_elements(self, soup: BeautifulSoup) -> Dict:
        """العثور على العناصر التفاعلية"""
        return {
            'forms': len(soup.find_all('form')),
            'buttons': len(soup.find_all('button')),
            'inputs': len(soup.find_all('input')),
            'dropdowns': len(soup.find_all('select')),
            'modals': len(soup.select('[data-toggle="modal"], .modal')),
            'tabs': len(soup.select('[role="tab"], .tab')),
            'accordions': len(soup.select('.accordion, [data-toggle="collapse"]'))
        }

    def _extract_seo_data(self, soup: BeautifulSoup):
        """استخراج بيانات SEO"""
        self.ai_analysis['seo_analysis'] = {
            'title': soup.find('title').get_text() if soup.find('title') else '',
            'meta_description': self._get_meta_content(soup, 'description'),
            'meta_keywords': self._get_meta_content(soup, 'keywords'),
            'headings': self._analyze_headings(soup),
            'open_graph': self._extract_open_graph(soup),
            'twitter_cards': self._extract_twitter_cards(soup),
            'structured_data': self._find_structured_data(soup)
        }

    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str:
        """الحصول على محتوى meta tag"""
        meta = soup.find('meta', {'name': name}) or soup.find('meta', {'property': name})
        return meta.get('content', '') if meta else ''

    def _analyze_headings(self, soup: BeautifulSoup) -> Dict:
        """تحليل العناوين"""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = {
                'count': len(h_tags),
                'texts': [h.get_text().strip() for h in h_tags[:5]]  # أول 5 عناوين فقط
            }
        return headings

    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict:
        """استخراج بيانات Open Graph"""
        og_data = {}
        og_tags = soup.find_all('meta', {'property': lambda x: x and x.startswith('og:')})
        
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                og_data[property_name] = content
        
        return og_data

    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict:
        """استخراج بيانات Twitter Cards"""
        twitter_data = {}
        twitter_tags = soup.find_all('meta', {'name': lambda x: x and x.startswith('twitter:')})
        
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                twitter_data[name] = content
        
        return twitter_data

    def _find_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """البحث عن البيانات المنظمة"""
        structured_data = []
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append({'type': 'json-ld', 'data': data})
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Microdata
        microdata_items = soup.find_all(attrs={'itemscope': True})
        for item in microdata_items:
            item_type = item.get('itemtype', '')
            if item_type:
                structured_data.append({'type': 'microdata', 'itemtype': item_type})
        
        return structured_data

    def _analyze_performance_metrics(self, response: requests.Response):
        """تحليل مقاييس الأداء"""
        self.ai_analysis['performance_metrics'] = {
            'response_time': getattr(response, 'elapsed', None),
            'content_size': len(response.content),
            'compression': 'gzip' in response.headers.get('content-encoding', ''),
            'cache_headers': {
                'cache_control': response.headers.get('cache-control', ''),
                'expires': response.headers.get('expires', ''),
                'etag': response.headers.get('etag', '')
            },
            'security_headers': {
                'https': response.url.startswith('https://'),
                'hsts': 'strict-transport-security' in response.headers,
                'content_security_policy': 'content-security-policy' in response.headers,
                'x_frame_options': response.headers.get('x-frame-options', '')
            }
        }

    def _smart_asset_extraction(self, soup: BeautifulSoup):
        """استخراج الأصول بذكاء"""
        # تحديد الأصول الأساسية vs الثانوية
        critical_assets = self._identify_critical_assets(soup)
        
        # استخراج متوازي للأصول الحيوية
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for asset_type, assets in critical_assets.items():
                for asset_url in assets:
                    future = executor.submit(self._download_asset, asset_url, asset_type)
                    futures.append(future)
            
            # انتظار انتهاء جميع التحميلات
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.warning(f"فشل تحميل أصل: {e}")

    def _identify_critical_assets(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """تحديد الأصول الحيوية"""
        critical_assets = {
            'css': [],
            'js': [],
            'images': []
        }
        
        # CSS حيوي
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        for link in css_links:
            href = link.get('href')
            if href and not any(skip in href.lower() for skip in ['print', 'alternate']):
                critical_assets['css'].append(urljoin(self.base_url, href))
        
        # JavaScript حيوي (استثناء Analytics وTracking)
        js_scripts = soup.find_all('script', src=True)
        for script in js_scripts:
            src = script.get('src')
            if src and not any(skip in src.lower() for skip in ['analytics', 'tracking', 'ads']):
                critical_assets['js'].append(urljoin(self.base_url, src))
        
        # الصور الأساسية (logos، hero images)
        images = soup.find_all('img')
        for img in images:
            src = img.get('src')
            if src:
                # أولوية للصور الكبيرة أو ذات الأهمية
                if (img.get('alt', '').lower() in ['logo', 'hero', 'banner'] or
                    any(cls in ' '.join(img.get('class', [])).lower() 
                        for cls in ['logo', 'hero', 'banner', 'main'])):
                    critical_assets['images'].append(urljoin(self.base_url, src))
        
        return critical_assets

    def _process_content_intelligently(self, soup: BeautifulSoup) -> BeautifulSoup:
        """معالجة المحتوى بذكاء"""
        # إزالة العناصر غير المرغوبة
        if self.config.remove_ads:
            soup = self._remove_ads_intelligently(soup)
        
        # تحسين الصور
        soup = self._optimize_images(soup)
        
        # تنظيف الكود
        soup = self._clean_html_code(soup)
        
        return soup

    def _remove_ads_intelligently(self, soup: BeautifulSoup) -> BeautifulSoup:
        """إزالة الإعلانات بذكاء"""
        ad_selectors = [
            '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
            '.google-ads', '.adsbygoogle', '[data-ad-client]',
            '[class*="banner"]', '[class*="popup"]', '[class*="modal"]'
        ]
        
        for selector in ad_selectors:
            elements = soup.select(selector)
            for element in elements:
                # فحص إضافي للتأكد من أنه إعلان
                if self._is_likely_ad(element):
                    element.decompose()
        
        return soup

    def _is_likely_ad(self, element: Tag) -> bool:
        """فحص ما إذا كان العنصر إعلاناً"""
        if not isinstance(element, Tag):
            return False
        
        # فحص النص
        text = element.get_text().lower()
        ad_keywords = ['sponsored', 'advertisement', 'ads by', 'promoted']
        
        if any(keyword in text for keyword in ad_keywords):
            return True
        
        # فحص الخصائص
        attrs = str(element.attrs).lower()
        if any(word in attrs for word in ['doubleclick', 'googleads', 'adsystem']):
            return True
        
        return False

    def _optimize_images(self, soup: BeautifulSoup) -> BeautifulSoup:
        """تحسين الصور"""
        for img in soup.find_all('img'):
            # إضافة loading="lazy" للصور غير الحيوية
            if not any(cls in ' '.join(img.get('class', [])).lower() 
                      for cls in ['hero', 'logo', 'above-fold']):
                img['loading'] = 'lazy'
            
            # إضافة alt إذا لم يكن موجوداً
            if not img.get('alt'):
                img['alt'] = 'صورة'
        
        return soup

    def _clean_html_code(self, soup: BeautifulSoup) -> BeautifulSoup:
        """تنظيف كود HTML"""
        # إزالة التعليقات
        for comment in soup.find_all(string=lambda text: isinstance(text, type(soup))):
            if hasattr(comment, 'extract'):
                comment.extract()
        
        # إزالة الخصائص غير الضرورية
        for element in soup.find_all():
            # إزالة خصائص التتبع
            tracking_attrs = ['data-track', 'data-analytics', 'onclick', 'onload']
            for attr in tracking_attrs:
                if element.has_attr(attr):
                    del element[attr]
        
        return soup

    def _save_ai_analysis(self):
        """حفظ تحليل AI"""
        ai_report_path = self.site_dir / 'ai_analysis.json'
        ai_report_path.write_text(
            json.dumps(self.ai_analysis, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def _is_external_link(self, href: str) -> bool:
        """فحص ما إذا كان الرابط خارجياً"""
        if not href or href.startswith('#') or href.startswith('mailto:'):
            return False
        
        parsed = urlparse(href)
        return parsed.netloc and parsed.netloc != self.domain

# وظائف مساعدة للاستخدام السريع
def extract_website_simple(url: str, extraction_level: str = "standard") -> Tuple[Path, Dict[str, Any]]:
    """استخراج بسيط للموقع"""
    config = ExtractionConfig(
        url=url,
        extraction_level=ExtractionLevel(extraction_level)
    )
    extractor = SimpleWebsiteExtractor(config)
    return extractor.extract_website()

def extract_website_ultra(url: str, config: Dict[str, Any] = None) -> Tuple[Path, Dict[str, Any]]:
    """استخراج فائق للموقع"""
    extraction_config = ExtractionConfig(
        url=url,
        extraction_level=ExtractionLevel.ULTRA,
        **(config if config else {})
    )
    extractor = UltraWebsiteExtractor(extraction_config)
    return extractor.extract_ultra_smart()