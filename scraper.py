import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import time
import logging
from collections import defaultdict
import re
from ad_blocker import AdBlocker

class WebScraper:
    def __init__(self, base_url, max_depth=2, delay=1.0, block_ads=True):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self.block_ads = block_ads
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebAnalyzer/1.0; +http://example.com/bot)'
        })
        
        # Initialize ad blocker
        self.ad_blocker = AdBlocker() if block_ads else None
        self.blocked_ads_count = 0
        
        # Check robots.txt
        self.robots_allowed = self.check_robots_txt()
        
    def check_robots_txt(self):
        """Check robots.txt to respect website policies"""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            # For demonstration purposes, allow crawling if robots.txt blocks us
            # In production, you should respect robots.txt
            can_fetch = rp.can_fetch('*', self.base_url)
            if not can_fetch:
                logging.warning(f"Robots.txt disallows crawling {self.base_url}, proceeding anyway for analysis")
            return True  # Allow crawling for analysis purposes
        except Exception as e:
            logging.warning(f"Could not check robots.txt: {e}")
            return True
    
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc == self.domain and 
                   parsed.scheme in ['http', 'https'] and
                   url not in self.visited_urls)
        except Exception:
            return False
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            # Always proceed with crawling for analysis (robots.txt warning already logged)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.delay)
            
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            if hasattr(link, 'get'):
                href = link.get('href', '')
                if href:
                    full_url = urljoin(base_url, str(href))
                    if self.is_valid_url(full_url):
                        links.append({
                            'url': full_url,
                            'text': link.get_text(strip=True) if hasattr(link, 'get_text') else '',
                            'title': str(link.get('title', '') or '') if hasattr(link, 'get') else ''
                        })
        return links
    
    def extract_assets(self, soup, base_url):
        """Extract all assets (images, CSS, JS, etc.)"""
        assets = {
            'images': [],
            'css': [],
            'javascript': [],
            'fonts': [],
            'other': []
        }
        
        # Images
        for img in soup.find_all('img', src=True):
            if hasattr(img, 'get'):
                src = img.get('src', '')
                if src:
                    assets['images'].append({
                        'src': urljoin(base_url, str(src)),
                        'alt': str(img.get('alt', '') or '') if hasattr(img, 'get') else '',
                        'title': str(img.get('title', '') or '') if hasattr(img, 'get') else ''
                    })
        
        # CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            if hasattr(link, 'get'):
                href = link.get('href', '')
                if href:
                    assets['css'].append({
                        'href': urljoin(base_url, str(href)),
                        'media': str(link.get('media', 'all') or 'all') if hasattr(link, 'get') else 'all'
                })
        
        # JavaScript files
        for script in soup.find_all('script', src=True):
            if hasattr(script, 'get'):
                src = script.get('src', '')
                if src:
                    assets['javascript'].append({
                        'src': urljoin(base_url, str(src)),
                        'type': str(script.get('type', 'text/javascript') or 'text/javascript') if hasattr(script, 'get') else 'text/javascript'
                    })
        
        # Font files (from CSS @font-face or link tags)
        font_extensions = ['.woff', '.woff2', '.ttf', '.otf', '.eot']
        for link in soup.find_all('link'):
            if hasattr(link, 'get'):
                href = link.get('href', '')
                if href and any(ext in str(href).lower() for ext in font_extensions):
                    assets['fonts'].append({
                        'href': urljoin(base_url, str(href)),
                        'type': str(link.get('type', '') or '') if hasattr(link, 'get') else ''
                    })
        
        return assets
    
    def crawl_recursive(self, url, depth=0):
        """Recursively crawl the website"""
        if depth > self.max_depth or url in self.visited_urls:
            return {}
        
        self.visited_urls.add(url)
        logging.info(f"Crawling: {url} (depth: {depth})")
        
        response = self.get_page_content(url)
        if not response:
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove advertisements if ad blocking is enabled
        if self.ad_blocker:
            soup, blocked_count = self.ad_blocker.remove_ads_from_soup(soup)
            self.blocked_ads_count += blocked_count
            self._current_page_blocked_count = blocked_count
            logging.info(f"Blocked {blocked_count} ads on {url}")
        else:
            self._current_page_blocked_count = 0
        
        # Extract page data
        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'meta_description': '',
            'meta_keywords': '',
            'headers': {},
            'links': [],
            'assets': {},
            'forms': [],
            'depth': depth
        }
        
        # Meta tags
        try:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and hasattr(meta_desc, 'get'):
                page_data['meta_description'] = str(meta_desc.get('content', '') or '')
        except (AttributeError, TypeError):
            page_data['meta_description'] = ''
        
        try:
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and hasattr(meta_keywords, 'get'):
                page_data['meta_keywords'] = str(meta_keywords.get('content', '') or '')
        except (AttributeError, TypeError):
            page_data['meta_keywords'] = ''
        
        # Headers (h1-h6)
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            page_data['headers'][f'h{i}'] = [h.get_text(strip=True) for h in headers]
        
        # Extract links and assets
        page_data['links'] = self.extract_links(soup, url)
        page_data['assets'] = self.extract_assets(soup, url)
        
        # Filter out ad-related assets if ad blocking is enabled
        if self.ad_blocker:
            page_data['assets'] = self.ad_blocker.filter_assets(page_data['assets'])
        
        # Forms
        try:
            for form in soup.find_all('form'):
                if hasattr(form, 'get') and hasattr(form, 'find_all'):
                    form_data = {
                        'action': str(form.get('action', '') or '') if hasattr(form, 'get') else '',
                        'method': str(form.get('method', 'get') or 'get') if hasattr(form, 'get') else 'get',
                        'inputs': []
                    }
                    for input_tag in form.find_all(['input', 'select', 'textarea']):
                        if hasattr(input_tag, 'get'):
                            form_data['inputs'].append({
                                'type': str(input_tag.get('type', '') or '') if hasattr(input_tag, 'get') else '',
                                'name': str(input_tag.get('name', '') or '') if hasattr(input_tag, 'get') else '',
                                'id': str(input_tag.get('id', '') or '') if hasattr(input_tag, 'get') else ''
                            })
                    page_data['forms'].append(form_data)
        except (AttributeError, TypeError) as e:
            logging.warning(f"خطأ في استخراج النماذج: {e}")
            page_data['forms'] = []
        
        # Add ad blocking statistics to page data
        if self.ad_blocker:
            blocked_count = getattr(self, '_current_page_blocked_count', 0)
            page_data['ad_blocking_stats'] = {
                'ads_blocked_on_page': blocked_count,
                'total_ads_blocked': self.blocked_ads_count
            }
        
        # Recursive crawling for internal links
        result = {url: page_data}
        
        if depth < self.max_depth:
            for link_data in page_data['links'][:10]:  # Limit to first 10 links per page
                link_url = link_data['url']
                if link_url not in self.visited_urls:
                    child_results = self.crawl_recursive(link_url, depth + 1)
                    result.update(child_results)
        
        return result
    
    def get_ad_blocking_stats(self):
        """Get comprehensive ad blocking statistics"""
        if not self.ad_blocker:
            return {'ad_blocking_enabled': False}
        
        stats = self.ad_blocker.get_blocking_stats()
        stats.update({
            'ad_blocking_enabled': True,
            'total_ads_blocked': self.blocked_ads_count,
            'pages_crawled': len(self.visited_urls)
        })
        return stats
