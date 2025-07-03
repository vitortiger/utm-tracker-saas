from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(50), default='free')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'plan': self.plan,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'plan': self.plan,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


class TelegramBot(db.Model):
    __tablename__ = 'telegram_bots'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.func.gen_random_uuid()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    bot_token = db.Column(db.String(255), nullable=False)
    bot_username = db.Column(db.String(255))
    chat_id = db.Column(db.String(255), nullable=False)
    chat_name = db.Column(db.String(255))
    chat_type = db.Column(db.String(50), default='channel')  # channel, group, supergroup
    is_private = db.Column(db.Boolean, default=False)
    webhook_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='telegram_bot', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bot_username': self.bot_username,
            'chat_id': self.chat_id,
            'chat_name': self.chat_name,
            'chat_type': self.chat_type,
            'is_private': self.is_private,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<TelegramBot {self.bot_username}>'


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.func.gen_random_uuid()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    telegram_bot_id = db.Column(db.String(36), db.ForeignKey('telegram_bots.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    script_code = db.Column(db.Text)
    capture_webhook_url = db.Column(db.String(500))
    member_webhook_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invite_links = db.relationship('InviteLink', backref='campaign', lazy=True, cascade='all, delete-orphan')
    telegram_leads = db.relationship('TelegramLead', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'telegram_bot_id': self.telegram_bot_id,
            'name': self.name,
            'description': self.description,
            'script_code': self.script_code,
            'capture_webhook_url': self.capture_webhook_url,
            'member_webhook_url': self.member_webhook_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'telegram_bot': self.telegram_bot.to_dict() if self.telegram_bot else None
        }

    def __repr__(self):
        return f'<Campaign {self.name}>'


class InviteLink(db.Model):
    __tablename__ = 'invite_links'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.func.gen_random_uuid()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    utm_source = db.Column(db.String(255))
    utm_medium = db.Column(db.String(255))
    utm_campaign = db.Column(db.String(255))
    utm_content = db.Column(db.String(255))
    utm_term = db.Column(db.String(255))
    invite_link_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    telegram_leads = db.relationship('TelegramLead', backref='invite_link', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'code': self.code,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'invite_link_url': self.invite_link_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<InviteLink {self.code}>'


class TelegramLead(db.Model):
    __tablename__ = 'telegram_leads'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.func.gen_random_uuid()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    invite_link_id = db.Column(db.String(36), db.ForeignKey('invite_links.id'))
    telegram_id = db.Column(db.String(50), nullable=False, index=True)
    username = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    group_name = db.Column(db.String(255))
    entry_date = db.Column(db.DateTime)
    utm_source = db.Column(db.String(255))
    utm_medium = db.Column(db.String(255))
    utm_campaign = db.Column(db.String(255))
    utm_content = db.Column(db.String(255))
    utm_term = db.Column(db.String(255))
    status = db.Column(db.String(50), default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate leads per campaign
    __table_args__ = (db.UniqueConstraint('campaign_id', 'telegram_id', name='unique_campaign_telegram_id'),)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'invite_link_id': self.invite_link_id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'group_name': self.group_name,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<TelegramLead {self.telegram_id}>'

