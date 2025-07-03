from datetime import datetime
import uuid
from src.models import db

class InviteLink(db.Model):
    __tablename__ = 'invite_links'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    code = db.Column(db.String(255), unique=True, nullable=False)
    
    # UTM Parameters
    utm_source = db.Column(db.String(255))
    utm_medium = db.Column(db.String(255))
    utm_campaign = db.Column(db.String(255))
    utm_content = db.Column(db.String(255))
    utm_term = db.Column(db.String(255))
    
    # Telegram invite link
    telegram_invite_link = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'telegram_invite_link': self.telegram_invite_link,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

