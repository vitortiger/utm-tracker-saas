from datetime import datetime
import uuid
from src.models import db

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    telegram_bot_id = db.Column(db.String(36), db.ForeignKey('telegram_bots.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def script_code(self):
        """Generate JavaScript tracking script for this campaign"""
        return f'''<script>
document.addEventListener("DOMContentLoaded", function() {{
  const btn = document.getElementById("btn-telegram");
  if (!btn) return;

  const base = "http://localhost:5000/api/webhooks/utm-capture/{self.id}";
  btn.href = base + window.location.search;
}});
</script>'''
    
    @property
    def capture_webhook_url(self):
        return f"http://localhost:5000/api/webhooks/utm-capture/{self.id}"
    
    @property
    def member_webhook_url(self):
        return f"http://localhost:5000/api/webhooks/telegram-member/{self.id}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'telegram_bot_id': self.telegram_bot_id,
            'is_active': self.is_active,
            'script_code': self.script_code,
            'capture_webhook_url': self.capture_webhook_url,
            'member_webhook_url': self.member_webhook_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

