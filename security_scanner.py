#!/usr/bin/env python3
"""
نظام فحص الأمان والثغرات
"""
import requests
import ssl
import socket
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import re

class SecurityScanner:
    """ماسح الأمان والثغرات"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SecurityScanner/1.0)'
        })
        
        # قائمة فحوصات الأمان
        self.security_checks = [
            'ssl_analysis',
            'header_security',
            'form_security',
            'directory_enumeration',
            'information_disclosure',
            'injection_vulnerabilities',
            'authentication_analysis'
        ]
    
    def scan_website_security(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """فحص أمان شامل للموقع"""
        
        results = {
            'target_url': url,
            'scan_timestamp': datetime.now().isoformat(),
            'overall_security_score': 0,
            'vulnerabilities_found': [],
            'security_recommendations': [],
            'detailed_results': {}
        }
        
        try:
            # فحص SSL/TLS
            ssl_results = self._check_ssl_security(url)
            results['detailed_results']['ssl_analysis'] = ssl_results
            
            # فحص HTTP Headers
            headers_results = self._check_security_headers(url)
            results['detailed_results']['header_security'] = headers_results
            
            # فحص أمان النماذج
            forms_results = self._check_form_security(url)
            results['detailed_results']['form_security'] = forms_results
            
            # فحص تعداد المجلدات
            directory_results = self._check_directory_enumeration(url)
            results['detailed_results']['directory_enumeration'] = directory_results
            
            # فحص تسريب المعلومات
            info_disclosure = self._check_information_disclosure(url)
            results['detailed_results']['information_disclosure'] = info_disclosure
            
            # فحص ثغرات الحقن
            injection_results = self._check_injection_vulnerabilities(url)
            results['detailed_results']['injection_vulnerabilities'] = injection_results
            
            # تحليل نظام المصادقة
            auth_results = self._analyze_authentication(url)
            results['detailed_results']['authentication_analysis'] = auth_results
            
            # حساب النتيجة الإجمالية
            results['overall_security_score'] = self._calculate_security_score(results['detailed_results'])
            
            # جمع الثغرات والتوصيات
            results['vulnerabilities_found'] = self._collect_vulnerabilities(results['detailed_results'])
            results['security_recommendations'] = self._generate_recommendations(results['detailed_results'])
            
            # إنشاء تقرير
            self._generate_security_report(results, output_dir)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _check_ssl_security(self, url: str) -> Dict[str, Any]:
        """فحص أمان SSL/TLS"""
        
        ssl_results = {
            'https_enabled': False,
            'ssl_version': '',
            'certificate_info': {},
            'vulnerabilities': [],
            'recommendations': []
        }
        
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme == 'https':
                ssl_results['https_enabled'] = True
                
                # فحص شهادة SSL
                hostname = parsed_url.netloc
                port = parsed_url.port or 443
                
                # الحصول على معلومات الشهادة
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        ssl_results['ssl_version'] = ssock.version()
                        
                        ssl_results['certificate_info'] = {
                            'subject': dict(x[0] for x in cert.get('subject', [])),
                            'issuer': dict(x[0] for x in cert.get('issuer', [])),
                            'not_before': cert.get('notBefore'),
                            'not_after': cert.get('notAfter'),
                            'serial_number': cert.get('serialNumber'),
                            'version': cert.get('version')
                        }
                
                # فحص إعادة التوجيه HTTPS
                http_url = url.replace('https://', 'http://')
                try:
                    response = self.session.get(http_url, allow_redirects=False, timeout=10)
                    if response.status_code not in [301, 302, 308]:
                        ssl_results['vulnerabilities'].append('HTTP not redirected to HTTPS')
                        ssl_results['recommendations'].append('إعداد إعادة توجيه تلقائي من HTTP إلى HTTPS')
                except:
                    pass
                
            else:
                ssl_results['vulnerabilities'].append('HTTPS not enabled')
                ssl_results['recommendations'].append('تفعيل HTTPS لتشفير البيانات')
                
        except Exception as e:
            ssl_results['error'] = str(e)
        
        return ssl_results
    
    def _check_security_headers(self, url: str) -> Dict[str, Any]:
        """فحص رؤوس الأمان"""
        
        headers_results = {
            'security_headers_present': {},
            'missing_headers': [],
            'vulnerabilities': [],
            'recommendations': []
        }
        
        # قائمة رؤوس الأمان المهمة
        security_headers = {
            'Strict-Transport-Security': 'HSTS protection',
            'Content-Security-Policy': 'XSS protection',
            'X-Frame-Options': 'Clickjacking protection',
            'X-Content-Type-Options': 'MIME sniffing protection',
            'X-XSS-Protection': 'XSS filter',
            'Referrer-Policy': 'Referrer information control',
            'Permissions-Policy': 'Browser features control'
        }
        
        try:
            response = self.session.get(url, timeout=10)
            
            for header, description in security_headers.items():
                if header.lower() in [h.lower() for h in response.headers.keys()]:
                    headers_results['security_headers_present'][header] = {
                        'value': response.headers.get(header),
                        'description': description
                    }
                else:
                    headers_results['missing_headers'].append(header)
                    headers_results['vulnerabilities'].append(f'Missing {header}')
                    headers_results['recommendations'].append(f'إضافة رأس {header} للحماية من {description}')
            
            # فحص رؤوس إضافية قد تكشف معلومات
            info_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in info_headers:
                if header in response.headers:
                    headers_results['vulnerabilities'].append(f'Information disclosure: {header}')
                    headers_results['recommendations'].append(f'إخفاء رأس {header} لتجنب كشف معلومات النظام')
            
        except Exception as e:
            headers_results['error'] = str(e)
        
        return headers_results
    
    def _check_form_security(self, url: str) -> Dict[str, Any]:
        """فحص أمان النماذج"""
        
        forms_results = {
            'total_forms': 0,
            'forms_with_csrf': 0,
            'forms_without_csrf': 0,
            'insecure_forms': [],
            'vulnerabilities': [],
            'recommendations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            forms = soup.find_all('form')
            forms_results['total_forms'] = len(forms)
            
            for i, form in enumerate(forms):
                form_analysis = {
                    'form_index': i,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET').upper(),
                    'has_csrf_token': False,
                    'uses_https': False,
                    'vulnerabilities': []
                }
                
                # فحص CSRF token
                csrf_inputs = form.find_all('input', attrs={'name': re.compile(r'csrf|token', re.I)})
                if csrf_inputs:
                    form_analysis['has_csrf_token'] = True
                    forms_results['forms_with_csrf'] += 1
                else:
                    forms_results['forms_without_csrf'] += 1
                    form_analysis['vulnerabilities'].append('No CSRF protection')
                
                # فحص استخدام HTTPS للنماذج الحساسة
                password_inputs = form.find_all('input', type='password')
                if password_inputs:
                    action_url = urljoin(url, form_analysis['action'])
                    if not action_url.startswith('https://'):
                        form_analysis['vulnerabilities'].append('Password form not using HTTPS')
                        forms_results['vulnerabilities'].append(f'Form {i}: Password transmitted over insecure connection')
                
                # فحص autocomplete على الحقول الحساسة
                sensitive_inputs = form.find_all('input', type=['password', 'email'])
                for inp in sensitive_inputs:
                    if inp.get('autocomplete') != 'off':
                        form_analysis['vulnerabilities'].append('Sensitive input allows autocomplete')
                
                if form_analysis['vulnerabilities']:
                    forms_results['insecure_forms'].append(form_analysis)
            
            # توصيات عامة
            if forms_results['forms_without_csrf'] > 0:
                forms_results['recommendations'].append('إضافة CSRF tokens لجميع النماذج')
            
            if any('Password' in vuln for vuln in forms_results['vulnerabilities']):
                forms_results['recommendations'].append('استخدام HTTPS لجميع النماذج التي تحتوي على بيانات حساسة')
                
        except Exception as e:
            forms_results['error'] = str(e)
        
        return forms_results
    
    def _check_directory_enumeration(self, url: str) -> Dict[str, Any]:
        """فحص تعداد المجلدات"""
        
        directory_results = {
            'accessible_directories': [],
            'sensitive_files_found': [],
            'vulnerabilities': [],
            'recommendations': []
        }
        
        # قائمة المجلدات والملفات الحساسة للفحص
        sensitive_paths = [
            '/admin',
            '/administrator',
            '/wp-admin',
            '/phpmyadmin',
            '/cpanel',
            '/.git',
            '/.svn',
            '/backup',
            '/backups',
            '/config',
            '/configs',
            '/database',
            '/db',
            '/logs',
            '/log',
            '/test',
            '/tests',
            '/dev',
            '/debug',
            '/robots.txt',
            '/sitemap.xml',
            '/.htaccess',
            '/web.config',
            '/.env',
            '/composer.json',
            '/package.json'
        ]
        
        base_url = url.rstrip('/')
        
        for path in sensitive_paths:
            try:
                test_url = base_url + path
                response = self.session.get(test_url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    directory_results['accessible_directories'].append({
                        'path': path,
                        'status_code': response.status_code,
                        'content_length': len(response.content)
                    })
                    
                    # فحص ملفات حساسة محددة
                    if path in ['/.env', '/.git', '/config', '/backup']:
                        directory_results['sensitive_files_found'].append(path)
                        directory_results['vulnerabilities'].append(f'Sensitive directory/file accessible: {path}')
                        directory_results['recommendations'].append(f'منع الوصول إلى {path}')
                
                elif response.status_code in [403, 401]:
                    # محمي ولكن موجود
                    directory_results['accessible_directories'].append({
                        'path': path,
                        'status_code': response.status_code,
                        'note': 'Protected but exists'
                    })
                    
            except:
                continue  # تجاهل الأخطاء
        
        return directory_results
    
    def _check_information_disclosure(self, url: str) -> Dict[str, Any]:
        """فحص تسريب المعلومات"""
        
        info_results = {
            'information_leaked': [],
            'vulnerabilities': [],
            'recommendations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = response.text.lower()
            
            # فحص تسريب معلومات في التعليقات
            comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text)
            for comment in comments:
                comment_text = str(comment).lower()
                if any(keyword in comment_text for keyword in ['password', 'username', 'admin', 'secret', 'key', 'token']):
                    info_results['information_leaked'].append(f'Sensitive information in HTML comment: {comment[:100]}...')
                    info_results['vulnerabilities'].append('Sensitive information in HTML comments')
            
            # فحص تسريب معلومات في JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text().lower()
                if any(keyword in script_text for keyword in ['api_key', 'password', 'secret', 'token']):
                    info_results['information_leaked'].append('Potential sensitive data in JavaScript')
                    info_results['vulnerabilities'].append('Sensitive information exposed in JavaScript')
            
            # فحص error messages
            error_patterns = [
                'error',
                'exception',
                'stack trace',
                'debug',
                'warning',
                'mysql',
                'postgresql',
                'oracle'
            ]
            
            for pattern in error_patterns:
                if pattern in content:
                    info_results['information_leaked'].append(f'Potential error message: {pattern}')
            
            # فحص meta tags حساسة
            generator_meta = soup.find('meta', attrs={'name': 'generator'})
            if generator_meta:
                generator_content = generator_meta.get('content', '')
                info_results['information_leaked'].append(f'Generator meta tag: {generator_content}')
                info_results['vulnerabilities'].append('Technology stack information disclosed')
                info_results['recommendations'].append('إزالة meta tag generator لإخفاء معلومات التقنية')
            
        except Exception as e:
            info_results['error'] = str(e)
        
        return info_results
    
    def _check_injection_vulnerabilities(self, url: str) -> Dict[str, Any]:
        """فحص ثغرات الحقن"""
        
        injection_results = {
            'sql_injection_indicators': [],
            'xss_vulnerabilities': [],
            'vulnerabilities': [],
            'recommendations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # فحص نماذج قابلة للاستغلال
            forms = soup.find_all('form')
            
            for form in forms:
                inputs = form.find_all(['input', 'textarea'])
                
                for inp in inputs:
                    input_type = inp.get('type', 'text')
                    input_name = inp.get('name', '')
                    
                    # فحص inputs معرضة لـ SQL injection
                    if input_type in ['text', 'search'] and any(keyword in input_name.lower() for keyword in ['search', 'query', 'id', 'user']):
                        injection_results['sql_injection_indicators'].append(f'Potential SQL injection point: {input_name}')
                    
                    # فحص inputs معرضة لـ XSS
                    if input_type in ['text', 'textarea'] and not inp.get('maxlength'):
                        injection_results['xss_vulnerabilities'].append(f'Potential XSS point: {input_name} (no length limit)')
            
            # فحص URL parameters
            if '?' in url:
                injection_results['sql_injection_indicators'].append('URL contains parameters - potential injection point')
            
            # توصيات
            if injection_results['sql_injection_indicators']:
                injection_results['vulnerabilities'].append('Potential SQL injection vulnerabilities found')
                injection_results['recommendations'].append('استخدام prepared statements وتصفية المدخلات')
            
            if injection_results['xss_vulnerabilities']:
                injection_results['vulnerabilities'].append('Potential XSS vulnerabilities found')
                injection_results['recommendations'].append('تصفية وتشفير جميع المدخلات من المستخدمين')
                
        except Exception as e:
            injection_results['error'] = str(e)
        
        return injection_results
    
    def _analyze_authentication(self, url: str) -> Dict[str, Any]:
        """تحليل نظام المصادقة"""
        
        auth_results = {
            'login_forms_found': 0,
            'password_requirements': [],
            'session_security': {},
            'vulnerabilities': [],
            'recommendations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن نماذج تسجيل الدخول
            forms = soup.find_all('form')
            
            for form in forms:
                password_inputs = form.find_all('input', type='password')
                if password_inputs:
                    auth_results['login_forms_found'] += 1
                    
                    # فحص معايير كلمة المرور
                    for pwd_input in password_inputs:
                        min_length = pwd_input.get('minlength')
                        pattern = pwd_input.get('pattern')
                        required = pwd_input.get('required')
                        
                        if min_length:
                            auth_results['password_requirements'].append(f'Minimum length: {min_length}')
                        else:
                            auth_results['vulnerabilities'].append('No minimum password length requirement')
                        
                        if not pattern:
                            auth_results['vulnerabilities'].append('No password complexity requirements')
                        
                        if not required:
                            auth_results['vulnerabilities'].append('Password field not marked as required')
            
            # فحص أمان الجلسة
            cookies = response.cookies
            for cookie in cookies:
                if 'session' in cookie.name.lower():
                    auth_results['session_security']['session_cookie_found'] = True
                    auth_results['session_security']['secure_flag'] = cookie.secure
                    auth_results['session_security']['httponly_flag'] = getattr(cookie, 'httponly', False)
                    
                    if not cookie.secure:
                        auth_results['vulnerabilities'].append('Session cookie not marked as Secure')
                    
                    if not getattr(cookie, 'httponly', False):
                        auth_results['vulnerabilities'].append('Session cookie not marked as HttpOnly')
            
            # توصيات
            if auth_results['login_forms_found'] > 0:
                auth_results['recommendations'].append('تطبيق Two-Factor Authentication')
                auth_results['recommendations'].append('استخدام CAPTCHA لمنع الهجمات الآلية')
            
            if auth_results['vulnerabilities']:
                auth_results['recommendations'].append('تحسين أمان المصادقة والجلسات')
                
        except Exception as e:
            auth_results['error'] = str(e)
        
        return auth_results
    
    def _calculate_security_score(self, detailed_results: Dict[str, Any]) -> int:
        """حساب النتيجة الإجمالية للأمان"""
        
        total_score = 100
        
        # خصم نقاط حسب الثغرات المكتشفة
        for category, results in detailed_results.items():
            vulnerabilities = results.get('vulnerabilities', [])
            
            # خصم نقاط حسب شدة الثغرة
            for vuln in vulnerabilities:
                if any(keyword in vuln.lower() for keyword in ['critical', 'high', 'sql injection', 'xss']):
                    total_score -= 15  # ثغرات عالية الخطورة
                elif any(keyword in vuln.lower() for keyword in ['medium', 'csrf', 'information disclosure']):
                    total_score -= 10  # ثغرات متوسطة الخطورة
                else:
                    total_score -= 5   # ثغرات منخفضة الخطورة
        
        return max(0, total_score)  # عدم السماح بدرجات سالبة
    
    def _collect_vulnerabilities(self, detailed_results: Dict[str, Any]) -> List[str]:
        """جمع جميع الثغرات المكتشفة"""
        
        all_vulnerabilities = []
        
        for category, results in detailed_results.items():
            vulnerabilities = results.get('vulnerabilities', [])
            for vuln in vulnerabilities:
                all_vulnerabilities.append(f"{category}: {vuln}")
        
        return all_vulnerabilities
    
    def _generate_recommendations(self, detailed_results: Dict[str, Any]) -> List[str]:
        """إنشاء توصيات أمنية"""
        
        all_recommendations = []
        
        for category, results in detailed_results.items():
            recommendations = results.get('recommendations', [])
            all_recommendations.extend(recommendations)
        
        # إضافة توصيات عامة
        general_recommendations = [
            'تحديث جميع البرامج والمكونات بانتظام',
            'إجراء فحوصات أمان دورية',
            'تطبيق مبدأ الصلاحيات الأدنى',
            'إنشاء نسخ احتياطية آمنة',
            'مراقبة سجلات النظام'
        ]
        
        all_recommendations.extend(general_recommendations)
        
        return list(set(all_recommendations))  # إزالة التكرارات
    
    def _generate_security_report(self, results: Dict[str, Any], output_dir: Path) -> None:
        """إنشاء تقرير أمان مفصل"""
        
        # تقرير JSON
        report_file = output_dir / 'security_scan_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # تقرير HTML
        html_report = self._create_html_security_report(results)
        html_file = output_dir / 'security_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
    
    def _create_html_security_report(self, results: Dict[str, Any]) -> str:
        """إنشاء تقرير HTML للأمان"""
        
        score = results.get('overall_security_score', 0)
        score_color = '#4CAF50' if score >= 80 else '#FF9800' if score >= 60 else '#F44336'
        
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الأمان - {urlparse(results['target_url']).netloc}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            direction: rtl;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .security-score {{
            font-size: 48px;
            font-weight: bold;
            color: {score_color};
            margin: 20px 0;
        }}
        .vulnerabilities {{
            background: rgba(244,67,54,0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-right: 4px solid #f44336;
        }}
        .recommendations {{
            background: rgba(76,175,80,0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-right: 4px solid #4caf50;
        }}
        .section {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        li:last-child {{
            border-bottom: none;
        }}
        .timestamp {{
            text-align: center;
            opacity: 0.7;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 تقرير الأمان</h1>
            <h2>{results['target_url']}</h2>
            <div class="security-score">{score}/100</div>
            <p>النتيجة الإجمالية للأمان</p>
        </div>
        
        <div class="vulnerabilities">
            <h3>⚠️ الثغرات المكتشفة ({len(results.get('vulnerabilities_found', []))})</h3>
            <ul>
                {''.join([f'<li>🔴 {vuln}</li>' for vuln in results.get('vulnerabilities_found', [])])}
            </ul>
            {('<p>لم يتم العثور على ثغرات أمنية ظاهرة.</p>' if not results.get('vulnerabilities_found') else '')}
        </div>
        
        <div class="recommendations">
            <h3>💡 التوصيات الأمنية</h3>
            <ul>
                {''.join([f'<li>✅ {rec}</li>' for rec in results.get('security_recommendations', [])])}
            </ul>
        </div>
        
        <div class="section">
            <h3>📋 تفاصيل الفحص</h3>
            {''.join([f'<h4>{category.replace("_", " ").title()}</h4><p>تم فحص {len(data.get("vulnerabilities", []))} عنصر</p>' for category, data in results.get('detailed_results', {}).items()])}
        </div>
        
        <div class="timestamp">
            تم إنشاء التقرير: {results.get('scan_timestamp', '')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_content