"""
Unified Routes for All Analysis Tools
Enhanced with MasterExtractor integration
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import ScrapeResult
from urllib.parse import urlparse
from extractors.master_extractor import MasterExtractor, ExtractionConfig, ExtractionMode
import json
import logging
from datetime import datetime
import threading
import time
import requests
import hashlib
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

# Enhanced unified routes
@app.route('/unified_extractor')
def unified_extractor():
    """Unified extractor interface"""
    return render_template('unified_extractor.html')

@app.route('/unified_analyzer')  
def unified_analyzer():
    """Unified analyzer interface"""
    return render_template('unified_analyzer.html')

@app.route('/unified_blocker')
def unified_blocker():
    """Unified blocker interface"""
    return render_template('unified_blocker.html')

@app.route('/advanced_extract', methods=['POST'])
def advanced_extract():
    """Advanced extraction using MasterExtractor"""
    try:
        url = request.form.get('url', '').strip()
        mode = request.form.get('mode', 'basic')
        max_pages = int(request.form.get('max_pages', 10))
        extract_images = request.form.get('extract_images') == 'on'
        block_ads = request.form.get('block_ads') == 'on'
        output_format = request.form.get('output_format', 'json')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                return jsonify({'error': 'Invalid URL'}), 400
        except Exception:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Configure extraction
        extraction_mode = {
            'basic': ExtractionMode.BASIC,
            'standard': ExtractionMode.STANDARD,
            'advanced': ExtractionMode.ADVANCED,
            'ultra': ExtractionMode.ULTRA,
            'secure': ExtractionMode.SECURE
        }.get(mode, ExtractionMode.BASIC)
        
        config = ExtractionConfig(
            mode=extraction_mode,
            max_pages=min(max_pages, 100),  # Safety limit
            timeout=30,
            extract_images=extract_images,
            block_ads=block_ads,
            output_format=output_format
        )
        
        # Perform extraction in background
        def extract_in_background():
            with app.app_context():
                try:
                    extractor = MasterExtractor(config)
                    result = extractor.extract(url, save_report=True)
                    
                    if 'error' not in result:
                        # Save to database
                        db_result = ScrapeResult(
                            url=url, 
                            status='completed',
                            analysis_type='extraction'
                        )
                        db_result.data = json.dumps(result, default=str, ensure_ascii=False)
                        db.session.add(db_result)
                        db.session.commit()
                        
                        logging.info(f"Advanced extraction completed for {url}")
                    else:
                        logging.error(f"Extraction failed for {url}: {result['error']}")
                        
                except Exception as e:
                    logging.error(f"Background extraction failed: {e}")
        
        # Start background extraction
        thread = threading.Thread(target=extract_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Extraction started successfully',
            'url': url,
            'mode': mode,
            'estimated_time': '30-60 seconds'
        })
        
    except Exception as e:
        logging.error(f"Advanced extraction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extraction_status/<int:result_id>')
def extraction_status(result_id):
    """Get extraction status"""
    try:
        result = ScrapeResult.query.get_or_404(result_id)
        return jsonify({
            'status': result.status,
            'url': result.url,
            'created_at': result.created_at.isoformat(),
            'completed_at': result.completed_at.isoformat() if result.completed_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/results')
def api_results():
    """API endpoint for results"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        results = ScrapeResult.query.order_by(
            ScrapeResult.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'results': [{
                'id': r.id,
                'url': r.url,
                'status': r.status,
                'analysis_type': r.analysis_type,
                'created_at': r.created_at.isoformat(),
                'completed_at': r.completed_at.isoformat() if r.completed_at else None
            } for r in results.items],
            'total': results.total,
            'pages': results.pages,
            'current_page': page
        })
        
    except Exception as e:
        logging.error(f"API results error: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced analysis routes
@app.route('/comprehensive_analysis')
def comprehensive_analysis():
    """Comprehensive analysis page"""
    return render_template('comprehensive_analysis.html')

@app.route('/performance_analysis')
def performance_analysis():
    """Performance analysis page"""
    return render_template('performance_analysis.html')

@app.route('/security_analysis')
def security_analysis():
    """Security analysis page"""
    return render_template('security_analysis.html')

@app.route('/seo_analysis')
def seo_analysis():
    """SEO analysis page"""
    return render_template('seo_analysis.html')

@app.route('/competitor_analysis')
def competitor_analysis():
    """Competitor analysis page"""
    return render_template('competitor_analysis.html')

# Export routes
@app.route('/export/<int:result_id>/<format>')
def export_result(result_id, format):
    """Export analysis result in various formats"""
    try:
        result = ScrapeResult.query.get_or_404(result_id)
        
        if format not in ['json', 'pdf', 'docx', 'csv']:
            flash('Invalid export format', 'error')
            return redirect(url_for('view_result', result_id=result_id))
        
        # For now, return JSON export
        if format == 'json':
            response = app.response_class(
                response=result.data or '{}',
                status=200,
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=analysis_{result_id}.json'
                }
            )
            return response
        else:
            flash(f'{format.upper()} export will be available soon', 'info')
            return redirect(url_for('view_result', result_id=result_id))
            
    except Exception as e:
        logging.error(f"Export error: {e}")
        flash('Error exporting result', 'error')
        return redirect(url_for('index'))

# Settings and configuration
@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Settings API"""
    if request.method == 'GET':
        return jsonify({
            'default_extraction_mode': 'standard',
            'max_pages_limit': 100,
            'timeout_seconds': 30,
            'auto_save_reports': True,
            'block_ads_default': True
        })
    else:
        # Handle settings update
        try:
            settings = request.get_json()
            # In a real app, you'd save these to database
            return jsonify({'message': 'Settings updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

# Live dashboard with real-time updates
@app.route('/live_dashboard')
def live_dashboard():
    """Live dashboard with real-time data"""
    return render_template('dashboard.html')

@app.route('/api/live_stats')
def live_stats():
    """Live statistics API"""
    try:
        # Calculate real-time statistics
        total_analyses = ScrapeResult.query.count()
        completed_today = ScrapeResult.query.filter(
            ScrapeResult.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
        ).count()
        
        success_rate = 0
        if total_analyses > 0:
            successful = ScrapeResult.query.filter_by(status='completed').count()
            success_rate = (successful / total_analyses) * 100
        
        return jsonify({
            'total_analyses': total_analyses,
            'completed_today': completed_today,
            'success_rate': round(success_rate, 1),
            'active_extractions': 0,  # Would track ongoing processes
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Live stats error: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403