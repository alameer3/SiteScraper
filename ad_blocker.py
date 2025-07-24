"""
Ad Blocker Module for Website Analyzer
Filters out common advertisements and tracking elements for cleaner content analysis
"""

import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

class AdBlocker:
    def __init__(self):
        # Common ad-related selectors
        self.ad_selectors = [
            # Generic ad containers
            '[class*="ad-"]', '[id*="ad-"]', '[class*="ads-"]', '[id*="ads-"]',
            '[class*="advertisement"]', '[id*="advertisement"]',
            '[class*="banner"]', '[id*="banner"]',
            '[class*="sponsor"]', '[id*="sponsor"]',
            '[class*="promo"]', '[id*="promo"]',
            
            # Specific ad networks
            '.google-ad', '.adsense', '.adsbygoogle',
            '.amazon-ad', '.facebook-ad', '.twitter-ad',
            '.outbrain', '.taboola', '.disqus',
            
            # Common ad containers
            '.ad-container', '.ad-wrapper', '.ad-block', '.ad-slot',
            '.advertisement-container', '.banner-container',
            '.sidebar-ads', '.header-ads', '.footer-ads',
            
            # Social media widgets (often promotional)
            '.facebook-widget', '.twitter-widget', '.instagram-widget',
            '.social-share', '.social-follow',
            
            # Newsletter signups (promotional)
            '.newsletter', '.signup-form', '.email-capture',
            '.subscribe-box', '.mailing-list'
        ]
        
        # URL patterns for ad networks and trackers
        self.ad_domains = [
            'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
            'facebook.com/tr', 'google-analytics.com', 'googletagmanager.com',
            'outbrain.com', 'taboola.com', 'amazon-adsystem.com',
            'adsystem.amazon.com', 'media.net', 'criteo.com',
            'adskeeper.com', 'mgid.com', 'revcontent.com',
            'contentad.net', 'smartadserver.com', 'pubmatic.com'
        ]
        
        # Common ad-related attributes
        self.ad_patterns = [
            r'advertisement', r'adsense', r'ad[-_]banner',
            r'ad[-_]container', r'ad[-_]wrapper', r'ad[-_]slot',
            r'sponsored', r'promotion', r'affiliate',
            r'tracking', r'analytics', r'gtm'
        ]
        
        # Content that's likely promotional
        self.promotional_keywords = [
            'sponsored', 'advertisement', 'promoted', 'affiliate',
            'buy now', 'click here', 'limited time', 'special offer',
            'subscribe', 'newsletter', 'mailing list', 'email updates'
        ]
    
    def is_ad_url(self, url):
        """Check if a URL is from an ad network or tracker"""
        try:
            domain = urlparse(url).netloc.lower()
            return any(ad_domain in domain for ad_domain in self.ad_domains)
        except Exception:
            return False
    
    def has_ad_attributes(self, element):
        """Check if an element has ad-related attributes"""
        if not hasattr(element, 'attrs'):
            return False
            
        attrs_text = ' '.join([
            str(element.get('class', [])),
            str(element.get('id', '')),
            str(element.get('data-ad', '')),
            str(element.get('data-google-ad', '')),
            str(element.get('data-amazon-ad', ''))
        ]).lower()
        
        return any(re.search(pattern, attrs_text, re.IGNORECASE) 
                  for pattern in self.ad_patterns)
    
    def is_promotional_content(self, text):
        """Check if text content is promotional"""
        if not text:
            return False
            
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.promotional_keywords)
    
    def remove_ads_from_soup(self, soup):
        """Remove advertisement elements from BeautifulSoup object"""
        removed_count = 0
        
        try:
            # Remove elements matching ad selectors
            for selector in self.ad_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        element.decompose()
                        removed_count += 1
                except Exception as e:
                    logging.debug(f"Error removing selector {selector}: {e}")
            
            # Remove elements with ad-related attributes
            for element in soup.find_all():
                if self.has_ad_attributes(element):
                    element.decompose()
                    removed_count += 1
            
            # Remove script tags from ad networks
            for script in soup.find_all('script', src=True):
                if self.is_ad_url(script.get('src', '')):
                    script.decompose()
                    removed_count += 1
            
            # Remove iframe ads
            for iframe in soup.find_all('iframe', src=True):
                if self.is_ad_url(iframe.get('src', '')):
                    iframe.decompose()
                    removed_count += 1
            
            # Remove elements with promotional content
            for element in soup.find_all(string=True):
                if self.is_promotional_content(element.string):
                    parent = element.parent
                    if parent and parent.name not in ['title', 'h1', 'h2', 'h3']:
                        parent.decompose()
                        removed_count += 1
            
            logging.info(f"Removed {removed_count} advertisement elements")
            
        except Exception as e:
            logging.error(f"Error removing ads: {e}")
        
        return soup, removed_count
    
    def filter_assets(self, assets):
        """Filter out ad-related assets from extracted assets"""
        filtered_assets = {}
        
        for asset_type, asset_list in assets.items():
            filtered_list = []
            
            for asset in asset_list:
                asset_url = asset.get('src', asset.get('href', ''))
                
                # Skip if it's from an ad network
                if not self.is_ad_url(asset_url):
                    # Check if the asset has ad-related attributes
                    if not any(pattern in asset_url.lower() for pattern in self.ad_patterns):
                        filtered_list.append(asset)
            
            filtered_assets[asset_type] = filtered_list
        
        return filtered_assets
    
    def clean_text_content(self, text):
        """Clean text content by removing promotional phrases"""
        if not text:
            return text
            
        # Remove common promotional phrases
        promotional_phrases = [
            r'sponsored by.*?(?=\.|$)',
            r'advertisement.*?(?=\.|$)',
            r'click here.*?(?=\.|$)',
            r'buy now.*?(?=\.|$)',
            r'limited time.*?(?=\.|$)',
            r'special offer.*?(?=\.|$)'
        ]
        
        cleaned_text = text
        for phrase in promotional_phrases:
            cleaned_text = re.sub(phrase, '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def get_blocking_stats(self):
        """Get statistics about what was blocked"""
        return {
            'ad_selectors_count': len(self.ad_selectors),
            'blocked_domains_count': len(self.ad_domains),
            'pattern_rules_count': len(self.ad_patterns)
        }