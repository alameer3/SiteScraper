"""
ملف الطرق الرئيسي - Main Routes File
جميع طرق التطبيق منظمة ونظيفة
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, make_response, abort, send_from_directory
from app import app, db
from models import ScrapeResult
from simple_scraper import SimpleScraper
from analyzer import WebsiteAnalyzer
from advanced_analyzer import AdvancedWebsiteAnalyzer
from technical_extractor import TechnicalExtractor
from arabic_generator import ArabicGenerator
from urllib.parse import urlparse
import json
import logging
from datetime import datetime
import threading
import time
from pathlib import Path
import os

# استيراد المحللات المتقدمة
try:
    from security_analyzer import SecurityAnalyzer
    from performance_analyzer import PerformanceAnalyzer
    from seo_analyzer import SEOAnalyzer
    from competitor_analyzer import CompetitorAnalyzer
    from website_extractor import WebsiteExtractor
except ImportError as e:
    logging.warning(f"Some analyzers not available: {e}")

@app.route('/')
def index():
    """الصفحة الرئيسية مع نموذج إدخال الرابط"""
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering index page: {e}")
        return f"خطأ في تحميل الصفحة الرئيسية: {str(e)}", 500

@app.route('/analyze', methods=['POST'])
def analyze_website():
    """بدء تحليل الموقع"""
    try:
        url = request.form.get('url', '').strip()
        max_depth = int(request.form.get('max_depth', 2))
        block_ads = request.form.get('block_ads') == 'on'
        
        if not url:
            flash('يرجى إدخال رابط صحيح', 'error')
            return redirect(url_for('index'))
            
        # التحقق من صحة الرابط
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # التحقق من صحة الرابط
        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                flash('رابط غير صحيح', 'error')
                return redirect(url_for('index'))
        except Exception:
            flash('رابط غير صحيح', 'error')
            return redirect(url_for('index'))
        
        # بدء التحليل في الخلفية
        def analyze_in_background():
            with app.app_context():
                try:
                    scraper = SimpleScraper(url, max_depth=max_depth)
                    analyzer = AdvancedWebsiteAnalyzer()
                    
                    # كشط الموقع
                    scrape_data = scraper.crawl_recursive(url, 0)
                    
                    # تحليل البيانات المكشطة
                    analysis_result = analyzer.extract_complete_structure(scrape_data)
                    
                    # حفظ في قاعدة البيانات
                    result = ScrapeResult(url=url, status='completed')
                    result.set_structure_data(analysis_result.get('html_structure', {}))
                    result.set_assets_data(scrape_data)
                    result.set_technology_data(analysis_result.get('semantic_structure', {}))
                    result.set_seo_data({'analyzed': True, 'data': scrape_data})
                    result.set_navigation_data(analysis_result.get('interactive_elements', {}))
                    db.session.add(result)
                    db.session.commit()
                    
                    logging.info(f"Analysis completed for {url}")
                    
                except Exception as e:
                    logging.error(f"Analysis failed for {url}: {e}")
                
        # بدء التحليل في الخلفية
        thread = threading.Thread(target=analyze_in_background)
        thread.daemon = True
        thread.start()
        
        flash('تم بدء تحليل الموقع، ستظهر النتائج قريباً', 'success')
        return redirect(url_for('dashboard'))
        
    except ValueError as e:
        flash('خطأ في قيم النموذج', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error processing form: {e}")
        flash('حدث خطأ في معالجة النموذج', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم الرئيسية"""
    try:
        recent_results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(10).all()
        return render_template('dashboard.html', results=recent_results)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', results=[])

@app.route('/history')
def history():
    """صفحة تاريخ التحليل"""
    try:
        results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(50).all()
        return render_template('history.html', results=results)
    except Exception as e:
        logging.error(f"Error loading history: {e}")
        return render_template('history.html', results=[])

