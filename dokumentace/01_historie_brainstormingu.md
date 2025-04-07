# Historie brainstormingu - Aplikace pro registraci dovolených

## Základní požadavky
- Platforma: Python + Flask s SQLite databází
- Účel: Registrace dovolených a jiného volna zaměstnanců
- Typy volna: dovolená, nemoc, náhradní volno, sick day
- Schvalování: Určený nadřízený bude dovolenou schvalovat

## Implementované funkce

### Základní struktura
- Vytvořeno virtuální prostředí (venv)
- Nainstalované potřebné balíčky (Flask, SQLAlchemy, atd.)
- Adresářová struktura projektu

### Databázový model
- Uživatelé (User) s rolemi (Admin, Manager, Employee)
- Typy volna (LeaveType)
- Žádosti o volno (LeaveRequest) s různými stavy (pending, approved, rejected, cancelled)
- Vztahy mezi uživateli (nadřízený-podřízený)

### Autentizace a autorizace
- Přihlášení a odhlášení uživatelů
- Různá oprávnění podle role uživatele
- Změna hesla

### Správa volna
- Vytvoření žádosti o volno
- Schvalování/zamítání žádostí nadřízeným
- Přehled žádostí o volno
- Kalendářní zobrazení volna

### Správa uživatelů
- Registrace nových uživatelů (pouze admin)
- Úprava údajů uživatelů (pouze nadřízený nebo admin)
- Přidání údajů o dovolené (nečerpaná dovolená z minulého roku, nárok na dovolenou)

### Reporty
- Přehled čerpání dovolené zaměstnanců
- Detailní report o volnu konkrétního zaměstnance
- Grafy čerpání volna podle měsíců a typů

### Validace a kontroly
- Kontrola překrývajících se žádostí o volno
- Zobrazení neschválených volna jinou barvou v kalendáři
- Nezobrazování zamítnutých žádostí v kalendáři
- Kontrola žádostí o volno na víkendy a svátky
- Kontrola půldenního volna pouze pro jeden den
- Mazání zrušených žádostí o volno
- Zálohování a obnovení databáze

## Technické detaily
- Použití Flask-SQLAlchemy pro ORM
- Použití Flask-Login pro autentizaci
- Použití Flask-WTF pro formuláře
- Bootstrap 5 pro frontend
- Jinja2 šablony
- SQLite databáze

## Další možná vylepšení
- Statistiky čerpání dovolené
- Plánování týmových kapacit
- Mobilní verze aplikace
- In-app notifikace
- Připomenutí nevyčerpané dovolené

## Řešené problémy
- Ambiguita ve vztazích mezi tabulkami (řešeno explicitním určením join podmínek)
- Přidání nových sloupců do existující databáze (řešeno přetvořením databáze)
- Validace překrývajících se žádostí o volno
- Zobrazení v kalendáři podle stavu žádosti
