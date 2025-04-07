from app import db, create_app
from app.models import User, Role, LeaveType, Holiday
from datetime import datetime, date
import os

def init_db():
    """Inicializuje databázi s výchozími daty"""
    app = create_app()
    with app.app_context():
        # Vytvoření tabulek
        db.create_all()

        # Kontrola, zda již existují role
        if Role.query.count() == 0:
            print("Vytvářím role...")
            admin_role = Role(name='Admin')
            manager_role = Role(name='Manager')
            employee_role = Role(name='Employee')

            db.session.add_all([admin_role, manager_role, employee_role])
            db.session.commit()

        # Kontrola, zda již existují uživatelé
        if User.query.count() == 0:
            print("Vytvářím uživatele...")
            admin_role = Role.query.filter_by(name='Admin').first()
            manager_role = Role.query.filter_by(name='Manager').first()
            employee_role = Role.query.filter_by(name='Employee').first()

            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='Systému',
                role=admin_role
            )
            admin.set_password('admin')

            manager = User(
                username='manager',
                email='manager@example.com',
                first_name='Manažer',
                last_name='Týmu',
                role=manager_role
            )
            manager.set_password('manager')

            employee = User(
                username='employee',
                email='employee@example.com',
                first_name='Zaměstnanec',
                last_name='Běžný',
                role=employee_role,
                manager=manager
            )
            employee.set_password('employee')

            db.session.add_all([admin, manager, employee])
            db.session.commit()

        # Kontrola, zda již existují typy volna
        if LeaveType.query.count() == 0:
            print("Vytvářím typy volna...")
            vacation = LeaveType(
                name='Dovolená',
                description='Řádná dovolená',
                color_code='#4CAF50',
                auto_approve=False
            )

            sick_leave = LeaveType(
                name='Nemoc',
                description='Nemocenská',
                color_code='#F44336',
                auto_approve=True
            )

            comp_time = LeaveType(
                name='Náhradní volno',
                description='Náhradní volno za přesčasy',
                color_code='#2196F3',
                auto_approve=False
            )

            personal_day = LeaveType(
                name='Sick day',
                description='Osobní volno',
                color_code='#FF9800',
                auto_approve=True
            )

            db.session.add_all([vacation, sick_leave, comp_time, personal_day])
            db.session.commit()

        # Kontrola, zda již existují svátky
        if Holiday.query.count() == 0:
            print("Vytvářím svátky...")
            holidays = [
                Holiday(name='Nový rok', date=date(2025, 1, 1)),
                Holiday(name='Velký pátek', date=date(2025, 4, 18)),
                Holiday(name='Velikonoční pondělí', date=date(2025, 4, 21)),
                Holiday(name='Svátek práce', date=date(2025, 5, 1)),
                Holiday(name='Den vítězství', date=date(2025, 5, 8)),
                Holiday(name='Den slovanských věrozvěstů Cyrila a Metoděje', date=date(2025, 7, 5)),
                Holiday(name='Den upálení mistra Jana Husa', date=date(2025, 7, 6)),
                Holiday(name='Den české státnosti', date=date(2025, 9, 28)),
                Holiday(name='Den vzniku samostatného československého státu', date=date(2025, 10, 28)),
                Holiday(name='Den boje za svobodu a demokracii', date=date(2025, 11, 17)),
                Holiday(name='Štědrý den', date=date(2025, 12, 24)),
                Holiday(name='1. svátek vánoční', date=date(2025, 12, 25)),
                Holiday(name='2. svátek vánoční', date=date(2025, 12, 26))
            ]

            db.session.add_all(holidays)
            db.session.commit()

        print("Inicializace databáze byla dokončena.")

if __name__ == "__main__":
    init_db()
