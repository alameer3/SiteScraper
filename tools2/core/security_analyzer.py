"""
محلل الأمان المتطور
Advanced Security Analyzer
"""

import ssl
import socket
import re
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, Tag
from .config import ExtractionConfig
from .session_manager import SessionManager


class SecurityAnalyzer:
    """محلل أمان شامل للمواقع"""
    
    def __init__(self, config: ExtractionConfig, session_manager: SessionManager):
        self.config = config
        self.session = session_manager
        
    def analyze_security(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """تحليل أمان شامل للموقع"""
        
        security_analysis = {
            'ssl_analysis': self._analyze_ssl(url),
            'headers_analysis': self._analyze_security_headers(response),
            'content_analysis': self._analyze_content_security(soup),
            'form_analysis': self._analyze_forms_security(soup),
            'vulnerability_scan': self._scan_common_vulnerabilities(soup, response.text),
            'privacy_analysis': self._analyze_privacy_features(soup),
            'security_score': None
        }
        
        # حساب النقاط الأمنية
        security_analysis['security_score'] = self._calculate_security_score(security_analysis)
        
        return security_analysis
    
    def _analyze_ssl(self, url: str) -> Dict[str, Any]:
        """تحليل شهادة SSL"""
        parsed_url = urlparse(url)
        
        if parsed_url.scheme != 'https':
            return {
                'enabled': False,
                'grade': 'F',
                'issues': ['الموقع لا يستخدم HTTPS'],
                'recommendations': ['تفعيل HTTPS لحماية البيانات']
            }
        
        try:
            hostname = parsed_url.netloc
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
            
            # تحليل الشهادة
            cert_analysis = self._analyze_certificate(cert)
            
            # تحليل التشفير
            cipher_analysis = self._analyze_cipher(cipher, version)
            
            return {
                'enabled': True,
                'certificate': cert_analysis,
                'cipher': cipher_analysis,
                'tls_version': version,
                'grade': self._calculate_ssl_grade(cert_analysis, cipher_analysis),
                'issues': cert_analysis.get('issues', []) + cipher_analysis.get('issues', []),
                'recommendations': self._get_ssl_recommendations(cert_analysis, cipher_analysis)
            }
            
        except Exception as e:
            return {
                'enabled': True,
                'error': str(e),
                'grade': 'Unknown',
                'issues': ['فشل في تحليل شهادة SSL'],
                'recommendations': ['التحقق من إعدادات SSL']
            }
    
    def _analyze_certificate(self, cert: Dict) -> Dict[str, Any]:
        """تحليل شهادة SSL"""
        import datetime
        
        issues = []
        
        # تحقق من تاريخ انتهاء الصلاحية
        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_until_expiry = (not_after - datetime.datetime.now()).days
        
        if days_until_expiry < 30:
            issues.append(f'الشهادة ستنتهي خلال {days_until_expiry} يوم')
        elif days_until_expiry < 0:
            issues.append('الشهادة منتهية الصلاحية')
        
        # تحقق من الجهة المُصدرة
        issuer = dict(x[0] for x in cert['issuer'])
        
        return {
            'subject': dict(x[0] for x in cert['subject']),
            'issuer': issuer,
            'not_before': cert['notBefore'],
            'not_after': cert['notAfter'],
            'days_until_expiry': days_until_expiry,
            'serial_number': cert['serialNumber'],
            'version': cert['version'],
            'issues': issues
        }
    
    def _analyze_cipher(self, cipher: tuple, tls_version: str) -> Dict[str, Any]:
        """تحليل خوارزمية التشفير"""
        issues = []
        
        if cipher:
            cipher_name, tls_version_cipher, key_length = cipher
            
            # فحص قوة التشفير
            if key_length < 128:
                issues.append(f'طول مفتاح التشفير ضعيف: {key_length} بت')
            
            # فحص خوارزميات التشفير القديمة
            weak_ciphers = ['RC4', 'DES', '3DES', 'MD5']
            if any(weak in cipher_name for weak in weak_ciphers):
                issues.append(f'خوارزمية تشفير ضعيفة: {cipher_name}')
            
            return {
                'cipher_name': cipher_name,
                'tls_version': tls_version_cipher,
                'key_length': key_length,
                'issues': issues
            }
        
        return {'issues': ['لا يمكن تحديد معلومات التشفير']}
    
    def _calculate_ssl_grade(self, cert_analysis: Dict, cipher_analysis: Dict) -> str:
        """حساب درجة SSL"""
        issues_count = len(cert_analysis.get('issues', [])) + len(cipher_analysis.get('issues', []))
        
        if issues_count == 0:
            return 'A'
        elif issues_count <= 2:
            return 'B'
        elif issues_count <= 4:
            return 'C'
        else:
            return 'F'
    
    def _get_ssl_recommendations(self, cert_analysis: Dict, cipher_analysis: Dict) -> List[str]:
        """توصيات تحسين SSL"""
        recommendations = []
        
        if cert_analysis.get('days_until_expiry', 365) < 60:
            recommendations.append('تجديد شهادة SSL قبل انتهاء صلاحيتها')
        
        if cipher_analysis.get('key_length', 256) < 256:
            recommendations.append('استخدام مفاتيح تشفير أقوى (256 بت أو أكثر)')
        
        if any('ضعيف' in issue for issue in cipher_analysis.get('issues', [])):
            recommendations.append('ترقية خوارزميات التشفير إلى إصدارات أحدث')
        
        return recommendations
    
    def _analyze_security_headers(self, response) -> Dict[str, Any]:
        """تحليل headers الأمان"""
        headers = response.headers
        
        security_headers = {
            'Strict-Transport-Security': {
                'present': 'strict-transport-security' in headers,
                'value': headers.get('strict-transport-security', ''),
                'importance': 'عالية',
                'description': 'يجبر المتصفح على استخدام HTTPS'
            },
            'Content-Security-Policy': {
                'present': 'content-security-policy' in headers,
                'value': headers.get('content-security-policy', ''),
                'importance': 'عالية',
                'description': 'يمنع هجمات XSS'
            },
            'X-Frame-Options': {
                'present': 'x-frame-options' in headers,
                'value': headers.get('x-frame-options', ''),
                'importance': 'متوسطة',
                'description': 'يمنع Clickjacking'
            },
            'X-Content-Type-Options': {
                'present': 'x-content-type-options' in headers,
                'value': headers.get('x-content-type-options', ''),
                'importance': 'متوسطة',
                'description': 'يمنع MIME sniffing'
            },
            'Referrer-Policy': {
                'present': 'referrer-policy' in headers,
                'value': headers.get('referrer-policy', ''),
                'importance': 'منخفضة',
                'description': 'يتحكم في مشاركة معلومات المُحيل'
            },
            'Permissions-Policy': {
                'present': 'permissions-policy' in headers,
                'value': headers.get('permissions-policy', ''),
                'importance': 'متوسطة',
                'description': 'يتحكم في صلاحيات المتصفح'
            }
        }
        
        # حساب النقاط
        present_count = sum(1 for h in security_headers.values() if h['present'])
        total_count = len(security_headers)
        score = (present_count / total_count) * 100
        
        # توصيات
        missing_headers = [name for name, info in security_headers.items() if not info['present']]
        recommendations = [f'إضافة header: {header}' for header in missing_headers]
        
        return {
            'headers': security_headers,
            'score': round(score, 1),
            'present_count': present_count,
            'total_count': total_count,
            'missing_headers': missing_headers,
            'recommendations': recommendations
        }
    
    def _analyze_content_security(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل أمان المحتوى"""
        issues = []
        recommendations = []
        
        # فحص inline scripts
        inline_scripts = soup.find_all('script', src=False)
        inline_count = len([s for s in inline_scripts if s.string and s.string.strip()])
        
        if inline_count > 0:
            issues.append(f'{inline_count} سكريبت inline قد يشكل خطراً أمنياً')
            recommendations.append('نقل السكريبتات إلى ملفات خارجية')
        
        # فحص inline styles
        inline_styles = len(soup.find_all(style=True))
        if inline_styles > 5:
            issues.append(f'{inline_styles} عنصر يحتوي على أنماط inline')
            recommendations.append('استخدام ملفات CSS خارجية')
        
        # فحص external resources من domains غير آمنة
        external_scripts = soup.find_all('script', src=True)
        unsafe_domains = []
        
        for script in external_scripts:
            src = script.get('src', '')
            if src.startswith('http://'):  # غير مشفر
                unsafe_domains.append(src)
        
        if unsafe_domains:
            issues.append(f'{len(unsafe_domains)} مورد يُحمَّل عبر HTTP غير آمن')
            recommendations.append('استخدام HTTPS لجميع الموارد الخارجية')
        
        return {
            'inline_scripts_count': inline_count,
            'inline_styles_count': inline_styles,
            'unsafe_external_resources': unsafe_domains,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _analyze_forms_security(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل أمان النماذج"""
        forms = soup.find_all('form')
        forms_analysis = []
        total_issues = 0
        
        for i, form in enumerate(forms):
            if not isinstance(form, Tag):
                continue
                
            form_issues = []
            
            # فحص method
            method = form.get('method', 'get').lower()
            if method == 'get':
                form_issues.append('استخدام GET method قد يعرض البيانات في URL')
            
            # فحص action
            action = form.get('action', '')
            if action and action.startswith('http://'):
                form_issues.append('إرسال البيانات عبر HTTP غير آمن')
            
            # فحص CSRF protection
            csrf_token = form.find('input', {'name': re.compile(r'csrf|token|_token', re.I)})
            if not csrf_token:
                form_issues.append('لا يوجد حماية من CSRF')
            
            # فحص password fields
            password_fields = form.find_all('input', {'type': 'password'})
            if password_fields and not action.startswith('https://'):
                form_issues.append('كلمات مرور قد تُرسل بدون تشفير')
            
            forms_analysis.append({
                'form_index': i + 1,
                'method': method,
                'action': action,
                'has_csrf_protection': bool(csrf_token),
                'password_fields_count': len(password_fields),
                'issues': form_issues
            })
            
            total_issues += len(form_issues)
        
        recommendations = []
        if total_issues > 0:
            recommendations.extend([
                'استخدام POST method للنماذج الحساسة',
                'إضافة CSRF tokens لجميع النماذج',
                'استخدام HTTPS لإرسال البيانات الحساسة',
                'تطبيق validation على الخادم'
            ])
        
        return {
            'total_forms': len(forms),
            'forms_details': forms_analysis,
            'total_issues': total_issues,
            'recommendations': recommendations
        }
    
    def _scan_common_vulnerabilities(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """فحص الثغرات الأمنية الشائعة"""
        vulnerabilities = {
            'xss_risks': self._scan_xss_risks(soup),
            'sql_injection_risks': self._scan_sql_injection_risks(content),
            'information_disclosure': self._scan_information_disclosure(content),
            'outdated_libraries': self._scan_outdated_libraries(content)
        }
        
        total_risks = sum(len(v) for v in vulnerabilities.values() if isinstance(v, list))
        
        return {
            'vulnerabilities': vulnerabilities,
            'total_risks_found': total_risks,
            'risk_level': self._calculate_risk_level(total_risks)
        }
    
    def _scan_xss_risks(self, soup: BeautifulSoup) -> List[str]:
        """فحص مخاطر XSS"""
        risks = []
        
        # فحص user input fields
        input_fields = soup.find_all(['input', 'textarea'])
        for field in input_fields:
            if isinstance(field, Tag):
                field_type = field.get('type', 'text')
                if field_type in ['text', 'search', 'url'] or field.name == 'textarea':
                    if not field.get('pattern') and not field.get('maxlength'):
                        risks.append('حقل إدخال بدون validation قد يسمح بـ XSS')
                        break
        
        # فحص innerHTML usage
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'innerHTML' in script.string:
                risks.append('استخدام innerHTML قد يسمح بـ XSS')
                break
        
        return risks
    
    def _scan_sql_injection_risks(self, content: str) -> List[str]:
        """فحص مخاطر SQL Injection"""
        risks = []
        
        # البحث عن أنماط SQL خطيرة
        sql_patterns = [
            r'SELECT.*FROM.*WHERE.*=.*\$',
            r'INSERT.*INTO.*VALUES.*\$',
            r'UPDATE.*SET.*WHERE.*=.*\$',
            r'DELETE.*FROM.*WHERE.*=.*\$'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                risks.append('استعلام SQL قد يكون عرضة للـ SQL Injection')
                break
        
        return risks
    
    def _scan_information_disclosure(self, content: str) -> List[str]:
        """فحص تسريب المعلومات"""
        risks = []
        
        # البحث عن معلومات حساسة
        sensitive_patterns = [
            (r'password\s*[:=]\s*["\'][^"\']+["\']', 'كلمات مرور مكشوفة في الكود'),
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']', 'مفاتيح API مكشوفة'),
            (r'secret\s*[:=]\s*["\'][^"\']+["\']', 'أسرار مكشوفة في الكود'),
            (r'debug\s*[:=]\s*true', 'وضع التطوير مفعل في الإنتاج')
        ]
        
        for pattern, description in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                risks.append(description)
        
        return risks
    
    def _scan_outdated_libraries(self, content: str) -> List[str]:
        """فحص المكتبات القديمة"""
        risks = []
        
        # مكتبات معروفة بثغرات أمنية
        vulnerable_libs = {
            'jquery-1.': 'إصدار jQuery قديم وغير آمن',
            'angular-1.0': 'إصدار AngularJS قديم',
            'bootstrap-2.': 'إصدار Bootstrap قديم'
        }
        
        for lib_pattern, description in vulnerable_libs.items():
            if lib_pattern in content.lower():
                risks.append(description)
        
        return risks
    
    def _calculate_risk_level(self, total_risks: int) -> str:
        """حساب مستوى المخاطر"""
        if total_risks == 0:
            return 'منخفض'
        elif total_risks <= 3:
            return 'متوسط'
        elif total_risks <= 6:
            return 'عالي'
        else:
            return 'خطير'
    
    def _analyze_privacy_features(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل ميزات الخصوصية"""
        
        # البحث عن سياسة الخصوصية
        privacy_links = soup.find_all('a', href=True)
        has_privacy_policy = any(
            'privacy' in link.get('href', '').lower() or 
            'privacy' in link.get_text().lower()
            for link in privacy_links
        )
        
        # البحث عن إشعارات الكوكيز
        has_cookie_notice = bool(
            soup.find(string=re.compile(r'cookie|كوكيز', re.I)) or
            soup.find(class_=re.compile(r'cookie', re.I))
        )
        
        # البحث عن Google Analytics
        has_analytics = 'google-analytics' in str(soup).lower()
        
        # البحث عن Facebook Pixel
        has_facebook_pixel = 'facebook.com/tr' in str(soup).lower()
        
        return {
            'has_privacy_policy': has_privacy_policy,
            'has_cookie_notice': has_cookie_notice,
            'tracking_services': {
                'google_analytics': has_analytics,
                'facebook_pixel': has_facebook_pixel
            },
            'privacy_score': self._calculate_privacy_score(
                has_privacy_policy, has_cookie_notice, has_analytics, has_facebook_pixel
            )
        }
    
    def _calculate_privacy_score(self, privacy_policy: bool, cookie_notice: bool, 
                                analytics: bool, facebook_pixel: bool) -> Dict[str, Any]:
        """حساب نقاط الخصوصية"""
        score = 0
        issues = []
        
        if privacy_policy:
            score += 30
        else:
            issues.append('سياسة خصوصية مفقودة')
        
        if cookie_notice:
            score += 20
        else:
            issues.append('إشعار الكوكيز مفقود')
        
        if analytics:
            score -= 10
            issues.append('يتم تتبع المستخدمين بواسطة Google Analytics')
        
        if facebook_pixel:
            score -= 15
            issues.append('يتم تتبع المستخدمين بواسطة Facebook Pixel')
        
        # التأكد من أن النقاط لا تقل عن 0
        score = max(0, score)
        
        return {
            'score': score,
            'max_score': 50,
            'percentage': min(int((score / 50) * 100), 100),
            'issues': issues
        }
    
    def _calculate_security_score(self, security_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """حساب النقاط الأمنية الإجمالية"""
        
        # نقاط SSL
        ssl_grade = security_analysis['ssl_analysis'].get('grade', 'F')
        ssl_score = {'A': 25, 'B': 20, 'C': 15, 'D': 10, 'F': 0}.get(ssl_grade, 0)
        
        # نقاط Headers
        headers_score = security_analysis['headers_analysis'].get('score', 0) * 0.25
        
        # نقاط المحتوى (عكسية - كلما قل عدد المشاكل كانت النقاط أعلى)
        content_issues = len(security_analysis['content_analysis'].get('issues', []))
        content_score = max(0, 25 - (content_issues * 5))
        
        # نقاط النماذج
        forms_issues = security_analysis['form_analysis'].get('total_issues', 0)
        forms_score = max(0, 15 - (forms_issues * 3))
        
        # نقاط الثغرات (عكسية)
        vulnerability_risks = security_analysis['vulnerability_scan'].get('total_risks_found', 0)
        vulnerability_score = max(0, 10 - (vulnerability_risks * 2))
        
        total_score = ssl_score + headers_score + content_score + forms_score + vulnerability_score
        
        # تحديد المستوى
        if total_score >= 80:
            level = 'ممتاز'
        elif total_score >= 60:
            level = 'جيد'
        elif total_score >= 40:
            level = 'متوسط'
        elif total_score >= 20:
            level = 'ضعيف'
        else:
            level = 'خطير'
        
        return {
            'total_score': round(total_score, 1),
            'max_score': 100,
            'percentage': round(total_score, 1),
            'level': level,
            'breakdown': {
                'ssl_security': ssl_score,
                'headers_security': round(headers_score, 1),
                'content_security': content_score,
                'forms_security': forms_score,
                'vulnerability_security': vulnerability_score
            }
        }