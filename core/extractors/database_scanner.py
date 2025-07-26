"""
Database Scanner - ماسح قواعد البيانات المتقدم
المرحلة الأولى: محرك الاستخراج العميق

يكتشف ويحلل:
1. أنواع قواعد البيانات المستخدمة
2. هيكل قواعد البيانات والجداول
3. العلاقات بين البيانات
4. أنماط الاستعلامات والAPIات
"""

import re
import json
import logging
import hashlib
from typing import Dict, List, Set, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass
from datetime import datetime
import asyncio

from bs4 import BeautifulSoup, Tag
import aiohttp

@dataclass
class DatabaseScanConfig:
    """تكوين مسح قواعد البيانات"""
    scan_api_endpoints: bool = True
    analyze_form_structures: bool = True
    detect_database_patterns: bool = True
    scan_javascript_queries: bool = True
    analyze_url_patterns: bool = True
    detect_orm_patterns: bool = True
    scan_admin_interfaces: bool = True
    deep_pattern_analysis: bool = True

class DatabaseScanner:
    """ماسح قواعد البيانات الذكي"""
    
    def __init__(self, config: Optional[DatabaseScanConfig] = None):
        self.config = config or DatabaseScanConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # نتائج المسح
        self.scan_results = {
            'database_types': [],
            'detected_tables': [],
            'api_endpoints': [],
            'form_structures': [],
            'query_patterns': [],
            'admin_interfaces': [],
            'data_relationships': [],
            'security_findings': []
        }
        
        # أنماط قواعد البيانات
        self.database_patterns = {
            'mysql': [
                r'mysql://',
                r'SELECT.*FROM',
                r'INSERT INTO',
                r'UPDATE.*SET',
                r'DELETE FROM',
                r'mysqli_',
                r'PDO.*mysql',
                r'SHOW TABLES',
                r'DESCRIBE',
                r'mysql_connect',
                r'mysql_query'
            ],
            'postgresql': [
                r'postgresql://',
                r'postgres://',
                r'pg_connect',
                r'psycopg2',
                r'PostgreSQL',
                r'SELECT.*FROM.*pg_',
                r'\\dt',
                r'\\d\+',
                r'pg_dump'
            ],
            'mongodb': [
                r'mongodb://',
                r'db\.collection',
                r'find\(\)',
                r'insertOne',
                r'updateOne',
                r'deleteOne',
                r'aggregate',
                r'mongoose',
                r'MongoClient',
                r'ObjectId'
            ],
            'redis': [
                r'redis://',
                r'Redis',
                r'redis\.get',
                r'redis\.set',
                r'redis\.hget',
                r'redis\.lpush',
                r'HGETALL',
                r'ZADD'
            ],
            'sqlite': [
                r'sqlite:',
                r'\.db$',
                r'sqlite3',
                r'PRAGMA',
                r'sqlite_master',
                r'\.sqlite'
            ],
            'elasticsearch': [
                r'elasticsearch',
                r'_search',
                r'_bulk',
                r'_index',
                r'query.*match',
                r'aggregations'
            ]
        }
        
        # أنماط ORM
        self.orm_patterns = {
            'django': [
                r'models\.Model',
                r'ForeignKey',
                r'ManyToManyField',
                r'CharField',
                r'IntegerField',
                r'DateTimeField',
                r'django\.db'
            ],
            'laravel': [
                r'Eloquent',
                r'Schema::',
                r'Migration',
                r'hasMany',
                r'belongsTo',
                r'Model::',
                r'DB::'
            ],
            'rails': [
                r'ActiveRecord',
                r'has_many',
                r'belongs_to',
                r'validates',
                r'migration',
                r'create_table',
                r'add_column'
            ],
            'sqlalchemy': [
                r'SQLAlchemy',
                r'db\.Model',
                r'db\.Column',
                r'relationship',
                r'backref',
                r'foreign_key'
            ]
        }
        
        # أنماط جداول شائعة
        self.common_table_patterns = [
            r'\busers?\b',
            r'\bproducts?\b',
            r'\borders?\b',
            r'\bcustomers?\b',
            r'\bcategories\b',
            r'\barticles?\b',
            r'\bposts?\b',
            r'\bcomments?\b',
            r'\breviews?\b',
            r'\bpayments?\b',
            r'\binvoices?\b',
            r'\bsessions?\b',
            r'\baddresses?\b',
            r'\bpermissions?\b',
            r'\broles?\b'
        ]
        
        # أنماط API endpoints
        self.api_patterns = [
            r'/api/v?\d*/users?',
            r'/api/v?\d*/products?',
            r'/api/v?\d*/orders?',
            r'/api/v?\d*/auth',
            r'/api/v?\d*/login',
            r'/api/v?\d*/register',
            r'/api/v?\d*/search',
            r'/api/v?\d*/data',
            r'/graphql',
            r'/rest/',
            r'\.json$',
            r'\.xml$'
        ]
    
    async def __aenter__(self):
        """بدء جلسة المسح"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """إنهاء جلسة المسح"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def scan_website_database(self, site_map: Dict[str, Dict], base_url: str) -> Dict[str, Any]:
        """مسح شامل لقواعد البيانات في الموقع"""
        logging.info("بدء مسح قواعد البيانات...")
        
        # مسح كل صفحة
        scan_tasks = []
        for page_url, page_data in list(site_map.items())[:20]:  # محدود لأول 20 صفحة
            task = asyncio.create_task(self._scan_single_page(page_url))
            scan_tasks.append(task)
        
        await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # التحليل المتقدم
        await self._analyze_database_architecture()
        await self._detect_data_relationships()
        await self._scan_admin_interfaces(base_url)
        
        return self._generate_database_report()
    
    async def _scan_single_page(self, page_url: str):
        """مسح صفحة واحدة"""
        if not self.session:
            return
        
        try:
            async with self.session.get(page_url) as response:
                if response.status != 200:
                    return
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # تحليل النماذج
                if self.config.analyze_form_structures:
                    await self._analyze_forms(soup, page_url)
                
                # كشف أنماط قواعد البيانات
                if self.config.detect_database_patterns:
                    await self._detect_database_types(html_content, page_url)
                
                # تحليل JavaScript للاستعلامات
                if self.config.scan_javascript_queries:
                    await self._analyze_javascript_queries(soup, page_url)
                
                # تحليل أنماط الروابط
                if self.config.analyze_url_patterns:
                    await self._analyze_url_patterns(soup, page_url)
                
                # كشف أنماط ORM
                if self.config.detect_orm_patterns:
                    await self._detect_orm_usage(html_content, page_url)
                
        except Exception as e:
            logging.error(f"خطأ في مسح {page_url}: {e}")
    
    async def _analyze_forms(self, soup: BeautifulSoup, page_url: str):
        """تحليل النماذج لاستنتاج هيكل قاعدة البيانات"""
        forms = soup.find_all('form')
        
        for form in forms:
            if isinstance(form, Tag):
                form_analysis = {
                    'url': page_url,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get').lower(),
                    'fields': [],
                    'inferred_table': '',
                    'data_types': {},
                    'relationships': []
                }
                
                # تحليل الحقول
                for input_tag in form.find_all(['input', 'select', 'textarea']):
                    if isinstance(input_tag, Tag):
                        field_name = input_tag.get('name', '')
                        field_type = input_tag.get('type', 'text')
                        
                        if field_name:
                            form_analysis['fields'].append({
                                'name': field_name,
                                'type': field_type,
                                'required': input_tag.has_attr('required'),
                                'max_length': input_tag.get('maxlength'),
                                'pattern': input_tag.get('pattern')
                            })
                            
                            # استنتاج نوع البيانات
                            data_type = self._infer_data_type(field_name, field_type)
                            form_analysis['data_types'][field_name] = data_type
                            
                            # استنتاج العلاقات
                            if 'id' in field_name.lower() and field_name != 'id':
                                form_analysis['relationships'].append({
                                    'field': field_name,
                                    'related_table': field_name.replace('_id', '').replace('id', ''),
                                    'type': 'foreign_key'
                                })
                
                # استنتاج اسم الجدول
                form_analysis['inferred_table'] = self._infer_table_name(form_analysis['action'], form_analysis['fields'])
                
                self.scan_results['form_structures'].append(form_analysis)
    
    async def _detect_database_types(self, html_content: str, page_url: str):
        """كشف أنواع قواعد البيانات"""
        for db_type, patterns in self.database_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    self.scan_results['database_types'].append({
                        'type': db_type,
                        'pattern': pattern,
                        'url': page_url,
                        'confidence': self._calculate_confidence(pattern, html_content)
                    })
                    break
    
    async def _analyze_javascript_queries(self, soup: BeautifulSoup, page_url: str):
        """تحليل استعلامات JavaScript"""
        scripts = soup.find_all('script')
        
        for script in scripts:
            if isinstance(script, Tag) and script.string:
                script_content = script.string
                
                # البحث عن استعلامات SQL
                sql_patterns = [
                    r'SELECT\s+.*\s+FROM\s+(\w+)',
                    r'INSERT\s+INTO\s+(\w+)',
                    r'UPDATE\s+(\w+)\s+SET',
                    r'DELETE\s+FROM\s+(\w+)'
                ]
                
                for pattern in sql_patterns:
                    matches = re.finditer(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        table_name = match.group(1)
                        self.scan_results['query_patterns'].append({
                            'type': 'sql_query',
                            'table': table_name,
                            'pattern': match.group(0),
                            'url': page_url
                        })
                
                # البحث عن استعلامات MongoDB
                mongo_patterns = [
                    r'db\.(\w+)\.find',
                    r'db\.(\w+)\.insert',
                    r'db\.(\w+)\.update',
                    r'db\.(\w+)\.delete'
                ]
                
                for pattern in mongo_patterns:
                    matches = re.finditer(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        collection_name = match.group(1)
                        self.scan_results['query_patterns'].append({
                            'type': 'mongodb_query',
                            'collection': collection_name,
                            'pattern': match.group(0),
                            'url': page_url
                        })
                
                # البحث عن API calls
                api_patterns = [
                    r'fetch\(["\']([^"\']*api[^"\']*)["\']',
                    r'axios\.\w+\(["\']([^"\']*api[^"\']*)["\']',
                    r'\.ajax\({[^}]*url[^}]*["\']([^"\']*api[^"\']*)["\']'
                ]
                
                for pattern in api_patterns:
                    matches = re.finditer(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        api_url = match.group(1)
                        self.scan_results['api_endpoints'].append({
                            'url': api_url,
                            'found_in': page_url,
                            'method': self._extract_http_method(match.group(0)),
                            'inferred_resource': self._infer_resource_from_url(api_url)
                        })
    
    async def _analyze_url_patterns(self, soup: BeautifulSoup, page_url: str):
        """تحليل أنماط الروابط لاستنتاج هيكل البيانات"""
        links = soup.find_all('a', href=True)
        
        for link in links:
            if isinstance(link, Tag):
                href = link.get('href', '')
                
                # البحث عن أنماط REST
                for pattern in self.api_patterns:
                    if re.search(pattern, href, re.IGNORECASE):
                        resource = self._infer_resource_from_url(href)
                        self.scan_results['api_endpoints'].append({
                            'url': href,
                            'found_in': page_url,
                            'type': 'rest_endpoint',
                            'inferred_resource': resource
                        })
                
                # البحث عن أنماط إدارة البيانات
                admin_patterns = [
                    r'/admin/',
                    r'/dashboard/',
                    r'/manage/',
                    r'/edit/',
                    r'/create/',
                    r'/delete/',
                    r'/update/'
                ]
                
                for pattern in admin_patterns:
                    if re.search(pattern, href, re.IGNORECASE):
                        self.scan_results['admin_interfaces'].append({
                            'url': href,
                            'type': pattern.strip('/'),
                            'found_in': page_url
                        })
    
    async def _detect_orm_usage(self, html_content: str, page_url: str):
        """كشف استخدام ORM"""
        for orm, patterns in self.orm_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    self.scan_results['database_types'].append({
                        'type': f'{orm}_orm',
                        'pattern': pattern,
                        'url': page_url,
                        'confidence': 'high'
                    })
                    break
    
    def _infer_data_type(self, field_name: str, field_type: str) -> str:
        """استنتاج نوع البيانات من اسم ونوع الحقل"""
        field_name_lower = field_name.lower()
        
        # أنواع محددة
        if field_type in ['email']:
            return 'email'
        elif field_type in ['password']:
            return 'password_hash'
        elif field_type in ['number']:
            return 'integer'
        elif field_type in ['date']:
            return 'date'
        elif field_type in ['datetime-local']:
            return 'datetime'
        elif field_type in ['tel']:
            return 'phone'
        elif field_type in ['url']:
            return 'url'
        
        # من اسم الحقل
        if 'email' in field_name_lower:
            return 'email'
        elif 'password' in field_name_lower:
            return 'password_hash'
        elif 'phone' in field_name_lower or 'tel' in field_name_lower:
            return 'phone'
        elif 'date' in field_name_lower:
            return 'date'
        elif 'time' in field_name_lower:
            return 'datetime'
        elif 'price' in field_name_lower or 'amount' in field_name_lower:
            return 'decimal'
        elif 'age' in field_name_lower or 'count' in field_name_lower:
            return 'integer'
        elif 'description' in field_name_lower or 'content' in field_name_lower:
            return 'text'
        elif field_name_lower.endswith('_id') or field_name_lower == 'id':
            return 'integer'
        else:
            return 'varchar'
    
    def _infer_table_name(self, action: str, fields: List[Dict]) -> str:
        """استنتاج اسم الجدول من النموذج"""
        # من مسار العمل
        if action:
            path_parts = action.strip('/').split('/')
            for part in path_parts:
                if any(pattern.strip('\\b') in part.lower() for pattern in self.common_table_patterns):
                    return part.lower()
        
        # من أسماء الحقول
        field_names = [field['name'].lower() for field in fields]
        for pattern in self.common_table_patterns:
            pattern_clean = pattern.strip('\\b')
            if any(pattern_clean in name for name in field_names):
                return pattern_clean
        
        return 'unknown_table'
    
    def _extract_http_method(self, code: str) -> str:
        """استخراج HTTP method"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        for method in methods:
            if method.lower() in code.lower():
                return method
        return 'GET'
    
    def _infer_resource_from_url(self, url: str) -> str:
        """استنتاج نوع المورد من الرابط"""
        path_parts = url.strip('/').split('/')
        
        for part in path_parts:
            for pattern in self.common_table_patterns:
                pattern_clean = pattern.strip('\\b')
                if pattern_clean in part.lower():
                    return pattern_clean
        
        # آخر جزء من المسار
        if path_parts:
            return path_parts[-1].lower()
        
        return 'unknown'
    
    def _calculate_confidence(self, pattern: str, content: str) -> str:
        """حساب مستوى الثقة في الكشف"""
        matches = len(re.findall(pattern, content, re.IGNORECASE))
        
        if matches >= 5:
            return 'very_high'
        elif matches >= 3:
            return 'high'
        elif matches >= 1:
            return 'medium'
        else:
            return 'low'
    
    async def _analyze_database_architecture(self):
        """تحليل بنية قاعدة البيانات المستنتجة"""
        # تجميع الجداول المكتشفة
        tables = set()
        
        # من النماذج
        for form in self.scan_results['form_structures']:
            if form['inferred_table'] != 'unknown_table':
                tables.add(form['inferred_table'])
        
        # من الاستعلامات
        for query in self.scan_results['query_patterns']:
            if 'table' in query:
                tables.add(query['table'])
            elif 'collection' in query:
                tables.add(query['collection'])
        
        # من endpoints
        for endpoint in self.scan_results['api_endpoints']:
            if endpoint['inferred_resource'] != 'unknown':
                tables.add(endpoint['inferred_resource'])
        
        self.scan_results['detected_tables'] = list(tables)
    
    async def _detect_data_relationships(self):
        """كشف العلاقات بين البيانات"""
        relationships = []
        
        # من النماذج
        for form in self.scan_results['form_structures']:
            relationships.extend(form.get('relationships', []))
        
        # من أسماء الحقول
        all_tables = set(self.scan_results['detected_tables'])
        for form in self.scan_results['form_structures']:
            for field in form['fields']:
                field_name = field['name'].lower()
                for table in all_tables:
                    if f"{table}_id" == field_name or f"{table}id" == field_name:
                        relationships.append({
                            'from_table': form['inferred_table'],
                            'to_table': table,
                            'field': field_name,
                            'type': 'foreign_key'
                        })
        
        self.scan_results['data_relationships'] = relationships
    
    async def _scan_admin_interfaces(self, base_url: str):
        """مسح واجهات الإدارة المحتملة"""
        admin_paths = [
            '/admin/',
            '/administration/',
            '/dashboard/',
            '/manage/',
            '/control/',
            '/cp/',
            '/backend/',
            '/cms/',
            '/wp-admin/',
            '/phpmyadmin/',
            '/adminer/'
        ]
        
        if not self.session:
            return
        
        for path in admin_paths:
            admin_url = urljoin(base_url, path)
            try:
                async with self.session.get(admin_url, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        if any(word in content.lower() for word in ['login', 'admin', 'dashboard', 'manage']):
                            self.scan_results['admin_interfaces'].append({
                                'url': admin_url,
                                'type': 'admin_panel',
                                'status': 'accessible',
                                'login_required': 'login' in content.lower()
                            })
            except:
                pass  # تجاهل الأخطاء
    
    def _generate_database_report(self) -> Dict[str, Any]:
        """إنشاء تقرير قاعدة البيانات النهائي"""
        # إحصائيات
        unique_db_types = list(set(item['type'] for item in self.scan_results['database_types']))
        unique_tables = self.scan_results['detected_tables']
        total_endpoints = len(self.scan_results['api_endpoints'])
        total_forms = len(self.scan_results['form_structures'])
        
        return {
            'database_summary': {
                'detected_database_types': unique_db_types,
                'total_tables_discovered': len(unique_tables),
                'total_api_endpoints': total_endpoints,
                'total_forms_analyzed': total_forms,
                'relationships_found': len(self.scan_results['data_relationships']),
                'admin_interfaces_found': len(self.scan_results['admin_interfaces'])
            },
            
            'database_schema': {
                'tables': unique_tables,
                'relationships': self.scan_results['data_relationships'],
                'inferred_structure': self._build_schema_structure()
            },
            
            'api_analysis': {
                'endpoints': self.scan_results['api_endpoints'],
                'resources': list(set(ep['inferred_resource'] for ep in self.scan_results['api_endpoints'])),
                'crud_operations': self._analyze_crud_operations()
            },
            
            'security_analysis': {
                'admin_interfaces': self.scan_results['admin_interfaces'],
                'potential_vulnerabilities': self._analyze_security_risks(),
                'recommendations': self._generate_security_recommendations()
            },
            
            'detailed_findings': {
                'database_types': self.scan_results['database_types'],
                'form_structures': self.scan_results['form_structures'],
                'query_patterns': self.scan_results['query_patterns']
            }
        }
    
    def _build_schema_structure(self) -> Dict[str, Any]:
        """بناء هيكل المخطط المستنتج"""
        schema = {}
        
        for table in self.scan_results['detected_tables']:
            schema[table] = {
                'fields': [],
                'relationships': []
            }
            
            # من النماذج
            for form in self.scan_results['form_structures']:
                if form['inferred_table'] == table:
                    schema[table]['fields'].extend(form['fields'])
                    schema[table]['relationships'].extend(form.get('relationships', []))
        
        return schema
    
    def _analyze_crud_operations(self) -> Dict[str, int]:
        """تحليل عمليات CRUD"""
        operations = {'create': 0, 'read': 0, 'update': 0, 'delete': 0}
        
        for endpoint in self.scan_results['api_endpoints']:
            method = endpoint.get('method', 'GET').upper()
            if method == 'POST':
                operations['create'] += 1
            elif method == 'GET':
                operations['read'] += 1
            elif method in ['PUT', 'PATCH']:
                operations['update'] += 1
            elif method == 'DELETE':
                operations['delete'] += 1
        
        return operations
    
    def _analyze_security_risks(self) -> List[str]:
        """تحليل المخاطر الأمنية"""
        risks = []
        
        # واجهات إدارة مكشوفة
        accessible_admin = [ai for ai in self.scan_results['admin_interfaces'] if ai.get('status') == 'accessible']
        if accessible_admin:
            risks.append(f"تم العثور على {len(accessible_admin)} واجهة إدارة قابلة للوصول")
        
        # endpoints بدون حماية
        unprotected_endpoints = [ep for ep in self.scan_results['api_endpoints'] if 'auth' not in ep['url'].lower()]
        if len(unprotected_endpoints) > len(self.scan_results['api_endpoints']) * 0.8:
            risks.append("معظم endpoints API قد تكون بدون حماية")
        
        # نماذج بدون CSRF protection
        unprotected_forms = [form for form in self.scan_results['form_structures'] 
                           if not any(field['name'].lower() in ['_token', 'csrf_token'] for field in form['fields'])]
        if unprotected_forms:
            risks.append(f"تم العثور على {len(unprotected_forms)} نموذج بدون حماية CSRF")
        
        return risks
    
    def _generate_security_recommendations(self) -> List[str]:
        """إنشاء توصيات الأمان"""
        recommendations = []
        
        if self.scan_results['admin_interfaces']:
            recommendations.append("تأمين واجهات الإدارة بكلمات مرور قوية ومصادقة ثنائية")
        
        if self.scan_results['api_endpoints']:
            recommendations.append("إضافة آليات المصادقة والتفويض لجميع API endpoints")
        
        if self.scan_results['form_structures']:
            recommendations.append("إضافة حماية CSRF لجميع النماذج")
            recommendations.append("تطبيق التحقق من صحة البيانات على جانب الخادم")
        
        recommendations.append("تشفير البيانات الحساسة في قاعدة البيانات")
        recommendations.append("تطبيق مبدأ الصلاحيات الأدنى للوصول لقاعدة البيانات")
        
        return recommendations