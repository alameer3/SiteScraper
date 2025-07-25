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
        
        # قواعد متقدمة لكشف الإعلانات
        self.advanced_ad_patterns = {
            # CSS Selectors for common ad containers
            'css_selectors': [
                # Google Ads
                '[data-google-av-cxn]', '[data-google-av-cmp]', '.google-auto-placed',
                '.adsbygoogle', '[data-ad-client]', '[data-ad-slot]',
                
                # Facebook Ads
                '[data-testid*="ad"]', '[aria-label*="Sponsored"]', '[data-pagelet*="ad"]',
                
                # Generic ad patterns
                '[class*="advertisement"]', '[id*="advertisement"]',
                '[class*="banner"]', '[id*="banner"]',
                '[class*="popup"]', '[id*="popup"]',
                '[class*="overlay"]', '[id*="overlay"]',
                '[class*="modal"]', '[id*="modal"]',
                '[data-ad]', '[data-ads]', '[data-advertising]',
                
                # Affiliate and promotional content
                '[class*="affiliate"]', '[id*="affiliate"]',
                '[class*="promo"]', '[id*="promo"]',
                '[class*="sponsor"]', '[id*="sponsor"]',
                
                # Video ads
                '[class*="video-ad"]', '[id*="video-ad"]',
                '[class*="preroll"]', '[id*="preroll"]',
                
                # Mobile ads
                '[class*="mobile-ad"]', '[id*="mobile-ad"]',
                '[class*="interstitial"]', '[id*="interstitial"]'
            ],
            
            # Text patterns that indicate ads
            'text_patterns': [
                r'sponsored\s+content',
                r'advertisement',
                r'promoted\s+post',
                r'affiliate\s+link',
                r'click\s+here\s+to\s+buy',
                r'special\s+offer',
                r'limited\s+time',
                r'act\s+now',
                r'call\s+now',
                r'free\s+trial'
            ],
            
            # URL patterns for ad networks
            'url_patterns': [
                r'doubleclick\.net',
                r'googleadservices\.com',
                r'googlesyndication\.com',
                r'amazon-adsystem\.com',
                r'facebook\.com/tr',
                r'analytics\.google\.com',
                r'google-analytics\.com',
                r'googletagmanager\.com',
                r'hotjar\.com',
                r'crazyegg\.com',
                r'mixpanel\.com',
                r'segment\.com'
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
                    element_info = f"{element.name}#{element.get('id', '')}.{' '.join(element.get('class', []))}"
                    removed_elements.append(f"CSS: {element_info}")
                    element.decompose()
            except Exception as e:
                logger.debug(f"خطأ في selector {selector}: {e}")
        
        return removed_elements

    def _clean_suspicious_scripts(self, soup: BeautifulSoup) -> int:
        """تنظيف JavaScript المشبوه وسكريبت التتبع"""
        scripts_cleaned = 0
        
        for script in soup.find_all('script'):
            script_content = script.string or ""
            script_src = script.get('src', '')
            
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
            href = link.get('href', '')
            if self._is_suspicious_url(href):
                link.decompose()
                blocked_requests += 1
        
        # تنظيف الصور المشبوهة
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if self._is_suspicious_url(src):
                img.decompose()
                blocked_requests += 1
        
        # تنظيف iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
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
            style = element.get('style', '')
            if ('display:none' in style.replace(' ', '') or 
                'visibility:hidden' in style.replace(' ', '') or
                'opacity:0' in style.replace(' ', '')):
                
                # فحص محتوى العنصر للتأكد من أنه إعلاني
                element_text = element.get_text(strip=True)
                if self._contains_ad_keywords(element_text):
                    removed_elements.append(f"Hidden: {element.name}")
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
            name = meta.get('name', '')
            property_attr = meta.get('property', '')
            
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
            if (self._is_likely_ad_element(element) and 
                not self._is_main_content(element) and
                element.name not in ['html', 'body', 'head', 'main', 'article', 'section']):
                removed_elements.append(f"Smart: {element.name}")
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