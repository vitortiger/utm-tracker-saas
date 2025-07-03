from datetime import datetime
import uuid
from src.models import db

class TelegramBot(db.Model):
    __tablename__ = 'telegram_bots'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    bot_token = db.Column(db.String(255), nullable=False)
    bot_username = db.Column(db.String(255))
    chat_id = db.Column(db.String(255), nullable=False)
    chat_name = db.Column(db.String(255))
    chat_type = db.Column(db.String(50), default='channel')  # channel, group, supergroup
    is_private = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bot_username': self.bot_username,
            'chat_id': self.chat_id,
            'chat_name': self.chat_name,
            'chat_type': self.chat_type,
            'is_private': self.is_private,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

