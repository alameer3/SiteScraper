"""
فاحص أنظمة إدارة المحتوى
CMS Detection Engine
"""

import re
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
from .session_manager import SessionManager


class CMSDetector:
    """فاحص متطور لأنظمة إدارة المحتوى"""
    
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager
        self.cms_patterns = self._load_cms_patterns()
        
    def _load_cms_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """تحميل أنماط اكتشاف أنظمة إدارة المحتوى"""
        return {
            'wordpress': {
                'meta_tags': [
                    'wp-content', 'wordpress', 'wp-includes', 'wp-admin',
                    'twentytwenty', 'twentynineteen', 'wp-theme'
                ],
                'urls': [
                    '/wp-content/', '/wp-includes/', '/wp-admin/', '/wp-login.php',
                    '/wp-json/', '/xmlrpc.php', '/wp-cron.php'
                ],
                'html_patterns': [
                    r'wp-content',
                    r'wordpress',
                    r'wp-includes',
                    r'/themes/.*?/',
                    r'/plugins/.*?/',
                    r'wp-emoji'
                ],
                'headers': [
                    'x-powered-by: WordPress',
                    'server: WordPress'
                ]
            },
            'drupal': {
                'meta_tags': [
                    'drupal', 'sites/default', 'sites/all', 'modules',
                    'themes/bartik', 'themes/seven'
                ],
                'urls': [
                    '/sites/default/', '/sites/all/', '/modules/', '/themes/',
                    '/core/', '/admin/', '/user/login'
                ],
                'html_patterns': [
                    r'Drupal\.settings',
                    r'sites/default',
                    r'sites/all',
                    r'/modules/.*?/',
                    r'/themes/.*?/',
                    r'drupal\.js'
                ],
                'headers': [
                    'x-powered-by: Drupal',
                    'x-drupal-cache'
                ]
            },
            'joomla': {
                'meta_tags': [
                    'joomla', 'com_content', 'com_user', 'administrator',
                    'templates/system', 'media/system'
                ],
                'urls': [
                    '/administrator/', '/templates/', '/media/system/',
                    '/modules/', '/plugins/', '/components/'
                ],
                'html_patterns': [
                    r'joomla',
                    r'com_content',
                    r'option=com_',
                    r'/templates/.*?/',
                    r'/media/system/',
                    r'mootools'
                ],
                'headers': [
                    'x-powered-by: Joomla'
                ]
            },
            'shopify': {
                'meta_tags': [
                    'shopify', 'cdn.shopify.com', 'myshopify.com',
                    'shopify-section', 'shopify-block'
                ],
                'urls': [
                    '/admin/', '/cart/', '/checkout/', '/collections/',
                    '/products/', '/pages/'
                ],
                'html_patterns': [
                    r'shopify',
                    r'cdn\.shopify\.com',
                    r'myshopify\.com',
                    r'Shopify\.theme',
                    r'shopify-section',
                    r'liquid'
                ],
                'headers': [
                    'x-powered-by: Shopify',
                    'server: cloudflare'
                ]
            },
            'wix': {
                'meta_tags': [
                    'wix.com', 'wixstatic.com', 'wix-code', 'wixsite.com'
                ],
                'urls': [
                    '/_api/', '/wix-code/', '/corvid/'
                ],
                'html_patterns': [
                    r'wix\.com',
                    r'wixstatic\.com',
                    r'wixsite\.com',
                    r'wix-code',
                    r'corvid'
                ],
                'headers': [
                    'x-wix-request-id',
                    'server: Wix.com'
                ]
            },
            'squarespace': {
                'meta_tags': [
                    'squarespace', 'squarespace.com', 'static1.squarespace.com'
                ],
                'urls': [
                    '/s/', '/universal/', '/assets/'
                ],
                'html_patterns': [
                    r'squarespace',
                    r'squarespace\.com',
                    r'static1\.squarespace\.com',
                    r'Y\.use'
                ],
                'headers': [
                    'x-served-by: Squarespace'
                ]
            },
            'magento': {
                'meta_tags': [
                    'magento', 'mage', 'skin/frontend', 'js/mage'
                ],
                'urls': [
                    '/admin/', '/downloader/', '/skin/', '/js/mage/',
                    '/media/catalog/', '/customer/'
                ],
                'html_patterns': [
                    r'magento',
                    r'mage',
                    r'skin/frontend',
                    r'js/mage',
                    r'Mage\.Cookies'
                ],
                'headers': [
                    'x-powered-by: Magento'
                ]
            },
            'prestashop': {
                'meta_tags': [
                    'prestashop', 'ps_', 'themes/default-bootstrap'
                ],
                'urls': [
                    '/admin/', '/themes/', '/modules/', '/js/jquery/',
                    '/img/p/', '/cache/'
                ],
                'html_patterns': [
                    r'prestashop',
                    r'ps_',
                    r'themes/default-bootstrap',
                    r'prestashop\.js'
                ],
                'headers': [
                    'x-powered-by: PrestaShop'
                ]
            }
        }
    
    def detect_cms(self, soup: BeautifulSoup, url: str, response_headers: Dict[str, str], 
                   html_content: str) -> Dict[str, Any]:
        """اكتشاف نظام إدارة المحتوى المستخدم"""
        
        detection_result = {
            'detected_cms': None,
            'confidence': 0,
            'details': {},
            'alternative_detections': [],
            'version_info': {},
            'plugins_detected': [],
            'themes_detected': []
        }
        
        cms_scores = {}
        
        # فحص كل نظام CMS
        for cms_name, patterns in self.cms_patterns.items():
            score = self._calculate_cms_score(
                cms_name, patterns, soup, url, response_headers, html_content
            )
            cms_scores[cms_name] = score
        
        # تحديد أفضل اكتشاف
        if cms_scores:
            best_cms = max(cms_scores.items(), key=lambda x: x[1]['total_score'])
            
            if best_cms[1]['total_score'] > 0:
                detection_result['detected_cms'] = best_cms[0]
                detection_result['confidence'] = min(best_cms[1]['total_score'] * 10, 100)
                detection_result['details'] = best_cms[1]
                
                # إضافة اكتشافات بديلة
                for cms, score_data in cms_scores.items():
                    if cms != best_cms[0] and score_data['total_score'] > 0:
                        detection_result['alternative_detections'].append({
                            'cms': cms,
                            'confidence': min(score_data['total_score'] * 10, 100),
                            'details': score_data
                        })
                
                # اكتشاف الإضافات والقوالب للـ CMS المكتشف
                if best_cms[0] == 'wordpress':
                    detection_result['plugins_detected'] = self._detect_wordpress_plugins(soup, html_content)
                    detection_result['themes_detected'] = self._detect_wordpress_themes(soup, html_content)
                    detection_result['version_info'] = self._detect_wordpress_version(soup, html_content)
                elif best_cms[0] == 'drupal':
                    detection_result['version_info'] = self._detect_drupal_version(soup, html_content)
                elif best_cms[0] == 'joomla':
                    detection_result['version_info'] = self._detect_joomla_version(soup, html_content)
        
        return detection_result
    
    def _calculate_cms_score(self, cms_name: str, patterns: Dict[str, List[str]], 
                           soup: BeautifulSoup, url: str, headers: Dict[str, str], 
                           content: str) -> Dict[str, Any]:
        """حساب نقاط اكتشاف CMS محدد"""
        
        score_data = {
            'meta_score': 0,
            'url_score': 0,
            'html_score': 0,
            'header_score': 0,
            'total_score': 0,
            'evidence': []
        }
        
        content_lower = content.lower()
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        
        # فحص meta tags
        for pattern in patterns.get('meta_tags', []):
            if pattern.lower() in content_lower:
                score_data['meta_score'] += 1
                score_data['evidence'].append(f"Meta pattern found: {pattern}")
        
        # فحص URLs
        for pattern in patterns.get('urls', []):
            if pattern.lower() in content_lower:
                score_data['url_score'] += 1
                score_data['evidence'].append(f"URL pattern found: {pattern}")
        
        # فحص HTML patterns
        for pattern in patterns.get('html_patterns', []):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score_data['html_score'] += len(matches)
                score_data['evidence'].append(f"HTML pattern found: {pattern} ({len(matches)} times)")
        
        # فحص Headers
        for pattern in patterns.get('headers', []):
            header_name, header_value = pattern.split(':', 1)
            header_name = header_name.strip().lower()
            header_value = header_value.strip().lower()
            
            if header_name in headers_lower:
                if header_value in headers_lower[header_name]:
                    score_data['header_score'] += 2
                    score_data['evidence'].append(f"Header found: {pattern}")
        
        # حساب النتيجة الإجمالية
        score_data['total_score'] = (
            score_data['meta_score'] * 0.3 +
            score_data['url_score'] * 0.2 +
            score_data['html_score'] * 0.4 +
            score_data['header_score'] * 0.6
        )
        
        return score_data
    
    def _detect_wordpress_plugins(self, soup: BeautifulSoup, content: str) -> List[Dict[str, str]]:
        """اكتشاف إضافات WordPress"""
        plugins = []
        
        # أنماط شائعة للإضافات
        plugin_patterns = [
            r'/wp-content/plugins/([^/]+)/',
            r"wp-plugin-([^'\"]+)",
            r'/plugins/([^/]+)/'
        ]
        
        for pattern in plugin_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                plugin_name = match.replace('-', ' ').title()
                if plugin_name not in [p['name'] for p in plugins]:
                    plugins.append({
                        'name': plugin_name,
                        'slug': match,
                        'type': 'plugin'
                    })
        
        return plugins[:10]  # أول 10 إضافات
    
    def _detect_wordpress_themes(self, soup: BeautifulSoup, content: str) -> List[Dict[str, str]]:
        """اكتشاف قوالب WordPress"""
        themes = []
        
        # أنماط شائعة للقوالب
        theme_patterns = [
            r'/wp-content/themes/([^/]+)/',
            r'/themes/([^/]+)/',
            r"template-([^'\"]+)"
        ]
        
        for pattern in theme_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                theme_name = match.replace('-', ' ').title()
                if theme_name not in [t['name'] for t in themes]:
                    themes.append({
                        'name': theme_name,
                        'slug': match,
                        'type': 'theme'
                    })
        
        return themes[:5]  # أول 5 قوالب
    
    def _detect_wordpress_version(self, soup: BeautifulSoup, content: str) -> Dict[str, str]:
        """اكتشاف إصدار WordPress"""
        version_info = {}
        
        # البحث عن رقم الإصدار
        version_patterns = [
            r'wp-includes/js/wp-emoji-release\.min\.js\?ver=([0-9.]+)',
            r'wp-includes.*?ver=([0-9.]+)',
            r'wordpress.*?([0-9]+\.[0-9]+\.[0-9]+)',
            r'generator.*?wordpress ([0-9.]+)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                version_info['version'] = match.group(1)
                break
        
        # البحث عن معلومات إضافية
        if 'wp-content' in content.lower():
            version_info['type'] = 'WordPress'
            version_info['status'] = 'detected'
        
        return version_info
    
    def _detect_drupal_version(self, soup: BeautifulSoup, content: str) -> Dict[str, str]:
        """اكتشاف إصدار Drupal"""
        version_info = {}
        
        # أنماط إصدار Drupal
        version_patterns = [
            r'Drupal\.settings',
            r'sites/default',
            r'drupal.*?([0-9]+\.[0-9]+)',
            r'/core/.*?([0-9]+\.[0-9]+)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match and len(match.groups()) > 0:
                version_info['version'] = match.group(1)
                break
        
        if 'drupal' in content.lower():
            version_info['type'] = 'Drupal'
            version_info['status'] = 'detected'
        
        return version_info
    
    def _detect_joomla_version(self, soup: BeautifulSoup, content: str) -> Dict[str, str]:
        """اكتشاف إصدار Joomla"""
        version_info = {}
        
        # أنماط إصدار Joomla
        version_patterns = [
            r'joomla.*?([0-9]+\.[0-9]+\.[0-9]+)',
            r'/media/system/.*?([0-9]+\.[0-9]+)',
            r'generator.*?joomla.*?([0-9.]+)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                version_info['version'] = match.group(1)
                break
        
        if 'joomla' in content.lower():
            version_info['type'] = 'Joomla'
            version_info['status'] = 'detected'
        
        return version_info
    
    def get_cms_statistics(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """إحصائيات اكتشاف CMS"""
        stats = {
            'total_sites_analyzed': len(detections),
            'cms_distribution': {},
            'detection_confidence_avg': 0,
            'most_common_cms': None,
            'plugins_found': 0,
            'themes_found': 0
        }
        
        if not detections:
            return stats
        
        cms_counts = {}
        total_confidence = 0
        total_plugins = 0
        total_themes = 0
        
        for detection in detections:
            cms = detection.get('detected_cms', 'Unknown')
            cms_counts[cms] = cms_counts.get(cms, 0) + 1
            total_confidence += detection.get('confidence', 0)
            total_plugins += len(detection.get('plugins_detected', []))
            total_themes += len(detection.get('themes_detected', []))
        
        stats['cms_distribution'] = cms_counts
        stats['detection_confidence_avg'] = total_confidence / len(detections)
        stats['most_common_cms'] = max(cms_counts.items(), key=lambda x: x[1])[0] if cms_counts else None
        stats['plugins_found'] = total_plugins
        stats['themes_found'] = total_themes
        
        return stats