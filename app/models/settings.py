from app import db
from datetime import datetime

class AppSettings(db.Model):
    """Model pro obecné nastavení aplikace"""
    id = db.Column(db.Integer, primary_key=True)
    allow_weekend_leave = db.Column(db.Boolean, default=False)
    allow_holiday_leave = db.Column(db.Boolean, default=False)

    # Nastavení pro mazání zrušených žádostí
    auto_delete_cancelled = db.Column(db.Boolean, default=False)
    delete_cancelled_period = db.Column(db.String(20), default='month')  # 'month', 'year', 'all'
    last_cancelled_cleanup = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AppSettings {self.id}>'

class SmtpSettings(db.Model):
    """Model pro nastavení SMTP serveru"""
    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=587)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    use_tls = db.Column(db.Boolean, default=True)
    use_ssl = db.Column(db.Boolean, default=False)
    default_sender = db.Column(db.String(255), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SmtpSettings {self.server}>'
