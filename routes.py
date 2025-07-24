from flask import render_template, request, jsonify, redirect, url_for, flash, make_response
from app import app, db
from models import ScrapeResult
from scraper import WebScraper
from analyzer import WebsiteAnalyzer
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
        args=(scrape_result.id, url, max_depth)
    )
    thread.daemon = True
    thread.start()
    
    flash('Analysis started! You will be redirected to results when complete.', 'success')
    return redirect(url_for('results', result_id=scrape_result.id))

def perform_analysis(result_id, url, max_depth):
    """Perform the actual website analysis in background"""
    with app.app_context():
        scrape_result = ScrapeResult.query.get(result_id)
        if not scrape_result:
            return
        
        try:
            logging.info(f"Starting analysis for {url}")
            
            # Initialize scraper and analyzer
            scraper = WebScraper(url, max_depth=max_depth, delay=1.0)
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
            
            # Mark as completed
            scrape_result.status = 'completed'
            scrape_result.completed_at = datetime.utcnow()
            
            logging.info(f"Analysis completed for {url}")
            
        except Exception as e:
            logging.error(f"Analysis failed for {url}: {str(e)}")
            scrape_result.status = 'failed'
            scrape_result.error_message = str(e)
        
        finally:
            db.session.commit()

@app.route('/results/<int:result_id>')
def results(result_id):
    """Display analysis results"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    
    # If still pending, show loading page
    if scrape_result.status == 'pending':
        return render_template('results.html', result=scrape_result, loading=True)
    
    # If failed, show error
    if scrape_result.status == 'failed':
        return render_template('results.html', result=scrape_result, error=True)
    
    # Show completed results
    return render_template('results.html', result=scrape_result, completed=True)

@app.route('/download/<int:result_id>/<format>')
def download_results(result_id, format):
    """Download analysis results in specified format"""
    scrape_result = ScrapeResult.query.get_or_404(result_id)
    
    if scrape_result.status != 'completed':
        flash('Analysis not completed yet', 'error')
        return redirect(url_for('results', result_id=result_id))
    
    # Compile all data
    report_data = {
        'url': scrape_result.url,
        'title': scrape_result.title,
        'analyzed_at': scrape_result.completed_at.isoformat() if scrape_result.completed_at else None,
        'structure_analysis': scrape_result.get_structure_data(),
        'assets_analysis': scrape_result.get_assets_data(),
        'technology_analysis': scrape_result.get_technology_data(),
        'seo_analysis': scrape_result.get_seo_data(),
        'navigation_analysis': scrape_result.get_navigation_data()
    }
    
    if format == 'json':
        response = make_response(json.dumps(report_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=website_analysis_{result_id}.json'
        return response
    
    elif format == 'html':
        html_content = render_template('report.html', data=report_data)
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=website_analysis_{result_id}.html'
        return response
    
    else:
        flash('Invalid format requested', 'error')
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

@app.route('/history')
def history():
    """Show analysis history"""
    results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(50).all()
    return render_template('history.html', results=results)
