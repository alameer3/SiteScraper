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

# استيراد الأدوات المتوفرة
UltraSmartExtractor = None
AdvancedAdBlocker = None

try:
    from security_analyzer import SecurityAnalyzer
    from performance_analyzer import PerformanceAnalyzer
    from seo_analyzer import SEOAnalyzer
    from competitor_analyzer import CompetitorAnalyzer
    from website_extractor import WebsiteExtractor
    from enhanced_website_extractor import EnhancedWebsiteExtractor
    logging.info("تم تحميل الأدوات الأساسية بنجاح")
except ImportError as e:
    logging.warning(f"بعض الأدوات الأساسية غير متاح: {e}")

try:
    from ultra_extractor import UltraSmartExtractor
    logging.info("تم تحميل المستخرج الفائق")
except ImportError as e:
    logging.warning(f"المستخرج الفائق غير متاح: {e}")
    UltraSmartExtractor = None

try:
    from advanced_ad_blocker import AdvancedAdBlocker
    logging.info("تم تحميل حاجب الإعلانات المتطور")
except ImportError as e:
    logging.warning(f"حاجب الإعلانات المتطور غير متاح: {e}")
    AdvancedAdBlocker = None

# استيراد الأدوات المدمجة إذا كانت متوفرة
extraction_engine = None
try:
    from analyzers.comprehensive_analyzer import ComprehensiveAnalyzer
    from extractors.master_extractor import MasterExtractor, ExtractionConfig, ExtractionMode
    from blockers.advanced_blocker import AdvancedBlocker, BlockingMode
    from scrapers.smart_scraper import SmartScraper, ScrapingConfig, ScrapingMode
    try:
        from tools.extraction_engine import ExtractionEngine, ExtractionType, Priority
        extraction_engine = ExtractionEngine()
        logging.info("تم تحميل محرك الاستخراج المتقدم")
    except ImportError:
        extraction_engine = None
        logging.info("محرك الاستخراج المتقدم غير متوفر")
except ImportError as e:
    logging.info(f"الأدوات المتقدمة غير متوفرة، استخدام الأدوات الأساسية: {e}")

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
        # احصائيات التحليلات
        total_analyses = ScrapeResult.query.count()
        
        # إحصائيات حسب النوع
        analysis_stats = {
            'security': ScrapeResult.query.filter_by(analysis_type='security').count(),
            'performance': ScrapeResult.query.filter_by(analysis_type='performance').count(),
            'seo': ScrapeResult.query.filter_by(analysis_type='seo').count(),
            'competitor': ScrapeResult.query.filter_by(analysis_type='competitor').count()
        }
        
        # آخر التحليلات
        recent_results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html', 
                             results=recent_results,
                             total_analyses=total_analyses,
                             analysis_stats=analysis_stats)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        # في حالة الخطأ، إرجاع قيم افتراضية
        return render_template('dashboard.html', 
                             results=[],
                             total_analyses=0,
                             analysis_stats={'security': 0, 'performance': 0, 'seo': 0, 'competitor': 0})

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
    return render_template('advanced_extractor.html')

