"""
Data formatting and presentation utilities.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class DataFormatter:
    """Format data for different presentation needs."""
    
    @staticmethod
    def format_file_size(bytes_size: float) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """Format percentage with specified decimal places."""
        return f"{value:.{decimal_places}f}%"
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Format timestamp for display."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_analysis_score(score: float) -> Dict[str, Any]:
        """Format analysis score with rating and color."""
        if score >= 90:
            return {"score": score, "rating": "Excellent", "color": "success"}
        elif score >= 75:
            return {"score": score, "rating": "Good", "color": "primary"}
        elif score >= 60:
            return {"score": score, "rating": "Fair", "color": "warning"}
        else:
            return {"score": score, "rating": "Poor", "color": "danger"}

class ReportFormatter:
    """Format reports and analysis results."""
    
    @staticmethod
    def format_extraction_summary(data: Dict) -> Dict[str, Any]:
        """Format extraction data for summary display."""
        summary = {
            "basic_info": {
                "url": data.get('url', 'N/A'),
                "mode": data.get('mode', 'N/A'),
                "extraction_time": DataFormatter.format_timestamp(data.get('extraction_time', ''))
            },
            "statistics": {},
            "key_metrics": {}
        }
        
        # Format statistics
        if 'statistics' in data:
            stats = data['statistics']
            summary["statistics"] = {
                "content_size": stats.get('extraction_summary', {}).get('content_size', 0),
                "asset_count": stats.get('extraction_summary', {}).get('asset_count', 0),
                "link_count": stats.get('extraction_summary', {}).get('link_count', 0)
            }
        
        # Format key metrics
        if 'seo' in data:
            summary["key_metrics"]["seo_score"] = DataFormatter.format_analysis_score(
                data['seo'].get('overall_score', 0)
            )
        
        if 'security' in data:
            summary["key_metrics"]["security_score"] = DataFormatter.format_analysis_score(
                data['security'].get('security_score', 0)
            )
        
        return summary