"""
نظام متطور لحجب الإعلانات وتنظيف المواقع
- AI-powered ad detection
- Pattern recognition for ads
- Smart content filtering
- Anti-tracking protection
- Malicious script removal
"""

import re
import json
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Comment
from typing import Dict, List, Set, Tuple, Optional
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class AdvancedAdBlocker:
    """نظام متطور لحجب الإعلانات وتنظيف المحتوى"""
    
    def __init__(self):
        self.blocked_stats = {
            'ads_blocked': 0,
            'trackers_blocked': 0,
            'malicious_scripts': 0,
            'suspicious_elements': 0,
            'cleaned_urls': 0
        }
        
        # قواعد متقدمة جداً لكشف الإعلانات والمحتوى المخفي
        self.advanced_ad_patterns = {
            # CSS Selectors for common ad containers - شامل جداً
            'css_selectors': [
                # Google Ads - جميع الأنواع
                '[data-google-av-cxn]', '[data-google-av-cmp]', '.google-auto-placed',
                '.adsbygoogle', '[data-ad-client]', '[data-ad-slot]', '.google-ads',
                '[data-google-query-id]', '.google-ad-unit', '.gpt-ad',
                
                # Facebook Ads - جميع الأنواع
                '[data-testid*="ad"]', '[aria-label*="Sponsored"]', '[data-pagelet*="ad"]',
                '.fb-ad', '[data-ft*="ei"]', '[data-ad-preview]',
                
                # أنماط إعلانية عامة - شاملة
                '[class*="advertisement"]', '[id*="advertisement"]', '[class*="ads"]', '[id*="ads"]',
                '[class*="banner"]', '[id*="banner"]', '[class*="ad-"]', '[id*="ad-"]',
                '[class*="popup"]', '[id*="popup"]', '[class*="popover"]', '[id*="popover"]',
                '[class*="overlay"]', '[id*="overlay"]', '[class*="lightbox"]', '[id*="lightbox"]',
                '[class*="modal"]', '[id*="modal"]', '[class*="dialog"]', '[id*="dialog"]',
                '[data-ad]', '[data-ads]', '[data-advertising]', '[data-ad-unit]',
                
                # محتوى ترويجي وأفلييت
                '[class*="affiliate"]', '[id*="affiliate"]', '[class*="referral"]', '[id*="referral"]',
                '[class*="promo"]', '[id*="promo"]', '[class*="promotion"]', '[id*="promotion"]',
                '[class*="sponsor"]', '[id*="sponsor"]', '[class*="sponsored"]', '[id*="sponsored"]',
                '[class*="partnership"]', '[id*="partnership"]', '[class*="commercial"]', '[id*="commercial"]',
                
                # إعلانات فيديو وصوت
                '[class*="video-ad"]', '[id*="video-ad"]', '[class*="preroll"]', '[id*="preroll"]',
                '[class*="midroll"]', '[id*="midroll"]', '[class*="postroll"]', '[id*="postroll"]',
                '[class*="vast"]', '[id*="vast"]', '[class*="vpaid"]', '[id*="vpaid"]',
                
                # إعلانات موبايل ومتجاوبة
                '[class*="mobile-ad"]', '[id*="mobile-ad"]', '[class*="responsive-ad"]', '[id*="responsive-ad"]',
                '[class*="interstitial"]', '[id*="interstitial"]', '[class*="fullscreen"]', '[id*="fullscreen"]',
                
                # شبكات إعلانية محددة
                '.outbrain', '.taboola', '.revcontent', '.mgid', '.criteo', '.adskeeper',
                '.adnxs', '.pubmatic', '.rubiconproject', '.smartadserver', '.media-net',
                
                # عناصر تتبع وتحليلات مخفية
                '[class*="tracking"]', '[id*="tracking"]', '[class*="analytics"]', '[id*="analytics"]',
                '[class*="pixel"]', '[id*="pixel"]', '[class*="beacon"]', '[id*="beacon"]',
                '[class*="tag"]', '[id*="tag"]', '[class*="gtm"]', '[id*="gtm"]',
                
                # عناصر اجتماعية ترويجية
                '[class*="social-share"]', '[id*="social-share"]', '[class*="like-button"]', '[id*="like-button"]',
                '[class*="follow-button"]', '[id*="follow-button"]', '[class*="widget"]', '[id*="widget"]',
                
                # نماذج تسويقية
                '[class*="newsletter"]', '[id*="newsletter"]', '[class*="signup"]', '[id*="signup"]',
                '[class*="subscribe"]', '[id*="subscribe"]', '[class*="email-capture"]', '[id*="email-capture"]',
                '[class*="lead-gen"]', '[id*="lead-gen"]', '[class*="conversion"]', '[id*="conversion"]',
                
                # عناصر مخفية وضارة
                '[style*="display:none"]', '[style*="visibility:hidden"]', '[style*="opacity:0"]',
                '[style*="position:absolute"][style*="left:-"]', '[style*="position:fixed"][style*="left:-"]',
                '[style*="width:1px"]', '[style*="height:1px"]', '[style*="font-size:0"]'
            ],
            
            # Text patterns that indicate ads - شامل ومتطور
            'text_patterns': [
                # إعلانات مباشرة
                r'sponsored\s+content', r'advertisement', r'promoted\s+post', r'paid\s+content',
                r'affiliate\s+link', r'referral\s+link', r'partnership\s+content',
                
                # دعوات للعمل
                r'click\s+here\s+to\s+buy', r'buy\s+now', r'order\s+now', r'purchase\s+now',
                r'special\s+offer', r'limited\s+time', r'limited\s+offer', r'exclusive\s+deal',
                r'act\s+now', r'act\s+fast', r'hurry\s+up', r'don\'t\s+miss',
                r'call\s+now', r'contact\s+us\s+now', r'get\s+quote',
                
                # عروض مجانية وتجريبية
                r'free\s+trial', r'free\s+download', r'free\s+shipping', r'no\s+cost',
                r'risk\s+free', r'money\s+back', r'guarantee', r'satisfaction\s+guaranteed',
                
                # كلمات تسويقية
                r'best\s+deal', r'lowest\s+price', r'discount', r'sale\s+now',
                r'save\s+money', r'cheap', r'affordable', r'bargain',
                
                # محتوى عربي إعلاني
                r'الإعلان\s+المدفوع', r'محتوى\s+مُمول', r'رعاية\s+تجارية',
                r'اشتري\s+الآن', r'اطلب\s+الآن', r'عرض\s+خاص', r'عرض\s+محدود',
                r'مجاناً\s+لفترة', r'تجربة\s+مجانية', r'خصم\s+خاص',
                r'اتصل\s+الآن', r'لا\s+تفوت', r'سارع\s+بالطلب',
                
                # تتبع وتحليلات
                r'google\s+analytics', r'facebook\s+pixel', r'conversion\s+tracking',
                r'utm_source', r'utm_campaign', r'tracking\s+code',
                
                # شبكات اجتماعية ترويجية
                r'like\s+and\s+share', r'follow\s+us', r'subscribe\s+now',
                r'join\s+our\s+newsletter', r'email\s+updates', r'notification\s+settings'
            ],
            
            # URL patterns for ad networks - قائمة شاملة ومحدثة
            'url_patterns': [
                # Google - جميع الخدمات الإعلانية
                r'doubleclick\.net', r'googleadservices\.com', r'googlesyndication\.com',
                r'googletagservices\.com', r'google-analytics\.com', r'analytics\.google\.com',
                r'googletagmanager\.com', r'googleoptimize\.com', r'google\.com/adsense',
                
                # Facebook & Meta
                r'facebook\.com/tr', r'connect\.facebook\.net', r'fbcdn\.net/tr',
                r'instagram\.com/logging', r'whatsapp\.com/tr',
                
                # Amazon
                r'amazon-adsystem\.com', r'adsystem\.amazon\.com', r'amazon\.com/gp/aw/cr',
                
                # شبكات إعلانية كبرى
                r'outbrain\.com', r'taboola\.com', r'revcontent\.com', r'mgid\.com',
                r'criteo\.com', r'adskeeper\.com', r'adnxs\.com', r'adsystem\.com',
                r'pubmatic\.com', r'rubiconproject\.com', r'smartadserver\.com',
                r'media\.net', r'bidswitch\.net', r'turn\.com', r'rlcdn\.com',
                
                # تحليلات وتتبع
                r'hotjar\.com', r'crazyegg\.com', r'mixpanel\.com', r'segment\.com',
                r'amplitude\.com', r'fullstory\.com', r'logrocket\.com',
                r'mouseflow\.com', r'clicktale\.com', r'inspectlet\.com',
                
                # أدوات تسويقية
                r'mailchimp\.com/track', r'constantcontact\.com/track',
                r'aweber\.com/track', r'getresponse\.com/track',
                r'klaviyo\.com/track', r'drip\.com/track',
                
                # شبكات اجتماعية للتتبع
                r'twitter\.com/i/adsct', r'linkedin\.com/li/track',
                r'pinterest\.com/ct', r'snapchat\.com/tr',
                r'tiktok\.com/i18n/pixel', r'reddit\.com/api/jail',
                
                # أنظمة دفع وتتبع
                r'paypal\.com/webapps/hermes', r'stripe\.com/v1/m',
                r'visa\.com/track', r'mastercard\.com/track',
                
                # شبكات إعلانية إقليمية
                r'yandex\.ru/clck', r'baidu\.com/rp', r'naver\.com/track',
                r'bing\.com/api/v1/impression', r'yahoo\.com/p',
                
                # أدوات A/B testing
                r'optimizely\.com', r'vwo\.com', r'unbounce\.com/track',
                r'leadpages\.com/track', r'clickfunnels\.com/track',
                
                # برامج ضارة وتتبع خفي
                r'track\.php', r'pixel\.php', r'beacon\.php', r'collect\.php',
                r'impression\.php', r'click\.php', r'redirect\.php',
                r'/track/', r'/pixel/', r'/beacon/', r'/collect/',
                r'/analytics/', r'/metrics/', r'/stats/', r'/log/'
            ]
        }
        
        # قائمة المجالات الإعلانية المعروفة
        self.ad_domains = {
            'google_ads': [
                'googleadservices.com', 'googlesyndication.com', 'doubleclick.net',
                'googletagservices.com', 'google-analytics.com'
            ],
            'facebook_ads': [
                'facebook.com', 'connect.facebook.net', 'fbcdn.net'
            ],
            'amazon_ads': [
                'amazon-adsystem.com', 'adsystem.amazon.com'
            ],
            'analytics': [
                'analytics.google.com', 'googletagmanager.com', 'hotjar.com',
                'crazyegg.com', 'mixpanel.com', 'segment.com'
            ],
            'ad_networks': [
                'adsense.com', 'adsystem.com', 'advertising.com',
                'adnxs.com', 'rubiconproject.com', 'pubmatic.com'
            ]
        }
        
        # JavaScript patterns للكشف عن سكريبت التتبع
        self.tracking_js_patterns = [
            r'ga\s*\(["\']send["\']',  # Google Analytics
            r'gtag\s*\(',  # Google Tag Manager
            r'fbq\s*\(',   # Facebook Pixel
            r'_paq\.push',  # Matomo
            r'amplitude\.',  # Amplitude
            r'mixpanel\.',   # Mixpanel
        ]

    def clean_html_content(self, html_content: str, url: str = "") -> Tuple[str, Dict]:
        """تنظيف شامل لمحتوى HTML"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        cleaning_report = {
            'original_elements': len(soup.find_all()),
            'removed_elements': [],
            'cleaned_scripts': 0,
            'blocked_requests': 0
        }
        
        # 1. إزالة الإعلانات باستخدام CSS selectors
        ads_removed = self._remove_ads_by_selectors(soup)
        cleaning_report['removed_elements'].extend(ads_removed)
        
        # 2. تنظيف JavaScript المشبوه
        scripts_cleaned = self._clean_suspicious_scripts(soup)
        cleaning_report['cleaned_scripts'] = scripts_cleaned
        
        # 3. إزالة التعليقات المشبوهة
        comments_removed = self._remove_suspicious_comments(soup)
        cleaning_report['removed_elements'].extend(comments_removed)
        
        # 4. تنظيف الروابط والمراجع الخارجية
        links_cleaned = self._clean_external_links(soup, url)
        cleaning_report['blocked_requests'] = links_cleaned
        
        # 5. إزالة العناصر المخفية المشبوهة
        hidden_removed = self._remove_hidden_ads(soup)
        cleaning_report['removed_elements'].extend(hidden_removed)
        
        # 6. تنظيف البيانات الوصفية الإعلانية
        meta_cleaned = self._clean_ad_metadata(soup)
        cleaning_report['removed_elements'].extend(meta_cleaned)
        
        # 7. تطبيق الفلاتر الذكية
        smart_filtered = self._apply_smart_filters(soup)
        cleaning_report['removed_elements'].extend(smart_filtered)
        
        # تحديث الإحصائيات
        self.blocked_stats['ads_blocked'] += len(ads_removed)
        self.blocked_stats['trackers_blocked'] += scripts_cleaned
        self.blocked_stats['suspicious_elements'] += len(hidden_removed)
        
        cleaning_report['final_elements'] = len(soup.find_all())
        
        return str(soup), cleaning_report

    def _remove_ads_by_selectors(self, soup: BeautifulSoup) -> List[str]:
        """إزالة الإعلانات باستخدام CSS selectors متقدمة"""
        removed_elements = []
        
        for selector in self.advanced_ad_patterns['css_selectors']:
            try:
                elements = soup.select(selector)
                for element in elements:
                    element_id = element.get('id', '') if hasattr(element, 'get') else ''
                    element_classes = element.get('class', []) if hasattr(element, 'get') else []
                    if isinstance(element_classes, list):
                        class_str = ' '.join(element_classes)
                    else:
                        class_str = str(element_classes) if element_classes else ''
                    element_name = element.name if hasattr(element, 'name') else 'unknown'
                    element_info = f"{element_name}#{element_id}.{class_str}"
                    removed_elements.append(f"CSS: {element_info}")
                    element.decompose()
            except Exception as e:
                logger.debug(f"خطأ في selector {selector}: {e}")
        
        return removed_elements

    def _clean_suspicious_scripts(self, soup: BeautifulSoup) -> int:
        """تنظيف JavaScript المشبوه وسكريبت التتبع"""
        scripts_cleaned = 0
        
        for script in soup.find_all('script'):
            script_content = ""
            if hasattr(script, 'string') and script.string:
                script_content = str(script.string)
            script_src = script.get('src', '') if hasattr(script, 'get') else ''
            script_src = str(script_src) if script_src else ''
            
            # فحص محتوى السكريبت
            is_suspicious = False
            
            # فحص الأنماط المشبوهة في النص
            for pattern in self.tracking_js_patterns:
                if re.search(pattern, script_content, re.IGNORECASE):
                    is_suspicious = True
                    break
            
            # فحص رابط السكريبت
            if script_src:
                for domain_category, domains in self.ad_domains.items():
                    for domain in domains:
                        if domain in script_src:
                            is_suspicious = True
                            break
                    if is_suspicious:
                        break
            
            # إزالة السكريبت المشبوه
            if is_suspicious:
                script.decompose()
                scripts_cleaned += 1
        
        return scripts_cleaned

    def _remove_suspicious_comments(self, soup: BeautifulSoup) -> List[str]:
        """إزالة التعليقات المشبوهة في HTML"""
        removed_comments = []
        
        suspicious_comment_patterns = [
            r'google.*ad',
            r'advertisement',
            r'adsense',
            r'doubleclick',
            r'tracking',
            r'analytics'
        ]
        
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            for pattern in suspicious_comment_patterns:
                if re.search(pattern, str(comment), re.IGNORECASE):
                    removed_comments.append(f"Comment: {str(comment)[:50]}...")
                    comment.extract()
                    break
        
        return removed_comments

    def _clean_external_links(self, soup: BeautifulSoup, base_url: str) -> int:
        """تنظيف الروابط الخارجية المشبوهة"""
        blocked_requests = 0
        
        # تنظيف روابط CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '') if hasattr(link, 'get') else ''
            href = str(href) if href else ''
            if self._is_suspicious_url(href):
                link.decompose()
                blocked_requests += 1
        
        # تنظيف الصور المشبوهة
        for img in soup.find_all('img'):
            src = img.get('src', '') if hasattr(img, 'get') else ''
            src = str(src) if src else ''
            if self._is_suspicious_url(src):
                img.decompose()
                blocked_requests += 1
        
        # تنظيف iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '') if hasattr(iframe, 'get') else ''
            src = str(src) if src else ''
            if self._is_suspicious_url(src) or self._is_ad_iframe(iframe):
                iframe.decompose()
                blocked_requests += 1
        
        return blocked_requests

    def _is_suspicious_url(self, url: str) -> bool:
        """فحص الرابط للتأكد من أنه مشبوه"""
        if not url:
            return False
        
        for domain_category, domains in self.ad_domains.items():
            for domain in domains:
                if domain in url:
                    return True
        
        # فحص أنماط URL الإعلانية
        for pattern in self.advanced_ad_patterns['url_patterns']:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False

    def _is_ad_iframe(self, iframe) -> bool:
        """فحص iframe للتأكد من أنه إعلاني"""
        # فحص أبعاد الإطار
        width = iframe.get('width', '')
        height = iframe.get('height', '')
        
        # أحجام الإعلانات الشائعة
        common_ad_sizes = [
            ('728', '90'),   # Leaderboard
            ('300', '250'),  # Medium Rectangle
            ('336', '280'),  # Large Rectangle
            ('320', '50'),   # Mobile Banner
            ('468', '60'),   # Banner
        ]
        
        if (width, height) in common_ad_sizes:
            return True
        
        # فحص الفئات والمعرفات
        css_classes = ' '.join(iframe.get('class', []))
        iframe_id = iframe.get('id', '')
        
        ad_indicators = ['ad', 'banner', 'advertisement', 'adsense', 'doubleclick']
        
        for indicator in ad_indicators:
            if indicator in css_classes.lower() or indicator in iframe_id.lower():
                return True
        
        return False

    def _remove_hidden_ads(self, soup: BeautifulSoup) -> List[str]:
        """إزالة العناصر المخفية التي قد تكون إعلانات"""
        removed_elements = []
        
        # البحث عن العناصر مع display: none أو visibility: hidden
        for element in soup.find_all(style=True):
            style = element.get('style', '') if hasattr(element, 'get') else ''
            style = str(style) if style else ''
            if ('display:none' in style.replace(' ', '') or 
                'visibility:hidden' in style.replace(' ', '') or
                'opacity:0' in style.replace(' ', '')):
                
                # فحص محتوى العنصر للتأكد من أنه إعلاني
                element_text = element.get_text(strip=True) if hasattr(element, 'get_text') else ''
                if self._contains_ad_keywords(element_text):
                    element_name = element.name if hasattr(element, 'name') else 'unknown'
                    removed_elements.append(f"Hidden: {element_name}")
                    element.decompose()
        
        return removed_elements

    def _clean_ad_metadata(self, soup: BeautifulSoup) -> List[str]:
        """تنظيف البيانات الوصفية الإعلانية"""
        removed_elements = []
        
        # إزالة meta tags الإعلانية
        ad_meta_patterns = [
            r'google-adsense',
            r'fb:admins',
            r'fb:app_id',
            r'twitter:creator',
            r'google-site-verification'
        ]
        
        for meta in soup.find_all('meta'):
            name = meta.get('name', '') if hasattr(meta, 'get') else ''
            property_attr = meta.get('property', '') if hasattr(meta, 'get') else ''
            name = str(name) if name else ''
            property_attr = str(property_attr) if property_attr else ''
            
            for pattern in ad_meta_patterns:
                if (re.search(pattern, name, re.IGNORECASE) or 
                    re.search(pattern, property_attr, re.IGNORECASE)):
                    removed_elements.append(f"Meta: {name or property_attr}")
                    meta.decompose()
                    break
        
        return removed_elements

    def _apply_smart_filters(self, soup: BeautifulSoup) -> List[str]:
        """تطبيق فلاتر ذكية للكشف عن الإعلانات مع حماية المحتوى المفيد"""
        removed_elements = []
        
        # فلتر النصوص الإعلانية (بحذر لحماية المحتوى)
        for element in soup.find_all(text=True):
            element_text = str(element).strip()
            if len(element_text) > 5 and self._contains_ad_keywords(element_text):
                parent = element.parent
                if parent and parent.name not in ['script', 'style', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'article', 'main']:
                    # تأكد من أن العنصر ليس جزءاً من المحتوى الرئيسي
                    if not self._is_main_content(parent):
                        removed_elements.append(f"Text: {str(element)[:30]}...")
                        parent.decompose()
        
        # فلتر العناصر بناءً على النسبة والحجم (مع استثناءات للمحتوى)
        for element in soup.find_all():
            element_name = element.name if hasattr(element, 'name') else 'unknown'
            if (self._is_likely_ad_element(element) and 
                not self._is_main_content(element) and
                element_name not in ['html', 'body', 'head', 'main', 'article', 'section']):
                removed_elements.append(f"Smart: {element_name}")
                element.decompose()
        
        return removed_elements
    
    def _is_main_content(self, element) -> bool:
        """تحديد ما إذا كان العنصر جزءاً من المحتوى الرئيسي"""
        
        # فحص العناصر الرئيسية
        if element.name in ['main', 'article', 'section', 'div']:
            # فحص الكلاسات والمعرفات
            classes = ' '.join(element.get('class', [])).lower()
            element_id = element.get('id', '').lower()
            
            main_content_indicators = [
                'content', 'main', 'article', 'post', 'entry',
                'body', 'text', 'story', 'news', 'blog'
            ]
            
            for indicator in main_content_indicators:
                if indicator in classes or indicator in element_id:
                    return True
        
        # فحص العناصر الأصلية
        if element.find_parent(['main', 'article']):
            return True
        
        # فحص طول المحتوى النصي
        text_content = element.get_text(strip=True)
        if len(text_content) > 100:  # النصوص الطويلة عادة محتوى مفيد
            return True
        
        return False

    def _contains_ad_keywords(self, text: str) -> bool:
        """فحص النص للكلمات المفتاحية الإعلانية (محسّن لتجنب الإيجابيات الخاطئة)"""
        if not text or len(text.strip()) < 5:
            return False
        
        # كلمات إعلانية قوية (تأكيد عالي)
        strong_ad_keywords = [
            'advertisement', 'click here to buy', 'buy now', 'limited time offer',
            'call now', 'act fast', 'sponsored by', 'affiliate link',
            'الإعلان المدفوع', 'اشتري الآن', 'عرض محدود'
        ]
        
        # كلمات إعلانية ضعيفة (تحتاج سياق)
        weak_ad_keywords = [
            'sponsored', 'promoted', 'affiliate', 'special offer',
            'free trial', 'مُمول', 'رعاية', 'عرض خاص'
        ]
        
        text_lower = text.lower().strip()
        
        # فحص الكلمات القوية أولاً
        for keyword in strong_ad_keywords:
            if keyword in text_lower:
                return True
        
        # فحص الكلمات الضعيفة مع شروط إضافية
        for keyword in weak_ad_keywords:
            if keyword in text_lower:
                # تجنب النصوص الطويلة (أكثر من 50 كلمة)
                if len(text.split()) > 50:
                    continue
                # تجنب العناوين والمحتوى الأساسي
                if any(char in text for char in [':', '.', '?', '!']):
                    continue
                return True
        
        return False

    def _is_likely_ad_element(self, element) -> bool:
        """تحديد ما إذا كان العنصر يبدو كإعلان بناءً على خصائصه"""
        
        # فحص النسبة (العرض إلى الارتفاع)
        style = element.get('style', '')
        width_match = re.search(r'width:\s*(\d+)px', style)
        height_match = re.search(r'height:\s*(\d+)px', style)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            
            # نسب الإعلانات الشائعة
            ad_ratios = [
                (728, 90),   # Leaderboard
                (300, 250),  # Medium Rectangle  
                (336, 280),  # Large Rectangle
                (320, 50),   # Mobile Banner
                (468, 60),   # Banner
                (970, 250),  # Billboard
                (300, 600),  # Half Page
            ]
            
            for ad_width, ad_height in ad_ratios:
                if abs(width - ad_width) < 20 and abs(height - ad_height) < 20:
                    return True
        
        return False

    def generate_blocking_report(self) -> Dict:
        """إنشاء تقرير شامل لعملية الحجب"""
        return {
            'summary': {
                'total_ads_blocked': self.blocked_stats['ads_blocked'],
                'total_trackers_blocked': self.blocked_stats['trackers_blocked'],
                'malicious_scripts_removed': self.blocked_stats['malicious_scripts'],
                'suspicious_elements_removed': self.blocked_stats['suspicious_elements'],
                'urls_cleaned': self.blocked_stats['cleaned_urls']
            },
            'categories_blocked': {
                'google_ads': 'جوجل أدز وخدمات الإعلان',
                'facebook_trackers': 'تتبع فيسبوك ووسائل التواصل',
                'analytics_scripts': 'سكريبت التحليلات والإحصائيات',
                'affiliate_links': 'روابط الأفلييت والعمولة',
                'popup_overlays': 'النوافذ المنبثقة والأغطية'
            },
            'protection_features': [
                'حجب الإعلانات المرئية والمخفية',
                'إزالة سكريبت التتبع والتحليلات',
                'تنظيف الروابط المشبوهة',
                'حماية من البرامج الضارة',
                'تحسين سرعة التحميل'
            ]
        }

    def update_ad_patterns(self, new_patterns: Dict):
        """تحديث أنماط الإعلانات بأنماط جديدة"""
        if 'css_selectors' in new_patterns:
            self.advanced_ad_patterns['css_selectors'].extend(new_patterns['css_selectors'])
        
        if 'url_patterns' in new_patterns:
            self.advanced_ad_patterns['url_patterns'].extend(new_patterns['url_patterns'])
        
        if 'text_patterns' in new_patterns:
            self.advanced_ad_patterns['text_patterns'].extend(new_patterns['text_patterns'])

    def reset_stats(self):
        """إعادة تعيين الإحصائيات"""
        self.blocked_stats = {
            'ads_blocked': 0,
            'trackers_blocked': 0,
            'malicious_scripts': 0,
            'suspicious_elements': 0,
            'cleaned_urls': 0
        }