from app import db
from datetime import datetime

class ExtractionResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    extraction_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<ExtractionResult {self.url}>'