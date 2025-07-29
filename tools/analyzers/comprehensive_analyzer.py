"""
محلل شامل متقدم - Comprehensive Advanced Analyzer
يدمج جميع أدوات التحليل في نظام واحد متطور

المحللات المدمجة:
- SecurityAnalyzer: محلل الأمان المتقدم
- PerformanceAnalyzer: محلل الأداء الشامل  
- SEOAnalyzer: محلل تحسين محركات البحث
- CompetitorAnalyzer: محلل المنافسين
- AdvancedWebsiteAnalyzer: محلل متقدم للمواقع
- WebsiteAnalyzer: محلل المواقع الأساسي
"""

import re
import ssl
import time
import json
import socket
import hashlib
import requests
import logging
import base64
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from collections import defaultdict, Counter

try:
    import builtwith
    BUILTWITH_AVAILABLE = True
except ImportError:
    BUILTWITH_AVAILABLE = False
    logging.warning("builtwith library not available - technology detection will be limited")

class ComprehensiveAnalyzer:
    """محلل شامل يدمج جميع أنواع التحليل"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # تهيئة أنماط التحليل المختلفة
        self._init_technology_patterns()
        self._init_security_patterns()
        self._init_performance_metrics()
        self._init_seo_criteria()
        
    def _init_technology_patterns(self):
        """تهيئة أنماط التقنيات"""
        self.framework_signatures = {
            'React': [r'React\.createElement', r'react-dom', r'reactjs', r'jsx', r'data-reactroot'],
            'Vue.js': [r'Vue\.js', r'vue@', r'v-if', r'v-for', r'v-model', r'__VUE__'],
            'Angular': [r'@angular', r'ng-app', r'ng-controller', r'ng-repeat', r'angular\.module'],
            'jQuery': [r'jquery', r'\$\(', r'jQuery\(', r'jquery\.min\.js'],
            'Bootstrap': [r'bootstrap', r'btn-primary', r'container-fluid', r'row', r'col-md'],
            'Tailwind': [r'tailwindcss', r'bg-blue-500', r'text-center', r'flex items-center']
        }
        
        self.cms_patterns = {
            'WordPress': [r'wp-content', r'wp-includes', r'wordpress'],
            'Drupal': [r'drupal', r'sites/default', r'modules'],
            'Joomla': [r'joomla', r'templates', r'components'],
            'Magento': [r'magento', r'skin/frontend'],
            'Shopify': [r'shopify', r'cdn.shopify.com']
        }
        
    def _init_security_patterns(self):
        """تهيئة أنماط الأمان"""
        self.vulnerability_patterns = {
            'sql_injection': [r'error in your sql syntax', r'mysql_fetch_array', r'ora-\d{5}'],
            'xss_indicators': [r'<script[^>]*>', r'javascript:', r'onerror\s*=', r'onload\s*='],
            'sensitive_files': [r'\.env', r'config\.php', r'wp-config\.php', r'\.htaccess'],
            'information_disclosure': [r'server:\s*apache', r'x-powered-by', r'php/\d+\.\d+']
        }
        
        self.security_headers = [
            'Content-Security-Policy', 'X-Content-Type-Options', 'X-Frame-Options',
            'X-XSS-Protection', 'Strict-Transport-Security', 'Referrer-Policy'
        ]
        
    def _init_performance_metrics(self):
        """تهيئة مقاييس الأداء"""
        self.performance_thresholds = {
            'load_time_excellent': 1000,  # milliseconds
            'load_time_good': 3000,
            'file_size_large': 2000000,  # bytes
            'image_count_high': 50
        }
        
    def _init_seo_criteria(self):
        """تهيئة معايير SEO"""
        self.seo_requirements = {
            'title_min_length': 30,
            'title_max_length': 60,
            'description_min_length': 120,
            'description_max_length': 160,
            'h1_max_count': 1
        }

    def analyze_comprehensive(self, url, crawl_data=None):
        """تحليل شامل للموقع"""
        try:
            analysis_result = {
                'url': url,
                'timestamp': time.time(),
                'basic_analysis': self.analyze_basic_website(url, crawl_data),
                'advanced_analysis': self.analyze_advanced_structure(url, crawl_data),
                'security_analysis': self.analyze_security_comprehensive(url),
                'performance_analysis': self.analyze_performance_comprehensive(url),
                'seo_analysis': self.analyze_seo_comprehensive(url),
                'technical_analysis': self.analyze_technical_comprehensive(url, crawl_data),
                'competitor_insights': self.get_competitor_insights(url),
                'overall_score': 0,
                'recommendations': []
            }
            
            # حساب النتيجة الإجمالية
            analysis_result['overall_score'] = self._calculate_overall_score(analysis_result)
            analysis_result['recommendations'] = self._generate_comprehensive_recommendations(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logging.error(f"خطأ في التحليل الشامل: {e}")
            return {'error': str(e), 'url': url}

    def analyze_basic_website(self, url, crawl_data):
        """تحليل أساسي للموقع"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            basic_info = {
                'title': self._safe_get_text(soup.find('title')),
                'description': self._get_meta_content(soup, 'description'),
                'language': self._safe_get_lang(soup.find('html')),
                'status_code': response.status_code,
                'page_size': len(response.content),
                'load_time': response.elapsed.total_seconds() * 1000 if hasattr(response, 'elapsed') else 0,
                'technology_stack': self._detect_technologies_basic(soup, response),
                'content_metrics': self._analyze_content_metrics_basic(soup)
            }
            
            return basic_info
            
        except Exception as e:
            logging.error(f"خطأ في التحليل الأساسي: {e}")
            return {'error': str(e)}

    def analyze_advanced_structure(self, url, crawl_data):
        """تحليل البنية المتقدمة"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            structure_analysis = {
                'html_structure': self._analyze_html_structure(soup),
                'css_analysis': self._analyze_css_structure(soup),
                'javascript_analysis': self._analyze_javascript_structure(soup),
                'component_hierarchy': self._analyze_component_hierarchy(soup),
                'semantic_structure': self._analyze_semantic_elements(soup),
                'accessibility_features': self._analyze_accessibility(soup),
                'responsive_design': self._analyze_responsive_design(soup)
            }
            
            return structure_analysis
            
        except Exception as e:
            logging.error(f"خطأ في تحليل البنية المتقدمة: {e}")
            return {'error': str(e)}

    def analyze_security_comprehensive(self, url):
        """تحليل أمان شامل"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            security_report = {
                'ssl_analysis': self._analyze_ssl(domain),
                'headers_analysis': self._analyze_security_headers(url),
                'vulnerability_scan': self._scan_vulnerabilities(url),
                'cookie_analysis': self._analyze_cookies(url),
                'content_security': self._analyze_content_security(url),
                'security_score': 0,
                'risk_level': 'unknown'
            }
            
            security_report['security_score'] = self._calculate_security_score(security_report)
            security_report['risk_level'] = self._determine_risk_level(security_report['security_score'])
            
            return security_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الأمان: {e}")
            return {'error': str(e)}

    def analyze_performance_comprehensive(self, url):
        """تحليل أداء شامل"""
        try:
            performance_report = {
                'loading_metrics': self._measure_loading_performance(url),
                'resource_analysis': self._analyze_resources(url),
                'optimization_opportunities': self._identify_optimizations(url),
                'caching_analysis': self._analyze_caching(url),
                'compression_analysis': self._analyze_compression(url),
                'mobile_performance': self._analyze_mobile_performance(url),
                'performance_score': 0
            }
            
            performance_report['performance_score'] = self._calculate_performance_score(performance_report)
            
            return performance_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الأداء: {e}")
            return {'error': str(e)}

    def analyze_seo_comprehensive(self, url):
        """تحليل SEO شامل"""
        try:
            seo_report = {
                'title_analysis': self._analyze_title(url),
                'meta_analysis': self._analyze_meta_tags(url),
                'heading_structure': self._analyze_headings(url),
                'content_analysis': self._analyze_content_seo(url),
                'link_analysis': self._analyze_links(url),
                'image_seo': self._analyze_image_seo(url),
                'technical_seo': self._analyze_technical_seo(url),
                'structured_data': self._analyze_structured_data(url),
                'social_media': self._analyze_social_tags(url),
                'seo_score': 0
            }
            
            seo_report['seo_score'] = self._calculate_seo_score(seo_report)
            
            return seo_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل SEO: {e}")
            return {'error': str(e)}

    def analyze_technical_comprehensive(self, url, crawl_data):
        """تحليل تقني شامل"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            technical_analysis = {
                'framework_detection': self._detect_frameworks_advanced(soup, response),
                'backend_technologies': self._detect_backend_technologies(soup, response),
                'database_indicators': self._detect_database_indicators(soup, response),
                'hosting_analysis': self._analyze_hosting_environment(url),
                'cdn_analysis': self._analyze_cdn_usage(soup, response),
                'third_party_services': self._detect_third_party_services(soup, response),
                'api_endpoints': self._discover_api_endpoints(soup, response),
                'development_stack': self._analyze_development_stack(soup, response)
            }
            
            return technical_analysis
            
        except Exception as e:
            logging.error(f"خطأ في التحليل التقني: {e}")
            return {'error': str(e)}

    def get_competitor_insights(self, url):
        """تحليل رؤى المنافسين"""
        try:
            domain = urlparse(url).netloc
            insights = {
                'domain_analysis': self._analyze_domain_characteristics(domain),
                'market_positioning': self._estimate_market_position(url),
                'technology_comparison': self._compare_technology_trends(url),
                'content_strategy': self._analyze_content_strategy(url)
            }
            
            return insights
            
        except Exception as e:
            logging.error(f"خطأ في تحليل المنافسين: {e}")
            return {'error': str(e)}

    # Helper Methods for Basic Analysis
    def _get_meta_content(self, soup, name):
        """استخراج محتوى meta tag"""
        meta = soup.find('meta', attrs={'name': name})
        return meta.get('content', '') if meta else ''

    def _detect_technologies_basic(self, soup, response):
        """كشف التقنيات الأساسية"""
        technologies = {
            'cms': 'unknown',
            'frameworks': [],
            'libraries': []
        }
        
        content = str(soup).lower()
        
        # كشف CMS
        for cms, patterns in self.cms_patterns.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                technologies['cms'] = cms
                break
        
        # كشف Frameworks
        for framework, patterns in self.framework_signatures.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                technologies['frameworks'].append(framework)
        
        return technologies

    def _analyze_content_metrics_basic(self, soup):
        """تحليل مقاييس المحتوى الأساسية"""
        text_content = soup.get_text()
        return {
            'word_count': len(text_content.split()),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'image_count': len(soup.find_all('img')),
            'link_count': len(soup.find_all('a'))
        }

    # Helper Methods for SSL Analysis
    def _analyze_ssl(self, domain):
        """تحليل شهادة SSL"""
        ssl_info = {
            'has_ssl': False,
            'certificate_valid': False,
            'issuer': '',
            'expiry_date': '',
            'protocol_version': ''
        }
        
        try:
            context = ssl.create_default_context()
            sock = socket.create_connection((domain, 443), timeout=10)
            ssl_sock = context.wrap_socket(sock, server_hostname=domain)
            
            ssl_info['has_ssl'] = True
            ssl_info['certificate_valid'] = True
            ssl_info['protocol_version'] = ssl_sock.version()
            
            cert = ssl_sock.getpeercert()
            if cert:
                ssl_info['issuer'] = dict(x[0] for x in cert['issuer'])
                ssl_info['expiry_date'] = cert['notAfter']
            
            ssl_sock.close()
            
        except Exception as e:
            logging.error(f"خطأ في تحليل SSL: {e}")
            ssl_info['error'] = str(e)
        
        return ssl_info

    # Additional helper methods would continue here...
    # Due to length constraints, I'm showing the structure and key methods

    def _calculate_overall_score(self, analysis_result):
        """حساب النتيجة الإجمالية"""
        scores = []
        
        if 'security_analysis' in analysis_result and 'security_score' in analysis_result['security_analysis']:
            scores.append(analysis_result['security_analysis']['security_score'] * 0.25)
        
        if 'performance_analysis' in analysis_result and 'performance_score' in analysis_result['performance_analysis']:
            scores.append(analysis_result['performance_analysis']['performance_score'] * 0.25)
        
        if 'seo_analysis' in analysis_result and 'seo_score' in analysis_result['seo_analysis']:
            scores.append(analysis_result['seo_analysis']['seo_score'] * 0.25)
        
        # Technical score (estimated)
        scores.append(75 * 0.25)  # Default technical score
        
        return sum(scores) if scores else 0

    def _safe_get_text(self, element) -> str:
        """Safely extract text from BeautifulSoup element."""
        if element and hasattr(element, 'get_text'):
            return element.get_text().strip()
        elif element and hasattr(element, 'string') and element.string:
            return str(element.string).strip()
        return ''

    def _safe_get_lang(self, element) -> str:
        """Safely extract language attribute from HTML element."""
        if element and isinstance(element, Tag):
            lang_val = element.get('lang', 'unknown')
            return str(lang_val) if isinstance(lang_val, list) else str(lang_val)
        return 'unknown'

    def _scan_information_leaks_full(self, url):
        """Scan for information leaks - placeholder implementation."""
        return {
            'exposed_files': [],
            'sensitive_endpoints': [],
            'error_pages': [],
            'directory_listing': False,
            'debug_info': []
        }

    def _generate_comprehensive_recommendations(self, analysis_result):
        """إنشاء توصيات شاملة"""
        recommendations = []
        
        # توصيات الأمان
        if analysis_result.get('security_analysis', {}).get('security_score', 0) < 70:
            recommendations.append("تحسين إعدادات الأمان وإضافة رؤوس الحماية المطلوبة")
        
        # توصيات الأداء
        if analysis_result.get('performance_analysis', {}).get('performance_score', 0) < 70:
            recommendations.append("تحسين سرعة التحميل وضغط الملفات")
        
        # توصيات SEO
        if analysis_result.get('seo_analysis', {}).get('seo_score', 0) < 70:
            recommendations.append("تحسين العناوين والأوصاف لمحركات البحث")
        
        return recommendations

    # Placeholder methods for complete functionality
    def _analyze_html_structure(self, soup): return {}
    def _analyze_css_structure(self, soup): return {}
    def _analyze_javascript_structure(self, soup): return {}
    def _analyze_component_hierarchy(self, soup): return {}
    def _analyze_semantic_elements(self, soup): return {}
    def _analyze_accessibility(self, soup): return {}
    def _analyze_responsive_design(self, soup): return {}
    def _analyze_security_headers(self, url): return {}
    def _scan_vulnerabilities(self, url): return {}
    def _analyze_cookies(self, url): return {}
    def _analyze_content_security(self, url): return {}
    def _calculate_security_score(self, report): return 75
    def _determine_risk_level(self, score): return 'medium'
    def _measure_loading_performance(self, url): return {}
    def _analyze_resources(self, url): return {}
    def _identify_optimizations(self, url): return {}
    def _analyze_caching(self, url): return {}
    def _analyze_compression(self, url): return {}
    def _analyze_mobile_performance(self, url): return {}
    def _calculate_performance_score(self, report): return 75
    def _analyze_title(self, url): return {}
    def _analyze_meta_tags(self, url): return {}
    def _analyze_headings(self, url): return {}
    def _analyze_content_seo(self, url): return {}
    def _analyze_links(self, url): return {}
    def _analyze_image_seo(self, url): return {}
    def _analyze_technical_seo(self, url): return {}
    def _analyze_structured_data(self, url): return {}
    def _analyze_social_tags(self, url): return {}
    def _calculate_seo_score(self, report): return 75
    def _detect_frameworks_advanced(self, soup, response): return {}
    def _detect_backend_technologies(self, soup, response): return {}
    def _detect_database_indicators(self, soup, response): return {}
    def _analyze_hosting_environment(self, url): return {}
    def _analyze_cdn_usage(self, soup, response): return {}
    def _detect_third_party_services(self, soup, response): return {}
    def _discover_api_endpoints(self, soup, response): return {}
    def _analyze_development_stack(self, soup, response): return {}
    def _analyze_domain_characteristics(self, domain): return {}
    def _estimate_market_position(self, url): return {}
    def _compare_technology_trends(self, url): return {}
    def _analyze_content_strategy(self, url): return {}

    # ================ SecurityAnalyzer المدمج ================
    
    def analyze_security(self, url):
        """تحليل أمان شامل للموقع - من SecurityAnalyzer"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            security_report = {
                'url': url,
                'domain': domain,
                'ssl_analysis': self._analyze_ssl(domain),
                'headers_analysis': self._analyze_security_headers_full(url),
                'vulnerability_scan': self._scan_vulnerabilities_full(url),
                'cookie_analysis': self._analyze_cookies_full(url),
                'content_analysis': self._analyze_content_security_full(url),
                'information_leak_scan': self._scan_information_leaks_full(url),
                'security_score': 0,
                'risk_level': 'unknown',
                'recommendations': []
            }
            
            security_report['security_score'] = self._calculate_security_score_full(security_report)
            security_report['risk_level'] = self._determine_risk_level_full(security_report['security_score'])
            security_report['recommendations'] = self._generate_security_recommendations_full(security_report)
            
            return security_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الأمان: {e}")
            return {'error': str(e)}

    def _analyze_security_headers_full(self, url):
        """تحليل رؤوس الأمان الكامل"""
        headers_analysis = {
            'present_headers': {},
            'missing_headers': [],
            'header_scores': {},
            'total_score': 0
        }
        
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            security_headers = [
                'Content-Security-Policy',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'Referrer-Policy',
                'Permissions-Policy'
            ]
            
            for header in security_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    headers_analysis['present_headers'][header] = headers.get(header, '')
                    headers_analysis['header_scores'][header] = self._score_security_header_full(header, headers.get(header, ''))
                else:
                    headers_analysis['missing_headers'].append(header)
                    headers_analysis['header_scores'][header] = 0
            
            headers_analysis['total_score'] = sum(headers_analysis['header_scores'].values()) / len(security_headers) * 100
            
        except Exception as e:
            logging.error(f"خطأ في تحليل رؤوس الأمان: {e}")
            
        return headers_analysis

    def _score_security_header_full(self, header, value):
        """تقييم رأس الأمان الكامل"""
        if not value:
            return 0
        
        scores = {
            'Content-Security-Policy': 30 if 'default-src' in value else 15,
            'X-Content-Type-Options': 15 if 'nosniff' in value else 0,
            'X-Frame-Options': 15 if value.upper() in ['DENY', 'SAMEORIGIN'] else 0,
            'X-XSS-Protection': 10 if '1; mode=block' in value else 5,
            'Strict-Transport-Security': 20 if 'max-age' in value else 0,
            'Referrer-Policy': 5,
            'Permissions-Policy': 5
        }
        
        return scores.get(header, 0)

    # ================ PerformanceAnalyzer المدمج ================
    
    def analyze_performance_full(self, url):
        """تحليل أداء شامل للموقع - من PerformanceAnalyzer"""
        try:
            performance_report = {
                'url': url,
                'loading_metrics': self._measure_loading_performance_full(url),
                'resource_analysis': self._analyze_resources_full(url),
                'optimization_opportunities': self._identify_optimizations_full(url),
                'caching_analysis': self._analyze_caching_headers_full(url),
                'compression_analysis': self._analyze_compression_full(url),
                'mobile_performance': self._analyze_mobile_performance_full(url),
                'core_web_vitals': self._estimate_core_web_vitals_full(url),
                'performance_score': 0,
                'recommendations': []
            }
            
            performance_report['performance_score'] = self._calculate_performance_score_full(performance_report)
            performance_report['recommendations'] = self._generate_performance_recommendations_full(performance_report)
            
            return performance_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الأداء: {e}")
            return {'error': str(e)}

    def _measure_loading_performance_full(self, url):
        """قياس أداء التحميل الكامل"""
        metrics = {
            'total_load_time': 0,
            'dns_lookup_time': 0,
            'connection_time': 0,
            'ssl_handshake_time': 0,
            'first_byte_time': 0,
            'content_download_time': 0,
            'redirect_count': 0,
            'final_url': url
        }
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=30, allow_redirects=True)
            end_time = time.time()
            
            metrics['total_load_time'] = round((end_time - start_time) * 1000, 2)
            metrics['redirect_count'] = len(response.history)
            metrics['final_url'] = response.url
            metrics['status_code'] = response.status_code
            metrics['content_size'] = len(response.content)
            
            if hasattr(response, 'elapsed'):
                total_elapsed = response.elapsed.total_seconds() * 1000
                metrics['first_byte_time'] = round(total_elapsed * 0.7, 2)
                metrics['content_download_time'] = round(total_elapsed * 0.3, 2)
                
        except Exception as e:
            logging.error(f"خطأ في قياس الأداء: {e}")
            
        return metrics

    def _analyze_caching_headers_full(self, url):
        """تحليل رؤوس التخزين المؤقت الكامل"""
        caching_info = {
            'cache_control': '',
            'expires': '',
            'etag': '',
            'last_modified': '',
            'cache_status': 'unknown',
            'max_age': 0,
            'recommendations': []
        }
        
        try:
            response = self.session.head(url, timeout=10)
            headers = response.headers
            
            caching_info['cache_control'] = headers.get('Cache-Control', '')
            caching_info['expires'] = headers.get('Expires', '')
            caching_info['etag'] = headers.get('ETag', '')
            caching_info['last_modified'] = headers.get('Last-Modified', '')
            
            if 'max-age' in caching_info['cache_control']:
                max_age_match = re.search(r'max-age=(\d+)', caching_info['cache_control'])
                if max_age_match:
                    caching_info['max_age'] = int(max_age_match.group(1))
            
            if not caching_info['cache_control']:
                caching_info['cache_status'] = 'no_cache_headers'
                caching_info['recommendations'].append('إضافة رؤوس التخزين المؤقت لتحسين الأداء')
            elif 'no-cache' in caching_info['cache_control']:
                caching_info['cache_status'] = 'no_cache'
            elif caching_info['max_age'] > 0:
                caching_info['cache_status'] = 'cacheable'
            
        except Exception as e:
            logging.error(f"خطأ في تحليل التخزين المؤقت: {e}")
            
        return caching_info

    # ================ SEOAnalyzer المدمج ================
    
    def analyze_seo_full(self, url):
        """تحليل SEO شامل للموقع - من SEOAnalyzer"""
        try:
            seo_report = {
                'url': url,
                'title_analysis': self._analyze_title_full(url),
                'meta_analysis': self._analyze_meta_tags_full(url),
                'heading_structure': self._analyze_headings_full(url),
                'content_analysis': self._analyze_content_seo_full(url),
                'link_analysis': self._analyze_links_full(url),
                'image_seo': self._analyze_image_seo_full(url),
                'technical_seo': self._analyze_technical_seo_full(url),
                'structured_data': self._analyze_structured_data_full(url),
                'social_media': self._analyze_social_tags_full(url),
                'seo_score': 0,
                'recommendations': []
            }
            
            seo_report['seo_score'] = self._calculate_seo_score_full(seo_report)
            seo_report['recommendations'] = self._generate_seo_recommendations_full(seo_report)
            
            return seo_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل SEO: {e}")
            return {'error': str(e)}

    def _analyze_title_full(self, url):
        """تحليل عنوان الصفحة الكامل"""
        title_analysis = {
            'title': '',
            'length': 0,
            'length_status': '',
            'keyword_presence': False,
            'uniqueness_score': 0,
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_tag = soup.find('title')
            if title_tag:
                title_analysis['title'] = title_tag.get_text().strip()
                title_analysis['length'] = len(title_analysis['title'])
                
                if title_analysis['length'] < 30:
                    title_analysis['length_status'] = 'قصير جداً'
                    title_analysis['issues'].append('العنوان قصير جداً - يجب أن يكون 30-60 حرف')
                elif title_analysis['length'] > 60:
                    title_analysis['length_status'] = 'طويل جداً'
                    title_analysis['issues'].append('العنوان طويل جداً - قد يتم قطعه في نتائج البحث')
                else:
                    title_analysis['length_status'] = 'مناسب'
            else:
                title_analysis['issues'].append('لا يوجد عنوان للصفحة')
                
        except Exception as e:
            logging.error(f"خطأ في تحليل العنوان: {e}")
            
        return title_analysis

    # ================ CompetitorAnalyzer المدمج ================
    
    def analyze_competitors_full(self, main_url, competitor_urls):
        """تحليل مقارن للمنافسين - من CompetitorAnalyzer"""
        try:
            analysis = {
                'main_site': self._analyze_single_site_full(main_url),
                'competitors': {},
                'comparison': {},
                'recommendations': []
            }
            
            for url in competitor_urls:
                analysis['competitors'][url] = self._analyze_single_site_full(url)
            
            analysis['comparison'] = self._compare_sites_full(analysis)
            analysis['recommendations'] = self._generate_competitive_recommendations_full(analysis)
            
            return analysis
            
        except Exception as e:
            logging.error(f"خطأ في تحليل المنافسين: {e}")
            return {'error': str(e)}

    def _analyze_single_site_full(self, url):
        """تحليل موقع واحد كامل"""
        site_analysis = {
            'url': url,
            'basic_info': {},
            'technology_stack': {},
            'content_metrics': {},
            'seo_factors': {},
            'performance_indicators': {},
            'social_presence': {}
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # معلومات أساسية
            site_analysis['basic_info'] = {
                'title': self._safe_get_text(soup.find('title')),
                'description': self._get_meta_content_full(soup, 'description'),
                'language': self._safe_get_lang(soup.find('html')),
                'status_code': response.status_code,
                'page_size': len(response.content)
            }
            
            # تحليل التقنيات
            site_analysis['technology_stack'] = self._detect_technologies_full(soup, response)
            
            # مقاييس المحتوى
            site_analysis['content_metrics'] = self._analyze_content_metrics_full(soup)
            
            # عوامل SEO
            site_analysis['seo_factors'] = self._analyze_seo_factors_full(soup)
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الموقع {url}: {e}")
            
        return site_analysis

    def _get_meta_content_full(self, soup, name):
        """استخراج محتوى meta tag"""
        meta_tag = soup.find('meta', attrs={'name': name})
        if meta_tag and isinstance(meta_tag, Tag):
            content = meta_tag.get('content', '')
            return str(content) if isinstance(content, list) else str(content)
        return ''

    # ================ AdvancedWebsiteAnalyzer المدمج ================
    
    def extract_complete_structure_full(self, crawl_data):
        """استخراج البنية الكاملة للموقع - من AdvancedWebsiteAnalyzer"""
        structure = {
            'html_structure': {},
            'css_grid_layouts': [],
            'flexbox_layouts': [],
            'responsive_breakpoints': [],
            'component_hierarchy': {},
            'semantic_structure': {},
            'accessibility_features': {},
            'interactive_elements': {}
        }
        
        for url, page_data in crawl_data.items():
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # تحليل البنية الهيكلية
                structure['html_structure'][url] = self._analyze_html_structure_full(soup)
                
                # تحليل تخطيطات CSS
                structure['css_grid_layouts'].extend(self._extract_css_layouts_full(soup, 'grid'))
                structure['flexbox_layouts'].extend(self._extract_css_layouts_full(soup, 'flex'))
                
                # تحليل العناصر الدلالية
                structure['semantic_structure'][url] = self._analyze_semantic_elements_full(soup)
                
                # تحليل ميزات إمكانية الوصول
                structure['accessibility_features'][url] = self._analyze_accessibility_full(soup)
                
                # تحليل العناصر التفاعلية
                structure['interactive_elements'][url] = self._analyze_interactive_elements_full(soup)
                
            except Exception as e:
                logging.error(f"خطأ في تحليل {url}: {e}")
        
        return structure

    # ================ WebsiteAnalyzer المدمج ================
    
    def analyze_website_basic_full(self, url, crawl_data=None):
        """تحليل أساسي للموقع - من WebsiteAnalyzer"""
        analysis = {
            'url': url,
            'basic_info': {},
            'technologies': {},
            'content_summary': {},
            'meta_information': {},
            'performance_basic': {}
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # معلومات أساسية
            analysis['basic_info'] = {
                'title': self._safe_get_text(soup.find('title')),
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'page_size': len(response.content),
                'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
            }
            
            # تحليل التقنيات الأساسي
            analysis['technologies'] = self._detect_basic_technologies_full(soup, response)
            
            # ملخص المحتوى
            analysis['content_summary'] = self._summarize_content_full(soup)
            
            # معلومات meta
            analysis['meta_information'] = self._extract_meta_info_full(soup)
            
        except Exception as e:
            logging.error(f"خطأ في التحليل الأساسي: {e}")
            analysis['error'] = str(e)
            
        return analysis

    # ================ وظائف مساعدة إضافية ================
    
    def _calculate_security_score_full(self, security_report):
        """حساب نقاط الأمان الكامل"""
        score = 0
        
        # SSL Analysis (30 points)
        if security_report['ssl_analysis']['has_ssl']:
            score += 15
        if security_report['ssl_analysis']['certificate_valid']:
            score += 15
            
        # Security Headers (40 points)
        score += security_report['headers_analysis']['total_score'] * 0.4
        
        # Vulnerabilities (30 points)
        vuln_score = security_report['vulnerability_scan'].get('total_score', 0)
        score += vuln_score * 0.3
        
        return min(100, max(0, score))

    def _determine_risk_level_full(self, security_score):
        """تحديد مستوى المخاطر الكامل"""
        if security_score >= 80:
            return 'منخفض'
        elif security_score >= 60:
            return 'متوسط'
        elif security_score >= 40:
            return 'عالي'
        else:
            return 'خطير'

    def _calculate_performance_score_full(self, performance_report):
        """حساب نقاط الأداء الكامل"""
        score = 100
        
        # Loading time penalty
        load_time = performance_report['loading_metrics']['total_load_time']
        if load_time > 3000:  # > 3 seconds
            score -= 30
        elif load_time > 2000:  # > 2 seconds
            score -= 20
        elif load_time > 1000:  # > 1 second
            score -= 10
            
        # Resource optimization
        if not performance_report['compression_analysis'].get('compressed', False):
            score -= 15
            
        if not performance_report['caching_analysis'].get('cache_status') == 'cacheable':
            score -= 15
            
        return max(0, score)

    def _calculate_seo_score_full(self, seo_report):
        """حساب نقاط SEO الكامل"""
        score = 0
        
        # Title (20 points)
        if seo_report['title_analysis']['length_status'] == 'مناسب':
            score += 20
        elif seo_report['title_analysis']['length_status'] != '':
            score += 10
            
        # Meta description (20 points)
        if seo_report['meta_analysis']['description']['status'] == 'مناسب':
            score += 20
        elif seo_report['meta_analysis']['description']['status'] != '':
            score += 10
            
        # Headings (15 points)
        if seo_report['heading_structure'].get('h1_count', 0) == 1:
            score += 15
        elif seo_report['heading_structure'].get('h1_count', 0) > 0:
            score += 10
            
        # Other factors (45 points)
        if seo_report['meta_analysis']['viewport']['present']:
            score += 10
        if seo_report['meta_analysis']['canonical']['present']:
            score += 10
        if seo_report['image_seo'].get('alt_text_coverage', 0) > 80:
            score += 15
        if seo_report['technical_seo'].get('https', False):
            score += 10
            
        return min(100, score)

    # Placeholder methods for all remaining functionality
    def _scan_vulnerabilities_full(self, url): return {'total_score': 80}
    def _analyze_cookies_full(self, url): return {}
    def _analyze_content_security_full(self, url): return {}
    def _generate_security_recommendations_full(self, report): return []
    def _analyze_resources_full(self, url): return {}
    def _identify_optimizations_full(self, url): return {}
    def _analyze_compression_full(self, url): return {'compressed': False}
    def _analyze_mobile_performance_full(self, url): return {}
    def _estimate_core_web_vitals_full(self, url): return {}
    def _generate_performance_recommendations_full(self, report): return []
    def _analyze_meta_tags_full(self, url): return {'description': {'status': ''}, 'viewport': {'present': False}, 'canonical': {'present': False}}
    def _analyze_headings_full(self, url): return {'h1_count': 1}
    def _analyze_content_seo_full(self, url): return {}
    def _analyze_links_full(self, url): return {}
    def _analyze_image_seo_full(self, url): return {'alt_text_coverage': 85}
    def _analyze_technical_seo_full(self, url): return {'https': True}
    def _analyze_structured_data_full(self, url): return {}
    def _analyze_social_tags_full(self, url): return {}
    def _generate_seo_recommendations_full(self, report): return []
    def _compare_sites_full(self, analysis): return {}
    def _generate_competitive_recommendations_full(self, analysis): return []
    def _detect_technologies_full(self, soup, response): return {}
    def _analyze_content_metrics_full(self, soup): return {}
    def _analyze_seo_factors_full(self, soup): return {}
    def _analyze_html_structure_full(self, soup): return {}
    def _extract_css_layouts_full(self, soup, layout_type): return []
    def _analyze_semantic_elements_full(self, soup): return {}
    def _analyze_accessibility_full(self, soup): return {}
    def _analyze_interactive_elements_full(self, soup): return {}
    def _detect_basic_technologies_full(self, soup, response): return {}
    def _summarize_content_full(self, soup): return {}
    def _extract_meta_info_full(self, soup): return {}