import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import logging
from collections import Counter

try:
    import builtwith
    BUILTWITH_AVAILABLE = True
except ImportError:
    BUILTWITH_AVAILABLE = False
    logging.warning("builtwith library not available - technology detection will be limited")

class WebsiteAnalyzer:
    def __init__(self):
        self.common_frameworks = {
            'jquery': r'jquery',
            'bootstrap': r'bootstrap',
            'react': r'react',
            'vue': r'vue\.js|vuejs',
            'angular': r'angular',
            'backbone': r'backbone',
            'ember': r'ember',
            'lodash': r'lodash|underscore',
            'moment': r'moment\.js',
            'chart.js': r'chart\.js',
            'd3': r'd3\.js|d3\.min\.js'
        }
        
        self.cms_patterns = {
            'wordpress': [r'wp-content', r'wp-includes', r'wordpress'],
            'drupal': [r'drupal', r'sites/default', r'modules'],
            'joomla': [r'joomla', r'templates', r'components'],
            'magento': [r'magento', r'skin/frontend'],
            'shopify': [r'shopify', r'cdn.shopify.com'],
            'wix': [r'wix.com', r'parastorage'],
            'squarespace': [r'squarespace']
        }
    
    def analyze_technology_stack(self, url, crawl_data):
        """Analyze the technology stack used by the website"""
        tech_info = {
            'frameworks': [],
            'libraries': [],
            'cms': None,
            'server_info': {},
            'meta_generator': '',
            'builtwith_data': {}
        }
        
        # Use builtwith if available
        if BUILTWITH_AVAILABLE:
            try:
                tech_info['builtwith_data'] = builtwith.parse(url)
            except Exception as e:
                logging.error(f"Error using builtwith: {e}")
        
        # Analyze from crawled data
        all_assets = []
        all_html = []
        
        for page_url, page_data in crawl_data.items():
            # Collect all asset URLs
            assets = page_data.get('assets', {})
            for asset_type, asset_list in assets.items():
                if asset_type in ['css', 'javascript']:
                    for asset in asset_list:
                        asset_url = asset.get('src', asset.get('href', ''))
                        all_assets.append(asset_url.lower())
            
            # Get page content for analysis
            try:
                response = requests.get(page_url, timeout=10)
                all_html.append(response.text.lower())
            except Exception as e:
                logging.error(f"Error fetching page for analysis: {e}")
        
        # Detect frameworks and libraries
        combined_content = ' '.join(all_assets + all_html)
        
        for framework, pattern in self.common_frameworks.items():
            if re.search(pattern, combined_content, re.IGNORECASE):
                tech_info['frameworks'].append(framework)
        
        # Detect CMS
        for cms, patterns in self.cms_patterns.items():
            if any(re.search(pattern, combined_content, re.IGNORECASE) for pattern in patterns):
                tech_info['cms'] = cms
                break
        
        # Get server information from headers
        try:
            response = requests.head(url, timeout=10)
            tech_info['server_info'] = {
                'server': response.headers.get('Server', ''),
                'x_powered_by': response.headers.get('X-Powered-By', ''),
                'content_type': response.headers.get('Content-Type', '')
            }
        except Exception as e:
            logging.error(f"Error getting server info: {e}")
        
        return tech_info
    
    def analyze_seo(self, crawl_data):
        """Perform basic SEO analysis"""
        seo_analysis = {
            'title_analysis': {},
            'meta_description_analysis': {},
            'header_structure': {},
            'image_alt_analysis': {},
            'internal_linking': {},
            'page_count': len(crawl_data),
            'issues': []
        }
        
        titles = []
        meta_descriptions = []
        all_headers = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        images_without_alt = 0
        total_images = 0
        internal_links = 0
        
        for page_url, page_data in crawl_data.items():
            title = page_data.get('title', '')
            meta_desc = page_data.get('meta_description', '')
            
            titles.append(title)
            meta_descriptions.append(meta_desc)
            
            # Analyze headers
            headers = page_data.get('headers', {})
            for level, header_list in headers.items():
                all_headers[level].extend(header_list)
            
            # Analyze images
            images = page_data.get('assets', {}).get('images', [])
            total_images += len(images)
            for img in images:
                if not img.get('alt', '').strip():
                    images_without_alt += 1
            
            # Count internal links
            internal_links += len(page_data.get('links', []))
            
            # Check for SEO issues
            if not title:
                seo_analysis['issues'].append(f"Missing title tag: {page_url}")
            elif len(title) > 60:
                seo_analysis['issues'].append(f"Title too long ({len(title)} chars): {page_url}")
            
            if not meta_desc:
                seo_analysis['issues'].append(f"Missing meta description: {page_url}")
            elif len(meta_desc) > 160:
                seo_analysis['issues'].append(f"Meta description too long ({len(meta_desc)} chars): {page_url}")
            
            if not headers.get('h1'):
                seo_analysis['issues'].append(f"Missing H1 tag: {page_url}")
            elif len(headers.get('h1', [])) > 1:
                seo_analysis['issues'].append(f"Multiple H1 tags: {page_url}")
        
        # Compile analysis results
        seo_analysis['title_analysis'] = {
            'average_length': sum(len(t) for t in titles) / len(titles) if titles else 0,
            'unique_titles': len(set(titles)),
            'total_titles': len(titles),
            'duplicate_titles': len(titles) - len(set(titles))
        }
        
        seo_analysis['meta_description_analysis'] = {
            'average_length': sum(len(m) for m in meta_descriptions) / len(meta_descriptions) if meta_descriptions else 0,
            'unique_descriptions': len(set(meta_descriptions)),
            'missing_descriptions': sum(1 for m in meta_descriptions if not m)
        }
        
        seo_analysis['header_structure'] = {
            level: len(header_list) for level, header_list in all_headers.items()
        }
        
        seo_analysis['image_alt_analysis'] = {
            'total_images': total_images,
            'images_without_alt': images_without_alt,
            'alt_coverage': ((total_images - images_without_alt) / total_images * 100) if total_images > 0 else 0
        }
        
        seo_analysis['internal_linking'] = {
            'total_internal_links': internal_links,
            'average_links_per_page': internal_links / len(crawl_data) if crawl_data else 0
        }
        
        return seo_analysis
    
    def analyze_structure(self, crawl_data):
        """Analyze the overall structure of the website"""
        structure_analysis = {
            'page_types': {},
            'navigation_patterns': {},
            'content_patterns': {},
            'url_patterns': {},
            'site_depth': 0
        }
        
        url_patterns = Counter()
        page_types = Counter()
        max_depth = 0
        
        for page_url, page_data in crawl_data.items():
            # Analyze URL patterns
            parsed_url = urlparse(page_url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            
            if len(path_parts) > 0:
                url_patterns[path_parts[0]] += 1
            
            # Determine page type based on URL and content
            page_type = self.classify_page_type(page_url, page_data)
            page_types[page_type] += 1
            
            # Track depth
            depth = page_data.get('depth', 0)
            max_depth = max(max_depth, depth)
        
        structure_analysis['url_patterns'] = dict(url_patterns.most_common(10))
        structure_analysis['page_types'] = dict(page_types)
        structure_analysis['site_depth'] = max_depth
        
        return structure_analysis
    
    def classify_page_type(self, url, page_data):
        """Classify the type of page based on URL and content"""
        url_lower = url.lower()
        title = page_data.get('title', '').lower()
        
        # Common page type patterns
        if any(keyword in url_lower for keyword in ['about', 'about-us']):
            return 'about'
        elif any(keyword in url_lower for keyword in ['contact', 'contact-us']):
            return 'contact'
        elif any(keyword in url_lower for keyword in ['blog', 'news', 'article']):
            return 'blog'
        elif any(keyword in url_lower for keyword in ['product', 'shop', 'store']):
            return 'product'
        elif any(keyword in url_lower for keyword in ['service', 'services']):
            return 'service'
        elif url_lower.endswith('/') and url_lower.count('/') <= 3:
            return 'homepage'
        else:
            return 'content'
    
    def generate_navigation_map(self, crawl_data):
        """Generate a navigation map of the website"""
        navigation_map = {
            'pages': [],
            'hierarchy': {},
            'orphaned_pages': [],
            'most_linked_pages': {}
        }
        
        link_counts = Counter()
        page_links = {}
        
        for page_url, page_data in crawl_data.items():
            page_info = {
                'url': page_url,
                'title': page_data.get('title', ''),
                'depth': page_data.get('depth', 0),
                'outbound_links': len(page_data.get('links', [])),
                'forms': len(page_data.get('forms', []))
            }
            navigation_map['pages'].append(page_info)
            
            # Count links to each page
            links = page_data.get('links', [])
            page_links[page_url] = [link['url'] for link in links]
            for link in links:
                link_counts[link['url']] += 1
        
        # Find most linked pages
        navigation_map['most_linked_pages'] = dict(link_counts.most_common(10))
        
        # Find orphaned pages (pages with no incoming links)
        all_urls = set(crawl_data.keys())
        linked_urls = set(link_counts.keys())
        navigation_map['orphaned_pages'] = list(all_urls - linked_urls)
        
        return navigation_map
