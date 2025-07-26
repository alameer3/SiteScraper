"""
API endpoints for website analysis functionality.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

# Import the new organized modules
from core.analyzers.ai_analyzer import AIAnalyzer
from core.extractors.advanced_extractor import AdvancedExtractor
from core.scrapers.smart_scraper import SmartScraper
from core.blockers.advanced_blocker import AdvancedAdBlocker
from data.manager import DataManager
from utils.validators import URLValidator, DataValidator
from utils.formatters import DataFormatter, ReportFormatter

analyzer_api = Blueprint('analyzer_api', __name__, url_prefix='/api/v1')
logger = logging.getLogger(__name__)

# Initialize components
ai_analyzer = AIAnalyzer()
advanced_extractor = AdvancedExtractor()
data_manager = DataManager()

@analyzer_api.route('/analyze', methods=['POST'])
def analyze_website():
    """Analyze website with comprehensive features."""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        mode = data.get('mode', 'standard')
        enable_cache = data.get('cache', True)
        
        # Validate input
        if not URLValidator.is_valid_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        if not DataValidator.validate_extraction_mode(mode):
            return jsonify({'error': 'Invalid extraction mode'}), 400
        
        # Normalize URL
        url = URLValidator.normalize_url(url)
        
        # Check cache first
        if enable_cache:
            cached_result = data_manager.get_cached_data(url)
            if cached_result:
                logger.info(f"Returning cached result for {url}")
                return jsonify({
                    'success': True,
                    'data': cached_result,
                    'from_cache': True
                })
        
        # Perform extraction
        result = advanced_extractor.extract_with_mode(url, mode)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Add AI analysis if enabled
        if mode in ['advanced', 'ultra'] and 'content' in result:
            content_text = result['content'].get('text_content', '')
            metadata = result.get('metadata', {})
            
            ai_analysis = ai_analyzer.analyze_content_with_ai(content_text, metadata)
            result['ai_analysis'] = ai_analysis
        
        # Cache the result
        if enable_cache:
            data_manager.cache_data(url, result)
        
        # Format for response
        formatted_result = ReportFormatter.format_extraction_summary(result)
        
        return jsonify({
            'success': True,
            'data': result,
            'summary': formatted_result
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@analyzer_api.route('/export', methods=['POST'])
def export_analysis():
    """Export analysis results in various formats."""
    try:
        data = request.get_json()
        
        if not data or 'analysis_data' not in data:
            return jsonify({'error': 'Analysis data is required'}), 400
        
        format_type = data.get('format', 'json')
        
        if not DataValidator.validate_export_format(format_type):
            return jsonify({'error': 'Invalid export format'}), 400
        
        analysis_data = data['analysis_data']
        
        # Export data
        export_result = advanced_extractor.export_data(analysis_data, format_type)
        
        return jsonify({
            'success': True,
            'message': export_result,
            'format': format_type
        })
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({'error': str(e)}), 500

@analyzer_api.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = data_manager.get_cache_statistics()
        return jsonify({
            'success': True,
            'cache_stats': stats
        })
        
    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        return jsonify({'error': str(e)}), 500

@analyzer_api.route('/reports', methods=['GET'])
def list_reports():
    """List saved reports."""
    try:
        report_type = request.args.get('type')
        reports = data_manager.list_reports(report_type)
        
        return jsonify({
            'success': True,
            'reports': reports
        })
        
    except Exception as e:
        logger.error(f"Report listing failed: {e}")
        return jsonify({'error': str(e)}), 500

@analyzer_api.route('/storage/info', methods=['GET'])
def get_storage_info():
    """Get storage information."""
    try:
        storage_info = data_manager.get_storage_info()
        
        # Format file sizes
        for category, info in storage_info.items():
            if 'total_size_bytes' in info:
                info['total_size_formatted'] = DataFormatter.format_file_size(info['total_size_bytes'])
        
        return jsonify({
            'success': True,
            'storage_info': storage_info
        })
        
    except Exception as e:
        logger.error(f"Storage info failed: {e}")
        return jsonify({'error': str(e)}), 500

@analyzer_api.route('/validate/url', methods=['POST'])
def validate_url():
    """Validate URL before analysis."""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        
        is_valid = URLValidator.is_valid_url(url)
        normalized_url = URLValidator.normalize_url(url) if is_valid else None
        domain = URLValidator.extract_domain(url) if is_valid else None
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'normalized_url': normalized_url,
            'domain': domain
        })
        
    except Exception as e:
        logger.error(f"URL validation failed: {e}")
        return jsonify({'error': str(e)}), 500