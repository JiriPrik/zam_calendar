from app import create_app, db
from app.models import User, Role, LeaveType, Holiday
from werkzeug.security import generate_password_hash
from datetime import date

def init_db():
    """Inicializuje databázi základními daty"""
    app = create_app()

    with app.app_context():
        # Vytvoření tabulek
        db.create_all()

        # Kontrola, zda již existují role
        if Role.query.count() == 0:
            # Vytvoření rolí
            roles = [
                Role(name='Admin'),
                Role(name='Manager'),
                Role(name='Employee')
            ]
            db.session.add_all(roles)
            db.session.commit()
            print("Role byly vytvořeny.")

        # Kontrola, zda již existují typy volna
        if LeaveType.query.count() == 0:
            # Vytvoření typů volna
            leave_types = [
                LeaveType(name='Dovolená', description='Řádná dovolená', color_code='#4CAF50', auto_approve=False),
                LeaveType(name='Nemoc', description='Nemocenská', color_code='#F44336', auto_approve=True, max_days=3),
                LeaveType(name='Náhradní volno', description='Náhradní volno za přesčasy', color_code='#2196F3', auto_approve=True, max_days=1),
                LeaveType(name='Sick day', description='Krátkodobé volno při nevolnosti', color_code='#FF9800', auto_approve=True, max_days=1)
            ]
            db.session.add_all(leave_types)
            db.session.commit()
            print("Typy volna byly vytvořeny.")

        # Kontrola, zda již existuje admin uživatel
        if User.query.filter_by(username='admin').first() is None:
            # Vytvoření admin uživatele
            admin_role = Role.query.filter_by(name='Admin').first()
            admin_user = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='Systému',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')  # Výchozí heslo, které by mělo být změněno

            db.session.add(admin_user)
            db.session.commit()
            print("Admin uživatel byl vytvořen.")

        # Kontrola, zda již existují svátky
        if Holiday.query.count() == 0:
            # Vytvoření základních českých státních svátků
            holidays = [
                Holiday(name='Nový rok', date=date(2023, 1, 1), description='Den obnovy samostatného českého státu', is_recurring=True),
                Holiday(name='Velký pátek', date=date(2023, 4, 7), description='Velký pátek', is_recurring=True),
                Holiday(name='Velikonoční pondělí', date=date(2023, 4, 10), description='Velikonoční pondělí', is_recurring=True),
                Holiday(name='Svátek práce', date=date(2023, 5, 1), description='Svátek práce', is_recurring=True),
                Holiday(name='Den vítězství', date=date(2023, 5, 8), description='Den vítězství', is_recurring=True),
                Holiday(name='Den slovanských věrozvěstů', date=date(2023, 7, 5), description='Den slovanských věrozvěstů Cyrila a Metoděje', is_recurring=True),
                Holiday(name='Den upálení mistra Jana Husa', date=date(2023, 7, 6), description='Den upálení mistra Jana Husa', is_recurring=True),
                Holiday(name='Den české státnosti', date=date(2023, 9, 28), description='Den české státnosti', is_recurring=True),
                Holiday(name='Den vzniku Československa', date=date(2023, 10, 28), description='Den vzniku samostatného československého státu', is_recurring=True),
                Holiday(name='Den boje za svobodu a demokracii', date=date(2023, 11, 17), description='Den boje za svobodu a demokracii', is_recurring=True),
                Holiday(name='Štědrý den', date=date(2023, 12, 24), description='Štědrý den', is_recurring=True),
                Holiday(name='1. svátek vánoční', date=date(2023, 12, 25), description='1. svátek vánoční', is_recurring=True),
                Holiday(name='2. svátek vánoční', date=date(2023, 12, 26), description='2. svátek vánoční', is_recurring=True)
            ]
            db.session.add_all(holidays)
            db.session.commit()
            print("Svátky byly vytvořeny.")

        print("Inicializace databáze byla dokončena.")

if __name__ == '__main__':
    init_db()
