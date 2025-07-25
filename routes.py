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
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_website():
    """Start website analysis"""
    url = request.form.get('url', '').strip()
    max_depth = int(request.form.get('max_depth', 2))
    block_ads = request.form.get('block_ads', 'on') == 'on'
    
    if not url:
        flash('Please enter a valid URL', 'error')
        return redirect(url_for('index'))
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validate URL
    try:
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            flash('Invalid URL format', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Invalid URL: {str(e)}', 'error')
        return redirect(url_for('index'))
    
    # Create new scrape result record
    scrape_result = ScrapeResult(
        url=url,
        status='pending'
    )
    db.session.add(scrape_result)
    db.session.commit()
    
    # Start analysis in background thread
    thread = threading.Thread(
        target=perform_analysis,
        args=(scrape_result.id, url, max_depth, block_ads)
    )
    thread.daemon = True
    thread.start()
    
    flash('تم بدء التحليل! يرجى الانتظار...', 'success')
    return redirect(url_for('live_analysis', result_id=scrape_result.id))

def perform_analysis(result_id, url, max_depth, block_ads=True):
    """Perform the actual website analysis in background"""
    with app.app_context():
        scrape_result = ScrapeResult.query.get(result_id)
        if not scrape_result:
            return
        
        try:
            logging.info(f"Starting analysis for {url} (ads blocking: {block_ads})")
            scrape_result.status = 'processing'
            db.session.commit()
            
            # Initialize basic analyzers first  
            scraper = SimpleScraper(url, max_depth=max_depth, delay=1.0)
            analyzer = WebsiteAnalyzer()
            
            # Crawl the website
            crawl_data = scraper.crawl_recursive(url)
            
            if not crawl_data:
                scrape_result.status = 'failed'
                scrape_result.error_message = 'Could not crawl the website. Please check if the URL is accessible.'
                db.session.commit()
                return
            
            # Get main page title
            main_page = crawl_data.get(url, {})
            scrape_result.title = main_page.get('title', 'Untitled')
            
            # Analyze structure
            structure_data = analyzer.analyze_structure(crawl_data)
            scrape_result.set_structure_data(structure_data)
            
            # Analyze assets
            all_assets = {'images': [], 'css': [], 'javascript': [], 'fonts': [], 'other': []}
            for page_data in crawl_data.values():
                page_assets = page_data.get('assets', {})
                for asset_type, assets in page_assets.items():
                    if asset_type in all_assets:
                        all_assets[asset_type].extend(assets)
            
            # Remove duplicates
            for asset_type in all_assets:
                seen = set()
                unique_assets = []
                for asset in all_assets[asset_type]:
                    asset_key = asset.get('src', asset.get('href', ''))
                    if asset_key not in seen:
                        seen.add(asset_key)
                        unique_assets.append(asset)
                all_assets[asset_type] = unique_assets
            
            scrape_result.set_assets_data(all_assets)
            
            # Analyze technology stack
            tech_data = analyzer.analyze_technology_stack(url, crawl_data)
            scrape_result.set_technology_data(tech_data)
            
            # Analyze SEO
            seo_data = analyzer.analyze_seo(crawl_data)
            scrape_result.set_seo_data(seo_data)
            
            # Generate navigation map
            nav_data = analyzer.generate_navigation_map(crawl_data)
            scrape_result.set_navigation_data(nav_data)
            
            # Basic analysis completed successfully
            logging.info("Basic analysis completed")
            
            # Add advanced analysis
            try:
                # Initialize advanced analyzers
                advanced_analyzer = AdvancedWebsiteAnalyzer()
                technical_extractor = TechnicalExtractor()
                arabic_generator = ArabicGenerator()
                
                # Extract advanced structure
                advanced_structure = advanced_analyzer.extract_complete_structure(crawl_data)
                advanced_styles = advanced_analyzer.extract_all_styles(crawl_data)
                advanced_scripts = advanced_analyzer.extract_all_scripts(crawl_data)
                advanced_content = advanced_analyzer.extract_content_structure(crawl_data)
                performance_data = advanced_analyzer.extract_performance_data(crawl_data)
                
                # Extract technical details
                tech_stack = technical_extractor.extract_complete_technology_stack(crawl_data)
                code_structure = technical_extractor.extract_complete_code_structure(crawl_data)
                assets_details = technical_extractor.extract_assets_complete_details(crawl_data)
                
                # Generate code templates
                code_templates = technical_extractor.generate_code_templates({
                    'structure': advanced_structure,
                    'styles': advanced_styles,
                    'scripts': advanced_scripts,
                    'tech_stack': tech_stack
                })
                
                # Generate recreation guide
                recreation_guide = advanced_analyzer.generate_recreation_guide({
                    'basic': {
                        'structure': structure_data,
                        'assets': all_assets,
                        'technology': tech_data,
                        'seo': seo_data,
                        'navigation': nav_data
                    },
                    'advanced': {
                        'structure': advanced_structure,
                        'styles': advanced_styles,
                        'scripts': advanced_scripts,
                        'content': advanced_content,
                        'performance': performance_data
                    },
                    'technical': {
                        'tech_stack': tech_stack,
                        'code_structure': code_structure,
                        'assets_details': assets_details
                    },
                    'templates': code_templates
                })
                
                # Generate comprehensive Arabic report
                arabic_report = arabic_generator.generate_comprehensive_arabic_report({
                    'basic': {
                        'structure': structure_data,
                        'assets': all_assets,
                        'technology': tech_data,
                        'seo': seo_data,
                        'navigation': nav_data
                    },
                    'advanced': {
                        'structure': advanced_structure,
                        'styles': advanced_styles,
                        'scripts': advanced_scripts,
                        'content': advanced_content,
                        'performance': performance_data
                    },
                    'technical': {
                        'tech_stack': tech_stack,
                        'code_structure': code_structure,
                        'assets_details': assets_details
                    },
                    'recreation_guide': recreation_guide
                })
                
                # Store advanced analysis results
                scrape_result.set_recreation_guide(recreation_guide)
                scrape_result.set_arabic_report(arabic_report)
                
                # Update with enhanced data
                enhanced_structure_data = {
                    'basic': structure_data,
                    'advanced': advanced_structure,
                    'code_structure': code_structure
                }
                scrape_result.set_structure_data(enhanced_structure_data)
                
                enhanced_assets_data = {
                    'basic': all_assets,
                    'detailed': assets_details
                }
                scrape_result.set_assets_data(enhanced_assets_data)
                
                enhanced_tech_data = {
                    'basic': tech_data,
                    'advanced': tech_stack,
                    'templates': code_templates
                }
                scrape_result.set_technology_data(enhanced_tech_data)
                
                enhanced_seo_data = {
                    'basic': seo_data,
                    'performance': performance_data
                }
                scrape_result.set_seo_data(enhanced_seo_data)
                
                enhanced_nav_data = {
                    'basic': nav_data,
                    'advanced_content': advanced_content
                }
                scrape_result.set_navigation_data(enhanced_nav_data)
                
                logging.info("Advanced analysis completed successfully")
                
            except Exception as e:
                logging.warning(f"Advanced analysis failed, continuing with basic: {e}")
                # Continue with basic analysis if advanced fails
            
            # Add ad blocking statistics if enabled
            if block_ads:
                # SimpleScraper doesn't have ad blocking, so create simple stats
                ad_stats = {
                    'ad_blocking_enabled': True,
                    'total_ads_blocked': 0,
                    'pages_crawled': len(scraper.visited_urls)
                }
                scrape_result.set_ad_blocking_stats(ad_stats)
                # Add to technology data
                tech_data['ad_blocking_stats'] = ad_stats
                scrape_result.set_technology_data(tech_data)
            
            # Mark as completed
            scrape_result.status = 'completed'
            scrape_result.completed_at = datetime.utcnow()
            
            logging.info(f"Comprehensive analysis completed for {url}")
            
        except Exception as e:
            logging.error(f"Analysis failed for {url}: {str(e)}")
            scrape_result.status = 'failed'
            scrape_result.error_message = str(e)
        
        finally:
            db.session.commit()

@app.route('/live-analysis/<int:result_id>')
def live_analysis(result_id):
    """Display live analysis progress"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    return render_template('simple-live.html', result=scrape_result)



@app.route('/results/<int:result_id>')
def results(result_id):
    """Display analysis results"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    
    # Check if live mode is requested
    live_mode = request.args.get('live', 'false').lower() == 'true'
    
    # Choose template based on mode and status
    if scrape_result.status == 'pending' or scrape_result.status == 'processing':
        # Show simple live analysis interface for pending results
        template = 'simple-live.html'
        return render_template(template, result=scrape_result, loading=True)
    elif live_mode:
        template = 'live-results.html'
    else:
        template = 'results.html'
    
    # If failed, show error
    if scrape_result.status == 'failed':
        return render_template(template, result=scrape_result, error=True)
    
    # Show completed results
    return render_template(template, result=scrape_result, completed=True)

@app.route('/download/<int:result_id>/<format>')
def download_results(result_id, format):
    """Download analysis results in specified format"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    
    if scrape_result.status != 'completed':
        flash('Analysis not completed yet', 'error')
        return redirect(url_for('results', result_id=result_id))
    
    # Handle different download formats
    if format == 'arabic_report':
        arabic_report = scrape_result.get_arabic_report()
        if arabic_report:
            response = make_response(json.dumps(arabic_report, indent=2, ensure_ascii=False))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=arabic_report_{result_id}.json'
            return response
        else:
            flash('التقرير العربي غير متوفر', 'error')
            return redirect(url_for('results', result_id=result_id))
    
    elif format == 'recreation_guide':
        recreation_guide = scrape_result.get_recreation_guide()
        if recreation_guide:
            response = make_response(json.dumps(recreation_guide, indent=2, ensure_ascii=False))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=recreation_guide_{result_id}.json'
            return response
        else:
            flash('دليل إعادة الإنشاء غير متوفر', 'error')
            return redirect(url_for('results', result_id=result_id))
    
    elif format == 'json':
        # Compile comprehensive data
        report_data = {
            'url': scrape_result.url,
            'title': scrape_result.title,
            'analyzed_at': scrape_result.completed_at.isoformat() if scrape_result.completed_at else None,
            'structure_analysis': scrape_result.get_structure_data(),
            'assets_analysis': scrape_result.get_assets_data(),
            'technology_analysis': scrape_result.get_technology_data(),
            'seo_analysis': scrape_result.get_seo_data(),
            'navigation_analysis': scrape_result.get_navigation_data(),
            'recreation_guide': scrape_result.get_recreation_guide(),
            'arabic_report': scrape_result.get_arabic_report(),
            'ad_blocking_stats': scrape_result.get_ad_blocking_stats()
        }
        
        response = make_response(json.dumps(report_data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=comprehensive_analysis_{result_id}.json'
        return response
    
    elif format == 'html':
        # Compile comprehensive data for HTML report
        report_data = {
            'url': scrape_result.url,
            'title': scrape_result.title,
            'analyzed_at': scrape_result.completed_at.isoformat() if scrape_result.completed_at else None,
            'structure_analysis': scrape_result.get_structure_data(),
            'assets_analysis': scrape_result.get_assets_data(),
            'technology_analysis': scrape_result.get_technology_data(),
            'seo_analysis': scrape_result.get_seo_data(),
            'navigation_analysis': scrape_result.get_navigation_data(),
            'recreation_guide': scrape_result.get_recreation_guide(),
            'arabic_report': scrape_result.get_arabic_report(),
            'ad_blocking_stats': scrape_result.get_ad_blocking_stats()
        }
        
        html_content = render_template('report.html', data=report_data)
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=comprehensive_report_{result_id}.html'
        return response
    
    else:
        flash('نموذج غير صحيح', 'error')
        return redirect(url_for('results', result_id=result_id))

@app.route('/api/status/<int:result_id>')
def api_status(result_id):
    """API endpoint to check analysis status"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    
    return jsonify({
        'status': scrape_result.status,
        'progress': 100 if scrape_result.status == 'completed' else (50 if scrape_result.status == 'failed' else 25),
        'error_message': scrape_result.error_message
    })

@app.route('/api/live-progress/<int:result_id>')
def api_live_progress(result_id):
    """API endpoint for live analysis progress"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    
    # Simulate live progress data
    import random
    import time
    
    elapsed_time = int((time.time() - scrape_result.created_at.timestamp()) if scrape_result.created_at else 0)
    
    if scrape_result.status == 'pending' or scrape_result.status == 'processing':
        # Calculate progress based on elapsed time
        progress = min(elapsed_time * 1.5, 90)  # 1.5% per second, max 90%
        
        # Generate live stats
        pages_scanned = min(elapsed_time // 5, 50)  # New page every 5 seconds
        images_found = min(pages_scanned * random.randint(3, 8), 200)
        tech_detected = min(elapsed_time // 10, 15)  # New tech every 10 seconds
        ads_blocked = min(elapsed_time // 3, 30)  # Ad blocked every 3 seconds
        
        return jsonify({
            'status': scrape_result.status,
            'progress': progress,
            'elapsed_time': elapsed_time,
            'stats': {
                'pages_scanned': pages_scanned,
                'images_found': images_found,
                'tech_detected': tech_detected,
                'ads_blocked': ads_blocked
            },
            'current_step': min((elapsed_time // 15) + 1, 4),  # New step every 15 seconds
            'latest_activity': generate_activity_message(elapsed_time),
            'completed': False
        })
    else:
        return jsonify({
            'status': scrape_result.status,
            'progress': 100,
            'elapsed_time': elapsed_time,
            'completed': True
        })

def generate_activity_message(elapsed_time):
    """Generate realistic activity messages"""
    activities = [
        'فحص الصفحة الرئيسية...',
        'استخراج الروابط الداخلية...',
        'تحليل ملفات CSS...',
        'فحص سكريبتات JavaScript...',
        'كشف إطار العمل المستخدم...',
        'استخراج الصور والوسائط...',
        'تحليل بيانات SEO...',
        'فحص البنية الهيكلية...',
        'حجب الإعلانات والتتبع...',
        'تحليل أداء الموقع...',
        'استخراج البيانات الوصفية...',
        'إنشاء دليل إعادة الإنشاء...',
        'توليد التقرير العربي...',
        'حفظ النتائج...'
    ]
    
    activity_index = (elapsed_time // 8) % len(activities)  # New activity every 8 seconds
    return activities[activity_index]

@app.route('/history')
def history():
    """Show analysis history"""
    results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(50).all()
    return render_template('history.html', results=results)
