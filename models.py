from app import db
from datetime import datetime
import json
import logging

class ScrapeResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __init__(self, url, status='pending', analysis_type='basic', data=None, timestamp=None):
        self.url = url
        self.status = status
        self.analysis_type = analysis_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()

    # Analysis results stored as JSON
    structure_data = db.Column(db.Text)  # HTML structure analysis
    assets_data = db.Column(db.Text)     # Images, CSS, JS files
    technology_data = db.Column(db.Text) # Tech stack identification
    seo_data = db.Column(db.Text)        # SEO analysis
    navigation_data = db.Column(db.Text) # Site navigation structure
    error_message = db.Column(db.Text)

    # Advanced analysis fields
    recreation_guide = db.Column(db.Text)  # Complete recreation guide
    arabic_report = db.Column(db.Text)     # Arabic comprehensive report
    ad_blocking_stats = db.Column(db.Text) # Ad blocking statistics
    
    # Additional fields for enhanced routes
    analysis_type = db.Column(db.String(50), default='basic')  # Type of analysis
    data = db.Column(db.Text)  # Additional data storage
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Analysis timestamp

    def set_structure_data(self, data):
        try:
            self.structure_data = json.dumps(data, ensure_ascii=False) if data else None
        except (TypeError, ValueError) as e:
            logging.error(f"Error serializing structure data: {e}")
            self.structure_data = json.dumps({}, ensure_ascii=False)

    def get_structure_data(self):
        try:
            return json.loads(self.structure_data) if self.structure_data else {}
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Error deserializing structure data: {e}")
            return {}

    def set_assets_data(self, data):
        self.assets_data = json.dumps(data)

    def get_assets_data(self):
        return json.loads(self.assets_data) if self.assets_data else {}

    def set_technology_data(self, data):
        self.technology_data = json.dumps(data)

    def get_technology_data(self):
        return json.loads(self.technology_data) if self.technology_data else {}

    def set_seo_data(self, data):
        self.seo_data = json.dumps(data)

    def get_seo_data(self):
        return json.loads(self.seo_data) if self.seo_data else {}

    def set_navigation_data(self, data):
        self.navigation_data = json.dumps(data)

    def get_navigation_data(self):
        return json.loads(self.navigation_data) if self.navigation_data else {}

    def set_recreation_guide(self, data):
        self.recreation_guide = json.dumps(data)

    def get_recreation_guide(self):
        return json.loads(self.recreation_guide) if self.recreation_guide else {}

    def set_arabic_report(self, data):
        self.arabic_report = json.dumps(data)

    def get_arabic_report(self):
        return json.loads(self.arabic_report) if self.arabic_report else {}

    def set_ad_blocking_stats(self, data):
        self.ad_blocking_stats = json.dumps(data)

    def get_ad_blocking_stats(self):
        return json.loads(self.ad_blocking_stats) if self.ad_blocking_stats else {}