"""
محلل قواعد البيانات المتطور
Advanced Database Structure Analyzer
"""

import re
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
from .session_manager import SessionManager


class DatabaseAnalyzer:
    """محلل متطور لهياكل قواعد البيانات والـ APIs"""
    
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager
        self.detected_endpoints = set()
        self.discovered_schemas = {}
        
    def analyze_database_structure(self, soup: BeautifulSoup, url: str, 
                                 html_content: str) -> Dict[str, Any]:
        """تحليل شامل لبنية قاعدة البيانات المحتملة"""
        
        analysis_result = {
            'database_types_detected': [],
            'api_endpoints_discovered': [],
            'data_structures_inferred': {},
            'connection_patterns': [],
            'schema_analysis': {},
            'security_assessment': {},
            'technology_stack': []
        }
        
        # 1. اكتشاف أنواع قواعد البيانات
        db_types = self._detect_database_types(soup, html_content)
        analysis_result['database_types_detected'] = db_types
        
        # 2. اكتشاف نقاط API
        api_endpoints = self._discover_api_endpoints(soup, html_content, url)
        analysis_result['api_endpoints_discovered'] = api_endpoints
        
        # 3. تحليل أنماط الاتصال
        connection_patterns = self._analyze_connection_patterns(html_content)
        analysis_result['connection_patterns'] = connection_patterns
        
        # 4. استنتاج هياكل البيانات
        data_structures = self._infer_data_structures(soup, html_content)
        analysis_result['data_structures_inferred'] = data_structures
        
        # 5. تحليل الأمان
        security_assessment = self._assess_database_security(soup, html_content)
        analysis_result['security_assessment'] = security_assessment
        
        # 6. تحليل التقنيات
        tech_stack = self._analyze_technology_stack(soup, html_content)
        analysis_result['technology_stack'] = tech_stack
        
        return analysis_result
    
    def _detect_database_types(self, soup: BeautifulSoup, content: str) -> List[Dict[str, Any]]:
        """اكتشاف أنواع قواعد البيانات المستخدمة"""
        
        database_indicators = {
            'mysql': [
                'mysql', 'mysqli', 'pdo_mysql', 'mysql_connect', 'mysql_query',
                'phpmyadmin', 'mysql_error', 'mysql_fetch'
            ],
            'postgresql': [
                'postgresql', 'postgres', 'pg_connect', 'pg_query', 'pg_fetch',
                'psql', 'postgre', 'pgsql'
            ],
            'mongodb': [
                'mongodb', 'mongo', 'mongoclient', 'mongoose', 'mongodb://',
                'mongoengine', 'pymongo', 'bson'
            ],
            'sqlite': [
                'sqlite', 'sqlite3', 'pdo_sqlite', 'sqlite_open',
                'sqlite_query', 'sqlite.db'
            ],
            'redis': [
                'redis', 'redis_connect', 'redis_get', 'redis_set',
                'redis://', 'redis-server'
            ],
            'oracle': [
                'oracle', 'oci_connect', 'oci_execute', 'oracle_connect',
                'tnsnames', 'sqlplus'
            ],
            'sql_server': [
                'sql server', 'mssql', 'sqlsrv', 'sql_srv_connect',
                'microsoft sql', 'tsql'
            ],
            'firebase': [
                'firebase', 'firestore', 'firebase.initializeApp',
                'getFirestore', 'firebase-admin'
            ],
            'supabase': [
                'supabase', 'createClient', '@supabase/supabase-js',
                'supabase.from'
            ],
            'dynamodb': [
                'dynamodb', 'aws-sdk', 'dynamodb.putItem',
                'dynamodb.getItem', 'aws.dynamodb'
            ]
        }
        
        detected_types = []
        content_lower = content.lower()
        
        for db_type, indicators in database_indicators.items():
            confidence = 0
            found_indicators = []
            
            for indicator in indicators:
                if indicator in content_lower:
                    confidence += 1
                    found_indicators.append(indicator)
            
            if confidence > 0:
                detected_types.append({
                    'type': db_type,
                    'confidence': min(confidence * 20, 100),  # تحويل إلى نسبة مئوية
                    'indicators_found': found_indicators,
                    'total_indicators': len(indicators)
                })
        
        # ترتيب حسب الثقة
        detected_types.sort(key=lambda x: x['confidence'], reverse=True)
        
        return detected_types
    
    def _discover_api_endpoints(self, soup: BeautifulSoup, content: str, base_url: str) -> List[Dict[str, Any]]:
        """اكتشاف نقاط API المحتملة"""
        
        endpoints = []
        
        # أنماط API شائعة
        api_patterns = [
            r'/api/[^"\s]+',
            r'/v[0-9]+/[^"\s]+',
            r'/rest/[^"\s]+',
            r'/graphql[^"\s]*',
            r'/webhook[^"\s]*',
            r'\.json[^"\s]*',
            r'\.xml[^"\s]*'
        ]
        
        # البحث في JavaScript والـ HTML
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                endpoint_url = urljoin(base_url, match)
                
                if endpoint_url not in self.detected_endpoints:
                    self.detected_endpoints.add(endpoint_url)
                    endpoints.append({
                        'url': endpoint_url,
                        'method': 'GET',  # افتراضي
                        'type': self._classify_endpoint_type(match),
                        'pattern_matched': pattern,
                        'confidence': 70
                    })
        
        # البحث في forms للـ POST endpoints
        forms = soup.find_all('form')
        for form in forms:
            if isinstance(form, Tag):
                action = form.get('action', '')
                method = form.get('method', 'GET').upper()
                
                if action:
                    endpoint_url = urljoin(base_url, action)
                    endpoints.append({
                        'url': endpoint_url,
                        'method': method,
                        'type': 'form_submission',
                        'confidence': 90,
                        'form_fields': self._extract_form_fields(form)
                    })
        
        # البحث في AJAX calls
        ajax_patterns = [
            r'\.ajax\s*\(\s*[\'"][^\'"]*(api|/)[^\'\"]*[\'"]',
            r'fetch\s*\(\s*[\'"][^\'\"]*[\'"]',
            r'xhr\.open\s*\(\s*[\'"][^\'\"]*[\'"]'
        ]
        
        for pattern in ajax_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # استخراج URL من match
                url_match = re.search(r'[\'"]([^\'"]*)[\'"]', match)
                if url_match:
                    api_url = url_match.group(1)
                    endpoint_url = urljoin(base_url, api_url)
                    endpoints.append({
                        'url': endpoint_url,
                        'method': 'AJAX',
                        'type': 'javascript_api',
                        'confidence': 85
                    })
        
        return endpoints[:20]  # أول 20 endpoint
    
    def _classify_endpoint_type(self, endpoint: str) -> str:
        """تصنيف نوع نقطة API"""
        endpoint_lower = endpoint.lower()
        
        if 'graphql' in endpoint_lower:
            return 'GraphQL'
        elif 'webhook' in endpoint_lower:
            return 'Webhook'
        elif 'rest' in endpoint_lower or 'api' in endpoint_lower:
            return 'REST API'
        elif '.json' in endpoint_lower:
            return 'JSON API'
        elif '.xml' in endpoint_lower:
            return 'XML API'
        elif '/v' in endpoint_lower and any(char.isdigit() for char in endpoint_lower):
            return 'Versioned API'
        else:
            return 'Unknown API'
    
    def _extract_form_fields(self, form: Tag) -> List[Dict[str, str]]:
        """استخراج حقول النموذج"""
        fields = []
        
        inputs = form.find_all(['input', 'select', 'textarea'])
        for input_tag in inputs:
            if isinstance(input_tag, Tag):
                field_info = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', input_tag.name),
                    'required': input_tag.has_attr('required'),
                    'placeholder': input_tag.get('placeholder', '')
                }
                
                if field_info['name']:
                    fields.append(field_info)
        
        return fields
    
    def _analyze_connection_patterns(self, content: str) -> List[Dict[str, Any]]:
        """تحليل أنماط الاتصال بقاعدة البيانات"""
        
        connection_patterns = []
        
        # أنماط اتصال قواعد البيانات
        patterns = {
            'database_url': [
                r'DATABASE_URL\s*=\s*[\'"]([^\'"]*)[\'"]',
                r'DB_URL\s*=\s*[\'"]([^\'"]*)[\'"]',
                r'mongodb://[^\s\'"]*',
                r'mysql://[^\s\'"]*',
                r'postgresql://[^\s\'"]*'
            ],
            'connection_string': [
                r'connectionString\s*[=:]\s*[\'"]([^\'"]*)[\'"]',
                r'connection\s*[=:]\s*[\'"]([^\'"]*)[\'"]'
            ],
            'database_config': [
                r'host\s*[=:]\s*[\'"]([^\'"]*)[\'"]',
                r'database\s*[=:]\s*[\'"]([^\'"]*)[\'"]',
                r'username\s*[=:]\s*[\'"]([^\'"]*)[\'"]',
                r'port\s*[=:]\s*(\d+)'
            ]
        }
        
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    connection_patterns.append({
                        'type': pattern_type,
                        'pattern': pattern,
                        'matches': matches[:5],  # أول 5 مطابقات
                        'count': len(matches)
                    })
        
        return connection_patterns
    
    def _infer_data_structures(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """استنتاج هياكل البيانات من المحتوى"""
        
        data_structures = {
            'tables_detected': [],
            'json_schemas': [],
            'form_structures': [],
            'api_responses': []
        }
        
        # 1. تحليل الجداول
        tables = soup.find_all('table')
        for table in tables[:5]:  # أول 5 جداول
            if isinstance(table, Tag):
                table_structure = self._analyze_table_structure(table)
                if table_structure:
                    data_structures['tables_detected'].append(table_structure)
        
        # 2. البحث عن JSON structures
        json_patterns = [
            r'\{[^{}]*"[^"]+"\s*:\s*[^}]*\}',
            r'\[[^[\]]*\{[^}]*\}[^[\]]*\]'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content)
            for match in matches[:3]:  # أول 3 مطابقات
                try:
                    parsed_json = json.loads(match)
                    schema = self._analyze_json_schema(parsed_json)
                    data_structures['json_schemas'].append(schema)
                except:
                    continue
        
        # 3. تحليل النماذج
        forms = soup.find_all('form')
        for form in forms[:3]:  # أول 3 نماذج
            if isinstance(form, Tag):
                form_structure = self._analyze_form_structure(form)
                data_structures['form_structures'].append(form_structure)
        
        return data_structures
    
    def _analyze_table_structure(self, table: Tag) -> Optional[Dict[str, Any]]:
        """تحليل بنية الجدول"""
        
        headers = []
        rows_sample = []
        
        # استخراج العناوين
        header_row = table.find('tr')
        if header_row:
            header_cells = header_row.find_all(['th', 'td'])
            headers = [cell.get_text().strip() for cell in header_cells if isinstance(cell, Tag)]
        
        # استخراج عينة من الصفوف
        rows = table.find_all('tr')[1:4]  # أول 3 صفوف بعد العناوين
        for row in rows:
            if isinstance(row, Tag):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text().strip() for cell in cells if isinstance(cell, Tag)]
                if row_data:
                    rows_sample.append(row_data)
        
        if headers or rows_sample:
            return {
                'headers': headers,
                'sample_rows': rows_sample,
                'column_count': len(headers) if headers else len(rows_sample[0]) if rows_sample else 0,
                'row_count': len(table.find_all('tr')) - (1 if headers else 0)
            }
        
        return None
    
    def _analyze_json_schema(self, json_data: Any) -> Dict[str, Any]:
        """تحليل مخطط JSON"""
        
        if isinstance(json_data, dict):
            schema = {
                'type': 'object',
                'properties': {},
                'field_count': len(json_data)
            }
            
            for key, value in json_data.items():
                schema['properties'][key] = {
                    'type': type(value).__name__,
                    'sample_value': str(value)[:50] if value is not None else None
                }
        
        elif isinstance(json_data, list) and json_data:
            schema = {
                'type': 'array',
                'item_type': type(json_data[0]).__name__,
                'length': len(json_data)
            }
            
            if isinstance(json_data[0], dict):
                schema['item_schema'] = self._analyze_json_schema(json_data[0])
        
        else:
            schema = {
                'type': type(json_data).__name__,
                'sample_value': str(json_data)[:50]
            }
        
        return schema
    
    def _analyze_form_structure(self, form: Tag) -> Dict[str, Any]:
        """تحليل بنية النموذج"""
        
        fields = self._extract_form_fields(form)
        
        return {
            'action': form.get('action', ''),
            'method': form.get('method', 'GET'),
            'field_count': len(fields),
            'fields': fields,
            'validation_patterns': self._extract_validation_patterns(form)
        }
    
    def _extract_validation_patterns(self, form: Tag) -> List[Dict[str, str]]:
        """استخراج أنماط التحقق من النموذج"""
        patterns = []
        
        inputs = form.find_all('input')
        for input_tag in inputs:
            if isinstance(input_tag, Tag):
                pattern = input_tag.get('pattern')
                if pattern:
                    patterns.append({
                        'field': input_tag.get('name', ''),
                        'pattern': pattern,
                        'type': 'regex'
                    })
                
                min_length = input_tag.get('minlength')
                max_length = input_tag.get('maxlength')
                if min_length or max_length:
                    patterns.append({
                        'field': input_tag.get('name', ''),
                        'min_length': min_length,
                        'max_length': max_length,
                        'type': 'length'
                    })
        
        return patterns
    
    def _assess_database_security(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """تقييم أمان قاعدة البيانات"""
        
        security_issues = []
        security_score = 100
        
        # البحث عن أنماط غير آمنة
        unsafe_patterns = [
            (r'mysql_query\s*\(\s*[\'"][^\'"]* \. [^\'\"]*[\'"]', 'SQL Injection Risk'),
            (r'password\s*=\s*[\'"][^\'"]*[\'"]', 'Hardcoded Password'),
            (r'api_key\s*=\s*[\'"][^\'"]*[\'"]', 'Exposed API Key'),
            (r'mysqli_connect\s*\([^)]*[\'"][^\'"]*[\'"][^)]*\)', 'Insecure Connection'),
            (r'SELECT \* FROM', 'SELECT * Usage'),
            (r'eval\s*\(', 'Code Execution Risk')
        ]
        
        for pattern, issue_type in unsafe_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                security_issues.append({
                    'type': issue_type,
                    'pattern': pattern,
                    'occurrences': len(matches),
                    'severity': 'high' if 'injection' in issue_type.lower() else 'medium'
                })
                security_score -= 20 if 'injection' in issue_type.lower() else 10
        
        # فحص الحماية الموجودة
        security_features = []
        
        security_indicators = [
            (r'prepare\s*\(', 'Prepared Statements'),
            (r'csrf_token', 'CSRF Protection'),
            (r'sanitize', 'Input Sanitization'),
            (r'hash\s*\(', 'Password Hashing'),
            (r'ssl\s*=\s*true', 'SSL Connection')
        ]
        
        for pattern, feature in security_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                security_features.append(feature)
                security_score += 5
        
        return {
            'security_score': max(0, min(security_score, 100)),
            'security_issues': security_issues,
            'security_features': security_features,
            'recommendations': self._generate_security_recommendations(security_issues)
        }
    
    def _generate_security_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """توليد توصيات أمنية"""
        recommendations = []
        
        issue_types = [issue['type'] for issue in issues]
        
        if any('injection' in issue_type.lower() for issue_type in issue_types):
            recommendations.append("استخدم Prepared Statements لمنع SQL Injection")
        
        if any('password' in issue_type.lower() for issue_type in issue_types):
            recommendations.append("لا تُخزن كلمات المرور في الكود مباشرة")
        
        if any('api' in issue_type.lower() for issue_type in issue_types):
            recommendations.append("استخدم متغيرات البيئة لتخزين API Keys")
        
        recommendations.extend([
            "استخدم HTTPS لجميع الاتصالات",
            "فعّل تشفير قاعدة البيانات",
            "استخدم نظام مراجعة الصلاحيات",
            "قم بتحديث مكتبات قاعدة البيانات بانتظام"
        ])
        
        return recommendations[:5]  # أول 5 توصيات
    
    def _analyze_technology_stack(self, soup: BeautifulSoup, content: str) -> List[Dict[str, Any]]:
        """تحليل التقنيات المستخدمة"""
        
        technologies = []
        
        tech_patterns = {
            'Programming Languages': {
                'php': [r'\.php', r'<?php', r'<?='],
                'python': [r'django', r'flask', r'\.py'],
                'javascript': [r'\.js', r'javascript:', r'node\.js'],
                'java': [r'\.jsp', r'servlet', r'spring'],
                'ruby': [r'\.rb', r'rails', r'ruby'],
                'c#': [r'\.aspx', r'\.net', r'c#'],
                'go': [r'golang', r'\.go'],
                'rust': [r'\.rs', r'rust']
            },
            'Frameworks': {
                'react': [r'react', r'jsx', r'reactdom'],
                'vue': [r'vue\.js', r'vuejs', r'@vue'],
                'angular': [r'angular', r'@angular'],
                'laravel': [r'laravel', r'artisan'],
                'django': [r'django', r'{% '],
                'express': [r'express', r'app\.get'],
                'spring': [r'spring', r'@controller']
            },
            'Databases': {
                'mysql': [r'mysql', r'mysqli'],
                'postgresql': [r'postgresql', r'postgres'],
                'mongodb': [r'mongodb', r'mongo'],
                'redis': [r'redis'],
                'sqlite': [r'sqlite']
            }
        }
        
        content_lower = content.lower()
        
        for category, tech_dict in tech_patterns.items():
            for tech_name, patterns in tech_dict.items():
                confidence = 0
                found_patterns = []
                
                for pattern in patterns:
                    matches = len(re.findall(pattern, content_lower))
                    if matches > 0:
                        confidence += matches
                        found_patterns.append(pattern)
                
                if confidence > 0:
                    technologies.append({
                        'category': category,
                        'technology': tech_name,
                        'confidence': min(confidence * 20, 100),
                        'patterns_found': found_patterns
                    })
        
        # ترتيب حسب الثقة
        technologies.sort(key=lambda x: x['confidence'], reverse=True)
        
        return technologies[:15]  # أول 15 تقنية
    
    async def probe_api_endpoints(self, endpoints: List[str], 
                                base_url: str) -> Dict[str, Any]:
        """فحص نقاط API وتحليل الاستجابات"""
        
        results = {
            'accessible_endpoints': [],
            'protected_endpoints': [],
            'failed_endpoints': [],
            'response_schemas': {}
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints[:10]:  # أول 10 endpoints
                try:
                    endpoint_url = urljoin(base_url, endpoint)
                    
                    async with session.get(endpoint_url, timeout=10) as response:
                        status = response.status
                        content_type = response.headers.get('Content-Type', '')
                        
                        if status == 200:
                            text = await response.text()
                            results['accessible_endpoints'].append({
                                'url': endpoint_url,
                                'status': status,
                                'content_type': content_type,
                                'response_size': len(text),
                                'schema': self._analyze_response_schema(text, content_type)
                            })
                        
                        elif status in [401, 403]:
                            results['protected_endpoints'].append({
                                'url': endpoint_url,
                                'status': status,
                                'protection_type': 'authentication_required'
                            })
                        
                        else:
                            results['failed_endpoints'].append({
                                'url': endpoint_url,
                                'status': status,
                                'error': f"HTTP {status}"
                            })
                
                except Exception as e:
                    results['failed_endpoints'].append({
                        'url': endpoint,
                        'error': str(e)
                    })
        
        return results
    
    def _analyze_response_schema(self, response_text: str, content_type: str) -> Dict[str, Any]:
        """تحليل مخطط الاستجابة"""
        
        if 'json' in content_type.lower():
            try:
                json_data = json.loads(response_text)
                return self._analyze_json_schema(json_data)
            except:
                return {'type': 'invalid_json', 'raw_length': len(response_text)}
        
        elif 'xml' in content_type.lower():
            return {'type': 'xml', 'length': len(response_text)}
        
        else:
            return {'type': 'text', 'length': len(response_text)}