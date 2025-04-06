from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Role uživatelů
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

# Model uživatele
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Údaje o dovolené
    previous_year_leave = db.Column(db.Float, default=0.0)  # Nečerpaná dovolená z minulého roku
    current_year_leave = db.Column(db.Float, default=20.0)  # Nárok na dovolenou v aktuálním roce

    # Vztah nadřízený-podřízený
    subordinates = db.relationship('User',
                                  backref=db.backref('manager', remote_side=[id]),
                                  lazy='dynamic')

    # Vztah k žádostem o volno
    leave_requests = db.relationship('LeaveRequest',
                                    foreign_keys='LeaveRequest.user_id',
                                    backref='employee',
                                    lazy='dynamic')

    # Vztah k žádostem ke schválení
    approvals = db.relationship('LeaveRequest',
                               foreign_keys='LeaveRequest.manager_id',
                               backref='manager',
                               lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_manager(self):
        return self.role.name == 'Manager' or self.role.name == 'Admin'

    def is_admin(self):
        return self.role.name == 'Admin'

    def get_remaining_leave(self):
        """Vypočítá zbývající dovolenou uživatele"""
        # Získání všech schválených žádostí o dovolenou v aktuálním roce
        from app.models import LeaveRequest, LeaveType, LeaveStatus
        from datetime import datetime

        current_year = datetime.now().year
        leave_requests = LeaveRequest.query.join(LeaveType).filter(
            LeaveRequest.user_id == self.id,
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveType.name == 'Dovolená',
            db.extract('year', LeaveRequest.start_date) == current_year
        ).all()

        # Výpočet čerpané dovolené
        used_leave = sum(request.duration_days() for request in leave_requests)

        # Celkový nárok na dovolenou
        total_leave = self.previous_year_leave + self.current_year_leave

        # Zbývající dovolená
        remaining_leave = total_leave - used_leave

        return round(remaining_leave, 1)  # Zaokrouhlení na jedno desetinné místo

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
