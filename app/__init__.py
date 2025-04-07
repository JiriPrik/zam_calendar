from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Načtení proměnných prostředí z .env souboru
load_dotenv()

# Inicializace rozšíření
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Konfigurace aplikace
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializace rozšíření s aplikací
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Registrace blueprintů
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.routes.leave import leave as leave_blueprint
    app.register_blueprint(leave_blueprint)

    from app.routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from app.routes.report import report as report_blueprint
    app.register_blueprint(report_blueprint)

    from app.routes.holiday import holiday as holiday_blueprint
    app.register_blueprint(holiday_blueprint)

    from app.routes.leave_type import leave_type as leave_type_blueprint
    app.register_blueprint(leave_type_blueprint)

    from app.routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    from app.routes.settings import settings as settings_blueprint
    app.register_blueprint(settings_blueprint)

    # Vytvoření databáze při prvním spuštění
    with app.app_context():
        db.create_all()

        # Inicializace výchozích widgetů pro dashboard
        try:
            from app.scripts.init_dashboard import init_dashboard_widgets
            init_dashboard_widgets()
        except Exception as e:
            print(f"Chyba při inicializaci dashboardů: {e}")

    return app
