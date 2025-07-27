from app import db
from datetime import datetime
import json

class ExtractionResult(db.Model):
    __tablename__ = 'extraction_result'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    extraction_type = db.Column(db.String(50), default='basic')
    status = db.Column(db.String(20), default='completed')
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_data(self):
        """الحصول على البيانات المحفوظة"""
        return json.loads(self.result_data) if self.result_data else {}
    
    def __repr__(self):
        return f'<ExtractionResult {self.url}>'