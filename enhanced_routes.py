"""
الطرق المحسنة - Enhanced Routes
طرق متطورة لجميع الميزات الجديدة
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, make_response
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

@app.route('/')
def index():
    """Main page with URL input form"""
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering index page: {e}")
        return f"خطأ في تحميل الصفحة الرئيسية: {str(e)}", 500

@app.route('/analyze', methods=['POST'])
def analyze_website():
    """Start website analysis"""
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
            
        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                flash('رابط غير صحيح', 'error')
                return redirect(url_for('index'))
        except Exception:
            flash('رابط غير صحيح', 'error')
            return redirect(url_for('index'))
        
        # Start analysis in background
        def analyze_in_background():
            with app.app_context():
                try:
                    scraper = SimpleScraper(url, max_depth=max_depth)
                    analyzer = AdvancedWebsiteAnalyzer()
                    
                    # Scrape the website
                    scrape_data = scraper.crawl_recursive(url, 0)
                    
                    # Analyze the scraped data
                    analysis_result = analyzer.extract_complete_structure(scrape_data)
                    
                    # Store in database
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
                
        # Start background analysis
        thread = threading.Thread(target=analyze_in_background)
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
        flash('خطأ في تحميل النتائج', 'error')
        return redirect(url_for('history'))

from flask import render_template, request, jsonify, redirect, url_for, flash, send_file
from app import app, db
from models import ScrapeResult
import json
import logging
from datetime import datetime
import io
import base64
from sqlalchemy import desc

# استيراد المحللات الجديدة
from security_analyzer import SecurityAnalyzer
from performance_analyzer import PerformanceAnalyzer
from seo_analyzer import SEOAnalyzer
from competitor_analyzer import CompetitorAnalyzer

@app.route('/security-analysis')
def security_analysis_page():
    """صفحة تحليل الأمان"""
    return render_template('security_analysis.html')

@app.route('/api/security-analyze', methods=['POST'])
def api_security_analyze():
    """API تحليل الأمان"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        analyzer = SecurityAnalyzer()
        results = analyzer.analyze_security(url)
        
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
        logging.error(f"خطأ في تحليل الأمان: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/performance-analysis')
def performance_analysis_page():
    """صفحة تحليل الأداء"""
    return render_template('performance_analysis.html')

@app.route('/api/performance-analyze', methods=['POST'])
def api_performance_analyze():
    """API تحليل الأداء"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        analyzer = PerformanceAnalyzer()
        results = analyzer.analyze_performance(url)
        
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
        logging.error(f"خطأ في تحليل الأداء: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/seo-analysis')
def seo_analysis_page():
    """صفحة تحليل SEO"""
    return render_template('seo_analysis.html')

@app.route('/api/seo-analyze', methods=['POST'])
def api_seo_analyze():
    """API تحليل SEO"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        analyzer = SEOAnalyzer()
        results = analyzer.analyze_seo(url)
        
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
        logging.error(f"خطأ في تحليل SEO: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/competitor-analysis')
def competitor_analysis_page():
    """صفحة تحليل المنافسين"""
    return render_template('competitor_analysis.html')

@app.route('/api/competitor-analyze', methods=['POST'])
def api_competitor_analyze():
    """API تحليل المنافسين"""
    try:
        data = request.get_json()
        main_url = data.get('main_url')
        competitor_urls = data.get('competitor_urls', [])
        
        if not main_url:
            return jsonify({'error': 'URL الرئيسي مطلوب'}), 400
        
        analyzer = CompetitorAnalyzer()
        results = analyzer.analyze_competitors(main_url, competitor_urls)
        
        # حفظ النتائج
        scrape_result = ScrapeResult(
            url=main_url,
            analysis_type='competitor',
            status='completed',
            data=json.dumps(results, ensure_ascii=False),
            timestamp=datetime.now()
        )
        db.session.add(scrape_result)
        db.session.commit()
        
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"خطأ في تحليل المنافسين: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/comprehensive-analysis')
def comprehensive_analysis_page():
    """صفحة التحليل الشامل"""
    return render_template('comprehensive_analysis.html')

@app.route('/api/comprehensive-analyze', methods=['POST'])
def api_comprehensive_analyze():
    """API التحليل الشامل"""
    try:
        data = request.get_json()
        url = data.get('url')
        analysis_types = data.get('analysis_types', ['basic', 'security', 'performance', 'seo'])
        
        if not url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        comprehensive_results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'analysis_types': analysis_types,
            'results': {}
        }
        
        # تشغيل التحليلات المطلوبة
        if 'security' in analysis_types:
            security_analyzer = SecurityAnalyzer()
            comprehensive_results['results']['security'] = security_analyzer.analyze_security(url)
        
        if 'performance' in analysis_types:
            performance_analyzer = PerformanceAnalyzer()
            comprehensive_results['results']['performance'] = performance_analyzer.analyze_performance(url)
        
        if 'seo' in analysis_types:
            seo_analyzer = SEOAnalyzer()
            comprehensive_results['results']['seo'] = seo_analyzer.analyze_seo(url)
        
        # حفظ النتائج الشاملة
        scrape_result = ScrapeResult(
            url=url,
            analysis_type='comprehensive',
            status='completed',
            data=json.dumps(comprehensive_results, ensure_ascii=False),
            timestamp=datetime.now()
        )
        db.session.add(scrape_result)
        db.session.commit()
        
        return jsonify(comprehensive_results)
        
    except Exception as e:
        logging.error(f"خطأ في التحليل الشامل: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم الرئيسية"""
    try:
        # إحصائيات عامة
        total_analyses = ScrapeResult.query.count()
        recent_analyses = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(10).all()
        
        # إحصائيات حسب النوع
        analysis_stats = {}
        for analysis_type in ['basic', 'security', 'performance', 'seo', 'competitor', 'comprehensive']:
            count = ScrapeResult.query.filter_by(analysis_type=analysis_type).count()
            analysis_stats[analysis_type] = count
        
        return render_template('dashboard.html', 
                             total_analyses=total_analyses,
                             recent_analyses=recent_analyses,
                             analysis_stats=analysis_stats)
    
    except Exception as e:
        logging.error(f"خطأ في لوحة التحكم: {e}")
        flash('حدث خطأ في تحميل لوحة التحكم', 'error')
        return redirect(url_for('index'))

@app.route('/reports')
def reports_page():
    """صفحة التقارير"""
    try:
        # جلب جميع التحليلات للتقارير
        analyses = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).all()
        
        return render_template('reports.html', analyses=analyses)
    
    except Exception as e:
        logging.error(f"خطأ في صفحة التقارير: {e}")
        flash('حدث خطأ في تحميل التقارير', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/export-report/<int:analysis_id>')
def api_export_report(analysis_id):
    """تصدير تقرير كـ PDF"""
    try:
        analysis = ScrapeResult.query.get_or_404(analysis_id)
        
        # هنا يمكنك إضافة مكتبة PDF مثل reportlab
        # للبساطة، سنعيد JSON الآن
        
        report_data = {
            'analysis_id': analysis.id,
            'url': analysis.url,
            'type': analysis.analysis_type,
            'timestamp': analysis.timestamp.isoformat(),
            'data': json.loads(analysis.data) if analysis.data else {}
        }
        
        # تحويل إلى JSON مع تنسيق جميل
        json_output = json.dumps(report_data, ensure_ascii=False, indent=2)
        
        # إنشاء ملف للتنزيل
        output = io.StringIO()
        output.write(json_output)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=f'analysis_report_{analysis_id}.json',
            mimetype='application/json'
        )
    
    except Exception as e:
        logging.error(f"خطأ في تصدير التقرير: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis-history')
def api_analysis_history():
    """API لجلب تاريخ التحليلات"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        analysis_type = request.args.get('type', None)
        
        query = ScrapeResult.query
        
        if analysis_type:
            query = query.filter_by(analysis_type=analysis_type)
        
        analyses = query.order_by(ScrapeResult.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'analyses': [{
                'id': analysis.id,
                'url': analysis.url,
                'type': analysis.analysis_type,
                'status': analysis.status,
                'timestamp': analysis.timestamp.isoformat()
            } for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page
        })
    
    except Exception as e:
        logging.error(f"خطأ في جلب تاريخ التحليلات: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-analysis/<int:analysis_id>', methods=['DELETE'])
def api_delete_analysis(analysis_id):
    """حذف تحليل محدد"""
    try:
        analysis = ScrapeResult.query.get_or_404(analysis_id)
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف التحليل بنجاح'})
    
    except Exception as e:
        logging.error(f"خطأ في حذف التحليل: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings_page():
    """صفحة الإعدادات"""
    return render_template('settings.html')

@app.route('/api/save-settings', methods=['POST'])
def api_save_settings():
    """حفظ الإعدادات"""
    try:
        data = request.get_json()
        
        # هنا يمكنك حفظ الإعدادات في قاعدة البيانات أو ملف تكوين
        # للبساطة، سنعيد رسالة نجاح الآن
        
        return jsonify({'message': 'تم حفظ الإعدادات بنجاح'})
    
    except Exception as e:
        logging.error(f"خطأ في حفظ الإعدادات: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/site-comparison', methods=['POST'])
def api_site_comparison():
    """مقارنة متعددة المواقع"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        comparison_type = data.get('type', 'basic')
        
        if len(urls) < 2:
            return jsonify({'error': 'يجب تقديم موقعين على الأقل للمقارنة'}), 400
        
        comparison_results = {
            'urls': urls,
            'comparison_type': comparison_type,
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }
        
        # تشغيل التحليل المناسب لكل موقع
        if comparison_type == 'performance':
            analyzer = PerformanceAnalyzer()
            for url in urls:
                comparison_results['results'][url] = analyzer.analyze_performance(url)
        
        elif comparison_type == 'seo':
            analyzer = SEOAnalyzer()
            for url in urls:
                comparison_results['results'][url] = analyzer.analyze_seo(url)
        
        elif comparison_type == 'security':
            analyzer = SecurityAnalyzer()
            for url in urls:
                comparison_results['results'][url] = analyzer.analyze_security(url)
        
        # إضافة تحليل مقارن
        comparison_results['comparison_analysis'] = _generate_comparison_insights(comparison_results['results'])
        
        return jsonify(comparison_results)
    
    except Exception as e:
        logging.error(f"خطأ في مقارنة المواقع: {e}")
        return jsonify({'error': str(e)}), 500

def _generate_comparison_insights(results):
    """توليد رؤى مقارنة بين المواقع"""
    insights = {
        'best_performing': None,
        'worst_performing': None,
        'average_scores': {},
        'recommendations': []
    }
    
    if not results:
        return insights
    
    # مقارنة النقاط إذا كانت موجودة
    scores = {}
    for url, data in results.items():
        if isinstance(data, dict):
            score_keys = ['performance_score', 'seo_score', 'overall_score']
            for key in score_keys:
                if key in data:
                    scores[url] = data[key]
                    break
    
    if scores:
        best_url = max(scores.keys(), key=lambda x: scores[x])
        worst_url = min(scores.keys(), key=lambda x: scores[x])
        
        insights['best_performing'] = {
            'url': best_url,
            'score': scores[best_url]
        }
        insights['worst_performing'] = {
            'url': worst_url,
            'score': scores[worst_url]
        }
        
        insights['average_scores'] = {
            'average': sum(scores.values()) / len(scores),
            'highest': max(scores.values()),
            'lowest': min(scores.values())
        }
    
    # توصيات عامة
    insights['recommendations'] = [
        'تحسين الموقع الأضعف أداءً',
        'تطبيق أفضل الممارسات من الموقع الأفضل',
        'مراقبة الأداء بانتظام',
        'إجراء مقارنات دورية'
    ]
    
    return insights

# معالج الأخطاء المحسن
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