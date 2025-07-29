"""
نماذج قاعدة البيانات - Database Models
"""
import json
from datetime import datetime
from app import db

class AnalysisResult(db.Model):
    """نموذج نتائج التحليل"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, index=True)
    title = db.Column(db.String(200))
    analysis_type = db.Column(db.String(50), default='standard', index=True)
    status = db.Column(db.String(50), default='pending', index=True)
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalysisResult {self.id}: {self.url}>'
    
    def get_data(self):
        """الحصول على البيانات المحللة"""
        if self.result_data:
            try:
                return json.loads(self.result_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_data(self, data):
        """تعيين البيانات المحللة"""
        self.result_data = json.dumps(data, ensure_ascii=False, indent=2)
    
    def to_dict(self):
        """تحويل إلى قاموس"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'analysis_type': self.analysis_type,
            'status': self.status,
            'data': self.get_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }