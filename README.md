# Systém pro správu dovolených

Aplikace pro registraci a správu dovolených a jiného volna zaměstnanců.

## Funkce

- Registrace různých typů volna (dovolená, nemoc, náhradní volno, sick day)
- Schvalování žádostí o volno nadřízeným
- Automatické schvalování určitých typů volna
- Přehledný kalendář volna se zvýrazněním svátků a víkendů
- Nastavení aplikace (povolení/zakázání volna na víkendy a svátky)
- Mazání zrušených žádostí o volno
- Zálohování a obnovení databáze
- Emailové notifikace o nových žádostech a schválení/zamítnutí
- Přizpůsobitelný dashboard pro uživatele
- Tmavý režim a volitelná barevná schémata
- Správa uživatelů a rolí
- Reporting a statistiky
- Pokročilé filtrovaní a řazení v tabulkách

## Technologie

- Python 3.12+
- Flask - webový framework
- SQLite - databáze
- Flask-SQLAlchemy - ORM
- Flask-Login - autentizace
- Flask-WTF - formuláře
- Bootstrap 5 - frontend
- Chart.js - grafy a vizualizace dat
- FullCalendar.js - kalendářní komponenta

## Instalace a spuštění

1. Klonujte repozitář:
   ```
   git clone <url-repozitáře>
   cd calendar_python
   ```

2. Vytvořte a aktivujte virtuální prostředí:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Nainstalujte závislosti:
   ```
   pip install -r requirements.txt
   ```

4. Inicializujte databázi:
   ```
   python -m app.utils.init_db
   ```

5. Spusťte aplikaci:
   ```
   python run.py
   ```

6. Otevřete prohlížeč na adrese `http://localhost:5000`

## Výchozí přihlašovací údaje

- Uživatelské jméno: `admin`
- Heslo: `admin123`

Po prvním přihlášení doporučujeme změnit heslo.

## Struktura projektu

```
calendar_python/
├── app/                    # Hlavní balíček aplikace
│   ├── forms/              # Formuláře
│   ├── models/             # Databázové modely
│   ├── routes/             # Routy a kontrolery
│   ├── static/             # Statické soubory (CSS, JS)
│   ├── templates/          # HTML šablony
│   ├── utils/              # Pomocné utility
│   └── __init__.py         # Inicializace aplikace
├── venv/                   # Virtuální prostředí
├── .env                    # Konfigurační proměnné
├── app.db                  # SQLite databáze
├── requirements.txt        # Seznam závislostí
├── run.py                  # Spouštěcí skript
└── README.md               # Dokumentace
```