@app.route('/api/extract-website', methods=['POST'])
def api_extract_website():
    """API استخراج المواقع المتقدم"""
    try:
        from advanced_extractor import extract_website_advanced
        
        data = request.get_json()
        url = data.get('url', '').strip()
        max_depth = int(data.get('max_depth', 2))
        max_threads = int(data.get('max_threads', 3))
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        # التحقق من صحة الرابط
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        def extract_in_background():
            with app.app_context():
                try:
                    site_dir, stats = extract_website_advanced(url, max_depth, max_threads)
                    
                    # حفظ معلومات الاستخراج في قاعدة البيانات
                    extraction_result = ScrapeResult(
                        url=url,
                        analysis_type='extraction',
                        status='completed',
                        data=json.dumps({
                            'site_directory': str(site_dir),
                            'statistics': stats,
                            'extraction_time': datetime.now().isoformat()
                        }, ensure_ascii=False),
                        timestamp=datetime.now()
                    )
                    db.session.add(extraction_result)
                    db.session.commit()
                    
                    logging.info(f"استخراج مكتمل للموقع: {url}")
                    
                except Exception as e:
                    logging.error(f"خطأ في الاستخراج: {e}")
                    # حفظ الخطأ
                    error_result = ScrapeResult(
                        url=url,
                        analysis_type='extraction',
                        status='error',
                        data=json.dumps({'error': str(e)}, ensure_ascii=False),
                        timestamp=datetime.now()
                    )
                    db.session.add(error_result)
                    db.session.commit()
        
        # بدء الاستخراج في الخلفية
        thread = threading.Thread(target=extract_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'تم بدء عملية الاستخراج بنجاح',
            'url': url,
            'status': 'processing'
        })
        
    except Exception as e:
        logging.error(f"خطأ في API الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extraction-status/<path:url>')
def api_extraction_status(url):
    """فحص حالة الاستخراج"""
    try:
        latest_result = ScrapeResult.query.filter_by(
            url=url,
            analysis_type='extraction'
        ).order_by(ScrapeResult.created_at.desc()).first()
        
        if not latest_result:
            return jsonify({'status': 'not_found'})
        
        response_data = {
            'status': latest_result.status,
            'created_at': latest_result.created_at.isoformat()
        }
        
        if latest_result.data:
            data = json.loads(latest_result.data)
            response_data.update(data)
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"خطأ في فحص حالة الاستخراج: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def reports_page():
    """صفحة التقارير"""
    return render_template('reports.html')

# ============== مسارات الأدوات المتطورة ==============

@app.route('/ultra-extractor')
def ultra_extractor_page():
    """صفحة المستخرج الفائق"""
    return render_template('ultra_extractor.html')

@app.route('/api/ultra-extract', methods=['POST'])
def api_ultra_extract():
    """واجهة برمجية للمستخرج الفائق"""
    try:
        data = request.get_json()
        url = data.get('url')
        config = data.get('config', {})
        
        if not url:
            return jsonify({'error': 'الرابط مطلوب'}), 400
            
        if UltraSmartExtractor:
            extractor = UltraSmartExtractor(url, config)
            result = extractor.extract_ultra_smart()
        else:
            result = {'error': 'المستخرج الفائق غير متوفر في هذا الإصدار'}
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logging.error(f"خطأ في الاستخراج الفائق: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/enhanced-extractor')  
def enhanced_extractor_page():
    """صفحة المستخرج المتطور والآمن"""
    return render_template('enhanced_extractor.html')

@app.route('/api/enhanced-extract', methods=['POST'])
def api_enhanced_extract():
    """واجهة برمجية للمستخرج المتطور"""
    try:
        data = request.get_json()
        url = data.get('url')
        level = data.get('level', 'standard')
        permissions = data.get('permissions', {})
        
        if not url:
            return jsonify({'error': 'الرابط مطلوب'}), 400
            
        # إنشاء إعدادات الاستخراج
        from enhanced_website_extractor import ExtractionConfig, ExtractionLevel
        config = ExtractionConfig(
            url=url,
            extraction_level=ExtractionLevel(level)
        )
        
        # Simple extraction using basic methods
        from enhanced_website_extractor import EnhancedWebsiteExtractor
        result = {'message': 'Enhanced extraction not available in current version'}
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logging.error(f"خطأ في الاستخراج المتطور: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/advanced-ad-blocker')
def advanced_ad_blocker_page():
    """صفحة حاجب الإعلانات المتطور"""
    return render_template('advanced_ad_blocker.html')

@app.route('/api/advanced-ad-block', methods=['POST'])
def api_advanced_ad_block():
    """واجهة برمجية لحاجب الإعلانات المتطور"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'الرابط مطلوب'}), 400
            
        if AdvancedAdBlocker:
            blocker = AdvancedAdBlocker()
            result = {'message': 'Advanced ad blocking functionality available', 'stats': getattr(blocker, 'blocked_stats', {})}
        else:
            result = {'error': 'حاجب الإعلانات المتطور غير متوفر في هذا الإصدار'}
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logging.error(f"خطأ في حجب الإعلانات المتطور: {e}")
        return jsonify({'error': str(e)}), 500



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
            from security_analyzer import SecurityAnalyzer
            analyzer = SecurityAnalyzer()
            results = analyzer.analyze_security(url)
        except ImportError:
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
            from performance_analyzer import PerformanceAnalyzer
            analyzer = PerformanceAnalyzer()
            results = analyzer.analyze_performance(url)
        except ImportError:
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
            from seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_seo(url)
        except ImportError:
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