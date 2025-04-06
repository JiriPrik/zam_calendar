from app import db
from datetime import datetime

# Typy volna
class LeaveType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    color_code = db.Column(db.String(7), default="#3498db")  # Barva pro zobrazení v kalendáři
    auto_approve = db.Column(db.Boolean, default=False)  # Automatické schvalování
    max_days = db.Column(db.Integer, default=0)  # Maximální počet dní pro automatické schválení (0 = neomezeno)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Vztah k žádostem o volno
    leave_requests = db.relationship('LeaveRequest', backref='leave_type', lazy=True)

    def __repr__(self):
        return f'<LeaveType {self.name}>'

# Stavy žádosti o volno
class LeaveStatus:
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

# Model žádosti o volno
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_type.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    half_day = db.Column(db.Boolean, default=False)  # Příznak pro půldenní volno
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default=LeaveStatus.PENDING)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    manager_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LeaveRequest {self.id} - {self.status}>'

    def duration_days(self):
        """Vypočítá počet dní volna (včetně víkendů a svátků)"""
        delta = self.end_date - self.start_date
        days = delta.days + 1  # Včetně posledního dne

        if self.half_day:
            days -= 0.5

        return days

    @staticmethod
    def check_overlapping_leave(user_id, start_date, end_date, request_id=None):
        """Kontroluje, zda se žádost o volno nepřekrývá s existujícími žádostmi

        Args:
            user_id: ID uživatele
            start_date: Počáteční datum volna
            end_date: Koncové datum volna
            request_id: ID aktuální žádosti (pro případ úpravy existující žádosti)

        Returns:
            Seznam překrývajících se žádostí nebo prázdný seznam, pokud žádné nejsou
        """
        # Získání všech žádostí o volno pro daného uživatele, které nejsou zrušené nebo zamítnuté
        query = LeaveRequest.query.filter(
            LeaveRequest.user_id == user_id,
            LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
            # Kontrola překrytí: (start1 <= end2) AND (end1 >= start2)
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date
        )

        # Pokud upravujeme existující žádost, vyloučíme ji z kontroly
        if request_id:
            query = query.filter(LeaveRequest.id != request_id)

        return query.all()
