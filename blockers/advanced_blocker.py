"""
Advanced Blocking System - Fixed Version
Clean implementation with proper BeautifulSoup handling
"""

import re
import json
import time
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urlparse, urljoin
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockingMode:
    """Different blocking modes"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class AdvancedBlocker:
    """Comprehensive advanced blocking system"""
    
    def __init__(self, blocking_mode: str = BlockingMode.STANDARD):
        self.blocking_mode = blocking_mode
        self.stats = self._init_stats()
        self._init_blocking_lists()
        self._init_analysis_patterns()
        
        self.settings = {
            'preserve_main_content': True,
            'aggressive_tracking_removal': True,
            'remove_social_widgets': True,
            'clean_comment_sections': False,
            'preserve_navigation': True,
            'remove_popup_overlays': True,
            'block_cryptocurrency_miners': True,
            'remove_newsletter_popups': True
        }

    def _init_stats(self) -> Dict[str, Any]:
        """Initialize blocking statistics"""
        return {
            'session_start': time.time(),
            'total_elements_scanned': 0,
            'ads_blocked': 0,
            'trackers_blocked': 0,
            'popups_blocked': 0,
            'social_widgets_blocked': 0,
            'scripts_blocked': 0,
            'images_blocked': 0,
            'iframes_blocked': 0,
            'divs_removed': 0,
            'size_reduction_bytes': 0,
            'size_reduction_percentage': 0,
            'detection_accuracy': 0,
            'false_positives': 0,
            'processing_time_ms': 0,
            'blocked_domains': set(),
            'blocked_categories': Counter()
        }

    def _init_blocking_lists(self):
        """Initialize comprehensive blocking lists"""
        self.ad_selectors = [
            '[class*="ad-"]', '[id*="ad-"]', '[class*="ads"]', '[id*="ads"]',
            '[class*="advertisement"]', '[id*="advertisement"]',
            '[class*="banner"]', '[id*="banner"]',
            '[class*="sponsored"]', '[id*="sponsored"]',
            '.google-ads', '.adsense', '.doubleclick',
            '[class*="popup"]', '[id*="popup"]',
            '[class*="overlay"]', '[id*="overlay"]',
            '[class*="modal"]', '[id*="modal"]'
        ]
        
        self.tracking_domains = {
            'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
            'facebook.com', 'connect.facebook.net', 'twitter.com',
            'linkedin.com', 'pinterest.com', 'instagram.com',
            'hotjar.com', 'mouseflow.com', 'crazyegg.com',
            'mixpanel.com', 'segment.com', 'amplitude.com'
        }
        
        self.ad_keywords = {
            'advertisement', 'sponsored', 'promoted', 'ad-container',
            'banner', 'popup', 'overlay', 'modal', 'newsletter',
            'subscribe', 'sign-up', 'marketing', 'promotion'
        }

    def _init_analysis_patterns(self):
        """Initialize analysis patterns"""
        self.tracking_patterns = [
            r'ga\(.*\)', r'gtag\(.*\)', r'fbq\(.*\)',
            r'analytics\.track\(.*\)', r'mixpanel\.track\(.*\)',
            r'dataLayer\.push\(.*\)', r'_gaq\.push\(.*\)'
        ]

    def clean_content(self, html_content: str, base_url: str = "") -> Dict[str, Any]:
        """Clean HTML content from ads and trackers"""
        try:
            start_time = time.time()
            original_size = len(html_content)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            self.stats['total_elements_scanned'] = len(soup.find_all())
            
            # Apply different cleaning levels based on mode
            if self.blocking_mode in [BlockingMode.BASIC, BlockingMode.STANDARD]:
                soup = self._remove_ad_elements(soup)
                soup = self._remove_tracking_scripts(soup)
            
            if self.blocking_mode in [BlockingMode.ADVANCED, BlockingMode.AGGRESSIVE]:
                soup = self._remove_tracking_urls(soup, base_url)
                soup = self._remove_social_widgets(soup)
                soup = self._remove_popups_overlays(soup)
            
            if self.blocking_mode == BlockingMode.AGGRESSIVE:
                soup = self._aggressive_cleaning(soup)
            
            # Calculate statistics
            cleaned_html = str(soup)
            cleaned_size = len(cleaned_html)
            
            self.stats['size_reduction_bytes'] = original_size - cleaned_size
            self.stats['size_reduction_percentage'] = (
                (original_size - cleaned_size) / original_size * 100 
                if original_size > 0 else 0
            )
            self.stats['processing_time_ms'] = (time.time() - start_time) * 1000
            
            return {
                'cleaned_html': cleaned_html,
                'original_size': original_size,
                'cleaned_size': cleaned_size,
                'stats': self.stats,
                'blocking_mode': self.blocking_mode
            }
            
        except Exception as e:
            logger.error(f"Error in content cleaning: {e}")
            return {
                'cleaned_html': html_content,
                'error': str(e),
                'stats': self.stats
            }

    def _remove_ad_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove advertisement elements"""
        removed_count = 0
        
        for selector in self.ad_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_likely_ad(element):
                        element.decompose()
                        removed_count += 1
                        self.stats['ads_blocked'] += 1
            except Exception as e:
                logger.debug(f"Error processing selector {selector}: {e}")
        
        # Remove elements based on text content
        for element in soup.find_all(text=True):
            if isinstance(element, NavigableString):
                text_content = str(element).strip()
                if text_content and self._contains_ad_keywords(text_content):
                    parent = element.parent
                    if parent and isinstance(parent, Tag) and self._is_safe_to_remove(parent):
                        parent.decompose()
                        removed_count += 1
                        self.stats['ads_blocked'] += 1
        
        logger.debug(f"Removed {removed_count} ad elements")
        return soup

    def _remove_tracking_scripts(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove tracking scripts"""
        removed_count = 0
        
        # Remove external scripts
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and isinstance(src, str) and self._is_tracking_domain(src):
                script.decompose()
                removed_count += 1
                self.stats['scripts_blocked'] += 1
                try:
                    parsed_url = urlparse(src)
                    if parsed_url.netloc:
                        self.stats['blocked_domains'].add(parsed_url.netloc)
                except Exception:
                    pass
        
        # Remove inline scripts with tracking code
        for script in soup.find_all('script'):
            if script.string:
                script_content = str(script.string)
                if self._contains_tracking_code(script_content):
                    script.decompose()
                    removed_count += 1
                    self.stats['scripts_blocked'] += 1
        
        logger.debug(f"Removed {removed_count} tracking scripts")
        return soup

    def _remove_tracking_urls(self, soup: BeautifulSoup, base_url: str) -> BeautifulSoup:
        """Clean tracking URLs"""
        cleaned_count = 0
        
        for link in soup.find_all(['a', 'link'], href=True):
            href = link.get('href')
            if href and isinstance(href, str) and self._is_tracking_url(href):
                if isinstance(link, Tag) and self._is_safe_to_remove(link):
                    link.decompose()
                    cleaned_count += 1
                    self.stats['trackers_blocked'] += 1
        
        # Clean tracking images
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and isinstance(src, str):
                if self._is_tracking_domain(src) or self._is_tracking_pixel(img):
                    img.decompose()
                    cleaned_count += 1
                    self.stats['images_blocked'] += 1
        
        logger.debug(f"Cleaned {cleaned_count} tracking URLs")
        return soup

    def _remove_social_widgets(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove social media widgets"""
        social_selectors = [
            '[class*="facebook"]', '[class*="twitter"]', '[class*="linkedin"]',
            '[class*="pinterest"]', '[class*="instagram"]', '[class*="youtube"]',
            '[class*="social"]', '[id*="social"]',
            'iframe[src*="facebook"]', 'iframe[src*="twitter"]'
        ]
        
        removed_count = 0
        for selector in social_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_likely_social_widget(element):
                        element.decompose()
                        removed_count += 1
                        self.stats['social_widgets_blocked'] += 1
            except Exception as e:
                logger.debug(f"Error removing social widget {selector}: {e}")
        
        logger.debug(f"Removed {removed_count} social widgets")
        return soup

    def _remove_popups_overlays(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove popups and overlays"""
        popup_selectors = [
            '[class*="popup"]', '[id*="popup"]',
            '[class*="overlay"]', '[id*="overlay"]',
            '[class*="modal"]', '[id*="modal"]',
            '[class*="lightbox"]', '[id*="lightbox"]'
        ]
        
        removed_count = 0
        for selector in popup_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_likely_popup(element):
                        element.decompose()
                        removed_count += 1
                        self.stats['popups_blocked'] += 1
            except Exception as e:
                logger.debug(f"Error removing popup {selector}: {e}")
        
        logger.debug(f"Removed {removed_count} popups/overlays")
        return soup

    def _aggressive_cleaning(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Aggressive cleaning for maximum ad blocking"""
        # Remove all iframes (many contain ads)
        for iframe in soup.find_all('iframe'):
            iframe.decompose()
            self.stats['iframes_blocked'] += 1
        
        # Remove elements with suspicious dimensions
        for element in soup.find_all(True):
            if isinstance(element, Tag):
                style = element.get('style', '')
                if isinstance(style, str):
                    if any(suspicious in style.lower() for suspicious in 
                           ['width:1px', 'height:1px', 'display:none', 'visibility:hidden']):
                        element.decompose()
        
        return soup

    def _is_likely_ad(self, element: Tag) -> bool:
        """Check if element is likely an advertisement"""
        if not isinstance(element, Tag):
            return False
        
        # Check classes and IDs
        classes = element.get('class', [])
        element_id = element.get('id', '')
        
        if isinstance(classes, list):
            class_text = ' '.join(classes).lower()
        else:
            class_text = str(classes).lower()
        
        if isinstance(element_id, str):
            id_text = element_id.lower()
        else:
            id_text = ''
        
        combined_text = class_text + ' ' + id_text
        
        # Check for ad-related keywords
        for keyword in self.ad_keywords:
            if keyword in combined_text:
                return True
        
        # Check element content
        if element.get_text():
            text_content = element.get_text().lower()
            if any(keyword in text_content for keyword in ['advertisement', 'sponsored', 'ad']):
                return True
        
        return False

    def _is_likely_social_widget(self, element: Tag) -> bool:
        """Check if element is likely a social media widget"""
        if not isinstance(element, Tag):
            return False
        
        social_indicators = [
            'facebook', 'twitter', 'linkedin', 'pinterest',
            'instagram', 'youtube', 'social', 'share'
        ]
        
        element_text = str(element).lower()
        return any(indicator in element_text for indicator in social_indicators)

    def _is_likely_popup(self, element: Tag) -> bool:
        """Check if element is likely a popup"""
        if not isinstance(element, Tag):
            return False
        
        popup_indicators = [
            'popup', 'overlay', 'modal', 'lightbox',
            'newsletter', 'subscribe', 'signup'
        ]
        
        element_text = str(element).lower()
        return any(indicator in element_text for indicator in popup_indicators)

    def _contains_ad_keywords(self, text: str) -> bool:
        """Check if text contains advertisement keywords"""
        if not isinstance(text, str):
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.ad_keywords)

    def _contains_tracking_code(self, script_content: str) -> bool:
        """Check if script contains tracking code"""
        if not isinstance(script_content, str):
            return False
        
        for pattern in self.tracking_patterns:
            if re.search(pattern, script_content):
                return True
        return False

    def _is_tracking_domain(self, url: str) -> bool:
        """Check if URL belongs to a tracking domain"""
        if not isinstance(url, str):
            return False
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            return any(tracking_domain in domain for tracking_domain in self.tracking_domains)
        except Exception:
            return False

    def _is_tracking_url(self, url: str) -> bool:
        """Check if URL is used for tracking"""
        if not isinstance(url, str):
            return False
        
        tracking_params = ['utm_', 'fbclid', 'gclid', '_ga', 'mc_eid']
        return any(param in url for param in tracking_params)

    def _is_tracking_pixel(self, img_element: Tag) -> bool:
        """Check if image is a tracking pixel"""
        if not isinstance(img_element, Tag):
            return False
        
        # Check dimensions
        width = img_element.get('width')
        height = img_element.get('height')
        
        if width == '1' and height == '1':
            return True
        
        # Check style for 1x1 dimensions
        style = img_element.get('style', '')
        if isinstance(style, str):
            if 'width:1px' in style and 'height:1px' in style:
                return True
        
        return False

    def _is_safe_to_remove(self, element: Tag) -> bool:
        """Check if element is safe to remove"""
        if not isinstance(element, Tag):
            return False
        
        # Don't remove essential elements
        essential_tags = ['html', 'head', 'body', 'main', 'article', 'section']
        if element.name in essential_tags:
            return False
        
        # Don't remove navigation elements if setting is enabled
        if self.settings.get('preserve_navigation', True):
            nav_indicators = ['nav', 'navigation', 'menu']
            element_text = str(element).lower()
            if any(indicator in element_text for indicator in nav_indicators):
                return False
        
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed blocking statistics"""
        return {
            'session_duration': time.time() - self.stats['session_start'],
            'elements_scanned': self.stats['total_elements_scanned'],
            'ads_blocked': self.stats['ads_blocked'],
            'trackers_blocked': self.stats['trackers_blocked'],
            'scripts_blocked': self.stats['scripts_blocked'],
            'images_blocked': self.stats['images_blocked'],
            'popups_blocked': self.stats['popups_blocked'],
            'social_widgets_blocked': self.stats['social_widgets_blocked'],
            'blocked_domains': list(self.stats['blocked_domains']),
            'size_reduction_bytes': self.stats['size_reduction_bytes'],
            'size_reduction_percentage': self.stats['size_reduction_percentage'],
            'processing_time_ms': self.stats['processing_time_ms'],
            'blocking_mode': self.blocking_mode
        }

    def export_blocked_domains(self) -> List[str]:
        """Export list of blocked domains"""
        return sorted(list(self.stats['blocked_domains']))

    def reset_statistics(self):
        """Reset blocking statistics"""
        self.stats = self._init_stats()

# Convenience functions
def block_ads_basic(html_content: str) -> str:
    """Quick basic ad blocking"""
    blocker = AdvancedBlocker(BlockingMode.BASIC)
    result = blocker.clean_content(html_content)
    return result.get('cleaned_html', html_content)

def block_ads_advanced(html_content: str, base_url: str = "") -> Dict[str, Any]:
    """Advanced ad blocking with statistics"""
    blocker = AdvancedBlocker(BlockingMode.ADVANCED)
    return blocker.clean_content(html_content, base_url)

def block_ads_aggressive(html_content: str, base_url: str = "") -> Dict[str, Any]:
    """Aggressive ad blocking"""
    blocker = AdvancedBlocker(BlockingMode.AGGRESSIVE)
    return blocker.clean_content(html_content, base_url)

# Main execution for testing
if __name__ == "__main__":
    # Test the blocker
    test_html = """
    <html>
        <head>
            <script src="https://google-analytics.com/analytics.js"></script>
        </head>
        <body>
            <div class="ad-banner">Advertisement</div>
            <div class="content">Main content here</div>
            <div class="popup-overlay">Subscribe to newsletter!</div>
        </body>
    </html>
    """
    
    result = block_ads_advanced(test_html)
    print(f"Original size: {result.get('original_size', 0)} bytes")
    print(f"Cleaned size: {result.get('cleaned_size', 0)} bytes")
    print(f"Ads blocked: {result.get('stats', {}).get('ads_blocked', 0)}")