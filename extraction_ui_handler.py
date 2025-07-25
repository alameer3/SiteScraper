"""
معالج واجهة الاستخراج المتطورة
Advanced Extraction UI Handler
- التحكم في عمليات الاستخراج عبر واجهة ويب آمنة
- إدارة الأذونات والموافقات
- عرض المعاينات والتحليلات
"""

from flask import render_template, request, jsonify, session, redirect, url_for
from enhanced_website_extractor import (
    EnhancedWebsiteExtractor, 
    ExtractionConfig, 
    ExtractionLevel, 
    PermissionType,
    create_extraction_config
)
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ExtractionUIHandler:
    """معالج واجهة الاستخراج المتطورة"""
    
    def __init__(self, app):
        self.app = app
        self.active_extractors: Dict[str, EnhancedWebsiteExtractor] = {}
        self.pending_approvals: Dict[str, Dict] = {}
        
    def register_routes(self):
        """تسجيل مسارات واجهة الاستخراج"""
        
        @self.app.route('/advanced-extractor')
        def advanced_extractor_page():
            """صفحة الاستخراج المتطورة"""
            return render_template('advanced_extractor.html')
        
        @self.app.route('/api/extraction/analyze', methods=['POST'])
        def analyze_for_extraction():
            """تحليل الموقع لإنشاء معاينة الاستخراج"""
            try:
                data = request.get_json()
                url = data.get('url')
                level = data.get('level', 'standard')
                max_pages = data.get('max_pages', 5)
                remove_ads = data.get('remove_ads', True)
                
                if not url:
                    return jsonify({'error': 'URL مطلوب'}), 400
                
                # إنشاء إعدادات الاستخراج
                config = create_extraction_config(
                    url=url,
                    level=level,
                    max_pages=max_pages,
                    remove_ads=remove_ads
                )
                
                # إنشاء أداة الاستخراج
                extractor = EnhancedWebsiteExtractor(config)
                
                # تحليل أولي للموقع
                preview = extractor.analyze_website_preview()
                
                # حفظ الأداة للاستخدام اللاحق
                session_id = self._generate_session_id()
                session['extraction_session'] = session_id
                self.active_extractors[session_id] = extractor
                
                return jsonify({
                    'status': 'success',
                    'session_id': session_id,
                    'preview': {
                        'target_url': preview.target_url,
                        'estimated_pages': preview.estimated_pages,
                        'estimated_images': preview.estimated_images,
                        'estimated_css_files': preview.estimated_css_files,
                        'estimated_js_files': preview.estimated_js_files,
                        'estimated_size_mb': preview.estimated_size_mb,
                        'detected_technologies': preview.detected_technologies,
                        'potential_issues': preview.potential_issues,
                        'required_permissions': [p.value for p in preview.required_permissions],
                        'extraction_time_estimate': preview.extraction_time_estimate
                    }
                })
                
            except Exception as e:
                logger.error(f"خطأ في التحليل: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/extraction/request-permissions', methods=['POST'])
        def request_permissions():
            """طلب الأذونات من المستخدم"""
            try:
                data = request.get_json()
                session_id = data.get('session_id')
                permissions = data.get('permissions', [])
                
                if not session_id or session_id not in self.active_extractors:
                    return jsonify({'error': 'جلسة استخراج غير صالحة'}), 400
                
                extractor = self.active_extractors[session_id]
                
                # تسجيل طلب الأذونات
                approval_id = self._generate_approval_id()
                self.pending_approvals[approval_id] = {
                    'session_id': session_id,
                    'permissions': permissions,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending'
                }
                
                return jsonify({
                    'status': 'permissions_requested',
                    'approval_id': approval_id,
                    'permissions': permissions,
                    'message': 'يرجى مراجعة الأذونات المطلوبة والموافقة عليها'
                })
                
            except Exception as e:
                logger.error(f"خطأ في طلب الأذونات: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/extraction/approve-permissions', methods=['POST'])
        def approve_permissions():
            """الموافقة على الأذونات"""
            try:
                data = request.get_json()
                approval_id = data.get('approval_id')
                approved_permissions = data.get('approved_permissions', [])
                
                if approval_id not in self.pending_approvals:
                    return jsonify({'error': 'طلب موافقة غير صالح'}), 400
                
                approval = self.pending_approvals[approval_id]
                session_id = approval['session_id']
                
                if session_id not in self.active_extractors:
                    return jsonify({'error': 'جلسة استخراج منتهية الصلاحية'}), 400
                
                extractor = self.active_extractors[session_id]
                
                # تحديث الأذونات في الأداة
                for permission_str in approved_permissions:
                    try:
                        permission = PermissionType(permission_str)
                        extractor.config.user_permissions[permission] = True
                    except ValueError:
                        logger.warning(f"إذن غير معروف: {permission_str}")
                
                # تحديث حالة الموافقة
                approval['status'] = 'approved'
                approval['approved_permissions'] = approved_permissions
                
                return jsonify({
                    'status': 'permissions_approved',
                    'approved_permissions': approved_permissions,
                    'message': 'تم الموافقة على الأذونات بنجاح'
                })
                
            except Exception as e:
                logger.error(f"خطأ في الموافقة: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/extraction/start', methods=['POST'])
        def start_extraction():
            """بدء عملية الاستخراج"""
            try:
                data = request.get_json()
                session_id = data.get('session_id')
                user_confirmed = data.get('confirmed', False)
                
                if not session_id or session_id not in self.active_extractors:
                    return jsonify({'error': 'جلسة استخراج غير صالحة'}), 400
                
                extractor = self.active_extractors[session_id]
                
                # بدء الاستخراج
                result = extractor.start_extraction(user_confirmed=user_confirmed)
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"خطأ في بدء الاستخراج: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/extraction/status/<session_id>')
        def extraction_status(session_id):
            """حالة عملية الاستخراج"""
            try:
                if session_id not in self.active_extractors:
                    return jsonify({'error': 'جلسة غير موجودة'}), 404
                
                extractor = self.active_extractors[session_id]
                summary = extractor.get_extraction_summary()
                
                return jsonify({
                    'status': 'active',
                    'summary': summary
                })
                
            except Exception as e:
                logger.error(f"خطأ في الحصول على الحالة: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/extraction/history')
        def extraction_history():
            """تاريخ عمليات الاستخراج"""
            try:
                # هنا يمكن إضافة منطق لاسترجاع التاريخ من قاعدة البيانات
                history = [
                    {
                        'id': session_id,
                        'url': extractor.config.url,
                        'level': extractor.config.extraction_level.value,
                        'status': 'completed' if extractor.stats.get('end_time') else 'active',
                        'timestamp': extractor.stats.get('start_time', datetime.now()).isoformat()
                    }
                    for session_id, extractor in self.active_extractors.items()
                ]
                
                return jsonify({
                    'status': 'success',
                    'history': history
                })
                
            except Exception as e:
                logger.error(f"خطأ في استرجاع التاريخ: {e}")
                return jsonify({'error': str(e)}), 500
    
    def _generate_session_id(self) -> str:
        """إنشاء معرف جلسة فريد"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _generate_approval_id(self) -> str:
        """إنشاء معرف موافقة فريد"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def cleanup_expired_sessions(self):
        """تنظيف الجلسات المنتهية الصلاحية"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, extractor in self.active_extractors.items():
            if extractor.stats.get('start_time'):
                time_diff = current_time - extractor.stats['start_time']
                if time_diff.total_seconds() > 3600:  # ساعة واحدة
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_extractors[session_id]
            logger.info(f"تم حذف الجلسة المنتهية: {session_id}")