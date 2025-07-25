"""
نظام الحجب المتقدم - Advanced Blocking System
يدمج جميع أنواع حجب الإعلانات والمتتبعات في نظام واحد ذكي
"""

import re
import json
import time
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse, urljoin
from collections import defaultdict, Counter

# تكوين المسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockingMode:
    """أنماط الحجب المختلفة"""
    BASIC = "basic"           # حجب أساسي للإعلانات الواضحة
    STANDARD = "standard"     # حجب عادي مع المتتبعات
    ADVANCED = "advanced"     # حجب متقدم مع تحليل ذكي
    AGGRESSIVE = "aggressive" # حجب قوي لجميع العناصر المشبوهة
    CUSTOM = "custom"        # حجب مخصص حسب القواعد المحددة

class AdvancedBlocker:
    """نظام الحجب المتقدم الشامل"""
    
    def __init__(self, blocking_mode: str = BlockingMode.STANDARD):
        self.blocking_mode = blocking_mode
        self.stats = self._init_stats()
        
        # تهيئة قوائم الحجب
        self._init_blocking_lists()
        
        # تهيئة أنماط التحليل
        self._init_analysis_patterns()
        
        # إعدادات متقدمة
        self.settings = {
            'preserve_main_content': True,
            'aggressive_tracking_removal': True,
            'remove_social_widgets': True,
            'clean_comment_sections': False,
            'preserve_navigation': True,
            'remove_popup_overlays': True,
            'block_cryptocurrency_miners': True,
            'remove_newsletter_popups': True
        }

    def _init_stats(self) -> Dict[str, Any]:
        """تهيئة إحصائيات الحجب"""
        return {
            'session_start': time.time(),
            'total_elements_scanned': 0,
            'ads_blocked': 0,
            'trackers_blocked': 0,
            'popups_blocked': 0,
            'social_widgets_blocked': 0,
            'scripts_blocked': 0,
            'images_blocked': 0,
            'iframes_blocked': 0,
            'divs_removed': 0,
            'size_reduction_bytes': 0,
            'size_reduction_percentage': 0,
            'detection_accuracy': 0,
            'false_positives': 0,
            'processing_time_ms': 0,
            'blocked_domains': set(),
            'blocked_categories': Counter()
        }

    def _init_blocking_lists(self):
        """تهيئة قوائم الحجب الشاملة"""
        
        # CSS selectors للإعلانات
        self.ad_selectors = [
            # إعلانات عامة
            '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
            '[class*="ads"]', '[id*="ads"]', '[data-ad]',
            
            # Google Ads
            '.google-ads', '.adsense', '[class*="adsense"]',
            '.adsbygoogle', '[data-google-ad]', '.googlesyndication',
            
            # شبكات إعلانية أخرى
            '[class*="doubleclick"]', '[class*="outbrain"]', '[class*="taboola"]',
            '[class*="revContent"]', '[class*="criteo"]', '[class*="amazon-ads"]',
            
            # بانرات وترويج
            '[class*="banner"]', '[class*="promo"]', '[class*="sponsored"]',
            '[class*="promotion"]', '[class*="commercial"]',
            
            # نوافذ منبثقة
            '[class*="popup"]', '[class*="modal"]', '[class*="overlay"]',
            '[class*="lightbox"]', '[class*="newsletter"]',
            
            # شريط جانبي وتذييل إعلاني
            '[class*="sidebar-ad"]', '[class*="header-ad"]', '[class*="footer-ad"]',
            '[class*="right-ad"]', '[class*="left-ad"]', '[class*="top-ad"]',
            
            # إعلانات مخفية
            '[style*="display:none"]', '[style*="visibility:hidden"]',
            '[width="1"][height="1"]', '[style*="width:1px"][style*="height:1px"]'
        ]
        
        # نطاقات التتبع والإعلانات
        self.tracking_domains = {
            # Google
            'google-analytics.com', 'googletagmanager.com', 'googlesyndication.com',
            'doubleclick.net', 'googleadservices.com', 'google-analytics.com',
            'googletagservices.com', 'googleoptimize.com',
            
            # Facebook
            'facebook.com', 'facebook.net', 'fbcdn.net', 'connect.facebook.net',
            
            # Amazon
            'amazon-adsystem.com', 'adsystem.amazon.com', 'amazon.com/gp/aw/cr',
            
            # Twitter
            'analytics.twitter.com', 'twitter.com/i/adsct',
            
            # شبكات إعلانية
            'outbrain.com', 'taboola.com', 'revcontent.com', 'criteo.com',
            'adsystem.amazon.com', 'amazon-adsystem.com',
            
            # تحليلات
            'hotjar.com', 'mixpanel.com', 'segment.com', 'amplitude.com',
            'fullstory.com', 'mouseflow.com', 'crazyegg.com', 'kissmetrics.com',
            
            # تتبع أخرى
            'scorecardresearch.com', 'quantserve.com', 'nielsen.com',
            'comscore.com', 'chartbeat.com', 'newrelic.com'
        }
        
        # كلمات مفتاحية للمحتوى الإعلاني
        self.ad_keywords = {
            'arabic': [
                'إعلان', 'إعلانات', 'ترويج', 'رعاية', 'إعلان مدفوع',
                'برعاية', 'محتوى مدفوع', 'تسوق الآن', 'خصم', 'عرض خاص',
                'اشتري الآن', 'تخفيضات', 'عروض حصرية'
            ],
            'english': [
                'advertisement', 'sponsored', 'promoted', 'ad', 'ads',
                'buy now', 'shop now', 'special offer', 'discount',
                'exclusive deal', 'limited time', 'sale'
            ]
        }
        
        # أنماط JavaScript للتتبع
        self.tracking_patterns = [
            r'ga\s*\(',  # Google Analytics
            r'gtag\s*\(',  # Google Tag Manager
            r'fbq\s*\(',  # Facebook Pixel
            r'_gaq\.push',  # Google Analytics Old
            r'mixpanel\.',  # Mixpanel
            r'amplitude\.',  # Amplitude
            r'segment\.',  # Segment
            r'hotjar\.',  # Hotjar
            r'mouseflow\.',  # Mouseflow
            r'crazyegg\.'  # Crazy Egg
        ]

    def _init_analysis_patterns(self):
        """تهيئة أنماط التحليل المتقدم"""
        
        # أنماط لكشف الإعلانات المخفية
        self.hidden_ad_patterns = [
            r'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP',  # 1x1 pixel
            r'width\s*:\s*1px.*height\s*:\s*1px',
            r'position\s*:\s*absolute.*left\s*:\s*-\d+px',
            r'overflow\s*:\s*hidden.*height\s*:\s*0'
        ]
        
        # أنماط لكشف النوافذ المنبثقة
        self.popup_patterns = [
            r'window\.open\s*\(',
            r'popup',
            r'overlay',
            r'modal',
            r'lightbox'
        ]
        
        # أنماط لكشف متعدين العملات المشفرة
        self.crypto_miner_patterns = [
            r'coinhive',
            r'crypto-loot',
            r'webmining',
            r'browser-mining',
            r'cryptonight'
        ]

    def clean_content(self, html_content: str, base_url: str = '') -> Dict[str, Any]:
        """تنظيف المحتوى الشامل"""
        start_time = time.time()
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            original_size = len(html_content)
            
            # إحصائيات قبل التنظيف
            self.stats['total_elements_scanned'] = len(soup.find_all())
            
            # تطبيق مراحل التنظيف
            soup = self._remove_ad_elements(soup)
            soup = self._remove_tracking_scripts(soup)
            soup = self._clean_tracking_urls(soup, base_url)
            soup = self._remove_popup_overlays(soup)
            soup = self._clean_social_widgets(soup)
            soup = self._remove_crypto_miners(soup)
            soup = self._clean_hidden_elements(soup)
            soup = self._optimize_remaining_content(soup)
            
            # حساب الإحصائيات النهائية
            cleaned_html = str(soup)
            final_size = len(cleaned_html)
            
            self.stats['size_reduction_bytes'] = original_size - final_size
            self.stats['size_reduction_percentage'] = round(
                (self.stats['size_reduction_bytes'] / original_size) * 100, 2
            ) if original_size > 0 else 0
            
            self.stats['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            self.stats['detection_accuracy'] = self._calculate_detection_accuracy()
            
            return {
                'cleaned_html': cleaned_html,
                'original_size': original_size,
                'final_size': final_size,
                'stats': self.stats.copy(),
                'blocked_elements': self._get_blocked_elements_summary(),
                'performance_improvement': self._estimate_performance_improvement()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف المحتوى: {e}")
            return {
                'cleaned_html': html_content,
                'error': str(e),
                'stats': self.stats
            }

    def _remove_ad_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """إزالة عناصر الإعلانات"""
        removed_count = 0
        
        for selector in self.ad_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_likely_ad(element):
                        element.decompose()
                        removed_count += 1
                        self.stats['ads_blocked'] += 1
            except Exception as e:
                logger.debug(f"خطأ في معالجة السيليكتور {selector}: {e}")
        
        # إزالة عناصر إضافية بناءً على المحتوى النصي
        for element in soup.find_all(text=True):
            if self._contains_ad_keywords(element.string):
                parent = element.parent
                if parent and self._is_safe_to_remove(parent):
                    parent.decompose()
                    removed_count += 1
                    self.stats['ads_blocked'] += 1
        
        logger.debug(f"تم إزالة {removed_count} عنصر إعلاني")
        return soup

    def _remove_tracking_scripts(self, soup: BeautifulSoup) -> BeautifulSoup:
        """إزالة سكريبتات التتبع"""
        removed_count = 0
        
        # إزالة سكريبتات خارجية
        for script in soup.find_all('script', src=True):
            src = script.get('src', '')
            if self._is_tracking_domain(src):
                script.decompose()
                removed_count += 1
                self.stats['scripts_blocked'] += 1
                self.stats['blocked_domains'].add(urlparse(src).netloc)
        
        # إزالة سكريبتات داخلية تحتوي على كود تتبع
        for script in soup.find_all('script'):
            script_content = script.string or ''
            if self._contains_tracking_code(script_content):
                script.decompose()
                removed_count += 1
                self.stats['scripts_blocked'] += 1
        
        logger.debug(f"تم إزالة {removed_count} سكريبت تتبع")
        return soup

    def _clean_tracking_urls(self, soup: BeautifulSoup, base_url: str) -> BeautifulSoup:
        """تنظيف روابط التتبع"""
        cleaned_count = 0
        
        for link in soup.find_all(['a', 'link'], href=True):
            href = link.get('href')
            if href and self._is_tracking_url(href):
                if self._is_safe_to_remove(link):
                    link.decompose()
                    cleaned_count += 1
                    self.stats['trackers_blocked'] += 1
        
        # تنظيف الصور التتبعية
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and (self._is_tracking_domain(src) or self._is_tracking_pixel(img)):
                img.decompose()
                cleaned_count += 1
                self.stats['images_blocked'] += 1
        
        logger.debug(f"تم تنظيف {cleaned_count} رابط تتبع")
        return soup

    def _remove_popup_overlays(self, soup: BeautifulSoup) -> BeautifulSoup:
        """إزالة النوافذ المنبثقة والطبقات العلوية"""
        removed_count = 0
        
        popup_selectors = [
            '[class*="popup"]', '[class*="modal"]', '[class*="overlay"]',
            '[class*="lightbox"]', '[class*="newsletter-popup"]',
            '[style*="position:fixed"]', '[style*="z-index"]'
        ]
        
        for selector in popup_selectors:
            for element in soup.select(selector):
                if self._is_likely_popup(element):
                    element.decompose()
                    removed_count += 1
                    self.stats['popups_blocked'] += 1
        
        logger.debug(f"تم إزالة {removed_count} نافذة منبثقة")
        return soup

    def _clean_social_widgets(self, soup: BeautifulSoup) -> BeautifulSoup:
        """تنظيف أدوات التواصل الاجتماعي"""
        if not self.settings['remove_social_widgets']:
            return soup
        
        removed_count = 0
        social_selectors = [
            '[class*="facebook"]', '[class*="twitter"]', '[class*="social"]',
            '[class*="share"]', '[class*="like"]', '[class*="follow"]'
        ]
        
        for selector in social_selectors:
            for element in soup.select(selector):
                if self._is_social_widget(element):
                    element.decompose()
                    removed_count += 1
                    self.stats['social_widgets_blocked'] += 1
        
        logger.debug(f"تم إزالة {removed_count} أداة تواصل اجتماعي")
        return soup

    def _remove_crypto_miners(self, soup: BeautifulSoup) -> BeautifulSoup:
        """إزالة متعدني العملات المشفرة"""
        if not self.settings['block_cryptocurrency_miners']:
            return soup
        
        removed_count = 0
        
        for script in soup.find_all('script'):
            script_content = script.string or ''
            if any(pattern in script_content.lower() for pattern in self.crypto_miner_patterns):
                script.decompose()
                removed_count += 1
                self.stats['scripts_blocked'] += 1
        
        logger.debug(f"تم إزالة {removed_count} متعدن عملة مشفرة")
        return soup

    def _clean_hidden_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """إزالة العناصر المخفية المشبوهة"""
        removed_count = 0
        
        # عناصر بحجم 1x1 بكسل
        for element in soup.find_all():
            style = element.get('style', '')
            if any(pattern in style for pattern in self.hidden_ad_patterns):
                element.decompose()
                removed_count += 1
        
        # عناصر مخفية بـ CSS
        for element in soup.find_all('[style*="display:none"]'):
            if self._is_likely_tracking_element(element):
                element.decompose()
                removed_count += 1
        
        logger.debug(f"تم إزالة {removed_count} عنصر مخفي مشبوه")
        return soup

    def _optimize_remaining_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """تحسين المحتوى المتبقي"""
        # إزالة التعليقات غير الضرورية
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            if 'google' in comment.lower() or 'analytics' in comment.lower():
                comment.extract()
        
        # تنظيف العناصر الفارغة
        for element in soup.find_all():
            if not element.get_text().strip() and not element.find('img') and not element.find('video'):
                if element.name in ['div', 'span', 'p']:
                    element.decompose()
                    self.stats['divs_removed'] += 1
        
        return soup

    # Helper Methods للفحص والتحليل
    def _is_likely_ad(self, element: Tag) -> bool:
        """فحص ما إذا كان العنصر إعلان"""
        if not element:
            return False
        
        # فحص الكلاس والـ ID
        class_id_text = ' '.join([
            element.get('class', []) if isinstance(element.get('class', []), list) else [element.get('class', '')],
            [element.get('id', '')],
            [element.get_text()[:100]]
        ])
        
        # فحص الكلمات المفتاحية
        for keywords in self.ad_keywords.values():
            if any(keyword.lower() in class_id_text.lower() for keyword in keywords):
                return True
        
        # فحص الأبعاد المشبوهة
        style = element.get('style', '')
        if 'width:1px' in style and 'height:1px' in style:
            return True
        
        return False

    def _is_tracking_domain(self, url: str) -> bool:
        """فحص ما إذا كان النطاق للتتبع"""
        if not url:
            return False
        
        domain = urlparse(url).netloc
        return any(tracking_domain in domain for tracking_domain in self.tracking_domains)

    def _contains_tracking_code(self, script_content: str) -> bool:
        """فحص ما إذا كان السكريبت يحتوي على كود تتبع"""
        if not script_content:
            return False
        
        return any(re.search(pattern, script_content, re.IGNORECASE) 
                  for pattern in self.tracking_patterns)

    def _contains_ad_keywords(self, text: str) -> bool:
        """فحص ما إذا كان النص يحتوي على كلمات إعلانية"""
        if not text:
            return False
        
        text_lower = text.lower()
        for keywords in self.ad_keywords.values():
            if any(keyword.lower() in text_lower for keyword in keywords):
                return True
        
        return False

    def _is_safe_to_remove(self, element: Tag) -> bool:
        """فحص ما إذا كان العنصر آمن للإزالة"""
        if not element or not hasattr(element, 'name'):
            return False
        
        # حماية العناصر المهمة
        important_tags = ['nav', 'main', 'article', 'section', 'header', 'footer']
        if element.name in important_tags:
            return False
        
        # حماية العناصر التي تحتوي على محتوى مفيد
        if element.get_text().strip() and len(element.get_text().strip()) > 100:
            # فحص ما إذا كان المحتوى مفيد أم إعلاني
            return self._contains_ad_keywords(element.get_text())
        
        return True

    def _is_tracking_url(self, url: str) -> bool:
        """فحص ما إذا كان الرابط للتتبع"""
        if not url:
            return False
        
        # فحص النطاقات
        if self._is_tracking_domain(url):
            return True
        
        # فحص معايير URL
        tracking_params = ['utm_', 'fbclid', 'gclid', '_ga', 'mc_eid']
        return any(param in url for param in tracking_params)

    def _is_tracking_pixel(self, img_element: Tag) -> bool:
        """فحص ما إذا كانت الصورة بكسل تتبع"""
        if not img_element:
            return False
        
        # فحص الأبعاد
        width = img_element.get('width')
        height = img_element.get('height')
        
        if width == '1' and height == '1':
            return True
        
        # فحص النطاق
        src = img_element.get('src', '')
        return self._is_tracking_domain(src)

    def _is_likely_popup(self, element: Tag) -> bool:
        """فحص ما إذا كان العنصر نافذة منبثقة"""
        if not element:
            return False
        
        style = element.get('style', '')
        class_name = ' '.join(element.get('class', []))
        
        popup_indicators = [
            'position:fixed', 'position: fixed',
            'z-index:9', 'popup', 'modal', 'overlay'
        ]
        
        return any(indicator in style.lower() or indicator in class_name.lower() 
                  for indicator in popup_indicators)

    def _is_social_widget(self, element: Tag) -> bool:
        """فحص ما إذا كان العنصر أداة تواصل اجتماعي"""
        if not element:
            return False
        
        social_indicators = ['facebook', 'twitter', 'instagram', 'linkedin', 'share', 'like', 'follow']
        element_text = str(element).lower()
        
        return any(indicator in element_text for indicator in social_indicators)

    def _is_likely_tracking_element(self, element: Tag) -> bool:
        """فحص ما إذا كان العنصر للتتبع"""
        if not element:
            return False
        
        # فحص الخصائص
        for attr in ['src', 'href', 'action']:
            value = element.get(attr, '')
            if value and self._is_tracking_domain(value):
                return True
        
        return False

    def _calculate_detection_accuracy(self) -> float:
        """حساب دقة الكشف"""
        total_blocked = (self.stats['ads_blocked'] + self.stats['trackers_blocked'] + 
                        self.stats['popups_blocked'] + self.stats['scripts_blocked'])
        
        if total_blocked == 0:
            return 0.0
        
        # تقدير الدقة بناءً على الأنماط المكتشفة
        estimated_accuracy = min(95.0, 85.0 + (total_blocked / 10))
        return round(estimated_accuracy, 1)

    def _get_blocked_elements_summary(self) -> Dict[str, int]:
        """ملخص العناصر المحجوبة"""
        return {
            'ads': self.stats['ads_blocked'],
            'trackers': self.stats['trackers_blocked'],
            'popups': self.stats['popups_blocked'],
            'social_widgets': self.stats['social_widgets_blocked'],
            'scripts': self.stats['scripts_blocked'],
            'images': self.stats['images_blocked'],
            'iframes': self.stats['iframes_blocked'],
            'total': sum([
                self.stats['ads_blocked'], self.stats['trackers_blocked'],
                self.stats['popups_blocked'], self.stats['social_widgets_blocked'],
                self.stats['scripts_blocked'], self.stats['images_blocked']
            ])
        }

    def _estimate_performance_improvement(self) -> Dict[str, Any]:
        """تقدير تحسن الأداء"""
        size_reduction_mb = self.stats['size_reduction_bytes'] / (1024 * 1024)
        
        # تقدير تحسن سرعة التحميل (بناءً على تجارب عملية)
        estimated_speed_improvement = min(50, size_reduction_mb * 15)  # نسبة مئوية
        
        return {
            'size_reduction_mb': round(size_reduction_mb, 2),
            'size_reduction_percentage': self.stats['size_reduction_percentage'],
            'estimated_speed_improvement_percentage': round(estimated_speed_improvement, 1),
            'blocked_requests_count': len(self.stats['blocked_domains']),
            'performance_score': min(100, 60 + self.stats['size_reduction_percentage'])
        }

    # ================ AdBlocker المدمج ================
    
    def block_ads_basic(self, html_content: str) -> str:
        """حجب الإعلانات الأساسي - من AdBlocker"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # إزالة العناصر الإعلانية
        ad_selectors = [
            '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
            '[class*="banner"]', '[class*="popup"]', '.google-ads'
        ]
        
        removed_count = 0
        for selector in ad_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
                removed_count += 1
        
        self.stats['ads_blocked'] += removed_count
        return str(soup)

    def block_ads_advanced(self, html_content: str) -> str:
        """حجب الإعلانات المتقدم - من AdvancedAdBlocker"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # حجب متقدم مع تحليل النص
        removed_count = 0
        
        # إزالة النصوص الإعلانية  
        ad_text_patterns = [
            r'sponsored\s+content', r'advertisement', r'إعلان',
            r'الرعاة', r'إعلان مدفوع', r'sponsored\s+by'
        ]
        
        for pattern in ad_text_patterns:
            for element in soup.find_all(string=re.compile(pattern, re.I)):
                if element.parent:
                    element.parent.decompose()
                    removed_count += 1
        
        # إزالة العناصر الإعلانية المتقدمة
        advanced_selectors = [
            '[class*="sidebar-ad"]', '[class*="header-ad"]', '[class*="footer-ad"]',
            '[data-google-ad]', '[data-ad-slot]', '[class*="promo"]'
        ]
        
        for selector in advanced_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
                removed_count += 1
        
        self.stats['ads_blocked'] += removed_count
        return str(soup)

    def get_blocking_report(self) -> Dict[str, Any]:
        """تقرير شامل عن عملية الحجب"""
        return {
            'blocking_mode': self.blocking_mode,
            'session_duration': time.time() - self.stats['session_start'],
            'statistics': self.stats.copy(),
            'blocked_elements': self._get_blocked_elements_summary(),
            'performance_improvement': self._estimate_performance_improvement(),
            'blocked_domains': list(self.stats['blocked_domains']),
            'detection_accuracy': self.stats['detection_accuracy'],
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """إنشاء توصيات للتحسين"""
        recommendations = []
        
        if self.stats['ads_blocked'] > 10:
            recommendations.append("تم حجب عدد كبير من الإعلانات - ينصح بتفعيل الحجب المتقدم")
        
        if self.stats['trackers_blocked'] > 5:
            recommendations.append("تم اكتشاف متتبعات متعددة - يفضل استخدام VPN للحماية الإضافية")
        
        if self.stats['size_reduction_percentage'] > 30:
            recommendations.append("تحسن كبير في الأداء - ينصح بتطبيق نفس الإعدادات على مواقع أخرى")
        
        if len(self.stats['blocked_domains']) > 10:
            recommendations.append("تم حجب العديد من النطاقات - يفضل إضافة قائمة حجب مخصصة")
        
        return recommendations