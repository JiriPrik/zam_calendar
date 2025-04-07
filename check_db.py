from app import db, create_app
from app.models import User, Role, LeaveType, Holiday, LeaveRequest

def check_db():
    """Zkontroluje obsah databáze"""
    app = create_app()
    with app.app_context():
        # Kontrola rolí
        roles = Role.query.all()
        print(f"Počet rolí: {len(roles)}")
        for role in roles:
            print(f"  - {role.name}")
        
        # Kontrola uživatelů
        users = User.query.all()
        print(f"\nPočet uživatelů: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.email}), role: {user.role.name if user.role else 'None'}")
        
        # Kontrola typů volna
        leave_types = LeaveType.query.all()
        print(f"\nPočet typů volna: {len(leave_types)}")
        for leave_type in leave_types:
            print(f"  - {leave_type.name}")
        
        # Kontrola svátků
        holidays = Holiday.query.all()
        print(f"\nPočet svátků: {len(holidays)}")
        
        # Kontrola žádostí o volno
        leave_requests = LeaveRequest.query.all()
        print(f"\nPočet žádostí o volno: {len(leave_requests)}")
        for request in leave_requests:
            print(f"  - {request.employee.username}: {request.start_date.strftime('%d.%m.%Y')} - {request.end_date.strftime('%d.%m.%Y')}, status: {request.status}")

if __name__ == "__main__":
    check_db()
