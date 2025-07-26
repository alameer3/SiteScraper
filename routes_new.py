"""
Main application routes with organized structure.
Updated to use the new modular architecture.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app import app, db
import logging
import json
from datetime import datetime

# Import all blueprints
from core.analyzers.ai_analyzer import AIAnalyzer
from core.extractors.advanced_extractor import AdvancedExtractor
from data.manager import DataManager
# استيراد المساعدات
from replicated_sites.utils.validators import URLValidator, DataValidator
from replicated_sites.utils.formatters import DataFormatter, ReportFormatter
from api.endpoints.analyzer_api import analyzer_api
from api.endpoints.deep_extraction_api import deep_extraction_bp
from api.endpoints.smart_replication_api import smart_replication_bp
from api.endpoints.advanced_ai_api import advanced_ai_bp

# Register all blueprints
app.register_blueprint(analyzer_api)
app.register_blueprint(deep_extraction_bp, url_prefix='/api')
app.register_blueprint(smart_replication_bp, url_prefix='/api')
app.register_blueprint(advanced_ai_bp)

# Import and register comprehensive extraction API
from api.endpoints.comprehensive_extraction_api import comprehensive_extraction_bp
app.register_blueprint(comprehensive_extraction_bp, url_prefix='/api')

# Import simple comprehensive API
from api.endpoints.simple_comprehensive_api import simple_comprehensive_bp
app.register_blueprint(simple_comprehensive_bp, url_prefix='/api')

# Initialize components
ai_analyzer = AIAnalyzer()
advanced_extractor = AdvancedExtractor()
data_manager = DataManager()
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard with organized features."""
    # Get recent analysis statistics
    cache_stats = data_manager.get_cache_statistics()
    recent_reports = data_manager.list_reports()[:5]  # Get 5 most recent
    storage_info = data_manager.get_storage_info()

    return render_template('pages/dashboard.html', 
                         cache_stats=cache_stats,
                         recent_reports=recent_reports,
                         storage_info=storage_info)

@app.route('/extractor')
def extractor():
    """Advanced content extraction page."""
    return render_template('pages/extractor.html')

@app.route('/deep-extraction')
def deep_extraction():
    """Deep extraction page."""
    return render_template('pages/deep_extraction.html')

@app.route('/smart-replication')
def smart_replication():
    """صفحة النسخ الذكي"""
    return render_template('pages/smart_replication.html')

@app.route('/advanced-ai')
def advanced_ai():
    """صفحة الذكاء الاصطناعي المتقدم"""
    return render_template('pages/advanced_ai.html')

