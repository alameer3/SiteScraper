"""
Database Scanner - Advanced Database Detection Tool
أداة كشف قواعد البيانات المتقدمة

هذه الأداة المتخصصة تكمل Website Cloner Pro في كشف:
- قواعد البيانات المخفية
- هياكل البيانات المعقدة  
- APIs وقواعد البيانات الخارجية
- أنظمة إدارة المحتوى
"""

import asyncio
import aiohttp
import logging
import re
import json
import time
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
from bs4 import BeautifulSoup

@dataclass
class DatabaseScanConfig:
    """إعدادات مسح قواعد البيانات"""
    deep_scan: bool = True
    scan_apis: bool = True
    detect_cms: bool = True
    analyze_forms: bool = True
    check_endpoints: bool = True
    timeout: int = 30
    max_concurrent: int = 5

class DatabaseScanner:
    """أداة كشف قواعد البيانات المتخصصة"""
    
    def __init__(self, config: Optional[DatabaseScanConfig] = None):
        self.config = config or DatabaseScanConfig()
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Database signatures
        self.db_signatures = {
            'mysql': [
                r'mysql_connect', r'mysqli_', r'SELECT.*FROM', 
                r'mysql error', r'mysql syntax error'
            ],
            'postgresql': [
                r'pg_connect', r'postgresql', r'psql', 
                r'postgres error', r'pg_query'
            ],
            'mongodb': [
                r'mongodb://', r'mongo\.(find|insert|update)', 
                r'db\.collection', r'ObjectId\('
            ],
            'sqlite': [
                r'sqlite', r'\.db', r'\.sqlite', 
                r'database is locked', r'sqlite error'
            ],
            'oracle': [
                r'oracle', r'oci_connect', r'ora-\d+', 
                r'sqlplus', r'tnsnames'
            ],
            'mssql': [
                r'sqlserver', r'mssql_connect', r'microsoft sql', 
                r'sql server', r'tsql'
            ]
        }
        
        # API patterns
        self.api_patterns = [
            r'/api/v\d+/', r'/rest/', r'/graphql', 
            r'/webhook/', r'\.json', r'\.xml',
            r'application/json', r'application/xml'
        ]
        
        # CMS signatures
        self.cms_signatures = {
            'wordpress': [
                r'wp-content', r'wp-admin', r'wp-includes',
                r'wordpress', r'wp_', r'/wp-json/'
            ],
            'drupal': [
                r'drupal', r'sites/default', r'modules/',
                r'themes/', r'/user/login'
            ],
            'joomla': [
                r'joomla', r'administrator/', r'components/',
                r'templates/', r'option=com_'
            ],
            'magento': [
                r'magento', r'skin/frontend', r'app/code',
                r'mage/', r'checkout/cart'
            ]
        }
    
    async def scan_website_databases(self, target_url: str) -> Dict[str, Any]:
        """مسح شامل لقواعد البيانات في الموقع"""
        self.logger.info(f"بدء مسح قواعد البيانات للموقع: {target_url}")
        
        scan_results = {
            'target_url': target_url,
            'scan_timestamp': time.time(),
            'databases_detected': {},
            'apis_discovered': [],
            'cms_detected': {},
            'data_endpoints': [],
            'forms_analysis': [],
            'security_issues': [],
            'recommendations': []
        }
        
        try:
            # Create session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Phase 1: Basic content analysis
            scan_results['databases_detected'] = await self._detect_databases(target_url)
            
            # Phase 2: API discovery
            if self.config.scan_apis:
                scan_results['apis_discovered'] = await self._discover_apis(target_url)
            
            # Phase 3: CMS detection
            if self.config.detect_cms:
                scan_results['cms_detected'] = await self._detect_cms(target_url)
            
            # Phase 4: Forms analysis
            if self.config.analyze_forms:
                scan_results['forms_analysis'] = await self._analyze_forms(target_url)
            
            # Phase 5: Endpoint checking
            if self.config.check_endpoints:
                scan_results['data_endpoints'] = await self._check_data_endpoints(target_url)
            
            # Phase 6: Security analysis
            scan_results['security_issues'] = await self._analyze_security_issues(scan_results)
            
            # Phase 7: Generate recommendations
            scan_results['recommendations'] = await self._generate_recommendations(scan_results)
            
        except Exception as e:
            self.logger.error(f"خطأ في مسح قواعد البيانات: {e}")
            scan_results['error'] = str(e)
        finally:
            if self.session:
                await self.session.close()
        
        return scan_results
    
    async def _detect_databases(self, target_url: str) -> Dict[str, Any]:
        """كشف قواعد البيانات المستخدمة"""
        databases = {}
        
        try:
            async with self.session.get(target_url) as response:
                content = await response.text()
                headers = dict(response.headers)
                
                # Check content for database signatures
                for db_type, patterns in self.db_signatures.items():
                    matches = []
                    for pattern in patterns:
                        found = re.findall(pattern, content, re.IGNORECASE)
                        matches.extend(found)
                    
                    if matches:
                        databases[db_type] = {
                            'detected': True,
                            'confidence': min(len(matches) * 20, 100),
                            'evidence': matches[:5],  # First 5 matches
                            'indicators': len(matches)
                        }
                
                # Check headers for database info
                for header, value in headers.items():
                    if 'mysql' in value.lower():
                        databases.setdefault('mysql', {})['header_evidence'] = f"{header}: {value}"
                    elif 'postgres' in value.lower():
                        databases.setdefault('postgresql', {})['header_evidence'] = f"{header}: {value}"
                
        except Exception as e:
            self.logger.error(f"خطأ في كشف قواعد البيانات: {e}")
        
        return databases
    
    async def _discover_apis(self, target_url: str) -> List[Dict[str, Any]]:
        """اكتشاف APIs ونقاط البيانات"""
        apis = []
        
        try:
            # Check common API endpoints
            api_endpoints = [
                '/api/', '/api/v1/', '/api/v2/', '/rest/', 
                '/graphql', '/webhook/', '/data/', '/json/'
            ]
            
            base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"
            
            for endpoint in api_endpoints:
                try:
                    url = base_url + endpoint
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            content = await response.text()
                            
                            apis.append({
                                'endpoint': endpoint,
                                'url': url,
                                'status': response.status,
                                'content_type': content_type,
                                'size': len(content),
                                'is_json': 'application/json' in content_type,
                                'is_xml': 'application/xml' in content_type
                            })
                except:
                    continue
            
            # Analyze main page for API references
            async with self.session.get(target_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for AJAX calls and API references
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        for pattern in self.api_patterns:
                            matches = re.findall(pattern, script.string, re.IGNORECASE)
                            for match in matches:
                                apis.append({
                                    'type': 'javascript_reference',
                                    'pattern': pattern,
                                    'match': match,
                                    'source': 'script_tag'
                                })
                
        except Exception as e:
            self.logger.error(f"خطأ في اكتشاف APIs: {e}")
        
        return apis
    
    async def _detect_cms(self, target_url: str) -> Dict[str, Any]:
        """كشف أنظمة إدارة المحتوى"""
        cms_detected = {}
        
        try:
            async with self.session.get(target_url) as response:
                content = await response.text()
                headers = dict(response.headers)
                
                # Check content for CMS signatures
                for cms_type, patterns in self.cms_signatures.items():
                    matches = []
                    confidence = 0
                    
                    for pattern in patterns:
                        found = re.findall(pattern, content, re.IGNORECASE)
                        matches.extend(found)
                        confidence += len(found) * 15
                    
                    if matches:
                        cms_detected[cms_type] = {
                            'detected': True,
                            'confidence': min(confidence, 100),
                            'evidence': matches[:3],
                            'version': await self._detect_cms_version(content, cms_type)
                        }
                
                # Check specific CMS endpoints
                cms_endpoints = {
                    'wordpress': ['/wp-admin/', '/wp-login.php', '/wp-json/'],
                    'drupal': ['/user/login', '/admin/', '/node/'],
                    'joomla': ['/administrator/', '/component/', '/index.php?option='],
                    'magento': ['/admin/', '/customer/account/', '/checkout/']
                }
                
                base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"
                
                for cms_type, endpoints in cms_endpoints.items():
                    for endpoint in endpoints:
                        try:
                            url = base_url + endpoint
                            async with self.session.get(url) as resp:
                                if resp.status in [200, 302, 403]:  # Found or redirected
                                    if cms_type not in cms_detected:
                                        cms_detected[cms_type] = {'detected': True, 'confidence': 60}
                                    cms_detected[cms_type]['admin_panel'] = url
                                    break
                        except:
                            continue
                
        except Exception as e:
            self.logger.error(f"خطأ في كشف CMS: {e}")
        
        return cms_detected
    
    async def _detect_cms_version(self, content: str, cms_type: str) -> Optional[str]:
        """كشف إصدار نظام إدارة المحتوى"""
        version_patterns = {
            'wordpress': [
                r'wp-includes/js/wp-embed\.min\.js\?ver=([\d\.]+)',
                r'wordpress ([\d\.]+)',
                r'wp-json/wp/v2'
            ],
            'drupal': [
                r'drupal ([\d\.]+)',
                r'sites/all/modules',
                r'misc/drupal\.js'
            ],
            'joomla': [
                r'joomla! ([\d\.]+)',
                r'media/system/js',
                r'administrator/templates'
            ]
        }
        
        if cms_type in version_patterns:
            for pattern in version_patterns[cms_type]:
                match = re.search(pattern, content, re.IGNORECASE)
                if match and match.groups():
                    return match.group(1)
        
        return None
    
    async def _analyze_forms(self, target_url: str) -> List[Dict[str, Any]]:
        """تحليل النماذج وإدخال البيانات"""
        forms = []
        
        try:
            async with self.session.get(target_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                form_tags = soup.find_all('form')
                
                for form in form_tags:
                    form_data = {
                        'action': form.get('action', ''),
                        'method': form.get('method', 'get').lower(),
                        'fields': [],
                        'has_file_upload': False,
                        'potential_database_interaction': False
                    }
                    
                    # Analyze form fields
                    inputs = form.find_all(['input', 'textarea', 'select'])
                    for input_tag in inputs:
                        field = {
                            'type': input_tag.get('type', 'text'),
                            'name': input_tag.get('name', ''),
                            'required': input_tag.has_attr('required')
                        }
                        form_data['fields'].append(field)
                        
                        # Check for file uploads
                        if field['type'] == 'file':
                            form_data['has_file_upload'] = True
                        
                        # Check for database-related fields
                        if any(keyword in field['name'].lower() for keyword in 
                               ['user', 'pass', 'email', 'login', 'register', 'search']):
                            form_data['potential_database_interaction'] = True
                    
                    forms.append(form_data)
                
        except Exception as e:
            self.logger.error(f"خطأ في تحليل النماذج: {e}")
        
        return forms
    
    async def _check_data_endpoints(self, target_url: str) -> List[Dict[str, Any]]:
        """فحص نقاط البيانات المحتملة"""
        endpoints = []
        
        # Common data endpoints to check
        common_endpoints = [
            '/sitemap.xml', '/robots.txt', '/feeds/', '/rss/',
            '/.env', '/config.php', '/database.php', '/wp-config.php',
            '/admin/', '/dashboard/', '/api/users/', '/api/posts/',
            '/data.json', '/config.json', '/manifest.json'
        ]
        
        base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"
        
        try:
            for endpoint in common_endpoints:
                try:
                    url = base_url + endpoint
                    async with self.session.get(url) as response:
                        endpoints.append({
                            'endpoint': endpoint,
                            'url': url,
                            'status': response.status,
                            'accessible': response.status == 200,
                            'size': response.headers.get('content-length', 0),
                            'content_type': response.headers.get('content-type', ''),
                            'sensitive': endpoint in ['/.env', '/config.php', '/wp-config.php']
                        })
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"خطأ في فحص نقاط البيانات: {e}")
        
        return endpoints
    
    async def _analyze_security_issues(self, scan_results: Dict[str, Any]) -> List[str]:
        """تحليل المشاكل الأمنية"""
        issues = []
        
        try:
            # Check for exposed sensitive files
            for endpoint in scan_results.get('data_endpoints', []):
                if endpoint.get('sensitive') and endpoint.get('accessible'):
                    issues.append(f"ملف حساس مكشوف: {endpoint['endpoint']}")
            
            # Check for outdated CMS
            cms_detected = scan_results.get('cms_detected', {})
            for cms_type, info in cms_detected.items():
                if info.get('version'):
                    # This would need a vulnerability database in real implementation
                    issues.append(f"إصدار {cms_type} قد يحتاج تحديث: {info['version']}")
            
            # Check for insecure forms
            forms = scan_results.get('forms_analysis', [])
            for form in forms:
                if form['method'] == 'get' and form['potential_database_interaction']:
                    issues.append("نموذج يستخدم GET لبيانات حساسة محتملة")
                if not any(field['type'] == 'hidden' and 'csrf' in field.get('name', '').lower() 
                          for field in form['fields']):
                    issues.append("نموذج قد يفتقر لحماية CSRF")
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الأمان: {e}")
        
        return issues
    
    async def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """إنشاء توصيات الأمان والتحسين"""
        recommendations = []
        
        try:
            # Database recommendations
            databases = scan_results.get('databases_detected', {})
            if databases:
                recommendations.append("تأكد من تشفير اتصالات قواعد البيانات")
                recommendations.append("استخدم prepared statements لمنع SQL injection")
            
            # API recommendations  
            apis = scan_results.get('apis_discovered', [])
            if apis:
                recommendations.append("تطبيق rate limiting على APIs")
                recommendations.append("استخدام authentication tokens للـ APIs")
            
            # CMS recommendations
            cms_detected = scan_results.get('cms_detected', {})
            for cms_type in cms_detected:
                recommendations.append(f"تحديث {cms_type} لآخر إصدار آمن")
                recommendations.append(f"تغيير كلمات مرور الافتراضية لـ {cms_type}")
            
            # Security recommendations
            security_issues = scan_results.get('security_issues', [])
            if security_issues:
                recommendations.append("إصلاح المشاكل الأمنية المكتشفة")
                recommendations.append("تطبيق حماية إضافية للملفات الحساسة")
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء التوصيات: {e}")
        
        return recommendations