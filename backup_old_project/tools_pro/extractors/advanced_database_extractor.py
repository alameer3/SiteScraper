
"""
Advanced Database Extractor - مستخرج قواعد البيانات المتقدم
يحلل ويستخرج بنية قواعد البيانات من المواقع
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class AdvancedDatabaseExtractor:
    """مستخرج قواعد البيانات المتقدم"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extracted_schemas = {}
        self.detected_databases = []
        self.api_patterns = []
        
    async def extract_database_structure(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """استخراج بنية قاعدة البيانات الكاملة"""
        self.logger.info("بدء استخراج بنية قاعدة البيانات...")
        
        database_analysis = {
            'detected_database_types': [],
            'extracted_schemas': {},
            'api_endpoints_analysis': {},
            'form_field_analysis': {},
            'data_relationships': {},
            'crud_operations': {},
            'database_indicators': {}
        }
        
        try:
            # 1. اكتشاف نوع قاعدة البيانات
            database_analysis['detected_database_types'] = await self._detect_database_types(url, session)
            
            # 2. تحليل نقاط API للحصول على بنية البيانات
            database_analysis['api_endpoints_analysis'] = await self._analyze_api_endpoints(url, session)
            
            # 3. تحليل النماذج لاستنباط بنية البيانات
            database_analysis['form_field_analysis'] = await self._analyze_form_fields(url, session)
            
            # 4. استخراج العلاقات بين البيانات
            database_analysis['data_relationships'] = await self._extract_data_relationships(url, session)
            
            # 5. تحليل عمليات CRUD
            database_analysis['crud_operations'] = await self._analyze_crud_operations(url, session)
            
            # 6. البحث عن مؤشرات قاعدة البيانات
            database_analysis['database_indicators'] = await self._find_database_indicators(url, session)
            
            # 7. إنشاء مخططات قاعدة البيانات المقترحة
            database_analysis['extracted_schemas'] = await self._generate_database_schemas(database_analysis)
            
        except Exception as e:
            self.logger.error(f"خطأ في استخراج بنية قاعدة البيانات: {e}")
            database_analysis['error'] = str(e)
        
        return database_analysis
    
    async def _detect_database_types(self, url: str, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """اكتشاف أنواع قواعد البيانات المستخدمة"""
        detected_types = []
        
        async with session.get(url) as response:
            html_content = await response.text()
            headers = dict(response.headers)
            
            # فحص Headers للحصول على معلومات الخادم
            server_header = headers.get('Server', '').lower()
            x_powered_by = headers.get('X-Powered-By', '').lower()
            
            # مؤشرات قواعد البيانات المختلفة
            database_indicators = {
                'mysql': ['mysql', 'phpmyadmin', 'mysql_connect'],
                'postgresql': ['postgresql', 'postgres', 'pg_connect'],
                'mongodb': ['mongodb', 'mongo', 'mongoose'],
                'sqlite': ['sqlite', 'sqlite3'],
                'oracle': ['oracle', 'oci_connect'],
                'mssql': ['mssql', 'sqlserver', 'sql server'],
                'redis': ['redis', 'redis-server'],
                'firebase': ['firebase', 'firestore', 'realtime database'],
                'supabase': ['supabase'],
                'aws_dynamodb': ['dynamodb', 'aws'],
                'prisma': ['prisma', '@prisma/client'],
                'sequelize': ['sequelize'],
                'typeorm': ['typeorm'],
                'mongoose': ['mongoose', 'mongodb']
            }
            
            content_to_check = html_content + server_header + x_powered_by
            
            for db_type, indicators in database_indicators.items():
                for indicator in indicators:
                    if indicator in content_to_check.lower():
                        confidence = self._calculate_detection_confidence(content_to_check, indicators)
                        detected_types.append({
                            'type': db_type,
                            'confidence': confidence,
                            'indicator_found': indicator,
                            'detection_method': 'content_analysis'
                        })
                        break
            
            # فحص JavaScript للبحث عن اتصالات قاعدة البيانات
            script_analysis = await self._analyze_js_for_database_connections(html_content)
            detected_types.extend(script_analysis)
        
        return detected_types
    
    def _calculate_detection_confidence(self, content: str, indicators: List[str]) -> float:
        """حساب درجة الثقة في اكتشاف قاعدة البيانات"""
        found_indicators = sum(1 for indicator in indicators if indicator in content.lower())
        return min(found_indicators / len(indicators) * 100, 100)
    
    async def _analyze_js_for_database_connections(self, html_content: str) -> List[Dict[str, Any]]:
        """تحليل JavaScript للبحث عن اتصالات قاعدة البيانات"""
        detections = []
        
        # أنماط اتصال قواعد البيانات في JavaScript
        connection_patterns = {
            'firebase': [
                r'firebase\.initializeApp',
                r'getFirestore\(\)',
                r'firebase\.firestore\(\)'
            ],
            'mongodb': [
                r'MongoClient',
                r'mongoose\.connect',
                r'mongodb://'
            ],
            'supabase': [
                r'createClient.*supabase',
                r'supabase\.from\(',
                r'@supabase/supabase-js'
            ],
            'prisma': [
                r'new PrismaClient',
                r'prisma\.\w+\.findMany',
                r'@prisma/client'
            ]
        }
        
        for db_type, patterns in connection_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    detections.append({
                        'type': db_type,
                        'confidence': 85,
                        'indicator_found': pattern,
                        'detection_method': 'javascript_pattern',
                        'matches_count': len(matches)
                    })
        
        return detections
    
    async def _analyze_api_endpoints(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """تحليل نقاط API لاستنباط بنية البيانات"""
        api_analysis = {
            'discovered_endpoints': [],
            'data_structures': {},
            'response_patterns': {},
            'parameter_analysis': {}
        }
        
        # اكتشاف نقاط API الشائعة
        common_api_paths = [
            '/api/users', '/api/user', '/users',
            '/api/posts', '/api/articles', '/posts',
            '/api/products', '/api/items', '/products',
            '/api/categories', '/api/tags',
            '/api/comments', '/api/reviews',
            '/api/orders', '/api/purchases',
            '/api/auth', '/api/login', '/api/register',
            '/api/search', '/api/filter',
            '/api/upload', '/api/files',
            '/api/settings', '/api/config'
        ]
        
        for api_path in common_api_paths:
            endpoint_url = urljoin(url, api_path)
            endpoint_analysis = await self._analyze_single_endpoint(endpoint_url, session)
            
            if endpoint_analysis['accessible']:
                api_analysis['discovered_endpoints'].append({
                    'path': api_path,
                    'url': endpoint_url,
                    'analysis': endpoint_analysis
                })
        
        return api_analysis
    
    async def _analyze_single_endpoint(self, endpoint_url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """تحليل نقطة API واحدة"""
        analysis = {
            'accessible': False,
            'status_code': None,
            'response_type': None,
            'data_structure': {},
            'fields_detected': [],
            'relationships': []
        }
        
        try:
            async with session.get(endpoint_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                analysis['status_code'] = response.status
                analysis['accessible'] = response.status < 400
                
                if analysis['accessible']:
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if 'json' in content_type:
                        try:
                            json_data = await response.json()
                            analysis['response_type'] = 'json'
                            analysis['data_structure'] = self._analyze_json_structure(json_data)
                            analysis['fields_detected'] = self._extract_fields_from_json(json_data)
                        except:
                            pass
                    
                    elif 'xml' in content_type:
                        analysis['response_type'] = 'xml'
                        # يمكن إضافة تحليل XML هنا
                    
                    else:
                        text_data = await response.text()
                        analysis['response_type'] = 'text'
                        # تحليل النص للبحث عن أنماط البيانات
        
        except asyncio.TimeoutError:
            analysis['error'] = 'timeout'
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_json_structure(self, json_data: Any) -> Dict[str, Any]:
        """تحليل بنية JSON لاستنباط مخطط البيانات"""
        if isinstance(json_data, dict):
            structure = {}
            for key, value in json_data.items():
                structure[key] = {
                    'type': type(value).__name__,
                    'nullable': value is None,
                    'sample_value': str(value)[:100] if value is not None else None
                }
                
                if isinstance(value, list) and value:
                    structure[key]['array_item_type'] = type(value[0]).__name__
                    if isinstance(value[0], dict):
                        structure[key]['array_structure'] = self._analyze_json_structure(value[0])
        
        elif isinstance(json_data, list) and json_data:
            structure = {
                'array_type': True,
                'item_structure': self._analyze_json_structure(json_data[0])
            }
        else:
            structure = {
                'type': type(json_data).__name__,
                'sample_value': str(json_data)[:100]
            }
        
        return structure
    
    def _extract_fields_from_json(self, json_data: Any, prefix: str = '') -> List[Dict[str, Any]]:
        """استخراج الحقول من JSON"""
        fields = []
        
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                field_name = f"{prefix}.{key}" if prefix else key
                
                field_info = {
                    'name': field_name,
                    'type': self._infer_field_type(value),
                    'nullable': value is None,
                    'is_array': isinstance(value, list)
                }
                
                # تحليل إضافي للحقول
                if isinstance(value, str):
                    field_info.update(self._analyze_string_field(value))
                elif isinstance(value, (int, float)):
                    field_info['numeric_type'] = 'integer' if isinstance(value, int) else 'float'
                
                fields.append(field_info)
                
                # تحليل متداخل للكائنات والمصفوفات
                if isinstance(value, dict):
                    fields.extend(self._extract_fields_from_json(value, field_name))
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    fields.extend(self._extract_fields_from_json(value[0], field_name))
        
        return fields
    
    def _infer_field_type(self, value: Any) -> str:
        """استنتاج نوع الحقل"""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'unknown'
    
    def _analyze_string_field(self, value: str) -> Dict[str, Any]:
        """تحليل الحقول النصية لتحديد نوعها"""
        analysis = {}
        
        # فحص البريد الإلكتروني
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            analysis['semantic_type'] = 'email'
        
        # فحص URL
        elif re.match(r'^https?://', value):
            analysis['semantic_type'] = 'url'
        
        # فحص التاريخ
        elif re.match(r'^\d{4}-\d{2}-\d{2}', value):
            analysis['semantic_type'] = 'date'
        
        # فحص UUID
        elif re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value.lower()):
            analysis['semantic_type'] = 'uuid'
        
        # فحص رقم الهاتف
        elif re.match(r'^[\+]?[1-9][\d]{0,15}$', value.replace(' ', '').replace('-', '')):
            analysis['semantic_type'] = 'phone'
        
        analysis['max_length'] = len(value)
        
        return analysis
    
    async def _analyze_form_fields(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """تحليل حقول النماذج لاستنباط بنية البيانات"""
        form_analysis = {
            'forms_found': [],
            'field_patterns': {},
            'validation_rules': {},
            'inferred_models': {}
        }
        
        async with session.get(url) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            forms = soup.find_all('form')
            
            for i, form in enumerate(forms):
                form_data = {
                    'form_index': i,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'fields': [],
                    'inferred_model': None
                }
                
                # تحليل حقول النموذج
                fields = form.find_all(['input', 'textarea', 'select'])
                
                for field in fields:
                    field_analysis = self._analyze_form_field(field)
                    form_data['fields'].append(field_analysis)
                
                # استنتاج نموذج البيانات من النموذج
                form_data['inferred_model'] = self._infer_model_from_form(form_data['fields'])
                
                form_analysis['forms_found'].append(form_data)
        
        return form_analysis
    
    def _analyze_form_field(self, field) -> Dict[str, Any]:
        """تحليل حقل نموذج واحد"""
        field_analysis = {
            'tag': field.name,
            'type': field.get('type', ''),
            'name': field.get('name', ''),
            'id': field.get('id', ''),
            'placeholder': field.get('placeholder', ''),
            'required': field.has_attr('required'),
            'pattern': field.get('pattern', ''),
            'min_length': field.get('minlength'),
            'max_length': field.get('maxlength'),
            'min_value': field.get('min'),
            'max_value': field.get('max'),
            'inferred_database_type': None,
            'constraints': []
        }
        
        # استنتاج نوع قاعدة البيانات
        field_type = field_analysis['type'].lower()
        field_name = field_analysis['name'].lower()
        
        if field_type == 'email' or 'email' in field_name:
            field_analysis['inferred_database_type'] = 'VARCHAR(255)'
            field_analysis['constraints'].append('UNIQUE')
        
        elif field_type == 'password':
            field_analysis['inferred_database_type'] = 'VARCHAR(255)'  # للهاش
        
        elif field_type in ['text', 'search']:
            max_length = field_analysis.get('max_length')
            if max_length:
                field_analysis['inferred_database_type'] = f'VARCHAR({max_length})'
            else:
                field_analysis['inferred_database_type'] = 'TEXT'
        
        elif field_type == 'number':
            if field_analysis.get('min_value') and field_analysis.get('max_value'):
                field_analysis['inferred_database_type'] = 'INT'
            else:
                field_analysis['inferred_database_type'] = 'DECIMAL'
        
        elif field_type == 'date':
            field_analysis['inferred_database_type'] = 'DATE'
        
        elif field_type == 'datetime-local':
            field_analysis['inferred_database_type'] = 'DATETIME'
        
        elif field_type == 'checkbox':
            field_analysis['inferred_database_type'] = 'BOOLEAN'
        
        elif field.name == 'select':
            field_analysis['inferred_database_type'] = 'ENUM'
            # استخراج القيم المحتملة
            options = field.find_all('option')
            field_analysis['enum_values'] = [opt.get('value', opt.get_text()) for opt in options]
        
        elif field.name == 'textarea':
            field_analysis['inferred_database_type'] = 'TEXT'
        
        # إضافة قيود إضافية
        if field_analysis['required']:
            field_analysis['constraints'].append('NOT NULL')
        
        if 'id' in field_name or field_name.endswith('_id'):
            field_analysis['constraints'].append('PRIMARY KEY' if field_name == 'id' else 'FOREIGN KEY')
            field_analysis['inferred_database_type'] = 'INT AUTO_INCREMENT' if field_name == 'id' else 'INT'
        
        return field_analysis
    
    def _infer_model_from_form(self, fields: List[Dict]) -> Dict[str, Any]:
        """استنتاج نموذج البيانات من حقول النموذج"""
        model = {
            'table_name': 'unknown',
            'fields': {},
            'relationships': [],
            'indexes': []
        }
        
        # تحديد اسم الجدول من أسماء الحقول
        field_names = [field['name'] for field in fields if field['name']]
        
        if any('user' in name.lower() for name in field_names):
            model['table_name'] = 'users'
        elif any('product' in name.lower() for name in field_names):
            model['table_name'] = 'products'
        elif any('post' in name.lower() or 'article' in name.lower() for name in field_names):
            model['table_name'] = 'posts'
        elif any('comment' in name.lower() for name in field_names):
            model['table_name'] = 'comments'
        elif any('order' in name.lower() for name in field_names):
            model['table_name'] = 'orders'
        
        # بناء تعريفات الحقول
        for field in fields:
            if field['name']:
                model['fields'][field['name']] = {
                    'type': field['inferred_database_type'],
                    'constraints': field['constraints'],
                    'nullable': not field['required']
                }
                
                # إضافة فهارس للحقول المهمة
                if 'email' in field['name'].lower():
                    model['indexes'].append(f"INDEX idx_{field['name']} ({field['name']})")
                
                if field['name'].endswith('_id'):
                    model['relationships'].append({
                        'type': 'belongs_to',
                        'foreign_key': field['name'],
                        'references': field['name'].replace('_id', 's')  # تخمين اسم الجدول المرجعي
                    })
        
        return model
    
    async def _extract_data_relationships(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """استخراج العلاقات بين البيانات"""
        relationships = {
            'detected_relationships': [],
            'foreign_key_patterns': [],
            'junction_tables': [],
            'inheritance_patterns': []
        }
        
        # هذا سيتطلب تحليل أعمق للكود والـ APIs
        # يمكن تطويره أكثر حسب الحاجة
        
        return relationships
    
    async def _analyze_crud_operations(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """تحليل عمليات CRUD"""
        crud_analysis = {
            'create_operations': [],
            'read_operations': [],
            'update_operations': [],
            'delete_operations': [],
            'bulk_operations': []
        }
        
        async with session.get(url) as response:
            html_content = await response.text()
            
            # البحث عن أنماط CRUD في HTML و JavaScript
            crud_patterns = {
                'create': [
                    r'method=["\']post["\']',
                    r'\.post\(',
                    r'INSERT\s+INTO',
                    r'create\w*\(',
                    r'save\(\)',
                    r'add\w*\('
                ],
                'read': [
                    r'method=["\']get["\']',
                    r'\.get\(',
                    r'SELECT\s+',
                    r'find\w*\(',
                    r'search\(',
                    r'fetch\w*\('
                ],
                'update': [
                    r'method=["\']put["\']',
                    r'method=["\']patch["\']',
                    r'\.put\(',
                    r'\.patch\(',
                    r'UPDATE\s+',
                    r'edit\w*\(',
                    r'modify\(',
                    r'update\w*\('
                ],
                'delete': [
                    r'method=["\']delete["\']',
                    r'\.delete\(',
                    r'DELETE\s+FROM',
                    r'remove\w*\(',
                    r'destroy\(',
                    r'delete\w*\('
                ]
            }
            
            for operation, patterns in crud_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        crud_analysis[f'{operation}_operations'].append({
                            'pattern': pattern,
                            'context': html_content[max(0, match.start()-50):match.end()+50],
                            'position': match.start()
                        })
        
        return crud_analysis
    
    async def _find_database_indicators(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """البحث عن مؤشرات قاعدة البيانات"""
        indicators = {
            'connection_strings': [],
            'orm_patterns': [],
            'migration_files': [],
            'admin_panels': []
        }
        
        # البحث عن أنماط ORM
        orm_patterns = [
            r'Model\.extend',
            r'class\s+\w+\(Model\)',
            r'@Entity',
            r'@Table',
            r'mongoose\.Schema',
            r'sequelize\.define',
            r'prisma\.\w+',
            r'ActiveRecord'
        ]
        
        async with session.get(url) as response:
            html_content = await response.text()
            
            for pattern in orm_patterns:
                matches = re.finditer(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    indicators['orm_patterns'].append({
                        'pattern': pattern,
                        'context': html_content[max(0, match.start()-30):match.end()+30]
                    })
        
        return indicators
    
    async def _generate_database_schemas(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء مخططات قاعدة البيانات المقترحة"""
        schemas = {
            'sql_schema': {},
            'nosql_schema': {},
            'prisma_schema': '',
            'mongoose_schema': {},
            'recommended_database': None
        }
        
        # تحليل النماذج المستنتجة من النماذج
        forms_analysis = analysis_data.get('form_field_analysis', {})
        inferred_models = []
        
        for form in forms_analysis.get('forms_found', []):
            if form.get('inferred_model'):
                inferred_models.append(form['inferred_model'])
        
        # إنشاء SQL Schema
        if inferred_models:
            schemas['sql_schema'] = self._generate_sql_schema(inferred_models)
            schemas['prisma_schema'] = self._generate_prisma_schema(inferred_models)
            schemas['mongoose_schema'] = self._generate_mongoose_schema(inferred_models)
        
        # توصية نوع قاعدة البيانات
        detected_types = analysis_data.get('detected_database_types', [])
        if detected_types:
            # اختيار النوع الأعلى ثقة
            best_match = max(detected_types, key=lambda x: x['confidence'])
            schemas['recommended_database'] = best_match['type']
        else:
            # التوصية الافتراضية بناء على التحليل
            if len(inferred_models) > 5:
                schemas['recommended_database'] = 'postgresql'
            else:
                schemas['recommended_database'] = 'sqlite'
        
        return schemas
    
    def _generate_sql_schema(self, models: List[Dict]) -> str:
        """إنشاء SQL Schema"""
        schema_lines = []
        
        for model in models:
            table_name = model['table_name']
            fields = model['fields']
            
            create_table = f"CREATE TABLE {table_name} (\n"
            field_definitions = []
            
            for field_name, field_info in fields.items():
                field_def = f"    {field_name} {field_info['type']}"
                
                if field_info['constraints']:
                    field_def += " " + " ".join(field_info['constraints'])
                
                field_definitions.append(field_def)
            
            create_table += ",\n".join(field_definitions)
            create_table += "\n);"
            
            schema_lines.append(create_table)
            
            # إضافة فهارس
            for index in model.get('indexes', []):
                schema_lines.append(f"{index};")
        
        return "\n\n".join(schema_lines)
    
    def _generate_prisma_schema(self, models: List[Dict]) -> str:
        """إنشاء Prisma Schema"""
        schema_lines = [
            'generator client {',
            '  provider = "prisma-client-js"',
            '}',
            '',
            'datasource db {',
            '  provider = "postgresql"',
            '  url      = env("DATABASE_URL")',
            '}',
            ''
        ]
        
        for model in models:
            table_name = model['table_name']
            fields = model['fields']
            
            model_def = f"model {table_name.title().rstrip('s')} {{\n"
            
            for field_name, field_info in fields.items():
                prisma_type = self._convert_to_prisma_type(field_info['type'])
                nullable = "?" if field_info.get('nullable', True) and 'NOT NULL' not in field_info.get('constraints', []) else ""
                
                field_line = f"  {field_name} {prisma_type}{nullable}"
                
                if 'PRIMARY KEY' in field_info.get('constraints', []):
                    field_line += " @id @default(autoincrement())"
                elif 'UNIQUE' in field_info.get('constraints', []):
                    field_line += " @unique"
                
                model_def += field_line + "\n"
            
            model_def += "}"
            schema_lines.append(model_def)
        
        return "\n\n".join(schema_lines)
    
    def _convert_to_prisma_type(self, sql_type: str) -> str:
        """تحويل نوع SQL إلى نوع Prisma"""
        type_mapping = {
            'INT': 'Int',
            'VARCHAR': 'String',
            'TEXT': 'String',
            'BOOLEAN': 'Boolean',
            'DATE': 'DateTime',
            'DATETIME': 'DateTime',
            'DECIMAL': 'Decimal',
            'FLOAT': 'Float'
        }
        
        for sql_pattern, prisma_type in type_mapping.items():
            if sql_pattern in sql_type.upper():
                return prisma_type
        
        return 'String'  # افتراضي
    
    def _generate_mongoose_schema(self, models: List[Dict]) -> Dict[str, str]:
        """إنشاء Mongoose Schemas"""
        schemas = {}
        
        for model in models:
            table_name = model['table_name']
            fields = model['fields']
            
            schema_def = "const mongoose = require('mongoose');\n\n"
            schema_def += f"const {table_name.rstrip('s')}Schema = new mongoose.Schema({{\n"
            
            field_definitions = []
            for field_name, field_info in fields.items():
                mongoose_type = self._convert_to_mongoose_type(field_info['type'])
                required = 'NOT NULL' in field_info.get('constraints', [])
                
                field_def = f"  {field_name}: {{\n    type: {mongoose_type}"
                
                if required:
                    field_def += ",\n    required: true"
                
                if 'UNIQUE' in field_info.get('constraints', []):
                    field_def += ",\n    unique: true"
                
                field_def += "\n  }"
                field_definitions.append(field_def)
            
            schema_def += ",\n".join(field_definitions)
            schema_def += "\n}, { timestamps: true });\n\n"
            schema_def += f"module.exports = mongoose.model('{table_name.title().rstrip('s')}', {table_name.rstrip('s')}Schema);"
            
            schemas[table_name] = schema_def
        
        return schemas
    
    def _convert_to_mongoose_type(self, sql_type: str) -> str:
        """تحويل نوع SQL إلى نوع Mongoose"""
        type_mapping = {
            'INT': 'Number',
            'VARCHAR': 'String',
            'TEXT': 'String',
            'BOOLEAN': 'Boolean',
            'DATE': 'Date',
            'DATETIME': 'Date',
            'DECIMAL': 'Number',
            'FLOAT': 'Number'
        }
        
        for sql_pattern, mongoose_type in type_mapping.items():
            if sql_pattern in sql_type.upper():
                return mongoose_type
        
        return 'String'  # افتراضي
