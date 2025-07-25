import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
import time
import logging
from collections import defaultdict


class SimpleScraper:
    def __init__(self, base_url, max_depth=2, delay=1.0):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebAnalyzer/1.0; +http://example.com/bot)'
        })
        
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
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            time.sleep(0.5)  # Faster delay
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = []
        try:
            for link in soup.find_all('a', href=True):
                if isinstance(link, Tag):
                    href = link.get('href', '')
                    if href:
                        full_url = urljoin(base_url, str(href))
                        if self.is_valid_url(full_url):
                            links.append({
                                'url': full_url,
                                'text': link.get_text(strip=True)[:100],
                                'title': link.get('title', '')
                            })
        except Exception as e:
            logging.warning(f"Error extracting links: {e}")
        return links
    
    def extract_assets(self, soup, base_url):
        """Extract all assets from the page"""
        assets = {
            'images': [],
            'css': [],
            'javascript': [],
            'fonts': [],
            'other': []
        }
        
        try:
            # Images
            for img in soup.find_all('img'):
                if isinstance(img, Tag):
                    src = img.get('src', '')
                    if src:
                        assets['images'].append({
                            'src': urljoin(base_url, str(src)),
                            'alt': img.get('alt', ''),
                            'title': img.get('title', '')
                        })
            
            # CSS files
            for link in soup.find_all('link', rel='stylesheet'):
                if isinstance(link, Tag):
                    href = link.get('href', '')
                    if href:
                        assets['css'].append({
                            'href': urljoin(base_url, str(href)),
                            'media': link.get('media', 'all')
                        })
            
            # JavaScript files
            for script in soup.find_all('script', src=True):
                if isinstance(script, Tag):
                    src = script.get('src', '')
                    if src:
                        assets['javascript'].append({
                            'src': urljoin(base_url, str(src)),
                            'type': script.get('type', 'text/javascript')
                        })
                        
        except Exception as e:
            logging.warning(f"Error extracting assets: {e}")
            
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
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logging.error(f"Error parsing HTML for {url}: {e}")
            return {}
        
        # Extract page data safely
        page_data = {
            'url': url,
            'title': '',
            'meta_description': '',
            'meta_keywords': '',
            'headers': {},
            'links': [],
            'assets': {},
            'forms': [],
            'depth': depth
        }
        
        try:
            # Title
            title_tag = soup.find('title')
            if title_tag and hasattr(title_tag, 'string') and title_tag.string:
                page_data['title'] = str(title_tag.string).strip()
            
            # Meta tags
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and isinstance(meta_desc, Tag):
                content = meta_desc.get('content')
                if content:
                    page_data['meta_description'] = str(content)
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and isinstance(meta_keywords, Tag):
                content = meta_keywords.get('content')
                if content:
                    page_data['meta_keywords'] = str(content)
            
            # Headers (h1-h6)
            for i in range(1, 7):
                headers = soup.find_all(f'h{i}')
                header_texts = []
                for h in headers:
                    if hasattr(h, 'get_text'):
                        text = h.get_text(strip=True)
                        if text:
                            header_texts.append(text)
                page_data['headers'][f'h{i}'] = header_texts
            
            # Extract links and assets
            page_data['links'] = self.extract_links(soup, url)
            page_data['assets'] = self.extract_assets(soup, url)
            
            # Forms
            for form in soup.find_all('form'):
                if isinstance(form, Tag):
                    form_data = {
                        'action': str(form.get('action', '')),
                        'method': str(form.get('method', 'get')),
                        'inputs': []
                    }
                    
                    for input_tag in form.find_all(['input', 'select', 'textarea']):
                        if isinstance(input_tag, Tag):
                            form_data['inputs'].append({
                                'type': str(input_tag.get('type', '')),
                                'name': str(input_tag.get('name', '')),
                                'id': str(input_tag.get('id', ''))
                            })
                    
                    page_data['forms'].append(form_data)
                    
        except Exception as e:
            logging.error(f"Error extracting page data from {url}: {e}")
        
        # Recursive crawling for internal links
        result = {url: page_data}
        
        if depth < self.max_depth:
            for link_data in page_data['links'][:5]:  # Limit to first 5 links per page
                link_url = link_data['url']
                if link_url not in self.visited_urls:
                    try:
                        child_results = self.crawl_recursive(link_url, depth + 1)
                        result.update(child_results)
                    except Exception as e:
                        logging.warning(f"Error crawling child URL {link_url}: {e}")
        
        return result