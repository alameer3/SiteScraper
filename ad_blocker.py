"""
نظام تخطي الإعلانات والمحتوى غير المرغوب فيه
Ad Blocker and Content Filter System
"""
import re
import logging
from typing import List, Set, Dict, Any
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

class AdBlocker:
    """نظام تخطي الإعلانات المتطور"""
    
    def __init__(self):
        # قوائم حظر الإعلانات
        self.ad_domains = {
            'doubleclick.net', 'googleadservices.com', 'googlesyndication.com',
            'facebook.com/tr', 'google-analytics.com', 'googletagmanager.com',
            'amazon-adsystem.com', 'adsystem.amazon.com', 'scorecardresearch.com',
            'outbrain.com', 'taboola.com', 'addthis.com', 'sharethis.com',
            'zedo.com', 'adsystem.com', 'adsys.com', 'ads.yahoo.com',
            'advertising.com', 'adsense.com', 'adnxs.com', 'bing.com/maps'
        }
        
        # محددات CSS للإعلانات
        self.ad_selectors = {
            '.ad', '.ads', '.advertisement', '.google-ad',
            '.adsense', '.adsbygoogle', '.banner', '.popup',
            '[id*="ad"]', '[class*="ad"]', '[id*="banner"]',
            '[class*="banner"]', '.sponsored', '.promo',
            '.marketing', '.commercial', '[data-ad]', '.ad-container'
        }
        
        # كلمات مفتاحية للإعلانات
        self.ad_keywords = {
            'advertisement', 'sponsored', 'promotion', 'banner',
            'popup', 'overlay', 'modal', 'interstitial',
            'إعلان', 'دعاية', 'ترويج', 'إعلانات'
        }
        
        # أنماط الروابط الإعلانية
        self.ad_url_patterns = [
            r'.*doubleclick\.net.*',
            r'.*googleadservices\.com.*',
            r'.*googlesyndication\.com.*',
            r'.*amazon-adsystem\.com.*',
            r'.*outbrain\.com.*',
            r'.*taboola\.com.*',
            r'.*facebook\.com/tr.*',
            r'.*google-analytics\.com.*',
            r'.*googletagmanager\.com.*'
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.ad_url_patterns]
    
    def clean_html(self, html_content: str, base_url: str = '') -> str:
        """تنظيف HTML من الإعلانات والمحتوى غير المرغوب فيه"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إزالة العناصر بناءً على المحددات
            removed_count = 0
            
            # إزالة النصوص البرمجية للإعلانات
            for script in soup.find_all('script'):
                if self._is_ad_script(script):
                    script.decompose()
                    removed_count += 1
            
            # إزالة الروابط الإعلانية
            for link in soup.find_all(['a', 'link']):
                if self._is_ad_link(link, base_url):
                    link.decompose()
                    removed_count += 1
            
            # إزالة الصور الإعلانية
            for img in soup.find_all('img'):
                if self._is_ad_image(img, base_url):
                    img.decompose()
                    removed_count += 1
            
            # إزالة العناصر بناءً على المحددات
            for selector in self.ad_selectors:
                elements = soup.select(selector)
                for element in elements:
                    element.decompose()
                    removed_count += 1
            
            # إزالة العناصر بناءً على النص
            for element in soup.find_all(string=True):
                if self._contains_ad_keywords(str(element)):
                    if element.parent:
                        element.parent.decompose()
                        removed_count += 1
            
            # إزالة iframe للإعلانات
            for iframe in soup.find_all('iframe'):
                if self._is_ad_iframe(iframe, base_url):
                    iframe.decompose()
                    removed_count += 1
            
            logger.info(f"تم إزالة {removed_count} عنصر إعلاني")
            
            return str(soup)
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف HTML: {str(e)}")
            return html_content
    
    def _is_ad_script(self, script_tag: Tag) -> bool:
        """فحص إذا كان النص البرمجي إعلانياً"""
        if not script_tag:
            return False
        
        # فحص مصدر النص البرمجي
        src = script_tag.get('src', '')
        if src and self._is_ad_url(src):
            return True
        
        # فحص محتوى النص البرمجي
        script_content = script_tag.string or ''
        ad_script_keywords = [
            'googletag', 'adsbygoogle', 'amazon-adsystem',
            'doubleclick', 'outbrain', 'taboola'
        ]
        
        return any(keyword in script_content.lower() for keyword in ad_script_keywords)
    
    def _is_ad_link(self, link_tag: Tag, base_url: str) -> bool:
        """فحص إذا كان الرابط إعلانياً"""
        if not link_tag:
            return False
        
        href = link_tag.get('href', '')
        if href:
            # تحويل الرابط إلى رابط مطلق
            if base_url:
                href = urljoin(base_url, href)
            
            if self._is_ad_url(href):
                return True
        
        # فحص النص المرئي للرابط
        link_text = link_tag.get_text(strip=True).lower()
        return self._contains_ad_keywords(link_text)
    
    def _is_ad_image(self, img_tag: Tag, base_url: str) -> bool:
        """فحص إذا كانت الصورة إعلانية"""
        if not img_tag:
            return False
        
        src = img_tag.get('src', '')
        if src:
            # تحويل إلى رابط مطلق
            if base_url:
                src = urljoin(base_url, src)
            
            if self._is_ad_url(src):
                return True
        
        # فحص النص البديل
        alt_text = img_tag.get('alt', '').lower()
        return self._contains_ad_keywords(alt_text)
    
    def _is_ad_iframe(self, iframe_tag: Tag, base_url: str) -> bool:
        """فحص إذا كان iframe إعلانياً"""
        if not iframe_tag:
            return False
        
        src = iframe_tag.get('src', '')
        if src:
            if base_url:
                src = urljoin(base_url, src)
            
            return self._is_ad_url(src)
        
        return False
    
    def _is_ad_url(self, url: str) -> bool:
        """فحص إذا كان الرابط يحتوي على إعلانات"""
        if not url:
            return False
        
        # فحص النطاقات المحظورة
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for ad_domain in self.ad_domains:
            if ad_domain in domain:
                return True
        
        # فحص الأنماط
        for pattern in self.compiled_patterns:
            if pattern.match(url):
                return True
        
        return False
    
    def _contains_ad_keywords(self, text: str) -> bool:
        """فحص إذا كان النص يحتوي على كلمات إعلانية"""
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.ad_keywords)
    
    def get_blocked_stats(self) -> Dict[str, int]:
        """إحصائيات المحتوى المحظور"""
        return {
            'ad_domains_count': len(self.ad_domains),
            'ad_selectors_count': len(self.ad_selectors),
            'ad_keywords_count': len(self.ad_keywords),
            'ad_patterns_count': len(self.ad_url_patterns)
        }
    
    def add_custom_filter(self, filter_type: str, filter_value: str) -> bool:
        """إضافة فلتر مخصص"""
        try:
            if filter_type == 'domain':
                self.ad_domains.add(filter_value.lower())
            elif filter_type == 'selector':
                self.ad_selectors.add(filter_value)
            elif filter_type == 'keyword':
                self.ad_keywords.add(filter_value.lower())
            elif filter_type == 'pattern':
                self.ad_url_patterns.append(filter_value)
                self.compiled_patterns.append(re.compile(filter_value, re.IGNORECASE))
            else:
                return False
            
            logger.info(f"تمت إضافة فلتر جديد: {filter_type} = {filter_value}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة الفلتر: {str(e)}")
            return False

class ContentProtector:
    """نظام حماية المحتوى والخصوصية"""
    
    def __init__(self):
        # المتتبعات الشائعة
        self.trackers = {
            'google-analytics.com', 'googletagmanager.com',
            'facebook.com/tr', 'twitter.com', 'linkedin.com',
            'scorecardresearch.com', 'quantserve.com',
            'hotjar.com', 'crazyegg.com', 'mouseflow.com'
        }
        
        # النصوص البرمجية الضارة المحتملة
        self.malicious_patterns = [
            r'eval\s*\(',
            r'document\.write\s*\(',
            r'innerHTML\s*=',
            r'crypto.*mining',
            r'bitcoin.*mining'
        ]
        
        self.compiled_malicious = [re.compile(pattern, re.IGNORECASE) for pattern in self.malicious_patterns]
    
    def scan_for_threats(self, html_content: str) -> Dict[str, Any]:
        """فحص المحتوى للتهديدات الأمنية"""
        threats = {
            'trackers': [],
            'malicious_scripts': [],
            'suspicious_iframes': [],
            'external_forms': [],
            'risk_score': 0
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # فحص المتتبعات
            for script in soup.find_all('script', src=True):
                src = script.get('src')
                if any(tracker in src for tracker in self.trackers):
                    threats['trackers'].append(src)
                    threats['risk_score'] += 1
            
            # فحص النصوص البرمجية الضارة
            for script in soup.find_all('script'):
                script_content = script.string or ''
                for pattern in self.compiled_malicious:
                    if pattern.search(script_content):
                        threats['malicious_scripts'].append(script_content[:100])
                        threats['risk_score'] += 3
            
            # فحص iframe المشبوهة
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                if src and not src.startswith(('https://', 'http://')):
                    threats['suspicious_iframes'].append(src)
                    threats['risk_score'] += 2
            
            # فحص النماذج الخارجية
            for form in soup.find_all('form'):
                action = form.get('action', '')
                if action and action.startswith(('http://', 'https://')):
                    threats['external_forms'].append(action)
                    threats['risk_score'] += 1
            
            logger.info(f"تم اكتشاف {len(threats['trackers'])} متتبع و {len(threats['malicious_scripts'])} نص مشبوه")
            
        except Exception as e:
            logger.error(f"خطأ في فحص التهديدات: {str(e)}")
        
        return threats
    
    def remove_trackers(self, html_content: str) -> str:
        """إزالة المتتبعات من المحتوى"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            removed_count = 0
            
            # إزالة نصوص المتتبعات
            for script in soup.find_all('script'):
                src = script.get('src', '')
                if src and any(tracker in src for tracker in self.trackers):
                    script.decompose()
                    removed_count += 1
                    continue
                
                # فحص محتوى النص البرمجي
                script_content = script.string or ''
                if any(tracker in script_content for tracker in self.trackers):
                    script.decompose()
                    removed_count += 1
            
            # إزالة pixel المتتبعة
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and any(tracker in src for tracker in self.trackers):
                    img.decompose()
                    removed_count += 1
            
            logger.info(f"تم إزالة {removed_count} متتبع")
            return str(soup)
            
        except Exception as e:
            logger.error(f"خطأ في إزالة المتتبعات: {str(e)}")
            return html_content
    
    def sanitize_content(self, html_content: str) -> str:
        """تعقيم المحتوى من العناصر الضارة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إزالة النصوص البرمجية المشبوهة
            for script in soup.find_all('script'):
                script_content = script.string or ''
                for pattern in self.compiled_malicious:
                    if pattern.search(script_content):
                        script.decompose()
                        break
            
            # إزالة العناصر الخطيرة
            dangerous_tags = ['object', 'embed', 'applet']
            for tag_name in dangerous_tags:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # تنظيف الخصائص الخطيرة
            for tag in soup.find_all():
                if tag.name:
                    # إزالة خصائص الأحداث
                    attrs_to_remove = []
                    for attr in tag.attrs:
                        if attr.startswith('on'):  # onclick, onload, etc.
                            attrs_to_remove.append(attr)
                    
                    for attr in attrs_to_remove:
                        del tag.attrs[attr]
            
            return str(soup)
            
        except Exception as e:
            logger.error(f"خطأ في تعقيم المحتوى: {str(e)}")
            return html_content

class PrivacyFilter:
    """فلتر الخصوصية وحماية البيانات"""
    
    def __init__(self):
        # أنماط البيانات الحساسة
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        self.compiled_sensitive = {
            name: re.compile(pattern) for name, pattern in self.sensitive_patterns.items()
        }
    
    def mask_sensitive_data(self, content: str, mask_char: str = '*') -> str:
        """إخفاء البيانات الحساسة"""
        try:
            masked_content = content
            
            for data_type, pattern in self.compiled_sensitive.items():
                def replace_func(match):
                    original = match.group()
                    if data_type == 'email':
                        # الحفاظ على بداية ونهاية البريد الإلكتروني
                        parts = original.split('@')
                        if len(parts) == 2:
                            username = parts[0]
                            domain = parts[1]
                            masked_username = username[:2] + mask_char * (len(username) - 2)
                            return f"{masked_username}@{domain}"
                    
                    # إخفاء عام للأنواع الأخرى
                    return mask_char * len(original)
                
                masked_content = pattern.sub(replace_func, masked_content)
            
            return masked_content
            
        except Exception as e:
            logger.error(f"خطأ في إخفاء البيانات الحساسة: {str(e)}")
            return content
    
    def detect_sensitive_data(self, content: str) -> Dict[str, List[str]]:
        """اكتشاف البيانات الحساسة"""
        detected = {data_type: [] for data_type in self.sensitive_patterns.keys()}
        
        try:
            for data_type, pattern in self.compiled_sensitive.items():
                matches = pattern.findall(content)
                detected[data_type] = matches
            
        except Exception as e:
            logger.error(f"خطأ في اكتشاف البيانات الحساسة: {str(e)}")
        
        return detected