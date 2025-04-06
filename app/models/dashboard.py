from app import db
from datetime import datetime

class DashboardWidget(db.Model):
    """Model pro widgety dashboardu"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default="fas fa-chart-bar")
    is_enabled = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)  # Pozice widgetu na dashboardu
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DashboardWidget {self.name}>'

class UserDashboardSetting(db.Model):
    """Model pro uživatelská nastavení dashboardu"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    widget_id = db.Column(db.Integer, db.ForeignKey('dashboard_widget.id'), nullable=False)
    is_visible = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)  # Pozice widgetu pro konkrétního uživatele
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vztahy
    user = db.relationship('User', backref=db.backref('dashboard_settings', lazy=True))
    widget = db.relationship('DashboardWidget', backref=db.backref('user_settings', lazy=True))
    
    def __repr__(self):
        return f'<UserDashboardSetting {self.user.username} - {self.widget.name}>'
