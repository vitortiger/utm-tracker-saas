from datetime import datetime
import uuid
from src.models import db

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    telegram_id = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    
    # UTM Parameters
    utm_source = db.Column(db.String(255))
    utm_medium = db.Column(db.String(255))
    utm_campaign = db.Column(db.String(255))
    utm_content = db.Column(db.String(255))
    utm_term = db.Column(db.String(255))
    
    # Additional data
    invite_link = db.Column(db.String(255))
    link_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='active')  # active, inactive, banned
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'invite_link': self.invite_link,
            'link_name': self.link_name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

