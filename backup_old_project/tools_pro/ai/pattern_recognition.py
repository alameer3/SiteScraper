
"""
نظام التعرف على الأنماط بالذكاء الاصطناعي
"""

import re
import ast
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PatternConfig:
    """إعدادات التعرف على الأنماط"""
    enable_design_patterns: bool = True
    enable_code_patterns: bool = True
    enable_ui_patterns: bool = True
    confidence_threshold: float = 0.7

class PatternRecognition:
    """نظام التعرف على الأنماط المتقدم"""
    
    def __init__(self, config: PatternConfig = None):
        self.config = config or PatternConfig()
        self.logger = logging.getLogger(__name__)
        
        # أنماط التصميم المعروفة
        self.design_patterns = {
            'mvc': self._detect_mvc_pattern,
            'singleton': self._detect_singleton_pattern,
            'factory': self._detect_factory_pattern,
            'observer': self._detect_observer_pattern,
            'decorator': self._detect_decorator_pattern
        }
        
        # أنماط واجهة المستخدم
        self.ui_patterns = {
            'navbar': self._detect_navbar_pattern,
            'sidebar': self._detect_sidebar_pattern,
            'modal': self._detect_modal_pattern,
            'carousel': self._detect_carousel_pattern,
            'accordion': self._detect_accordion_pattern,
            'tabs': self._detect_tabs_pattern,
            'dropdown': self._detect_dropdown_pattern
        }
        
        # أنماط الكود
        self.code_patterns = {
            'api_endpoints': self._detect_api_patterns,
            'authentication': self._detect_auth_patterns,
            'database_operations': self._detect_db_patterns,
            'form_handling': self._detect_form_patterns,
            'routing': self._detect_routing_patterns
        }
    
    async def analyze_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل شامل للأنماط"""
        self.logger.info("بدء تحليل الأنماط...")
        
        pattern_analysis = {
            'design_patterns': {},
            'ui_patterns': {},
            'code_patterns': {},
            'architectural_style': '',
            'recommendations': [],
            'confidence_scores': {}
        }
        
        try:
            # تحليل أنماط التصميم
            if self.config.enable_design_patterns:
                design_patterns = await self._analyze_design_patterns(extraction_data)
                pattern_analysis['design_patterns'] = design_patterns
            
            # تحليل أنماط واجهة المستخدم
            if self.config.enable_ui_patterns:
                ui_patterns = await self._analyze_ui_patterns(extraction_data)
                pattern_analysis['ui_patterns'] = ui_patterns
            
            # تحليل أنماط الكود
            if self.config.enable_code_patterns:
                code_patterns = await self._analyze_code_patterns(extraction_data)
                pattern_analysis['code_patterns'] = code_patterns
            
            # تحديد النمط المعماري العام
            architectural_style = self._determine_architectural_style(pattern_analysis)
            pattern_analysis['architectural_style'] = architectural_style
            
            # إنشاء التوصيات
            recommendations = self._generate_recommendations(pattern_analysis)
            pattern_analysis['recommendations'] = recommendations
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الأنماط: {e}")
            pattern_analysis['error'] = str(e)
        
        return pattern_analysis
    
    async def _analyze_design_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل أنماط التصميم"""
        detected_patterns = {}
        
        for pattern_name, detector_func in self.design_patterns.items():
            try:
                result = detector_func(extraction_data)
                if result['detected']:
                    detected_patterns[pattern_name] = result
            except Exception as e:
                self.logger.warning(f"خطأ في كشف نمط {pattern_name}: {e}")
        
        return detected_patterns
    
    async def _analyze_ui_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل أنماط واجهة المستخدم"""
        detected_ui_patterns = {}
        
        html_content = extraction_data.get('content', {}).get('html', '')
        css_content = extraction_data.get('assets', {}).get('css', [])
        js_content = extraction_data.get('assets', {}).get('javascript', [])
        
        for pattern_name, detector_func in self.ui_patterns.items():
            try:
                result = detector_func(html_content, css_content, js_content)
                if result['detected']:
                    detected_ui_patterns[pattern_name] = result
            except Exception as e:
                self.logger.warning(f"خطأ في كشف نمط UI {pattern_name}: {e}")
        
        return detected_ui_patterns
    
    async def _analyze_code_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل أنماط الكود"""
        detected_code_patterns = {}
        
        for pattern_name, detector_func in self.code_patterns.items():
            try:
                result = detector_func(extraction_data)
                if result['detected']:
                    detected_code_patterns[pattern_name] = result
            except Exception as e:
                self.logger.warning(f"خطأ في كشف نمط الكود {pattern_name}: {e}")
        
        return detected_code_patterns
    
    def _detect_mvc_pattern(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """كشف نمط MVC"""
        confidence = 0.0
        evidence = []
        
        # البحث عن مجلدات MVC
        structure = extraction_data.get('structure', {})
        
        if 'models' in str(structure).lower():
            confidence += 0.3
            evidence.append("وجود مجلد أو ملفات models")
        
        if 'views' in str(structure).lower() or 'templates' in str(structure).lower():
            confidence += 0.3
            evidence.append("وجود مجلد views أو templates")
        
        if 'controllers' in str(structure).lower() or 'routes' in str(structure).lower():
            confidence += 0.4
            evidence.append("وجود controllers أو routes")
        
        return {
            'detected': confidence >= self.config.confidence_threshold,
            'confidence': confidence,
            'evidence': evidence,
            'description': 'نمط Model-View-Controller للفصل بين طبقات التطبيق'
        }
    
    def _detect_navbar_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        """كشف نمط شريط التنقل"""
        confidence = 0.0
        evidence = []
        
        # البحث في HTML
        if re.search(r'<nav|navbar|navigation', html, re.IGNORECASE):
            confidence += 0.4
            evidence.append("وجود عنصر nav في HTML")
        
        if re.search(r'class=".*nav.*"', html, re.IGNORECASE):
            confidence += 0.2
            evidence.append("وجود CSS classes للتنقل")
        
        # البحث في CSS
        css_text = ' '.join([item.get('content', '') for item in css])
        if re.search(r'\.nav|\.navbar|\.menu', css_text, re.IGNORECASE):
            confidence += 0.3
            evidence.append("وجود أنماط CSS للتنقل")
        
        # البحث عن links متعددة
        links = re.findall(r'<a[^>]*href=[^>]*>', html)
        if len(links) >= 3:
            confidence += 0.1
            evidence.append(f"وجود {len(links)} روابط تنقل")
        
        return {
            'detected': confidence >= self.config.confidence_threshold,
            'confidence': confidence,
            'evidence': evidence,
            'elements_found': len(links),
            'description': 'شريط تنقل لعرض القوائم والروابط الرئيسية'
        }
    
    def _detect_modal_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        """كشف نمط النوافذ المنبثقة"""
        confidence = 0.0
        evidence = []
        
        # البحث في HTML
        if re.search(r'class=".*modal.*"', html, re.IGNORECASE):
            confidence += 0.5
            evidence.append("وجود عناصر modal في HTML")
        
        if re.search(r'data-toggle="modal"|data-bs-toggle="modal"', html, re.IGNORECASE):
            confidence += 0.3
            evidence.append("وجود triggers للـ modal")
        
        # البحث في CSS
        css_text = ' '.join([item.get('content', '') for item in css])
        if re.search(r'\.modal|\.popup|\.overlay', css_text, re.IGNORECASE):
            confidence += 0.2
            evidence.append("وجود أنماط CSS للـ modal")
        
        return {
            'detected': confidence >= self.config.confidence_threshold,
            'confidence': confidence,
            'evidence': evidence,
            'description': 'نوافذ منبثقة لعرض المحتوى'
        }
    
    def _detect_api_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """كشف أنماط API"""
        confidence = 0.0
        evidence = []
        
        js_content = extraction_data.get('assets', {}).get('javascript', [])
        js_text = ' '.join([item.get('content', '') for item in js_content])
        
        # البحث عن AJAX calls
        if re.search(r'fetch\(|\.ajax\(|XMLHttpRequest', js_text):
            confidence += 0.4
            evidence.append("وجود استدعاءات AJAX")
        
        # البحث عن REST patterns
        if re.search(r'/api/|/v\d+/', js_text):
            confidence += 0.3
            evidence.append("وجود مسارات API")
        
        # البحث عن HTTP methods
        methods_found = re.findall(r'method.*["\']?(GET|POST|PUT|DELETE|PATCH)["\']?', js_text, re.IGNORECASE)
        if methods_found:
            confidence += 0.2
            evidence.append(f"وجود HTTP methods: {set(methods_found)}")
        
        return {
            'detected': confidence >= self.config.confidence_threshold,
            'confidence': confidence,
            'evidence': evidence,
            'http_methods': list(set(methods_found)) if 'methods_found' in locals() else [],
            'description': 'استخدام APIs للتفاعل مع الخادم'
        }
    
    def _detect_auth_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """كشف أنماط المصادقة"""
        confidence = 0.0
        evidence = []
        
        html_content = extraction_data.get('content', {}).get('html', '')
        
        # البحث عن نماذج تسجيل الدخول
        if re.search(r'login|signin|log-in', html_content, re.IGNORECASE):
            confidence += 0.3
            evidence.append("وجود نماذج تسجيل دخول")
        
        if re.search(r'password|email.*password', html_content, re.IGNORECASE):
            confidence += 0.2
            evidence.append("وجود حقول كلمة مرور")
        
        # البحث عن tokens
        js_content = extraction_data.get('assets', {}).get('javascript', [])
        js_text = ' '.join([item.get('content', '') for item in js_content])
        
        if re.search(r'token|jwt|auth', js_text, re.IGNORECASE):
            confidence += 0.3
            evidence.append("وجود نظام tokens")
        
        return {
            'detected': confidence >= self.config.confidence_threshold,
            'confidence': confidence,
            'evidence': evidence,
            'description': 'نظام مصادقة وتسجيل دخول المستخدمين'
        }
    
    def _determine_architectural_style(self, patterns: Dict[str, Any]) -> str:
        """تحديد النمط المعماري العام"""
        if patterns.get('design_patterns', {}).get('mvc'):
            return "MVC Architecture"
        elif patterns.get('code_patterns', {}).get('api_endpoints'):
            return "API-First Architecture"
        elif len(patterns.get('ui_patterns', {})) > 3:
            return "Component-Based Architecture"
        else:
            return "Traditional Web Architecture"
    
    def _generate_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """إنشاء توصيات للتحسين"""
        recommendations = []
        
        if not patterns.get('design_patterns'):
            recommendations.append("ينصح بتطبيق أنماط التصميم لتحسين بنية الكود")
        
        if not patterns.get('code_patterns', {}).get('api_endpoints'):
            recommendations.append("ينصح بإضافة APIs لتحسين قابلية التشغيل البيني")
        
        if len(patterns.get('ui_patterns', {})) < 2:
            recommendations.append("ينصح بإضافة المزيد من مكونات واجهة المستخدم التفاعلية")
        
        return recommendations
    
    # باقي دوال الكشف...
    def _detect_singleton_pattern(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_factory_pattern(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_observer_pattern(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_decorator_pattern(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_sidebar_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_carousel_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_accordion_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_tabs_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_dropdown_pattern(self, html: str, css: List[Dict], js: List[Dict]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_db_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_form_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
    
    def _detect_routing_patterns(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'detected': False, 'confidence': 0.0, 'evidence': []}
