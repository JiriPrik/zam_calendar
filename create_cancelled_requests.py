from app import db, create_app
from app.models import LeaveRequest, LeaveType, User, LeaveStatus
from datetime import datetime, timedelta

def create_cancelled_requests():
    """
    Vytvoří několik zrušených žádostí o volno pro testování
    """
    app = create_app()
    with app.app_context():
        # Získání uživatele a typu volna
        employee = User.query.filter_by(username='employee').first()
        manager = User.query.filter_by(username='manager').first()
        leave_type = LeaveType.query.filter_by(name='Dovolená').first()

        if not employee or not leave_type:
            print(f"Chybí uživatel nebo typ volna. employee: {employee}, leave_type: {leave_type}")
            return

        # Vytvoření zrušených žádostí
        # 1. Žádost - starší než měsíc
        request1 = LeaveRequest(
            user_id=employee.id,
            manager_id=manager.id,
            leave_type_id=leave_type.id,
            start_date=datetime.now() - timedelta(days=40),
            end_date=datetime.now() - timedelta(days=38),
            status=LeaveStatus.CANCELLED,
            created_at=datetime.now() - timedelta(days=45),
            updated_at=datetime.now() - timedelta(days=40)
        )

        # 2. Žádost - starší než měsíc
        request2 = LeaveRequest(
            user_id=employee.id,
            manager_id=manager.id,
            leave_type_id=leave_type.id,
            start_date=datetime.now() - timedelta(days=35),
            end_date=datetime.now() - timedelta(days=33),
            status=LeaveStatus.CANCELLED,
            created_at=datetime.now() - timedelta(days=40),
            updated_at=datetime.now() - timedelta(days=35)
        )

        # 3. Žádost - novější než měsíc, ale starší než týden
        request3 = LeaveRequest(
            user_id=employee.id,
            manager_id=manager.id,
            leave_type_id=leave_type.id,
            start_date=datetime.now() - timedelta(days=20),
            end_date=datetime.now() - timedelta(days=18),
            status=LeaveStatus.CANCELLED,
            created_at=datetime.now() - timedelta(days=25),
            updated_at=datetime.now() - timedelta(days=20)
        )

        # 4. Žádost - z posledního týdne
        request4 = LeaveRequest(
            user_id=employee.id,
            manager_id=manager.id,
            leave_type_id=leave_type.id,
            start_date=datetime.now() - timedelta(days=5),
            end_date=datetime.now() - timedelta(days=3),
            status=LeaveStatus.CANCELLED,
            created_at=datetime.now() - timedelta(days=10),
            updated_at=datetime.now() - timedelta(days=5)
        )

        db.session.add_all([request1, request2, request3, request4])
        db.session.commit()

        print(f"Vytvořeno {4} zrušených žádostí o volno.")

if __name__ == "__main__":
    create_cancelled_requests()
