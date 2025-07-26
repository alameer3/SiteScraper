
from flask import Blueprint, request, jsonify
import asyncio
import logging
from datetime import datetime
from core.ai.advanced_ai_engine import AdvancedAIEngine
from data.manager import DataManager

advanced_ai_bp = Blueprint('advanced_ai', __name__, url_prefix='/api/advanced-ai')

@advanced_ai_bp.route('/analyze', methods=['POST'])
def analyze_with_advanced_ai():
    """تحليل موقع باستخدام الذكاء الاصطناعي المتقدم"""
    try:
        data = request.get_json()
        url = data.get('url')
        extraction_data = data.get('extraction_data', {})
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # تشغيل تحليل الذكاء الاصطناعي
        ai_engine = AdvancedAIEngine()
        
        # تشغيل التحليل في حلقة أحداث منفصلة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            ai_analysis = loop.run_until_complete(
                ai_engine.analyze_website_intelligence(extraction_data)
            )
            
            # حفظ النتائج
            data_manager = DataManager()
            analysis_id = data_manager.save_ai_analysis(url, ai_analysis)
            
            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'ai_analysis': ai_analysis,
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"خطأ في تحليل الذكاء الاصطناعي: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_ai_bp.route('/get-analysis/<analysis_id>', methods=['GET'])
def get_ai_analysis(analysis_id):
    """الحصول على تحليل الذكاء الاصطناعي"""
    try:
        data_manager = DataManager()
        analysis = data_manager.get_ai_analysis(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logging.error(f"خطأ في استرجاع التحليل: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_ai_bp.route('/semantic-analysis', methods=['POST'])
def semantic_analysis():
    """تحليل دلالي متقدم"""
    try:
        data = request.get_json()
        extraction_data = data.get('extraction_data', {})
        
        ai_engine = AdvancedAIEngine()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            semantic_analysis = loop.run_until_complete(
                ai_engine._analyze_semantic_structure(extraction_data)
            )
            
            return jsonify({
                'success': True,
                'semantic_analysis': semantic_analysis
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"خطأ في التحليل الدلالي: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_ai_bp.route('/business-logic-detection', methods=['POST'])
def business_logic_detection():
    """كشف منطق الأعمال"""
    try:
        data = request.get_json()
        extraction_data = data.get('extraction_data', {})
        
        ai_engine = AdvancedAIEngine()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            business_logic = loop.run_until_complete(
                ai_engine._detect_business_logic(extraction_data)
            )
            
            return jsonify({
                'success': True,
                'business_logic': business_logic
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"خطأ في كشف منطق الأعمال: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_ai_bp.route('/optimization-recommendations', methods=['POST'])
def optimization_recommendations():
    """توصيات التحسين"""
    try:
        data = request.get_json()
        extraction_data = data.get('extraction_data', {})
        
        ai_engine = AdvancedAIEngine()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            optimizations = loop.run_until_complete(
                ai_engine._generate_optimizations(extraction_data)
            )
            
            return jsonify({
                'success': True,
                'optimizations': optimizations
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"خطأ في توليد التوصيات: {str(e)}")
        return jsonify({'error': str(e)}), 500