@app.route('/results/<int:result_id>')
def view_results(result_id):
    """عرض نتائج التحليل"""
    try:
        result = ScrapeResult.query.get_or_404(result_id)
        return render_template('results.html', result=result)
    except Exception as e:
        logging.error(f"Error loading results: {e}")
        flash('خطأ في تحميل النتائج', 'error')
        return redirect(url_for('history'))

# صفحات التحليل المتخصصة
@app.route('/security-analysis')
def security_analysis_page():
    """صفحة تحليل الأمان"""
    return render_template('security_analysis.html')

@app.route('/performance-analysis')
def performance_analysis_page():
    """صفحة تحليل الأداء"""
    return render_template('performance_analysis.html')

@app.route('/seo-analysis')
def seo_analysis_page():
    """صفحة تحليل SEO"""
    return render_template('seo_analysis.html')

@app.route('/competitor-analysis')
def competitor_analysis_page():
    """صفحة تحليل المنافسين"""
    return render_template('competitor_analysis.html')

@app.route('/comprehensive-analysis')
def comprehensive_analysis_page():
    """صفحة التحليل الشامل"""
    return render_template('comprehensive_analysis.html')

@app.route('/live-search')
def live_search_page():
    """صفحة البحث المباشر"""
    return render_template('live_search.html')

@app.route('/settings')
def settings_page():
    """صفحة الإعدادات"""
    return render_template('settings.html')

@app.route('/website-extractor')
def website_extractor_page():
    """صفحة استخراج المواقع"""
    return render_template('website_extractor.html')

@app.route('/reports')
def reports_page():
    """صفحة التقارير"""
    return render_template('reports.html')

# APIs للتحليل المتقدم
@app.route('/api/security-analyze', methods=['POST'])
def api_security_analyze():
    """API تحليل الأمان"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        try:
            if 'SecurityAnalyzer' in globals():
                analyzer = SecurityAnalyzer()
                results = analyzer.analyze_security(url)
            else:
                results = {'error': 'محلل الأمان غير متوفر'}
            
            # حفظ النتائج في قاعدة البيانات
            scrape_result = ScrapeResult(
                url=url,
                analysis_type='security',
                status='completed',
                data=json.dumps(results, ensure_ascii=False),
                timestamp=datetime.now()
            )
            db.session.add(scrape_result)
            db.session.commit()
            
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': f'خطأ في تحليل الأمان: {str(e)}'}), 500
        
    except Exception as e:
        logging.error(f"خطأ في API تحليل الأمان: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-analyze', methods=['POST'])
def api_performance_analyze():
    """API تحليل الأداء"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        try:
            if 'PerformanceAnalyzer' in globals():
                analyzer = PerformanceAnalyzer()
                results = analyzer.analyze_performance(url)
            else:
                results = {'error': 'محلل الأداء غير متوفر'}
            
            # حفظ النتائج
            scrape_result = ScrapeResult(
                url=url,
                analysis_type='performance',
                status='completed',
                data=json.dumps(results, ensure_ascii=False),
                timestamp=datetime.now()
            )
            db.session.add(scrape_result)
            db.session.commit()
            
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': f'خطأ في تحليل الأداء: {str(e)}'}), 500
        
    except Exception as e:
        logging.error(f"خطأ في API تحليل الأداء: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/seo-analyze', methods=['POST'])
def api_seo_analyze():
    """API تحليل SEO"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        try:
            if 'SEOAnalyzer' in globals():
                analyzer = SEOAnalyzer()
                results = analyzer.analyze_seo(url)
            else:
                results = {'error': 'محلل SEO غير متوفر'}
            
            # حفظ النتائج
            scrape_result = ScrapeResult(
                url=url,
                analysis_type='seo',
                status='completed',
                data=json.dumps(results, ensure_ascii=False),
                timestamp=datetime.now()
            )
            db.session.add(scrape_result)
            db.session.commit()
            
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': f'خطأ في تحليل SEO: {str(e)}'}), 500
        
    except Exception as e:
        logging.error(f"خطأ في API تحليل SEO: {e}")
        return jsonify({'error': str(e)}), 500

# معالجات الأخطاء
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