@app.route('/extract-content', methods=['POST'])
def extract_content():
    """Handle content extraction requests."""
    try:
        url = request.form.get('url', '').strip()
        mode = request.form.get('extraction_mode', 'standard')
        export_format = request.form.get('export_format', 'json')

        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400

        # Validate URL
        if not URLValidator.is_valid_url(url):
            return jsonify({'success': False, 'error': 'Invalid URL format'}), 400

        # Normalize URL
        url = URLValidator.normalize_url(url)

        # Build extraction config from form
        extraction_config = {
            'depth': int(request.form.get('crawl_depth', 2)),
            'include_assets': request.form.get('include_assets') == 'on',
            'download_assets': request.form.get('download_assets') == 'on',
            'replicate_website': request.form.get('replicate_website') == 'on',
            'include_links': request.form.get('include_links') == 'on',
            'include_metadata': request.form.get('include_metadata') == 'on',
            'content_filtering': request.form.get('content_filtering') == 'on',
            'ai_analysis': request.form.get('ai_analysis') == 'on',
            'remove_ads': request.form.get('remove_ads') == 'on'
        }

        # Perform extraction
        result = advanced_extractor.extract_with_mode(url, mode, extraction_config)

        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 500

        # Export data in requested format
        export_result = advanced_extractor.export_data(result, export_format)

        # Save report
        report_path = data_manager.save_report(
            f"extraction_{URLValidator.extract_domain(url)}", 
            result, 
            'extraction'
        )

        return jsonify({
            'success': True,
            'message': 'Extraction completed successfully',
            'stats': {
                'pages': 1,
                'content_size': len(result.get('content', {}).get('text_content', '')),
                'links': len(result.get('links', {}).get('internal_links', {}).get('list', []))
            },
            'download_url': f'/download-report/{report_path.split("/")[-1]}',
            'export_message': export_result
        })

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Enhanced analysis page with new features."""
    if request.method == 'GET':
        return render_template('pages/analyze.html')

    try:
        url = request.form.get('url', '').strip()
        mode = request.form.get('mode', 'standard')
        enable_ai = request.form.get('enable_ai') == 'on'
        enable_cache = request.form.get('enable_cache') == 'on'

        if not url:
            flash('URL is required', 'error')
            return redirect(url_for('analyze'))

        # Validate URL
        if not URLValidator.is_valid_url(url):
            flash('Invalid URL format', 'error')
            return redirect(url_for('analyze'))

        # Normalize URL
        url = URLValidator.normalize_url(url)

        # Check cache first
        result = None
        from_cache = False

        if enable_cache:
            result = data_manager.get_cached_data(url)
            if result:
                from_cache = True
                logger.info(f"Retrieved cached result for {url}")

        # Perform new analysis if not cached
        if not result:
            result = advanced_extractor.extract_with_mode(url, mode)

            if 'error' in result:
                flash(f'Analysis failed: {result["error"]}', 'error')
                return redirect(url_for('analyze'))

            # Add AI analysis if enabled
            if enable_ai and 'content' in result:
                content_text = result['content'].get('text_content', '')
                metadata = result.get('metadata', {})

                ai_analysis = ai_analyzer.analyze_content_with_ai(content_text, metadata)
                result['ai_analysis'] = ai_analysis

            # Cache the result
            if enable_cache:
                data_manager.cache_data(url, result)

        # Save report
        report_path = data_manager.save_report(
            URLValidator.extract_domain(url), 
            result, 
            'analysis'
        )

        # Format for display
        formatted_result = ReportFormatter.format_extraction_summary(result)

        return render_template('pages/results.html', 
                             result=result,
                             formatted_result=formatted_result,
                             from_cache=from_cache,
                             report_path=report_path)

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        flash(f'Analysis failed: {str(e)}', 'error')
        return redirect(url_for('analyze'))

@app.route('/reports')
def reports():
    """Reports management page."""
    report_type = request.args.get('type')
    reports_list = data_manager.list_reports(report_type)

    # Format file sizes and dates
    for report in reports_list:
        report['size_formatted'] = DataFormatter.format_file_size(report['size'])
        report['created_formatted'] = DataFormatter.format_timestamp(report['created'])

    return render_template('pages/reports.html', 
                         reports=reports_list,
                         current_type=report_type)

@app.route('/export', methods=['POST'])
def export_data():
    """Export analysis data."""
    try:
        export_format = request.form.get('format', 'json')
        analysis_data = json.loads(request.form.get('data', '{}'))

        if not DataValidator.validate_export_format(export_format):
            flash('Invalid export format', 'error')
            return redirect(request.referrer or url_for('index'))

        # Export data
        export_result = advanced_extractor.export_data(analysis_data, export_format)

        flash(f'Export successful: {export_result}', 'success')
        return redirect(request.referrer or url_for('reports'))

    except Exception as e:
        logger.error(f"Export error: {e}")
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))

@app.route('/ai-analysis')
def ai_analysis():
    """AI-powered analysis features."""
    return render_template('pages/ai_analysis.html')

@app.route('/performance')
def performance():
    """Performance analysis dashboard."""
    # Get performance metrics
    storage_info = data_manager.get_storage_info()
    cache_stats = data_manager.get_cache_statistics()

    return render_template('pages/performance.html',
                         storage_info=storage_info,
                         cache_stats=cache_stats)

@app.route('/settings')
def settings():
    """Application settings and configuration."""
    return render_template('pages/settings.html')

@app.route('/data-management')
def data_management():
    """Data organization and management."""
    storage_info = data_manager.get_storage_info()
    cache_stats = data_manager.get_cache_statistics()

    # Format data for display
    for category, info in storage_info.items():
        if 'total_size_bytes' in info:
            info['size_formatted'] = DataFormatter.format_file_size(info['total_size_bytes'])

    return render_template('pages/data_management.html',
                         storage_info=storage_info,
                         cache_stats=cache_stats)

@app.route('/organize-data', methods=['POST'])
def organize_data():
    """Organize and clean data storage."""
    try:
        organization_result = data_manager.organize_data()

        flash(f"""Data organization completed:
        - Cache entries cleaned: {organization_result['cache_cleaned']}
        - Reports organized: {organization_result['reports_organized']}""", 'success')

    except Exception as e:
        logger.error(f"Data organization error: {e}")
        flash(f'Data organization failed: {str(e)}', 'error')

    return redirect(url_for('data_management'))

@app.route('/clean-cache', methods=['POST'])
def clean_cache():
    """Clean expired cache entries."""
    try:
        cleaned_count = data_manager.clean_expired_cache()
        flash(f'Cleaned {cleaned_count} expired cache entries', 'success')

    except Exception as e:
        logger.error(f"Cache cleaning error: {e}")
        flash(f'Cache cleaning failed: {str(e)}', 'error')

    return redirect(url_for('data_management'))

@app.route('/comprehensive_extractor')
def comprehensive_extractor():
    """صفحة الاستخراج الشامل المتقدم"""
    return render_template('pages/comprehensive_extractor.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('pages/errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('pages/errors/500.html'), 500

# Context processors for templates
@app.context_processor
def utility_processor():
    """Add utility functions to template context."""
    return {
        'format_file_size': DataFormatter.format_file_size,
        'format_percentage': DataFormatter.format_percentage,
        'format_timestamp': DataFormatter.format_timestamp,
        'truncate_text': DataFormatter.truncate_text
    }