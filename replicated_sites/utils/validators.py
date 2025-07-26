"""
Input validation and data validation utilities.
"""

import re
import os
from urllib.parse import urlparse
from typing import Dict, List, Any, Tuple, Optional

class URLValidator:
    """Advanced URL validation and processing."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL format."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash
        if url.endswith('/') and len(url) > 8:
            url = url[:-1]
        
        return url
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    @staticmethod
    def is_internal_url(url: str, base_domain: str) -> bool:
        """Check if URL is internal to the base domain."""
        try:
            url_domain = URLValidator.extract_domain(url)
            return url_domain == base_domain or url_domain.endswith('.' + base_domain)
        except:
            return False

class DataValidator:
    """Data validation and sanitization."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove invalid characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:250] + ext
        
        return sanitized
    
    @staticmethod
    def validate_extraction_mode(mode: str) -> bool:
        """Validate extraction mode."""
        valid_modes = ['basic', 'standard', 'advanced', 'ultra', 'secure']
        return mode.lower() in valid_modes
    
    @staticmethod
    def validate_export_format(format_type: str) -> bool:
        """Validate export format."""
        valid_formats = ['json', 'csv', 'xml', 'html', 'pdf']
        return format_type.lower() in valid_formats
    
    @staticmethod
    def clean_text_content(text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove control characters
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        return cleaned