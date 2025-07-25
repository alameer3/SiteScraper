"""
محلل الأمان المتقدم - Advanced Security Analyzer
يقوم بفحص شامل لأمان المواقع الإلكترونية
"""

import re
import ssl
import socket
import requests
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging

class SecurityAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # أنماط الثغرات الأمنية الشائعة
        self.vulnerability_patterns = {
            'sql_injection': [
                r'error in your sql syntax',
                r'mysql_fetch_array',
                r'ora-\d{5}',
                r'postgresql query failed'
            ],
            'xss_indicators': [
                r'<script[^>]*>',
                r'javascript:',
                r'onerror\s*=',
                r'onload\s*='
            ],
            'sensitive_files': [
                r'\.env',
                r'config\.php',
                r'wp-config\.php',
                r'\.htaccess'
            ],
            'information_disclosure': [
                r'server:\s*apache',
                r'x-powered-by',
                r'php/\d+\.\d+',
                r'asp\.net'
            ]
        }
        
        # رؤوس الأمان المطلوبة
        self.security_headers = [
            'Content-Security-Policy',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Referrer-Policy',
            'Permissions-Policy'
        ]

    def analyze_security(self, url):
        """تحليل أمان شامل للموقع"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            security_report = {
                'url': url,
                'domain': domain,
                'ssl_analysis': self._analyze_ssl(domain),
                'headers_analysis': self._analyze_security_headers(url),
                'vulnerability_scan': self._scan_vulnerabilities(url),
                'cookie_analysis': self._analyze_cookies(url),
                'content_analysis': self._analyze_content_security(url),
                'information_leak_scan': self._scan_information_leaks(url),
                'directory_traversal_scan': self._scan_directory_traversal(url),
                'injection_scan': self._scan_injection_vulnerabilities(url),
                'exposed_files_scan': self._scan_exposed_files(url),
                'admin_panel_detection': self._detect_admin_panels(url),
                'backup_files_scan': self._scan_backup_files(url),
                'overall_score': 0,
                'recommendations': [],
                'risk_level': 'unknown',
                'critical_vulnerabilities': [],
                'information_disclosure': []
            }
            
            # حساب النقاط الإجمالية
            security_report['overall_score'] = self._calculate_security_score(security_report)
            security_report['risk_level'] = self._determine_risk_level(security_report['overall_score'])
            security_report['recommendations'] = self._generate_recommendations(security_report)
            
            return security_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الأمان: {e}")
            return {'error': str(e)}

    def _analyze_ssl(self, domain):
        """تحليل شهادة SSL"""
        ssl_info = {
            'has_ssl': False,
            'certificate_valid': False,
            'certificate_issuer': '',
            'expiry_date': '',
            'protocol_version': '',
            'cipher_suite': '',
            'vulnerability_checks': {}
        }
        
        try:
            # فحص اتصال SSL
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    ssl_info['has_ssl'] = True
                    cert = ssock.getpeercert()
                    
                    if cert:
                        ssl_info['certificate_valid'] = True
                        ssl_info['certificate_issuer'] = cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
                        ssl_info['expiry_date'] = cert.get('notAfter', 'Unknown')
                    
                    ssl_info['protocol_version'] = ssock.version()
                    ssl_info['cipher_suite'] = ssock.cipher()[0] if ssock.cipher() else 'Unknown'
                    
        except Exception as e:
            logging.error(f"خطأ في تحليل SSL: {e}")
            ssl_info['error'] = str(e)
        
        return ssl_info

    def _analyze_security_headers(self, url):
        """تحليل رؤوس الأمان"""
        headers_analysis = {
            'present_headers': {},
            'missing_headers': [],
            'header_scores': {},
            'total_score': 0
        }
        
        try:
            response = self.session.get(url, timeout=10)
            headers = response.headers
            
            for header in self.security_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    headers_analysis['present_headers'][header] = headers.get(header, '')
                    headers_analysis['header_scores'][header] = self._score_header(header, headers.get(header, ''))
                else:
                    headers_analysis['missing_headers'].append(header)
                    headers_analysis['header_scores'][header] = 0
            
            headers_analysis['total_score'] = sum(headers_analysis['header_scores'].values())
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الرؤوس: {e}")
            headers_analysis['error'] = str(e)
        
        return headers_analysis

    def _scan_vulnerabilities(self, url):
        """فحص الثغرات الأمنية"""
        vulnerability_report = {
            'sql_injection': {'found': False, 'indicators': []},
            'xss_vulnerability': {'found': False, 'indicators': []},
            'sensitive_files': {'found': False, 'files': []},
            'information_disclosure': {'found': False, 'leaked_info': []}
        }
        
        try:
            response = self.session.get(url, timeout=10)
            content = response.text.lower()
            headers = str(response.headers).lower()
            
            # فحص SQL Injection
            for pattern in self.vulnerability_patterns['sql_injection']:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerability_report['sql_injection']['found'] = True
                    vulnerability_report['sql_injection']['indicators'].append(pattern)
            
            # فحص XSS
            for pattern in self.vulnerability_patterns['xss_indicators']:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerability_report['xss_vulnerability']['found'] = True
                    vulnerability_report['xss_vulnerability']['indicators'].append(pattern)
            
            # فحص تسريب المعلومات
            for pattern in self.vulnerability_patterns['information_disclosure']:
                if re.search(pattern, headers, re.IGNORECASE):
                    vulnerability_report['information_disclosure']['found'] = True
                    vulnerability_report['information_disclosure']['leaked_info'].append(pattern)
            
        except Exception as e:
            logging.error(f"خطأ في فحص الثغرات: {e}")
            vulnerability_report['error'] = str(e)
        
        return vulnerability_report

    def _analyze_cookies(self, url):
        """تحليل أمان الكوكيز"""
        cookie_analysis = {
            'total_cookies': 0,
            'secure_cookies': 0,
            'httponly_cookies': 0,
            'samesite_cookies': 0,
            'insecure_cookies': [],
            'recommendations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            cookies = response.cookies
            
            cookie_analysis['total_cookies'] = len(cookies)
            
            for cookie in cookies:
                if cookie.secure:
                    cookie_analysis['secure_cookies'] += 1
                else:
                    cookie_analysis['insecure_cookies'].append(cookie.name)
                
                if hasattr(cookie, 'has_nonstandard_attr') and cookie.has_nonstandard_attr('HttpOnly'):
                    cookie_analysis['httponly_cookies'] += 1
                
                if hasattr(cookie, 'has_nonstandard_attr') and cookie.has_nonstandard_attr('SameSite'):
                    cookie_analysis['samesite_cookies'] += 1
            
            # توليد التوصيات
            if cookie_analysis['insecure_cookies']:
                cookie_analysis['recommendations'].append('تأمين الكوكيز غير المحمية')
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الكوكيز: {e}")
            cookie_analysis['error'] = str(e)
        
        return cookie_analysis

    def _analyze_content_security(self, url):
        """تحليل أمان المحتوى"""
        content_security = {
            'mixed_content': False,
            'external_resources': [],
            'inline_scripts': 0,
            'eval_usage': False,
            'dangerous_functions': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            content = response.text
            
            # فحص المحتوى المختلط
            if 'http://' in content and url.startswith('https://'):
                content_security['mixed_content'] = True
            
            # عد النصوص المدمجة
            content_security['inline_scripts'] = len(re.findall(r'<script[^>]*>', content, re.IGNORECASE))
            
            # فحص استخدام eval
            if 'eval(' in content:
                content_security['eval_usage'] = True
            
            # فحص الوظائف الخطيرة
            dangerous_patterns = ['innerHTML', 'document.write', 'setTimeout', 'setInterval']
            for pattern in dangerous_patterns:
                if pattern in content:
                    content_security['dangerous_functions'].append(pattern)
            
        except Exception as e:
            logging.error(f"خطأ في تحليل أمان المحتوى: {e}")
            content_security['error'] = str(e)
        
        return content_security

    def _score_header(self, header, value):
        """تقييم رأس الأمان"""
        scoring = {
            'Content-Security-Policy': 25,
            'X-Content-Type-Options': 10,
            'X-Frame-Options': 15,
            'X-XSS-Protection': 10,
            'Strict-Transport-Security': 20,
            'Referrer-Policy': 10,
            'Permissions-Policy': 10
        }
        
        base_score = scoring.get(header, 5)
        
        # تقييم إضافي بناءً على القيمة
        if header == 'Content-Security-Policy' and len(value) > 50:
            return base_score
        elif header == 'Strict-Transport-Security' and 'max-age' in value:
            return base_score
        elif value:
            return base_score
        
        return 0

    def _calculate_security_score(self, security_report):
        """حساب النقاط الإجمالية للأمان"""
        total_score = 0
        
        # نقاط SSL
        if security_report['ssl_analysis'].get('has_ssl'):
            total_score += 30
        if security_report['ssl_analysis'].get('certificate_valid'):
            total_score += 20
        
        # نقاط الرؤوس
        total_score += security_report['headers_analysis'].get('total_score', 0)
        
        # خصم نقاط للثغرات التقليدية
        vulnerabilities = security_report['vulnerability_scan']
        if vulnerabilities.get('sql_injection', {}).get('found'):
            total_score -= 30
        if vulnerabilities.get('xss_vulnerability', {}).get('found'):
            total_score -= 25
        if vulnerabilities.get('information_disclosure', {}).get('found'):
            total_score -= 15
        
        # خصم نقاط للثغرات الجديدة
        injection_scan = security_report.get('injection_scan', {})
        if injection_scan.get('sql_injection', {}).get('vulnerable'):
            total_score -= 35  # ثغرة خطيرة جداً
        if injection_scan.get('xss_injection', {}).get('vulnerable'):
            total_score -= 25
        if injection_scan.get('command_injection', {}).get('vulnerable'):
            total_score -= 40  # ثغرة خطيرة جداً
        
        # خصم نقاط للملفات المكشوفة
        exposed_files = security_report.get('exposed_files_scan', {})
        if exposed_files.get('config_files'):
            total_score -= 20
        if exposed_files.get('database_files'):
            total_score -= 30
        if exposed_files.get('backup_files'):
            total_score -= 15
        
        # خصم نقاط لتسريب المعلومات
        info_leaks = security_report.get('information_leak_scan', {})
        if info_leaks.get('api_keys'):
            total_score -= 35
        if info_leaks.get('database_errors'):
            total_score -= 20
        if info_leaks.get('debug_info'):
            total_score -= 15
        
        # خصم نقاط للوحات الإدارة المكشوفة
        admin_panels = security_report.get('admin_panel_detection', {})
        if admin_panels.get('found_panels'):
            total_score -= 10
        
        return max(0, min(100, total_score))

    def _determine_risk_level(self, score):
        """تحديد مستوى المخاطر"""
        if score >= 80:
            return 'منخفض'
        elif score >= 60:
            return 'متوسط'
        elif score >= 40:
            return 'عالي'
        else:
            return 'خطير'

    def _generate_recommendations(self, security_report):
        """توليد التوصيات الأمنية"""
        recommendations = []
        critical_recommendations = []
        
        # توصيات SSL
        if not security_report['ssl_analysis'].get('has_ssl'):
            critical_recommendations.append('🔴 CRITICAL: تفعيل شهادة SSL/TLS فوراً')
        
        # توصيات الرؤوس
        missing_headers = security_report['headers_analysis'].get('missing_headers', [])
        for header in missing_headers:
            recommendations.append(f'إضافة رأس الأمان: {header}')
        
        # توصيات الثغرات الخطيرة
        injection_scan = security_report.get('injection_scan', {})
        if injection_scan.get('sql_injection', {}).get('vulnerable'):
            critical_recommendations.append('🔴 CRITICAL: إصلاح ثغرات SQL Injection فوراً - خطر اختراق قاعدة البيانات')
        if injection_scan.get('command_injection', {}).get('vulnerable'):
            critical_recommendations.append('🔴 CRITICAL: إصلاح ثغرات Command Injection فوراً - خطر السيطرة على الخادم')
        if injection_scan.get('xss_injection', {}).get('vulnerable'):
            recommendations.append('🟠 HIGH: إصلاح ثغرات XSS - خطر سرقة بيانات المستخدمين')
        
        # توصيات الملفات المكشوفة
        exposed_files = security_report.get('exposed_files_scan', {})
        if exposed_files.get('config_files'):
            critical_recommendations.append('🔴 CRITICAL: حماية ملفات التكوين - تحتوي على معلومات حساسة')
        if exposed_files.get('database_files'):
            critical_recommendations.append('🔴 CRITICAL: حماية ملفات قاعدة البيانات فوراً')
        if exposed_files.get('backup_files'):
            recommendations.append('🟠 HIGH: حماية ملفات النسخ الاحتياطية')
        
        # توصيات تسريب المعلومات
        info_leaks = security_report.get('information_leak_scan', {})
        if info_leaks.get('api_keys'):
            critical_recommendations.append('🔴 CRITICAL: تغيير مفاتيح API المكشوفة فوراً')
        if info_leaks.get('database_errors'):
            recommendations.append('🟠 HIGH: إخفاء رسائل أخطاء قاعدة البيانات')
        if info_leaks.get('debug_info'):
            recommendations.append('🟡 MEDIUM: تعطيل معلومات التصحيح في الإنتاج')
        if info_leaks.get('email_addresses'):
            recommendations.append('🟡 MEDIUM: حماية عناوين البريد الإلكتروني من البوتات')
        
        # توصيات لوحات الإدارة
        admin_panels = security_report.get('admin_panel_detection', {})
        if admin_panels.get('found_panels'):
            recommendations.append('🟠 HIGH: حماية لوحات الإدارة بمصادقة قوية')
        if admin_panels.get('login_pages'):
            recommendations.append('🟡 MEDIUM: تأمين صفحات تسجيل الدخول')
        
        # توصيات Directory Traversal
        traversal_scan = security_report.get('directory_traversal_scan', {})
        if traversal_scan.get('vulnerable_parameters'):
            critical_recommendations.append('🔴 CRITICAL: إصلاح ثغرات Directory Traversal فوراً')
        
        # توصيات الكوكيز
        cookie_recs = security_report['cookie_analysis'].get('recommendations', [])
        recommendations.extend(cookie_recs)
        
        # دمج التوصيات الحرجة أولاً
        all_recommendations = critical_recommendations + recommendations
        
        # إضافة توصيات عامة
        if len(critical_recommendations) > 0:
            all_recommendations.append('🛡️ نوصي بإجراء مراجعة أمنية شاملة للموقع')
            all_recommendations.append('📋 توثيق جميع الثغرات المكتشفة وخطة معالجتها')
            all_recommendations.append('🔄 إجراء اختبارات أمنية دورية')
        
        return all_recommendations

    def generate_security_report(self, analysis_results):
        """توليد تقرير أمان مفصل"""
        report = {
            'executive_summary': self._create_executive_summary(analysis_results),
            'detailed_findings': analysis_results,
            'risk_matrix': self._create_risk_matrix(analysis_results),
            'remediation_plan': self._create_remediation_plan(analysis_results),
            'compliance_check': self._check_compliance(analysis_results)
        }
        return report

    def _create_executive_summary(self, analysis):
        """إنشاء ملخص تنفيذي"""
        score = analysis.get('overall_score', 0)
        risk = analysis.get('risk_level', 'unknown')
        
        summary = {
            'overall_security_posture': f'النقاط: {score}/100 - المخاطر: {risk}',
            'critical_issues': len([r for r in analysis.get('recommendations', []) if 'خطير' in r or 'ثغرة' in r]),
            'compliance_status': 'متوافق جزئياً' if score > 60 else 'غير متوافق',
            'immediate_actions': analysis.get('recommendations', [])[:3]
        }
        return summary

    def _create_risk_matrix(self, analysis):
        """إنشاء مصفوفة المخاطر"""
        return {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': [],
            'informational': []
        }

    def _create_remediation_plan(self, analysis):
        """إنشاء خطة المعالجة"""
        return {
            'immediate': analysis.get('recommendations', [])[:2],
            'short_term': analysis.get('recommendations', [])[2:5],
            'long_term': analysis.get('recommendations', [])[5:]
        }

    def _scan_information_leaks(self, url):
        """فحص تسريب المعلومات الحساسة"""
        info_leaks = {
            'database_errors': [],
            'debug_info': [],
            'email_addresses': [],
            'phone_numbers': [],
            'api_keys': [],
            'internal_paths': [],
            'version_disclosure': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            content = response.text
            headers = response.headers
            
            # البحث عن أخطاء قواعد البيانات
            db_error_patterns = [
                r'mysql_connect\(\)',
                r'ORA-\d{5}',
                r'Microsoft OLE DB Provider',
                r'PostgreSQL query failed',
                r'sqlite3\.OperationalError',
                r'Warning: mysql_',
                r'MySQLSyntaxErrorException'
            ]
            
            for pattern in db_error_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    info_leaks['database_errors'].extend(matches)
            
            # البحث عن معلومات التصحيح
            debug_patterns = [
                r'Notice: Undefined',
                r'Warning: include',
                r'Fatal error:',
                r'Stack trace:',
                r'Call Stack:',
                r'DEBUG = True',
                r'SQLSTATE\[\d+\]'
            ]
            
            for pattern in debug_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    info_leaks['debug_info'].extend(matches)
            
            # البحث عن عناوين البريد الإلكتروني
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, content)
            info_leaks['email_addresses'] = list(set(emails))
            
            # البحث عن أرقام الهواتف
            phone_patterns = [
                r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                r'\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}',
                r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
            ]
            
            for pattern in phone_patterns:
                phones = re.findall(pattern, content)
                info_leaks['phone_numbers'].extend(phones)
            
            # البحث عن مفاتيح API
            api_key_patterns = [
                r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                r'secret[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                r'access[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                r'bearer\s+([a-zA-Z0-9_-]{20,})',
                r'AKIA[0-9A-Z]{16}'  # AWS Access Key
            ]
            
            for pattern in api_key_patterns:
                keys = re.findall(pattern, content, re.IGNORECASE)
                info_leaks['api_keys'].extend(keys)
            
            # البحث عن مسارات داخلية
            path_patterns = [
                r'[C-Z]:\\[^"<>|]*',  # Windows paths
                r'/home/[^/\s"<>|]+',  # Unix home paths
                r'/var/[^/\s"<>|]+',   # Unix var paths
                r'/etc/[^/\s"<>|]+',   # Unix etc paths
                r'/usr/[^/\s"<>|]+'    # Unix usr paths
            ]
            
            for pattern in path_patterns:
                paths = re.findall(pattern, content)
                info_leaks['internal_paths'].extend(paths)
            
            # البحث عن إفصاح الإصدارات
            version_patterns = [
                r'Apache/[\d.]+',
                r'nginx/[\d.]+',
                r'PHP/[\d.]+',
                r'Python/[\d.]+',
                r'jQuery v[\d.]+',
                r'WordPress [\d.]+'
            ]
            
            version_content = content + str(headers)
            for pattern in version_patterns:
                versions = re.findall(pattern, version_content, re.IGNORECASE)
                info_leaks['version_disclosure'].extend(versions)
            
        except Exception as e:
            logging.error(f"خطأ في فحص تسريب المعلومات: {e}")
        
        return info_leaks
    
    def _scan_directory_traversal(self, url):
        """فحص ثغرات Directory Traversal"""
        traversal_scan = {
            'vulnerable_parameters': [],
            'test_results': [],
            'payloads_tested': 0
        }
        
        try:
            # قائمة payloads لاختبار Directory Traversal
            payloads = [
                '../../../etc/passwd',
                '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
                '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
                '....//....//....//etc/passwd',
                '..%252f..%252f..%252fetc%252fpasswd'
            ]
            
            parsed_url = urlparse(url)
            
            # اختبار المعاملات المحتملة
            test_params = ['file', 'path', 'page', 'include', 'doc', 'template']
            
            for param in test_params:
                for payload in payloads:
                    test_url = f"{url}?{param}={payload}"
                    try:
                        response = self.session.get(test_url, timeout=5)
                        traversal_scan['payloads_tested'] += 1
                        
                        # فحص الاستجابة بحثاً عن علامات النجاح
                        if any(indicator in response.text.lower() for indicator in [
                            'root:x:', 'bin/bash', 'etc/passwd',
                            '[boot loader]', 'microsoft windows'
                        ]):
                            traversal_scan['vulnerable_parameters'].append({
                                'parameter': param,
                                'payload': payload,
                                'url': test_url,
                                'response_size': len(response.content)
                            })
                            
                    except Exception:
                        continue
                        
        except Exception as e:
            logging.error(f"خطأ في فحص Directory Traversal: {e}")
        
        return traversal_scan
    
    def _scan_injection_vulnerabilities(self, url):
        """فحص ثغرات الحقن المختلفة"""
        injection_scan = {
            'sql_injection': {'vulnerable': False, 'details': []},
            'xss_injection': {'vulnerable': False, 'details': []},
            'command_injection': {'vulnerable': False, 'details': []},
            'ldap_injection': {'vulnerable': False, 'details': []},
            'xxe_injection': {'vulnerable': False, 'details': []}
        }
        
        try:
            # SQL Injection payloads
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT NULL, NULL, NULL --",
                "1' AND SLEEP(5) --",
                "' OR BENCHMARK(1000000,MD5(1)) --"
            ]
            
            # XSS payloads
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "';alert('XSS');//",
                "<svg onload=alert('XSS')>"
            ]
            
            # Command Injection payloads
            cmd_payloads = [
                "; cat /etc/passwd",
                "| whoami",
                "&& dir",
                "; ls -la",
                "| id"
            ]
            
            test_params = ['q', 'search', 'id', 'user', 'name', 'cmd']
            
            for param in test_params:
                # اختبار SQL Injection
                for payload in sql_payloads:
                    test_url = f"{url}?{param}={payload}"
                    try:
                        response = self.session.get(test_url, timeout=10)
                        
                        # فحص علامات SQL Injection
                        if any(error in response.text.lower() for error in [
                            'sql syntax', 'mysql_fetch', 'ora-', 'postgresql',
                            'sqlite_step', 'microsoft jet database'
                        ]):
                            injection_scan['sql_injection']['vulnerable'] = True
                            injection_scan['sql_injection']['details'].append({
                                'parameter': param,
                                'payload': payload,
                                'url': test_url
                            })
                    except Exception:
                        continue
                
                # اختبار XSS
                for payload in xss_payloads:
                    test_url = f"{url}?{param}={payload}"
                    try:
                        response = self.session.get(test_url, timeout=5)
                        
                        if payload in response.text:
                            injection_scan['xss_injection']['vulnerable'] = True
                            injection_scan['xss_injection']['details'].append({
                                'parameter': param,
                                'payload': payload,
                                'url': test_url
                            })
                    except Exception:
                        continue
                
                # اختبار Command Injection
                for payload in cmd_payloads:
                    test_url = f"{url}?{param}={payload}"
                    try:
                        start_time = time.time()
                        response = self.session.get(test_url, timeout=10)
                        response_time = time.time() - start_time
                        
                        # فحص التأخير المشبوه أو نتائج الأوامر
                        if (response_time > 5 or 
                            any(indicator in response.text.lower() for indicator in [
                                'uid=', 'gid=', 'root:', 'administrator',
                                'volume in drive', 'directory of'
                            ])):
                            injection_scan['command_injection']['vulnerable'] = True
                            injection_scan['command_injection']['details'].append({
                                'parameter': param,
                                'payload': payload,
                                'url': test_url,
                                'response_time': response_time
                            })
                    except Exception:
                        continue
                        
        except Exception as e:
            logging.error(f"خطأ في فحص ثغرات الحقن: {e}")
        
        return injection_scan
    
    def _scan_exposed_files(self, url):
        """فحص الملفات المكشوفة والحساسة"""
        exposed_files = {
            'found_files': [],
            'backup_files': [],
            'config_files': [],
            'log_files': [],
            'database_files': []
        }
        
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # قائمة الملفات الحساسة للفحص
            sensitive_files = [
                '.env',
                'config.php',
                'wp-config.php',
                '.htaccess',
                'web.config',
                'robots.txt',
                'sitemap.xml',
                'phpinfo.php',
                'info.php',
                'test.php',
                'admin.php',
                'login.php',
                'backup.sql',
                'database.sql',
                'dump.sql',
                '.git/config',
                '.svn/entries',
                'composer.json',
                'package.json',
                'yarn.lock',
                'Gemfile',
                'requirements.txt',
                'error.log',
                'access.log',
                'debug.log',
                'application.log'
            ]
            
            # مجلدات إضافية للفحص
            directories = ['', 'admin/', 'backup/', 'config/', 'includes/', 'logs/']
            
            for directory in directories:
                for filename in sensitive_files:
                    file_url = urljoin(base_url, directory + filename)
                    try:
                        response = self.session.head(file_url, timeout=5)
                        
                        if response.status_code == 200:
                            file_info = {
                                'url': file_url,
                                'status_code': response.status_code,
                                'content_type': response.headers.get('Content-Type', ''),
                                'size': response.headers.get('Content-Length', 'Unknown')
                            }
                            
                            exposed_files['found_files'].append(file_info)
                            
                            # تصنيف الملفات
                            if any(ext in filename for ext in ['.bak', '.backup', '.old', '.orig']):
                                exposed_files['backup_files'].append(file_info)
                            elif any(name in filename for name in ['config', '.env', 'web.config']):
                                exposed_files['config_files'].append(file_info)
                            elif any(ext in filename for ext in ['.log', 'error', 'access']):
                                exposed_files['log_files'].append(file_info)
                            elif any(ext in filename for ext in ['.sql', '.db', '.sqlite']):
                                exposed_files['database_files'].append(file_info)
                                
                    except Exception:
                        continue
                        
        except Exception as e:
            logging.error(f"خطأ في فحص الملفات المكشوفة: {e}")
        
        return exposed_files
    
    def _detect_admin_panels(self, url):
        """اكتشاف لوحات الإدارة"""
        admin_detection = {
            'found_panels': [],
            'potential_panels': [],
            'login_pages': []
        }
        
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # مسارات لوحات الإدارة الشائعة
            admin_paths = [
                'admin/',
                'administrator/',
                'admin.php',
                'login.php',
                'wp-admin/',
                'wp-login.php',
                'cpanel/',
                'control/',
                'manage/',
                'management/',
                'manager/',
                'adminpanel/',
                'admin_area/',
                'admin-area/',
                'admincontrol/',
                'admin-control/',
                'admin_login/',
                'admin-login/',
                'adminlogin/',
                'controlpanel/',
                'control-panel/',
                'cp/',
                'adm/',
                'account/',
                'user/',
                'users/',
                'member/',
                'members/',
                'my-account/',
                'myaccount/',
                'user-login/',
                'userlogin/',
                'signin/',
                'sign-in/',
                'log-in/',
                'login/',
                'auth/',
                'authenticate/',
                'dashboard/',
                'admin-dashboard/',
                'admindashboard/'
            ]
            
            for path in admin_paths:
                admin_url = urljoin(base_url, path)
                try:
                    response = self.session.get(admin_url, timeout=5)
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # فحص علامات لوحة الإدارة
                        admin_indicators = [
                            'admin panel', 'administration', 'control panel',
                            'dashboard', 'login', 'username', 'password',
                            'sign in', 'log in', 'authentication'
                        ]
                        
                        if any(indicator in content for indicator in admin_indicators):
                            panel_info = {
                                'url': admin_url,
                                'title': self._extract_title(response.text),
                                'status_code': response.status_code,
                                'indicators_found': [ind for ind in admin_indicators if ind in content]
                            }
                            
                            # تحديد نوع اللوحة
                            if any(strong_indicator in content for strong_indicator in ['admin panel', 'administration']):
                                admin_detection['found_panels'].append(panel_info)
                            elif any(login_indicator in content for login_indicator in ['login', 'username', 'password']):
                                admin_detection['login_pages'].append(panel_info)
                            else:
                                admin_detection['potential_panels'].append(panel_info)
                                
                except Exception:
                    continue
                    
        except Exception as e:
            logging.error(f"خطأ في اكتشاف لوحات الإدارة: {e}")
        
        return admin_detection
    
    def _scan_backup_files(self, url):
        """فحص ملفات النسخ الاحتياطية"""
        backup_scan = {
            'found_backups': [],
            'suspicious_files': [],
            'archive_files': []
        }
        
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            domain_name = parsed_url.netloc.replace('www.', '').replace('.', '_')
            
            # امتدادات ملفات النسخ الاحتياطية
            backup_extensions = [
                '.bak', '.backup', '.old', '.orig', '.copy', '.tmp',
                '.zip', '.rar', '.tar', '.gz', '.tar.gz', '.7z',
                '.sql', '.dump', '.db'
            ]
            
            # أسماء ملفات مشتبه بها
            backup_names = [
                'backup',
                'database',
                'db',
                'dump',
                'export',
                'data',
                'site',
                'website',
                'www',
                'web',
                domain_name,
                'full',
                'complete',
                'archive'
            ]
            
            # اختبار تركيبات مختلفة
            for name in backup_names:
                for ext in backup_extensions:
                    backup_file = f"{name}{ext}"
                    backup_url = urljoin(base_url, backup_file)
                    
                    try:
                        response = self.session.head(backup_url, timeout=5)
                        
                        if response.status_code == 200:
                            file_info = {
                                'url': backup_url,
                                'filename': backup_file,
                                'size': response.headers.get('Content-Length', 'Unknown'),
                                'content_type': response.headers.get('Content-Type', ''),
                                'last_modified': response.headers.get('Last-Modified', '')
                            }
                            
                            if ext in ['.zip', '.rar', '.tar', '.gz', '.tar.gz', '.7z']:
                                backup_scan['archive_files'].append(file_info)
                            elif ext in ['.sql', '.dump', '.db']:
                                backup_scan['found_backups'].append(file_info)
                            else:
                                backup_scan['suspicious_files'].append(file_info)
                                
                    except Exception:
                        continue
                        
        except Exception as e:
            logging.error(f"خطأ في فحص ملفات النسخ الاحتياطية: {e}")
        
        return backup_scan
    
    def _extract_title(self, html_content):
        """استخراج عنوان الصفحة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.get_text().strip() if title_tag else 'No Title'
        except Exception:
            return 'Unknown'
    
    def _check_compliance(self, analysis):
        """فحص الامتثال للمعايير"""
        return {
            'owasp_top_10': 'فحص جزئي',
            'pci_dss': 'غير مطبق',
            'gdpr': 'يتطلب مراجعة',
            'iso_27001': 'غير متوافق'
        }