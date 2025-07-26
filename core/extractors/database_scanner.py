"""
ماسح قواعد البيانات المتقدم
Advanced Database Scanner - Deep Database Structure Analysis
"""

import asyncio
import aiohttp
import logging
import re
import json
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag

@dataclass
class DatabaseScanConfig:
    """إعدادات مسح قاعدة البيانات"""
    scan_depth: int = 3
    analyze_forms: bool = True
    detect_apis: bool = True
    analyze_javascript: bool = True
    scan_common_endpoints: bool = True
    timeout: int = 10

class DatabaseScanner:
    """ماسح قواعد البيانات المتقدم"""

    def __init__(self, config: Optional[DatabaseScanConfig] = None):
        self.config = config or DatabaseScanConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.discovered_endpoints: Set[str] = set()
        self.database_indicators: Dict[str, Any] = {}
        self.data_models: List[Dict[str, Any]] = []

    async def scan_database_structure(self, target_url: str) -> Dict[str, Any]:
        """مسح شامل لبنية قاعدة البيانات"""
        logging.info(f"بدء مسح قاعدة البيانات للموقع: {target_url}")

        try:
            self.session = aiohttp.ClientSession()

            scan_results = {
                'database_type': 'unknown',
                'detected_tables': [],
                'data_models': [],
                'relationships': [],
                'crud_operations': [],
                'api_endpoints': [],
                'security_analysis': {},
                'recommendations': []
            }

            # مسح البنية الأساسية
            basic_structure = await self._scan_basic_structure(target_url)
            scan_results.update(basic_structure)

            # تحليل النماذج والبيانات
            if self.config.analyze_forms:
                form_analysis = await self._analyze_forms_for_database(target_url)
                scan_results['data_models'].extend(form_analysis)

            # اكتشاف API endpoints
            if self.config.detect_apis:
                api_analysis = await self._discover_database_apis(target_url)
                scan_results['api_endpoints'] = api_analysis

            # تحليل JavaScript للحصول على معلومات قاعدة البيانات
            if self.config.analyze_javascript:
                js_analysis = await self._analyze_javascript_database_calls(target_url)
                scan_results['crud_operations'].extend(js_analysis)

            # مسح النقاط النهائية الشائعة
            if self.config.scan_common_endpoints:
                common_endpoints = await self._scan_common_database_endpoints(target_url)
                scan_results['api_endpoints'].extend(common_endpoints)

            # تحليل العلاقات
            scan_results['relationships'] = self._analyze_data_relationships(scan_results)

            # تحليل الأمان
            scan_results['security_analysis'] = await self._analyze_database_security(target_url)

            # إنتاج التوصيات
            scan_results['recommendations'] = self._generate_database_recommendations(scan_results)

            return scan_results

        except Exception as e:
            logging.error(f"خطأ في مسح قاعدة البيانات: {e}")
            return {'error': str(e)}

        finally:
            if self.session:
                await self.session.close()

    async def _scan_basic_structure(self, url: str) -> Dict[str, Any]:
        """مسح البنية الأساسية"""
        structure = {
            'database_type': 'unknown',
            'detected_tables': [],
            'technology_indicators': []
        }

        async with self.session.get(url) as response:
            html_content = await response.text()

            # فحص مؤشرات قاعدة البيانات
            db_indicators = {
                'mysql': ['mysql', 'phpmyadmin', 'innodb'],
                'postgresql': ['postgresql', 'postgres', 'psql'],
                'mongodb': ['mongodb', 'mongo', 'bson'],
                'sqlite': ['sqlite', 'sqlite3'],
                'oracle': ['oracle', 'plsql'],
                'sqlserver': ['sqlserver', 'mssql', 'tsql']
            }

            for db_type, indicators in db_indicators.items():
                if any(indicator in html_content.lower() for indicator in indicators):
                    structure['database_type'] = db_type
                    structure['technology_indicators'].extend(indicators)
                    break

        return structure

    async def _analyze_forms_for_database(self, url: str) -> List[Dict[str, Any]]:
        """تحليل النماذج لاستنتاج بنية قاعدة البيانات"""
        data_models = []

        async with self.session.get(url) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')

            forms = soup.find_all('form')
            for form in forms:
                if isinstance(form, Tag):
                    model = {
                        'table_name': self._extract_table_name_from_form(form),
                        'fields': [],
                        'validation_rules': [],
                        'relationships': []
                    }

                    # تحليل حقول النموذج
                    fields = form.find_all(['input', 'select', 'textarea'])
                    for field in fields:
                        if isinstance(field, Tag):
                            field_info = {
                                'name': field.get('name', ''),
                                'type': self._map_html_type_to_db_type(field),
                                'required': field.has_attr('required'),
                                'max_length': field.get('maxlength'),
                                'validation': field.get('pattern', '')
                            }
                            model['fields'].append(field_info)

                    if model['fields']:
                        data_models.append(model)

        return data_models

    async def _discover_database_apis(self, url: str) -> List[Dict[str, Any]]:
        """اكتشاف API endpoints المتعلقة بقاعدة البيانات"""
        api_endpoints = []

        async with self.session.get(url) as response:
            html_content = await response.text()

            # البحث عن أنماط API
            api_patterns = [
                r'/api/[a-zA-Z]+/?',
                r'/rest/[a-zA-Z]+/?',
                r'/data/[a-zA-Z]+/?',
                r'/json/[a-zA-Z]+/?'
            ]

            for pattern in api_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if match not in self.discovered_endpoints:
                        self.discovered_endpoints.add(match)

                        # محاولة الوصول للـ endpoint
                        endpoint_info = await self._test_api_endpoint(url, match)
                        if endpoint_info:
                            api_endpoints.append(endpoint_info)

        return api_endpoints

    async def _analyze_javascript_database_calls(self, url: str) -> List[Dict[str, Any]]:
        """تحليل استدعاءات قاعدة البيانات في JavaScript"""
        crud_operations = []

        async with self.session.get(url) as response:
            html_content = await response.text()

            # البحث عن أنماط CRUD في JavaScript
            crud_patterns = {
                'create': [r'\.post\s*\(', r'\.save\s*\(', r'\.create\s*\('],
                'read': [r'\.get\s*\(', r'\.find\s*\(', r'\.fetch\s*\('],
                'update': [r'\.put\s*\(', r'\.patch\s*\(', r'\.update\s*\('],
                'delete': [r'\.delete\s*\(', r'\.remove\s*\(', r'\.destroy\s*\(']
            }

            for operation, patterns in crud_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        crud_operations.append({
                            'operation': operation,
                            'pattern': pattern,
                            'occurrences': len(matches),
                            'source': 'javascript'
                        })

        return crud_operations

    async def _scan_common_database_endpoints(self, url: str) -> List[Dict[str, Any]]:
        """مسح النقاط النهائية الشائعة لقاعدة البيانات"""
        common_endpoints = [
            '/api/users', '/api/products', '/api/orders', '/api/categories',
            '/data/items', '/data/records', '/json/data', '/rest/entities'
        ]

        discovered_endpoints = []

        for endpoint in common_endpoints:
            endpoint_info = await self._test_api_endpoint(url, endpoint)
            if endpoint_info:
                discovered_endpoints.append(endpoint_info)

        return discovered_endpoints

    async def _test_api_endpoint(self, base_url: str, endpoint: str) -> Optional[Dict[str, Any]]:
        """اختبار endpoint للحصول على معلومات"""
        try:
            test_url = urljoin(base_url, endpoint)

            async with self.session.get(test_url, timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as response:
                if response.status < 400:
                    content_type = response.headers.get('Content-Type', '')

                    endpoint_info = {
                        'url': endpoint,
                        'status': response.status,
                        'content_type': content_type,
                        'methods': ['GET']
                    }

                    # محاولة تحليل البيانات المرجعة
                    if 'json' in content_type:
                        try:
                            data = await response.json()
                            endpoint_info['sample_data'] = data
                            endpoint_info['data_structure'] = self._analyze_json_structure(data)
                        except:
                            pass

                    return endpoint_info

        except Exception as e:
            logging.debug(f"فشل في اختبار {endpoint}: {e}")

        return None

    def _extract_table_name_from_form(self, form: Tag) -> str:
        """استخراج اسم الجدول من النموذج"""
        # محاولة استخراج اسم الجدول من action أو class أو id
        action = form.get('action', '')
        form_id = form.get('id', '')
        form_class = ' '.join(form.get('class', []))

        # البحث عن أنماط أسماء الجداول
        table_patterns = [
            r'/([a-zA-Z]+)/?(?:create|edit|update|new)',
            r'form-([a-zA-Z]+)',
            r'([a-zA-Z]+)-form'
        ]

        for pattern in table_patterns:
            for text in [action, form_id, form_class]:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)

        return 'unknown_table'

    def _map_html_type_to_db_type(self, field: Tag) -> str:
        """تحويل نوع HTML إلى نوع قاعدة البيانات"""
        html_type = field.get('type', 'text')
        field_name = field.get('name', '').lower()

        type_mapping = {
            'email': 'VARCHAR(255)',
            'password': 'VARCHAR(255)',
            'number': 'INTEGER',
            'date': 'DATE',
            'datetime-local': 'DATETIME',
            'time': 'TIME',
            'url': 'VARCHAR(255)',
            'tel': 'VARCHAR(20)',
            'checkbox': 'BOOLEAN',
            'file': 'VARCHAR(255)'  # للمسار
        }

        if html_type in type_mapping:
            return type_mapping[html_type]

        # تحليل أكثر تقدماً بناءً على اسم الحقل
        if 'id' in field_name:
            return 'INTEGER PRIMARY KEY'
        elif 'email' in field_name:
            return 'VARCHAR(255) UNIQUE'
        elif 'phone' in field_name or 'tel' in field_name:
            return 'VARCHAR(20)'
        elif 'date' in field_name or 'time' in field_name:
            return 'DATETIME'
        elif 'price' in field_name or 'amount' in field_name:
            return 'DECIMAL(10,2)'
        else:
            max_length = field.get('maxlength')
            if max_length:
                return f'VARCHAR({max_length})'
            return 'TEXT'

    def _analyze_json_structure(self, data: Any) -> Dict[str, Any]:
        """تحليل بنية JSON للحصول على معلومات قاعدة البيانات"""
        structure = {
            'type': type(data).__name__,
            'fields': {}
        }

        if isinstance(data, dict):
            for key, value in data.items():
                structure['fields'][key] = {
                    'type': type(value).__name__,
                    'nullable': value is None
                }
        elif isinstance(data, list) and data:
            # تحليل العنصر الأول للحصول على البنية
            first_item = data[0]
            if isinstance(first_item, dict):
                structure['fields'] = self._analyze_json_structure(first_item)['fields']

        return structure

    def _analyze_data_relationships(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """تحليل العلاقات بين البيانات"""
        relationships = []
        data_models = scan_results.get('data_models', [])

        # البحث عن foreign keys محتملة
        for model in data_models:
            for field in model.get('fields', []):
                field_name = field.get('name', '').lower()

                # البحث عن أنماط foreign key
                if field_name.endswith('_id') or field_name.endswith('id'):
                    related_table = field_name.replace('_id', '').replace('id', '')
                    if related_table:
                        relationships.append({
                            'from_table': model.get('table_name'),
                            'from_field': field_name,
                            'to_table': related_table,
                            'relationship_type': 'foreign_key',
                            'confidence': 0.8
                        })

        return relationships

    async def _analyze_database_security(self, url: str) -> Dict[str, Any]:
        """تحليل أمان قاعدة البيانات"""
        security_analysis = {
            'sql_injection_risk': 'unknown',
            'authentication_required': False,
            'input_validation': [],
            'security_headers': {},
            'recommendations': []
        }

        async with self.session.get(url) as response:
            # فحص Security Headers
            security_headers = {
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options'),
                'X-Frame-Options': response.headers.get('X-Frame-Options'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy')
            }
            security_analysis['security_headers'] = security_headers

            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')

            # فحص Input Validation
            forms = soup.find_all('form')
            for form in forms:
                if isinstance(form, Tag):
                    inputs = form.find_all('input')
                    for input_field in inputs:
                        if isinstance(input_field, Tag):
                            validation_attrs = []
                            if input_field.has_attr('required'):
                                validation_attrs.append('required')
                            if input_field.has_attr('pattern'):
                                validation_attrs.append('pattern')
                            if input_field.has_attr('maxlength'):
                                validation_attrs.append('maxlength')

                            if validation_attrs:
                                security_analysis['input_validation'].append({
                                    'field': input_field.get('name', ''),
                                    'validations': validation_attrs
                                })

        # إنتاج توصيات الأمان
        security_recommendations = [
            'استخدام Prepared Statements لمنع SQL Injection',
            'تطبيق Input Validation على جميع الحقول',
            'تشفير البيانات الحساسة في قاعدة البيانات',
            'تطبيق Access Control والصلاحيات',
            'مراقبة وتسجيل عمليات قاعدة البيانات'
        ]

        security_analysis['recommendations'] = security_recommendations

        return security_analysis

    def _generate_database_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """إنتاج توصيات قاعدة البيانات"""
        recommendations = []

        # توصيات بناءً على نوع قاعدة البيانات المكتشفة
        db_type = scan_results.get('database_type', 'unknown')

        if db_type == 'mysql':
            recommendations.extend([
                'استخدام InnoDB engine للمعاملات',
                'تطبيق indexing على الحقول المستخدمة في البحث',
                'تفعيل query caching لتحسين الأداء'
            ])
        elif db_type == 'postgresql':
            recommendations.extend([
                'استخدام VACUUM ANALYZE لتحسين الأداء',
                'تطبيق partial indexes للاستعلامات المعقدة',
                'استخدام connection pooling'
            ])

        # توصيات عامة
        recommendations.extend([
            'إنشاء backup منتظم لقاعدة البيانات',
            'مراقبة أداء الاستعلامات وتحسينها',
            'تطبيق data validation على مستوى التطبيق',
            'استخدام environment variables للاتصال بقاعدة البيانات'
        ])

        return recommendations