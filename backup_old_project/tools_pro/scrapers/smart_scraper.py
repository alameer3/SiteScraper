"""
Smart web scraping module with organized structure.
Advanced, real-world scraping with multiple engines and intelligent handling.
"""

import logging
import requests
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement, NavigableString
import random
from datetime import datetime

class SmartScraper:
    """Smart web scraper with advanced features and real extraction."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        # Set default headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_website(self, url: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Advanced website scraping with comprehensive data extraction."""
        try:
            # Default configuration
            default_config = {
                'timeout': 10,
                'max_retries': 3,
                'delay_range': (1, 3),
                'follow_redirects': True,
                'extract_assets': True,
                'extract_links': True,
                'extract_text': True,
                'extract_metadata': True,
                'respect_robots': False  # For analysis purposes
            }
            
            if config:
                default_config.update(config)
            
            # Rotate user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            
            # Add random delay to be respectful
            delay = random.uniform(*default_config['delay_range'])
            time.sleep(delay)
            
            # Make request with retries
            response = self._make_request_with_retries(url, default_config)
            
            if not response:
                return {'error': 'Failed to fetch URL after retries', 'url': url}
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract comprehensive data
            extracted_data = {
                'url': url,
                'final_url': response.url,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat(),
                'page_info': self._extract_page_info(soup, response),
                'content': self._extract_content(soup) if default_config['extract_text'] else {},
                'metadata': self._extract_metadata(soup) if default_config['extract_metadata'] else {},
                'assets': self._extract_assets(soup, url) if default_config['extract_assets'] else {},
                'links': self._extract_links(soup, url) if default_config['extract_links'] else {},
                'technical_info': self._extract_technical_info(response),
                'extraction_stats': self._calculate_extraction_stats(soup, response)
            }
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {e}")
            return {'error': str(e), 'url': url}
    
    def _make_request_with_retries(self, url: str, config: Dict) -> Optional[requests.Response]:
        """Make HTTP request with retry logic."""
        for attempt in range(config['max_retries']):
            try:
                response = self.session.get(
                    url,
                    timeout=config['timeout'],
                    allow_redirects=config['follow_redirects']
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code in [301, 302, 303, 307, 308]:
                    # Handle redirects manually if needed
                    self.logger.info(f"Redirect detected for {url}: {response.status_code}")
                    return response
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
                    if attempt == config['max_retries'] - 1:
                        return response
                        
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < config['max_retries'] - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _extract_page_info(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """Extract basic page information."""
        return {
            'title': self._safe_get_text(soup.find('title')),
            'charset': self._extract_charset(soup),
            'language': self._extract_language(soup),
            'doctype': self._extract_doctype(soup),
            'page_size': len(response.content),
            'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
        }
    
    def _extract_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract main content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        return {
            'headings': {
                'h1': [self._safe_get_text(h) for h in soup.find_all('h1')],
                'h2': [self._safe_get_text(h) for h in soup.find_all('h2')],
                'h3': [self._safe_get_text(h) for h in soup.find_all('h3')]
            },
            'paragraphs': [self._safe_get_text(p) for p in soup.find_all('p')],
            'lists': {
                'ordered': [self._safe_get_text(ol) for ol in soup.find_all('ol')],
                'unordered': [self._safe_get_text(ul) for ul in soup.find_all('ul')]
            },
            'text_content': self._safe_get_text(soup),
            'word_count': len(self._safe_get_text(soup).split()),
            'content_sections': self._identify_content_sections(soup)
        }
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive metadata."""
        metadata = {
            'basic': {},
            'social': {},
            'technical': {}
        }
        
        # Basic metadata
        for meta in soup.find_all('meta'):
            if isinstance(meta, Tag):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    name_str = str(name) if isinstance(name, list) else name
                    content_str = str(content) if isinstance(content, list) else content
                    if name_str and name_str.startswith('og:'):
                        metadata['social'][name_str] = content_str
                    elif name_str in ['description', 'keywords', 'author', 'viewport']:
                        metadata['basic'][name_str] = content_str
                    else:
                        metadata['technical'][name_str] = content_str
        
        # Link metadata
        metadata['links'] = {}
        for link in soup.find_all('link'):
            if isinstance(link, Tag) and link.get('rel') and link.get('href'):
                rel_val = link.get('rel')
                href_val = link.get('href')
                type_val = link.get('type')
                key = f"link_{len(metadata['links'])}"
                metadata['links'][key] = {
                    'rel': str(rel_val) if isinstance(rel_val, list) else rel_val,
                    'href': str(href_val) if isinstance(href_val, list) else href_val,
                    'type': str(type_val) if isinstance(type_val, list) else type_val
                }
        
        return metadata
    
    def _extract_assets(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract and catalog all page assets."""
        assets = {
            'images': [],
            'stylesheets': [],
            'scripts': [],
            'fonts': [],
            'videos': [],
            'audios': []
        }
        
        # Images
        for img in soup.find_all('img'):
            if isinstance(img, Tag):
                src = img.get('src') or img.get('data-src')
                if src:
                    src_str = str(src) if isinstance(src, list) else str(src)
                    alt_val = img.get('alt', '')
                    title_val = img.get('title', '')
                    width_val = img.get('width')
                    height_val = img.get('height')
                    assets['images'].append({
                        'src': urljoin(base_url, src_str),
                        'alt': str(alt_val) if isinstance(alt_val, list) else str(alt_val),
                        'title': str(title_val) if isinstance(title_val, list) else str(title_val),
                        'width': str(width_val) if width_val else None,
                        'height': str(height_val) if height_val else None
                    })
        
        # Stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            if isinstance(link, Tag):
                href = link.get('href')
                if href:
                    href_str = str(href) if isinstance(href, list) else str(href)
                    media_val = link.get('media', 'all')
                    type_val = link.get('type', 'text/css')
                    assets['stylesheets'].append({
                        'href': urljoin(base_url, href_str),
                        'media': str(media_val) if isinstance(media_val, list) else str(media_val),
                        'type': str(type_val) if isinstance(type_val, list) else str(type_val)
                    })
        
        # Scripts
        for script in soup.find_all('script'):
            if isinstance(script, Tag):
                src = script.get('src')
                if src:
                    src_str = str(src) if isinstance(src, list) else str(src)
                    type_val = script.get('type', 'text/javascript')
                    assets['scripts'].append({
                        'src': urljoin(base_url, src_str),
                        'type': str(type_val) if isinstance(type_val, list) else str(type_val),
                        'async': script.has_attr('async') if hasattr(script, 'has_attr') else False,
                        'defer': script.has_attr('defer') if hasattr(script, 'has_attr') else False
                    })
        
        return assets
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract and categorize all links."""
        internal_links = []
        external_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            if isinstance(link, Tag):
                href = link.get('href')
                if href:
                    href_str = str(href) if isinstance(href, list) else str(href)
                    full_url = urljoin(base_url, href_str)
                    link_domain = urlparse(full_url).netloc
                    
                    title_val = link.get('title') or ''
                    rel_val = link.get('rel') or []
                    link_data = {
                        'url': full_url,
                        'text': self._safe_get_text(link),
                        'title': str(title_val) if isinstance(title_val, list) else str(title_val),
                        'rel': rel_val if isinstance(rel_val, list) else [rel_val] if rel_val else []
                    }
            
                    if link_domain == base_domain or not link_domain:
                        internal_links.append(link_data)
                    else:
                        external_links.append(link_data)
        
        return {
            'internal': internal_links,
            'external': external_links,
            'total_count': len(internal_links) + len(external_links),
            'internal_count': len(internal_links),
            'external_count': len(external_links)
        }
    
    def _extract_technical_info(self, response: requests.Response) -> Dict[str, Any]:
        """Extract technical information from response."""
        return {
            'headers': dict(response.headers),
            'cookies': [{'name': c.name, 'value': c.value, 'domain': c.domain} for c in response.cookies],
            'encoding': response.encoding,
            'content_type': response.headers.get('content-type', ''),
            'server': response.headers.get('server', ''),
            'cache_control': response.headers.get('cache-control', '')
        }
    
    def _calculate_extraction_stats(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """Calculate extraction statistics."""
        all_tags = soup.find_all()
        tag_names = []
        for tag in all_tags:
            if isinstance(tag, Tag) and hasattr(tag, 'name'):
                tag_names.append(tag.name)
        
        return {
            'total_elements': len(all_tags),
            'text_elements': len(soup.find_all(text=True)),
            'unique_tags': len(set(tag_names)),
            'response_size': len(response.content),
            'processing_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
        }
    
    def _safe_get_text(self, element) -> str:
        """Safely extract text from BeautifulSoup element."""
        if element and hasattr(element, 'get_text'):
            return element.get_text().strip()
        elif element and hasattr(element, 'string'):
            return str(element.string).strip() if element.string else ''
        return ''
    
    def _extract_charset(self, soup: BeautifulSoup) -> str:
        """Extract page charset."""
        charset_meta = soup.find('meta', charset=True)
        if charset_meta and isinstance(charset_meta, Tag):
            charset_val = charset_meta.get('charset', 'UTF-8')
            return str(charset_val) if charset_val else 'UTF-8'
        
        content_type_meta = soup.find('meta', {'http-equiv': 'Content-Type'})
        if content_type_meta and isinstance(content_type_meta, Tag):
            content = content_type_meta.get('content', '')
            content_str = str(content) if isinstance(content, list) else str(content) if content else ''
            if 'charset=' in content_str:
                return content_str.split('charset=')[1].split(';')[0]
        
        return 'UTF-8'
    
    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Extract page language."""
        html_tag = soup.find('html')
        if html_tag and isinstance(html_tag, Tag):
            lang_val = html_tag.get('lang')
            if lang_val:
                return str(lang_val) if isinstance(lang_val, list) else str(lang_val)
        
        lang_meta = soup.find('meta', {'http-equiv': 'Content-Language'})
        if lang_meta and isinstance(lang_meta, Tag):
            content_val = lang_meta.get('content')
            if content_val:
                return str(content_val) if isinstance(content_val, list) else str(content_val)
        
        return 'unknown'
    
    def _extract_doctype(self, soup: BeautifulSoup) -> str:
        """Extract document type."""
        doctype = soup.contents[0] if soup.contents else None
        if doctype and hasattr(doctype, 'string'):
            string_val = getattr(doctype, 'string', None)
            return str(string_val) if string_val else 'unknown'
        return 'unknown'
    
    def _identify_content_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Identify main content sections."""
        sections = []
        
        # Look for semantic HTML5 elements
        for section in soup.find_all(['section', 'article', 'main', 'aside', 'nav', 'header', 'footer']):
            if isinstance(section, Tag):
                id_val = section.get('id') or ''
                class_val = section.get('class') or []
                sections.append({
                    'tag': section.name if hasattr(section, 'name') else 'unknown',
                    'id': str(id_val) if isinstance(id_val, list) else str(id_val),
                    'class': class_val if isinstance(class_val, list) else [class_val] if class_val else [],
                    'text_length': len(self._safe_get_text(section))
                })
        
        return sections