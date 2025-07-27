#!/usr/bin/env python3
"""
نظام كشف أنظمة إدارة المحتوى (CMS Detection)
"""
import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

class CMSDetector:
    """كاشف أنظمة إدارة المحتوى"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # قاعدة بيانات أنظمة CMS والعلامات المميزة
        self.cms_signatures = {
            'WordPress': {
                'meta_tags': ['wp-content', 'wordpress'],
                'headers': ['x-pingback'],
                'paths': ['/wp-content/', '/wp-admin/', '/wp-includes/'],
                'html_patterns': [
                    r'wp-content',
                    r'wp-includes',
                    r'wordpress',
                    r'twentytwenty',
                    r'wp-emoji'
                ],
                'generator_patterns': [r'WordPress.*'],
                'cookies': ['wordpress_']
            },
            'Joomla': {
                'meta_tags': ['joomla', 'com_content'],
                'paths': ['/administrator/', '/components/', '/modules/', '/templates/'],
                'html_patterns': [
                    r'Joomla!',
                    r'com_content',
                    r'modChrome',
                    r'T3 Framework'
                ],
                'generator_patterns': [r'Joomla!.*'],
                'cookies': ['joomla_']
            },
            'Drupal': {
                'meta_tags': ['drupal', 'sites/default'],
                'headers': ['x-drupal-cache', 'x-generator'],
                'paths': ['/sites/', '/modules/', '/themes/', '/misc/'],
                'html_patterns': [
                    r'Drupal',
                    r'sites/default',
                    r'misc/drupal',
                    r'jQuery.extend\(Drupal'
                ],
                'generator_patterns': [r'Drupal.*'],
                'cookies': ['SESS']
            },
            'Magento': {
                'meta_tags': ['magento'],
                'paths': ['/skin/', '/js/prototype/', '/media/'],
                'html_patterns': [
                    r'Magento',
                    r'Mage.Cookies',
                    r'skin/frontend',
                    r'prototype/prototype'
                ],
                'cookies': ['frontend']
            },
            'Shopify': {
                'meta_tags': ['shopify'],
                'headers': ['x-shopify-stage'],
                'html_patterns': [
                    r'Shopify',
                    r'shop_money_format',
                    r'myshopify\.com',
                    r'cdn\.shopify\.com'
                ],
                'cookies': ['_shopify_']
            },
            'PrestaShop': {
                'meta_tags': ['prestashop'],
                'paths': ['/modules/', '/themes/', '/img/'],
                'html_patterns': [
                    r'PrestaShop',
                    r'prestashop',
                    r'/modules/blockcart/',
                    r'/themes/default/'
                ],
                'cookies': ['PrestaShop']
            },
            'TYPO3': {
                'meta_tags': ['typo3'],
                'paths': ['/typo3/', '/fileadmin/', '/typo3conf/'],
                'html_patterns': [
                    r'TYPO3',
                    r'typo3temp',
                    r'fileadmin',
                    r'typo3conf'
                ],
                'generator_patterns': [r'TYPO3.*']
            },
            'OpenCart': {
                'meta_tags': ['opencart'],
                'paths': ['/catalog/', '/image/'],
                'html_patterns': [
                    r'OpenCart',
                    r'catalog/view',
                    r'common\.js'
                ],
                'cookies': ['OCSESSID']
            }
        }
    
    def detect_cms(self, url: str, html_content: str = None, response: requests.Response = None) -> Dict[str, Any]:
        """كشف نظام إدارة المحتوى المستخدم"""
        
        results = {
            'detected_cms': [],
            'confidence_scores': {},
            'evidence': {},
            'version_info': {},
            'additional_info': {},
            'scan_timestamp': '',
            'scan_url': url
        }
        
        try:
            # إذا لم يتم توفير المحتوى، قم بتحميله
            if html_content is None or response is None:
                response = self.session.get(url, timeout=10)
                html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # فحص كل CMS
            for cms_name, signatures in self.cms_signatures.items():
                confidence = 0
                evidence = []
                
                # فحص meta tags
                confidence += self._check_meta_tags(soup, signatures.get('meta_tags', []), evidence)
                
                # فحص headers
                confidence += self._check_headers(response, signatures.get('headers', []), evidence)
                
                # فحص HTML patterns
                confidence += self._check_html_patterns(html_content, signatures.get('html_patterns', []), evidence)
                
                # فحص generator meta tag
                confidence += self._check_generator(soup, signatures.get('generator_patterns', []), evidence)
                
                # فحص cookies
                confidence += self._check_cookies(response, signatures.get('cookies', []), evidence)
                
                # فحص paths المميزة
                confidence += self._check_paths(url, signatures.get('paths', []), evidence)
                
                # حفظ النتائج إذا كان هناك أدلة
                if confidence > 0:
                    results['confidence_scores'][cms_name] = confidence
                    results['evidence'][cms_name] = evidence
                    
                    # إذا كان الثقة عالية، أضف إلى القائمة المكتشفة
                    if confidence >= 30:  # حد أدنى للثقة
                        results['detected_cms'].append(cms_name)
                        
                        # محاولة كشف النسخة
                        version = self._detect_version(cms_name, soup, html_content)
                        if version:
                            results['version_info'][cms_name] = version
            
            # ترتيب النتائج حسب درجة الثقة
            results['detected_cms'] = sorted(
                results['detected_cms'], 
                key=lambda x: results['confidence_scores'][x], 
                reverse=True
            )
            
            # معلومات إضافية
            results['additional_info'] = self._get_additional_info(soup, html_content)
            results['scan_timestamp'] = self._get_timestamp()
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _check_meta_tags(self, soup: BeautifulSoup, patterns: List[str], evidence: List[str]) -> int:
        """فحص meta tags"""
        confidence = 0
        
        # فحص meta generator
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            content = generator.get('content').lower()
            for pattern in patterns:
                if pattern.lower() in content:
                    evidence.append(f"Meta generator: {generator.get('content')}")
                    confidence += 25
        
        # فحص جميع meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            content = str(meta).lower()
            for pattern in patterns:
                if pattern.lower() in content:
                    evidence.append(f"Meta tag: {str(meta)[:100]}...")
                    confidence += 10
        
        return confidence
    
    def _check_headers(self, response: requests.Response, patterns: List[str], evidence: List[str]) -> int:
        """فحص HTTP headers"""
        confidence = 0
        
        if response:
            headers = {k.lower(): v.lower() for k, v in response.headers.items()}
            for pattern in patterns:
                for header_name, header_value in headers.items():
                    if pattern.lower() in header_name or pattern.lower() in header_value:
                        evidence.append(f"Header: {header_name}: {header_value}")
                        confidence += 20
        
        return confidence
    
    def _check_html_patterns(self, html_content: str, patterns: List[str], evidence: List[str]) -> int:
        """فحص أنماط HTML"""
        confidence = 0
        html_lower = html_content.lower()
        
        for pattern in patterns:
            if re.search(pattern.lower(), html_lower):
                evidence.append(f"HTML pattern: {pattern}")
                confidence += 15
        
        return confidence
    
    def _check_generator(self, soup: BeautifulSoup, patterns: List[str], evidence: List[str]) -> int:
        """فحص generator meta tag بشكل خاص"""
        confidence = 0
        
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            content = generator.get('content')
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    evidence.append(f"Generator match: {content}")
                    confidence += 30
        
        return confidence
    
    def _check_cookies(self, response: requests.Response, patterns: List[str], evidence: List[str]) -> int:
        """فحص cookies"""
        confidence = 0
        
        if response and response.cookies:
            for cookie in response.cookies:
                cookie_name = cookie.name.lower()
                for pattern in patterns:
                    if pattern.lower() in cookie_name:
                        evidence.append(f"Cookie: {cookie.name}")
                        confidence += 15
        
        return confidence
    
    def _check_paths(self, url: str, paths: List[str], evidence: List[str]) -> int:
        """فحص مسارات مميزة"""
        confidence = 0
        
        # فحص المسارات عن طريق محاولة الوصول إليها
        base_url = url.rstrip('/')
        
        for path in paths[:3]:  # فحص أول 3 مسارات فقط لتوفير الوقت
            try:
                test_url = base_url + path
                response = self.session.head(test_url, timeout=5)
                if response.status_code in [200, 301, 302, 403]:  # موجود أو محمي
                    evidence.append(f"Path exists: {path}")
                    confidence += 10
            except:
                continue
        
        return confidence
    
    def _detect_version(self, cms_name: str, soup: BeautifulSoup, html_content: str) -> Optional[str]:
        """محاولة كشف نسخة CMS"""
        
        version_patterns = {
            'WordPress': [
                r'wp-includes/js/wp-emoji-release\.min\.js\?ver=([\d\.]+)',
                r'wp-content/themes/[^/]+/style\.css\?ver=([\d\.]+)',
                r'WordPress ([\d\.]+)',
            ],
            'Joomla': [
                r'Joomla! ([\d\.]+)',
                r'media/system/js/core\.js\?([0-9a-f]+)',
            ],
            'Drupal': [
                r'Drupal ([\d\.]+)',
                r'misc/drupal\.js\?([0-9a-z]+)',
            ]
        }
        
        patterns = version_patterns.get(cms_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # فحص meta generator للنسخة
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            content = generator.get('content')
            version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', content)
            if version_match:
                return version_match.group(1)
        
        return None
    
    def _get_additional_info(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """جمع معلومات إضافية عن الموقع"""
        
        info = {}
        
        # كشف JavaScript frameworks
        js_frameworks = []
        if 'jquery' in html_content.lower():
            js_frameworks.append('jQuery')
        if 'react' in html_content.lower():
            js_frameworks.append('React')
        if 'angular' in html_content.lower():
            js_frameworks.append('Angular')
        if 'vue' in html_content.lower():
            js_frameworks.append('Vue.js')
        
        info['javascript_frameworks'] = js_frameworks
        
        # كشف CSS frameworks
        css_frameworks = []
        if 'bootstrap' in html_content.lower():
            css_frameworks.append('Bootstrap')
        if 'foundation' in html_content.lower():
            css_frameworks.append('Foundation')
        if 'bulma' in html_content.lower():
            css_frameworks.append('Bulma')
        
        info['css_frameworks'] = css_frameworks
        
        # كشف analytics
        analytics = []
        if 'google-analytics' in html_content.lower() or 'gtag' in html_content.lower():
            analytics.append('Google Analytics')
        if 'googletagmanager' in html_content.lower():
            analytics.append('Google Tag Manager')
        if 'facebook.net' in html_content.lower():
            analytics.append('Facebook Pixel')
        
        info['analytics_tools'] = analytics
        
        # معلومات تقنية أخرى
        info['has_service_worker'] = 'service-worker' in html_content.lower()
        info['has_amp'] = 'amp-' in html_content.lower()
        info['has_pwa_manifest'] = bool(soup.find('link', rel='manifest'))
        
        return info
    
    def _get_timestamp(self) -> str:
        """الحصول على timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_cms_report(self, detection_results: Dict[str, Any], output_dir) -> str:
        """إنشاء تقرير CMS مفصل"""
        
        from pathlib import Path
        
        report_file = Path(output_dir) / 'cms_detection_report.json'
        
        # إنشاء تقرير شامل
        report = {
            'cms_detection': detection_results,
            'summary': {
                'cms_detected': len(detection_results.get('detected_cms', [])),
                'primary_cms': detection_results.get('detected_cms', [None])[0],
                'confidence_level': max(detection_results.get('confidence_scores', {}).values()) if detection_results.get('confidence_scores') else 0,
                'frameworks_detected': len(detection_results.get('additional_info', {}).get('javascript_frameworks', [])),
                'analytics_tools': len(detection_results.get('additional_info', {}).get('analytics_tools', []))
            },
            'recommendations': self._generate_recommendations(detection_results)
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(report_file)
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """إنشاء توصيات بناءً على النتائج"""
        
        recommendations = []
        detected_cms = results.get('detected_cms', [])
        
        if not detected_cms:
            recommendations.append("لم يتم كشف نظام إدارة محتوى محدد - قد يكون موقع مخصص")
        elif len(detected_cms) == 1:
            cms = detected_cms[0]
            recommendations.append(f"تم كشف {cms} - يمكن استخدام أدوات متخصصة لهذا النظام")
        else:
            recommendations.append("تم كشف عدة أنظمة - قد يكون هناك migratio أو hybrid setup")
        
        additional_info = results.get('additional_info', {})
        
        if additional_info.get('javascript_frameworks'):
            frameworks = ', '.join(additional_info['javascript_frameworks'])
            recommendations.append(f"JavaScript frameworks مكتشفة: {frameworks}")
        
        if additional_info.get('analytics_tools'):
            tools = ', '.join(additional_info['analytics_tools'])
            recommendations.append(f"أدوات التحليل المستخدمة: {tools}")
        
        return recommendations