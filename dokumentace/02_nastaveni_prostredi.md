# Vývoj aplikace pro registraci dovolených - Část 1

## Nastavení prostředí
1. Vytvoření virtuálního prostředí:
   ```
   python -m venv venv
   ```

2. Aktivace virtuálního prostředí:
   ```
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   .\venv\Scripts\activate.bat  # Windows CMD
   ```

3. Instalace potřebných balíčků:
   ```
   pip install flask flask-sqlalchemy flask-login flask-wtf email-validator python-dotenv
   ```

## Základní struktura projektu
1. Vytvoření adresářové struktury:
   ```
   mkdir app
   mkdir app\static
   mkdir app\static\css
   mkdir app\templates
   mkdir app\models
   mkdir app\routes
   mkdir app\forms
   mkdir app\utils
   ```

2. Vytvoření konfiguračního souboru `.env`:
   ```
   SECRET_KEY=your-secret-key-here
   FLASK_APP=run.py
   FLASK_ENV=development
   DATABASE_URL=sqlite:///app.db
   ```

3. Vytvoření hlavního souboru aplikace `app/__init__.py`:
   - Inicializace Flask aplikace
   - Konfigurace SQLAlchemy
   - Inicializace Flask-Login
   - Registrace blueprintů

4. Vytvoření modelů:
   - `app/models/user.py` - model uživatele a rolí
   - `app/models/leave.py` - model typů volna a žádostí o volno

5. Vytvoření formulářů:
   - `app/forms/auth.py` - formuláře pro autentizaci
   - `app/forms/leave.py` - formuláře pro žádosti o volno

6. Vytvoření rout:
   - `app/routes/auth.py` - routy pro autentizaci
   - `app/routes/main.py` - hlavní routy aplikace
   - `app/routes/leave.py` - routy pro správu volna

7. Vytvoření šablon:
   - `app/templates/base.html` - základní šablona
   - `app/templates/auth/` - šablony pro autentizaci
   - `app/templates/main/` - hlavní šablony
   - `app/templates/leave/` - šablony pro správu volna

8. Vytvoření CSS stylů:
   - `app/static/css/style.css`

9. Vytvoření inicializačního skriptu pro databázi:
   - `app/utils/init_db.py`

10. Vytvoření hlavního souboru pro spuštění aplikace:
    - `run.py`

## Databázový model
1. Model uživatele (`User`):
   - Základní údaje (jméno, příjmení, email, heslo)
   - Role (Admin, Manager, Employee)
   - Vztah nadřízený-podřízený

2. Model typů volna (`LeaveType`):
   - Název typu volna
   - Popis
   - Barva pro zobrazení v kalendáři

3. Model žádosti o volno (`LeaveRequest`):
   - Uživatel, který žádá o volno
   - Typ volna
   - Datum začátku a konce
   - Důvod
   - Stav žádosti (čeká na schválení, schváleno, zamítnuto, zrušeno)
   - Manažer, který schvaluje žádost
   - Komentář manažera

## Řešené problémy
1. Správná struktura projektu pro Flask aplikaci
2. Nastavení vztahů mezi modely v SQLAlchemy
3. Inicializace databáze základními daty (role, typy volna, admin uživatel)
