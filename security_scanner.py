"""
نظام فحص الحماية والأمان المتطور
Advanced Security Scanner System
"""
import re
import ssl
import socket
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# تعطيل تحذيرات SSL للفحص
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class SecurityScanner:
    """ماسح الأمان الشامل للمواقع"""
    
    def __init__(self):
        self.session = self._create_secure_session()
        
        # قوائم التهديدات المعروفة
        self.malicious_domains = {
            'malware.com', 'phishing.example', 'suspicious-site.net',
            'fake-bank.com', 'virus-download.org'
        }
        
        # أنماط الثغرات الأمنية
        self.vulnerability_patterns = {
            'sql_injection': [
                r"(?i)(union.*select|select.*from|insert.*into|delete.*from)",
                r"(?i)(or\s+1\s*=\s*1|and\s+1\s*=\s*1)",
                r"(?i)(exec\s*\(|execute\s*\()"
            ],
            'xss': [
                r"(?i)(<script|</script>|javascript:|vbscript:)",
                r"(?i)(onload\s*=|onclick\s*=|onerror\s*=)",
                r"(?i)(alert\s*\(|confirm\s*\(|prompt\s*\()"
            ],
            'csrf': [
                r"(?i)(csrf_token|authenticity_token)",
                r"(?i)(X-CSRF-Token|X-Requested-With)"
            ]
        }
        
        # رؤوس الأمان المطلوبة
        self.security_headers = {
            'X-Frame-Options': 'حماية من clickjacking',
            'X-Content-Type-Options': 'منع MIME type sniffing',
            'X-XSS-Protection': 'حماية من XSS',
            'Strict-Transport-Security': 'إجبار HTTPS',
            'Content-Security-Policy': 'سياسة أمان المحتوى',
            'Referrer-Policy': 'سياسة المرجع',
            'Permissions-Policy': 'أذونات المتصفح'
        }
    
    def _create_secure_session(self) -> requests.Session:
        """إنشاء جلسة آمنة للفحص"""
        session = requests.Session()
        
        # إعداد retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # رؤوس الأمان
        session.headers.update({
            'User-Agent': 'Security-Scanner/1.0 (Website Analysis)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def comprehensive_security_scan(self, url: str) -> Dict[str, Any]:
        """فحص أمني شامل للموقع"""
        logger.info(f"بدء الفحص الأمني الشامل للموقع: {url}")
        
        scan_results = {
            'url': url,
            'timestamp': '',
            'ssl_analysis': {},
            'header_analysis': {},
            'vulnerability_scan': {},
            'content_analysis': {},
            'domain_reputation': {},
            'overall_security_score': 0,
            'recommendations': [],
            'threats_detected': []
        }
        
        try:
            # فحص SSL/TLS
            scan_results['ssl_analysis'] = self._analyze_ssl(url)
            
            # فحص رؤوس الأمان
            scan_results['header_analysis'] = self._analyze_security_headers(url)
            
            # فحص الثغرات
            scan_results['vulnerability_scan'] = self._scan_vulnerabilities(url)
            
            # تحليل المحتوى
            scan_results['content_analysis'] = self._analyze_content_security(url)
            
            # فحص سمعة النطاق
            scan_results['domain_reputation'] = self._check_domain_reputation(url)
            
            # حساب النقاط الإجمالية
            scan_results['overall_security_score'] = self._calculate_security_score(scan_results)
            
            # توليد التوصيات
            scan_results['recommendations'] = self._generate_recommendations(scan_results)
            
        except Exception as e:
            logger.error(f"خطأ في الفحص الأمني: {str(e)}")
            scan_results['error'] = str(e)
        
        return scan_results
    
    def _analyze_ssl(self, url: str) -> Dict[str, Any]:
        """تحليل شهادة SSL/TLS"""
        ssl_info = {
            'has_ssl': False,
            'certificate_valid': False,
            'certificate_details': {},
            'cipher_suite': '',
            'protocol_version': '',
            'security_level': 'Unknown',
            'warnings': []
        }
        
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                ssl_info['has_ssl'] = True
                
                # الحصول على معلومات الشهادة
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        cipher = ssock.cipher()
                        
                        ssl_info['certificate_valid'] = True
                        ssl_info['certificate_details'] = {
                            'subject': dict(x[0] for x in cert.get('subject', [])),
                            'issuer': dict(x[0] for x in cert.get('issuer', [])),
                            'version': cert.get('version'),
                            'serial_number': cert.get('serialNumber'),
                            'not_before': cert.get('notBefore'),
                            'not_after': cert.get('notAfter')
                        }
                        
                        if cipher:
                            ssl_info['cipher_suite'] = cipher[0]
                            ssl_info['protocol_version'] = cipher[1]
                            ssl_info['security_level'] = self._evaluate_cipher_security(cipher[0])
            else:
                ssl_info['warnings'].append('الموقع لا يستخدم HTTPS')
                
        except ssl.SSLError as e:
            ssl_info['warnings'].append(f'خطأ SSL: {str(e)}')
        except Exception as e:
            ssl_info['warnings'].append(f'خطأ في تحليل SSL: {str(e)}')
        
        return ssl_info
    
    def _analyze_security_headers(self, url: str) -> Dict[str, Any]:
        """تحليل رؤوس الأمان"""
        header_analysis = {
            'present_headers': {},
            'missing_headers': [],
            'security_score': 0,
            'warnings': []
        }
        
        try:
            response = self.session.head(url, timeout=10, verify=False)
            headers = response.headers
            
            # فحص الرؤوس الموجودة
            for header_name, description in self.security_headers.items():
                if header_name.lower() in [h.lower() for h in headers.keys()]:
                    header_value = headers.get(header_name, '')
                    header_analysis['present_headers'][header_name] = {
                        'value': header_value,
                        'description': description
                    }
                    header_analysis['security_score'] += 10
                else:
                    header_analysis['missing_headers'].append({
                        'name': header_name,
                        'description': description
                    })
            
            # فحص رؤوس خطيرة
            dangerous_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in dangerous_headers:
                if header in headers:
                    header_analysis['warnings'].append(
                        f'رأس خطير مكشوف: {header} = {headers[header]}'
                    )
            
        except Exception as e:
            header_analysis['warnings'].append(f'خطأ في تحليل الرؤوس: {str(e)}')
        
        return header_analysis
    
    def _scan_vulnerabilities(self, url: str) -> Dict[str, Any]:
        """فحص الثغرات الأمنية"""
        vuln_scan = {
            'sql_injection': {'found': False, 'details': []},
            'xss': {'found': False, 'details': []},
            'csrf': {'found': False, 'details': []},
            'directory_traversal': {'found': False, 'details': []},
            'information_disclosure': {'found': False, 'details': []},
            'overall_risk': 'Low'
        }
        
        try:
            # جلب محتوى الصفحة
            response = self.session.get(url, timeout=15, verify=False)
            content = response.text
            
            # فحص SQL Injection
            for pattern in self.vulnerability_patterns['sql_injection']:
                if re.search(pattern, content):
                    vuln_scan['sql_injection']['found'] = True
                    vuln_scan['sql_injection']['details'].append(f'نمط مشبوه: {pattern}')
            
            # فحص XSS
            for pattern in self.vulnerability_patterns['xss']:
                if re.search(pattern, content):
                    vuln_scan['xss']['found'] = True
                    vuln_scan['xss']['details'].append(f'نمط XSS: {pattern}')
            
            # فحص CSRF
            csrf_tokens = re.findall(r'(?i)csrf[_-]?token["\']?\s*[:=]\s*["\']?([^"\'>\s]+)', content)
            if not csrf_tokens:
                vuln_scan['csrf']['found'] = True
                vuln_scan['csrf']['details'].append('لا يوجد حماية CSRF')
            
            # فحص كشف المعلومات
            sensitive_info = [
                r'(?i)password\s*[:=]\s*["\']?[^"\'>\s]+',
                r'(?i)api[_-]?key\s*[:=]\s*["\']?[^"\'>\s]+',
                r'(?i)secret\s*[:=]\s*["\']?[^"\'>\s]+',
                r'(?i)token\s*[:=]\s*["\']?[^"\'>\s]+'
            ]
            
            for pattern in sensitive_info:
                matches = re.findall(pattern, content)
                if matches:
                    vuln_scan['information_disclosure']['found'] = True
                    vuln_scan['information_disclosure']['details'].extend(matches[:3])  # أول 3 نتائج فقط
            
            # تقييم المخاطر الإجمالية
            risk_score = 0
            for vuln_type, details in vuln_scan.items():
                if isinstance(details, dict) and details.get('found'):
                    risk_score += 1
            
            if risk_score >= 3:
                vuln_scan['overall_risk'] = 'High'
            elif risk_score >= 1:
                vuln_scan['overall_risk'] = 'Medium'
            else:
                vuln_scan['overall_risk'] = 'Low'
                
        except Exception as e:
            logger.error(f'خطأ في فحص الثغرات: {str(e)}')
        
        return vuln_scan
    
    def _analyze_content_security(self, url: str) -> Dict[str, Any]:
        """تحليل أمان المحتوى"""
        content_security = {
            'external_scripts': [],
            'external_stylesheets': [],
            'external_iframes': [],
            'forms_analysis': {},
            'cookies_analysis': {},
            'security_warnings': []
        }
        
        try:
            response = self.session.get(url, timeout=15, verify=False)
            content = response.text
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # فحص النصوص البرمجية الخارجية
            for script in soup.find_all('script', src=True):
                src = script.get('src')
                if src and (src.startswith('http') or src.startswith('//')):
                    content_security['external_scripts'].append(src)
            
            # فحص ملفات CSS الخارجية
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href')
                if href and (href.startswith('http') or href.startswith('//')):
                    content_security['external_stylesheets'].append(href)
            
            # فحص iframe الخارجية
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src')
                if src and (src.startswith('http') or src.startswith('//')):
                    content_security['external_iframes'].append(src)
            
            # تحليل النماذج
            forms = soup.find_all('form')
            content_security['forms_analysis'] = {
                'total_forms': len(forms),
                'secure_forms': 0,
                'insecure_forms': []
            }
            
            for form in forms:
                action = form.get('action', '')
                method = form.get('method', 'get').lower()
                
                if action.startswith('https://') or not action.startswith('http'):
                    content_security['forms_analysis']['secure_forms'] += 1
                else:
                    content_security['forms_analysis']['insecure_forms'].append({
                        'action': action,
                        'method': method
                    })
            
            # تحليل الكوكيز
            cookies = response.cookies
            content_security['cookies_analysis'] = {
                'total_cookies': len(cookies),
                'secure_cookies': 0,
                'httponly_cookies': 0,
                'samesite_cookies': 0
            }
            
            for cookie in cookies:
                if cookie.secure:
                    content_security['cookies_analysis']['secure_cookies'] += 1
                if 'HttpOnly' in str(cookie):
                    content_security['cookies_analysis']['httponly_cookies'] += 1
                if 'SameSite' in str(cookie):
                    content_security['cookies_analysis']['samesite_cookies'] += 1
            
        except Exception as e:
            content_security['security_warnings'].append(f'خطأ في تحليل المحتوى: {str(e)}')
        
        return content_security
    
    def _check_domain_reputation(self, url: str) -> Dict[str, Any]:
        """فحص سمعة النطاق"""
        reputation = {
            'domain': '',
            'is_malicious': False,
            'reputation_score': 100,
            'blacklist_status': [],
            'age_analysis': {},
            'warnings': []
        }
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            reputation['domain'] = domain
            
            # فحص القائمة السوداء المحلية
            if domain.lower() in self.malicious_domains:
                reputation['is_malicious'] = True
                reputation['reputation_score'] = 0
                reputation['blacklist_status'].append('قائمة سوداء محلية')
            
            # فحص أنماط النطاقات المشبوهة
            suspicious_patterns = [
                r'.*-.*-.*-.*',  # نطاقات بعدة شرطات
                r'.*\d{4,}.*',   # أرقام طويلة
                r'.*phish.*',    # كلمات مشبوهة
                r'.*fake.*',
                r'.*scam.*'
            ]
            
            for pattern in suspicious_patterns:
                if re.match(pattern, domain.lower()):
                    reputation['reputation_score'] -= 20
                    reputation['warnings'].append(f'نمط مشبوه في النطاق: {pattern}')
            
            # فحص طول النطاق (النطاقات الطويلة جداً مشبوهة)
            if len(domain) > 30:
                reputation['reputation_score'] -= 10
                reputation['warnings'].append('النطاق طويل جداً')
            
            # فحص امتدادات النطاق المشبوهة
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf']
            for tld in suspicious_tlds:
                if domain.endswith(tld):
                    reputation['reputation_score'] -= 15
                    reputation['warnings'].append(f'امتداد نطاق مشبوه: {tld}')
            
        except Exception as e:
            reputation['warnings'].append(f'خطأ في فحص السمعة: {str(e)}')
        
        return reputation
    
    def _evaluate_cipher_security(self, cipher_name: str) -> str:
        """تقييم مستوى أمان التشفير"""
        if not cipher_name:
            return 'Unknown'
        
        cipher_lower = cipher_name.lower()
        
        # تشفير قوي
        if any(strong in cipher_lower for strong in ['aes256', 'chacha20', 'aes-256']):
            return 'Strong'
        
        # تشفير متوسط
        elif any(medium in cipher_lower for medium in ['aes128', 'aes-128']):
            return 'Medium'
        
        # تشفير ضعيف
        elif any(weak in cipher_lower for weak in ['rc4', 'des', 'md5']):
            return 'Weak'
        
        return 'Medium'
    
    def _calculate_security_score(self, scan_results: Dict[str, Any]) -> int:
        """حساب النقاط الأمنية الإجمالية"""
        total_score = 0
        
        # نقاط SSL
        ssl_info = scan_results.get('ssl_analysis', {})
        if ssl_info.get('has_ssl'):
            total_score += 25
            if ssl_info.get('certificate_valid'):
                total_score += 15
            if ssl_info.get('security_level') == 'Strong':
                total_score += 10
        
        # نقاط الرؤوس الأمنية
        header_score = scan_results.get('header_analysis', {}).get('security_score', 0)
        total_score += min(header_score, 30)
        
        # خصم نقاط للثغرات
        vuln_scan = scan_results.get('vulnerability_scan', {})
        for vuln_type, details in vuln_scan.items():
            if isinstance(details, dict) and details.get('found'):
                total_score -= 10
        
        # نقاط سمعة النطاق
        reputation_score = scan_results.get('domain_reputation', {}).get('reputation_score', 100)
        total_score += int(reputation_score * 0.2)  # 20% من نقاط السمعة
        
        return max(0, min(100, total_score))
    
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """توليد توصيات الأمان"""
        recommendations = []
        
        # توصيات SSL
        ssl_info = scan_results.get('ssl_analysis', {})
        if not ssl_info.get('has_ssl'):
            recommendations.append('استخدم HTTPS لحماية البيانات المنقولة')
        elif ssl_info.get('security_level') == 'Weak':
            recommendations.append('قم بترقية تشفير SSL إلى معايير أقوى')
        
        # توصيات الرؤوس
        missing_headers = scan_results.get('header_analysis', {}).get('missing_headers', [])
        if missing_headers:
            recommendations.append(f'أضف رؤوس الأمان المفقودة: {len(missing_headers)} رأس')
        
        # توصيات الثغرات
        vuln_scan = scan_results.get('vulnerability_scan', {})
        if vuln_scan.get('sql_injection', {}).get('found'):
            recommendations.append('قم بحماية التطبيق من هجمات SQL Injection')
        if vuln_scan.get('xss', {}).get('found'):
            recommendations.append('نظف مدخلات المستخدم لمنع هجمات XSS')
        if vuln_scan.get('csrf', {}).get('found'):
            recommendations.append('أضف حماية CSRF للنماذج')
        
        # توصيات المحتوى
        content_analysis = scan_results.get('content_analysis', {})
        external_scripts = content_analysis.get('external_scripts', [])
        if len(external_scripts) > 5:
            recommendations.append('قلل من النصوص البرمجية الخارجية')
        
        if not recommendations:
            recommendations.append('الموقع يتبع ممارسات أمنية جيدة')
        
        return recommendations

class ThreatDetector:
    """كاشف التهديدات المتقدم"""
    
    def __init__(self):
        # قاعدة بيانات التهديدات
        self.threat_signatures = {
            'malware': [
                r'(?i)(malware|virus|trojan|backdoor)',
                r'(?i)(ransomware|spyware|adware)',
                r'(?i)(crypto.*miner|bitcoin.*mine)'
            ],
            'phishing': [
                r'(?i)(urgent.*action|account.*suspended)',
                r'(?i)(verify.*account|update.*payment)',
                r'(?i)(click.*here.*now|limited.*time)'
            ],
            'scam': [
                r'(?i)(congratulations.*winner|lottery.*winner)',
                r'(?i)(claim.*prize|free.*money)',
                r'(?i)(nigerian.*prince|inheritance.*claim)'
            ]
        }
        
        self.compiled_threats = {}
        for threat_type, patterns in self.threat_signatures.items():
            self.compiled_threats[threat_type] = [
                re.compile(pattern) for pattern in patterns
            ]
    
    def detect_threats(self, content: str, url: str = '') -> Dict[str, Any]:
        """كشف التهديدات في المحتوى"""
        threats = {
            'threats_found': [],
            'threat_score': 0,
            'content_analysis': {},
            'url_analysis': {}
        }
        
        try:
            # فحص المحتوى
            for threat_type, patterns in self.compiled_threats.items():
                matches = []
                for pattern in patterns:
                    found = pattern.findall(content)
                    matches.extend(found)
                
                if matches:
                    threats['threats_found'].append({
                        'type': threat_type,
                        'matches': matches[:5],  # أول 5 نتائج
                        'count': len(matches)
                    })
                    threats['threat_score'] += len(matches) * 10
            
            # فحص الرابط
            if url:
                url_threats = self._analyze_url_threats(url)
                threats['url_analysis'] = url_threats
                threats['threat_score'] += url_threats.get('score', 0)
            
            # تصنيف مستوى التهديد
            if threats['threat_score'] >= 50:
                threats['threat_level'] = 'High'
            elif threats['threat_score'] >= 20:
                threats['threat_level'] = 'Medium'
            else:
                threats['threat_level'] = 'Low'
                
        except Exception as e:
            logger.error(f'خطأ في كشف التهديدات: {str(e)}')
        
        return threats
    
    def _analyze_url_threats(self, url: str) -> Dict[str, Any]:
        """تحليل التهديدات في الرابط"""
        url_analysis = {
            'suspicious_patterns': [],
            'score': 0,
            'warnings': []
        }
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # أنماط مشبوهة في النطاق
            suspicious_domain_patterns = [
                r'.*-.*-.*',      # عدة شرطات
                r'.*\d{5,}.*',    # أرقام طويلة
                r'.*\.tk$|.*\.ml$|.*\.ga$',  # امتدادات مشبوهة
            ]
            
            for pattern in suspicious_domain_patterns:
                if re.match(pattern, domain):
                    url_analysis['suspicious_patterns'].append(f'نطاق مشبوه: {pattern}')
                    url_analysis['score'] += 10
            
            # أنماط مشبوهة في المسار
            suspicious_path_patterns = [
                r'.*/download/.*\.exe',
                r'.*/admin/.*',
                r'.*/phishing/.*',
            ]
            
            for pattern in suspicious_path_patterns:
                if re.match(pattern, path):
                    url_analysis['suspicious_patterns'].append(f'مسار مشبوه: {pattern}')
                    url_analysis['score'] += 15
            
        except Exception as e:
            url_analysis['warnings'].append(f'خطأ في تحليل الرابط: {str(e)}')
        
        return url_analysis