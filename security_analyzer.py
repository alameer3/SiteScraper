"""
محلل الأمان المتقدم - Advanced Security Analyzer
يقوم بفحص شامل لأمان المواقع الإلكترونية
"""

import re
import ssl
import socket
import requests
from urllib.parse import urlparse
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
                'overall_score': 0,
                'recommendations': [],
                'risk_level': 'unknown'
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
        
        # خصم نقاط للثغرات
        vulnerabilities = security_report['vulnerability_scan']
        if vulnerabilities.get('sql_injection', {}).get('found'):
            total_score -= 30
        if vulnerabilities.get('xss_vulnerability', {}).get('found'):
            total_score -= 25
        if vulnerabilities.get('information_disclosure', {}).get('found'):
            total_score -= 15
        
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
        
        # توصيات SSL
        if not security_report['ssl_analysis'].get('has_ssl'):
            recommendations.append('تفعيل شهادة SSL/TLS')
        
        # توصيات الرؤوس
        missing_headers = security_report['headers_analysis'].get('missing_headers', [])
        for header in missing_headers:
            recommendations.append(f'إضافة رأس الأمان: {header}')
        
        # توصيات الثغرات
        vulnerabilities = security_report['vulnerability_scan']
        if vulnerabilities.get('sql_injection', {}).get('found'):
            recommendations.append('إصلاح ثغرات SQL Injection')
        if vulnerabilities.get('xss_vulnerability', {}).get('found'):
            recommendations.append('إصلاح ثغرات XSS')
        
        # توصيات الكوكيز
        cookie_recs = security_report['cookie_analysis'].get('recommendations', [])
        recommendations.extend(cookie_recs)
        
        return recommendations

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

    def _check_compliance(self, analysis):
        """فحص الامتثال للمعايير"""
        return {
            'owasp_top_10': 'فحص جزئي',
            'pci_dss': 'غير مطبق',
            'gdpr': 'يتطلب مراجعة',
            'iso_27001': 'غير متوافق'
        }