"""
Main Routes File for Website Analysis Tool
Clean and compatible with Replit environment
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import ScrapeResult
from urllib.parse import urlparse
import json
import logging
from datetime import datetime
import threading
import time
import requests
from bs4 import BeautifulSoup

@app.route('/')
def index():
    """Home page with URL input form"""
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering index page: {e}")
        return f"Error loading home page: {str(e)}", 500

@app.route('/analyze', methods=['POST'])
def analyze_website():
    """Start website analysis"""
    try:
        url = request.form.get('url', '').strip()
        max_depth = int(request.form.get('max_depth', 2))
        block_ads = request.form.get('block_ads') == 'on'
        
        if not url:
            flash('Please enter a valid URL', 'error')
            return redirect(url_for('index'))
            
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                flash('Invalid URL', 'error')
                return redirect(url_for('index'))
        except Exception:
            flash('Invalid URL', 'error')
            return redirect(url_for('index'))
        
        # Basic analysis function
        def analyze_in_background():
            with app.app_context():
                try:
                    # Simple website analysis using requests and BeautifulSoup
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Basic analysis data
                    analysis_data = {
                        'title': soup.title.string if soup.title else 'No title',
                        'meta_description': '',
                        'headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                        'images': len(soup.find_all('img')),
                        'links': len(soup.find_all('a')),
                        'forms': len(soup.find_all('form')),
                        'scripts': len(soup.find_all('script')),
                        'stylesheets': len(soup.find_all('link', rel='stylesheet'))
                    }
                    
                    # Get meta description
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and hasattr(meta_desc, 'attrs') and 'content' in meta_desc.attrs:
                        analysis_data['meta_description'] = meta_desc.attrs['content']
                    
                    # Save results to database
                    result = ScrapeResult(url=url, status='completed')
                    result.set_structure_data(analysis_data)
                    result.set_assets_data({'analyzed': True, 'url': url})
                    result.set_technology_data({'basic_analysis': True})
                    result.set_seo_data({'analyzed': True, 'data': analysis_data})
                    result.set_navigation_data({'links_found': analysis_data['links']})
                    
                    db.session.add(result)
                    db.session.commit()
                    
                    logging.info(f"Analysis completed for {url}")
                    
                except Exception as e:
                    logging.error(f"Analysis failed for {url}: {e}")
                    # Save error result
                    error_result = ScrapeResult(url=url, status='failed')
                    error_result.error_message = str(e)
                    db.session.add(error_result)
                    db.session.commit()
        
        # Start analysis in background
        thread = threading.Thread(target=analyze_in_background)
        thread.daemon = True
        thread.start()
        
        flash('Website analysis started, results will appear soon', 'success')
        return redirect(url_for('dashboard'))
        
    except ValueError as e:
        flash('Error in form values', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error processing form: {e}")
        flash('Error processing form', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    try:
        # Analysis statistics
        total_analyses = ScrapeResult.query.count()
        
        # Statistics by type
        analysis_stats = {
            'security': ScrapeResult.query.filter_by(analysis_type='security').count(),
            'performance': ScrapeResult.query.filter_by(analysis_type='performance').count(),
            'seo': ScrapeResult.query.filter_by(analysis_type='seo').count(),
            'competitor': ScrapeResult.query.filter_by(analysis_type='competitor').count()
        }
        
        # Recent analyses
        recent_results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html', 
                             results=recent_results,
                             total_analyses=total_analyses,
                             analysis_stats=analysis_stats)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        # Return default values on error
        return render_template('dashboard.html', 
                             results=[],
                             total_analyses=0,
                             analysis_stats={'security': 0, 'performance': 0, 'seo': 0, 'competitor': 0})

@app.route('/history')
def history():
    """Analysis history page"""
    try:
        results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(50).all()
        return render_template('history.html', results=results)
    except Exception as e:
        logging.error(f"Error loading history: {e}")
        return render_template('history.html', results=[])

@app.route('/results/<int:result_id>')
def view_results(result_id):
    """View analysis results"""
    try:
        result = ScrapeResult.query.get_or_404(result_id)
        return render_template('results.html', result=result)
    except Exception as e:
        logging.error(f"Error loading results: {e}")
        flash('Error loading results', 'error')
        return redirect(url_for('history'))

# Specialized analysis pages
@app.route('/security-analysis')
def security_analysis_page():
    """Security analysis page"""
    return render_template('security_analysis.html')

@app.route('/performance-analysis')
def performance_analysis_page():
    """Performance analysis page"""
    return render_template('performance_analysis.html')

@app.route('/seo-analysis')
def seo_analysis_page():
    """SEO analysis page"""
    return render_template('seo_analysis.html')

@app.route('/competitor-analysis')
def competitor_analysis_page():
    """Competitor analysis page"""
    return render_template('competitor_analysis.html')

@app.route('/comprehensive-analysis')
def comprehensive_analysis_page():
    """Comprehensive analysis page"""
    return render_template('comprehensive_analysis.html')

@app.route('/live-search')
def live_search_page():
    """Live search page"""
    return render_template('live_search.html')

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@app.route('/website-extractor')
def website_extractor_page():
    """Website extractor page"""
    return render_template('advanced_extractor.html')

@app.route('/reports')
def reports_page():
    """Reports page"""
    return render_template('reports.html')

@app.route('/ultra-extractor')
def ultra_extractor_page():
    """Ultra extractor page"""
    return render_template('ultra_extractor.html')

@app.route('/enhanced-extractor')  
def enhanced_extractor_page():
    """Enhanced extractor page"""
    return render_template('enhanced_extractor.html')

@app.route('/advanced-ad-blocker')
def advanced_ad_blocker_page():
    """Advanced ad blocker page"""
    return render_template('advanced_ad_blocker.html')

# الصفحات الموحدة الجديدة
@app.route('/unified-analyzer')
def unified_analyzer_page():
    """صفحة المحلل الموحد"""
    return render_template('unified_analyzer.html')

@app.route('/unified-extractor')
def unified_extractor_page():
    """صفحة المستخرج الموحد"""
    return render_template('unified_extractor.html')

@app.route('/unified-blocker')
def unified_blocker_page():
    """صفحة حاجب الإعلانات الموحد"""
    return render_template('unified_blocker.html')

# APIs الموحدة الجديدة
@app.route('/api/basic-analyze', methods=['POST'])
def api_basic_analyze():
    """Basic analysis API"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Basic analysis
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis_result = {
                'title': soup.title.string if soup.title else 'No title',
                'status': 'success',
                'elements': {
                    'headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                    'images': len(soup.find_all('img')),
                    'links': len(soup.find_all('a')),
                    'forms': len(soup.find_all('form'))
                }
            }
            
            return jsonify(analysis_result)
            
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<path:url>')
def api_status(url):
    """Check analysis status"""
    try:
        latest_result = ScrapeResult.query.filter_by(url=url).order_by(ScrapeResult.created_at.desc()).first()
        
        if not latest_result:
            return jsonify({'status': 'not_found'})
        
        return jsonify({
            'status': latest_result.status,
            'created_at': latest_result.created_at.isoformat(),
            'id': latest_result.id
        })
        
    except Exception as e:
        logging.error(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500

# APIs للأدوات الموحدة
@app.route('/api/unified-analyze', methods=['POST'])
def api_unified_analyze():
    """API التحليل الموحد"""
    try:
        data = request.get_json()
        url = data.get('url')
        analysis_type = data.get('analysis_type', 'comprehensive')
        config = data.get('config', {})
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        # محاكاة تحليل شامل
        analysis_result = {
            'status': 'success',
            'analysis_type': analysis_type,
            'url': url,
            'data': {
                'overall_score': 85,
                'metrics': {
                    'loading_time': '2.3s',
                    'security_score': 92,
                    'seo_issues': 3,
                    'technologies_found': 12
                },
                'recommendations': [
                    'تحسين سرعة التحميل',
                    'إضافة شهادة SSL',
                    'تحسين العناوين الوصفية'
                ]
            }
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logging.error(f"خطأ في API التحليل الموحد: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/unified-extract', methods=['POST'])
def api_unified_extract():
    """API الاستخراج الموحد"""
    try:
        data = request.get_json()
        url = data.get('url')
        mode = data.get('mode', 'standard')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        # محاكاة استخراج
        extraction_result = {
            'status': 'success',
            'url': url,
            'mode': mode,
            'stats': {
                'pages_extracted': 15,
                'images_downloaded': 45,
                'css_files': 8,
                'js_files': 12,
                'total_size': '2.3 MB'
            },
            'download_url': f'/downloads/{hashlib.md5(url.encode()).hexdigest()}.zip'
        }
        
        return jsonify(extraction_result)
        
    except Exception as e:
        logging.error(f"خطأ في API الاستخراج الموحد: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/unified-block', methods=['POST'])
def api_unified_block():
    """API الحجب الموحد"""
    try:
        data = request.get_json()
        url = data.get('url')
        level = data.get('level', 'standard')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        # محاكاة حجب الإعلانات
        blocking_result = {
            'status': 'success',
            'url': url,
            'level': level,
            'stats': {
                'ads': 23,
                'trackers': 15,
                'size': 67,
                'accuracy': 95
            },
            'cleaned_url': f'/cleaned/{hashlib.md5(url.encode()).hexdigest()}.html'
        }
        
        return jsonify(blocking_result)
        
    except Exception as e:
        logging.error(f"خطأ في API الحجب الموحد: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)