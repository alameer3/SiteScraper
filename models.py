from app import db
from datetime import datetime
import json

class ScrapeResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Analysis results stored as JSON
    structure_data = db.Column(db.Text)  # HTML structure analysis
    assets_data = db.Column(db.Text)     # Images, CSS, JS files
    technology_data = db.Column(db.Text) # Tech stack identification
    seo_data = db.Column(db.Text)        # SEO analysis
    navigation_data = db.Column(db.Text) # Site navigation structure
    error_message = db.Column(db.Text)
    
    def set_structure_data(self, data):
        self.structure_data = json.dumps(data)
    
    def get_structure_data(self):
        return json.loads(self.structure_data) if self.structure_data else {}
    
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
