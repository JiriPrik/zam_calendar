# Vývoj aplikace pro registraci dovolených - Část 2

## Implementace autentizace a autorizace
1. Přihlášení a odhlášení uživatelů:
   - Vytvoření formuláře pro přihlášení
   - Implementace rout pro přihlášení a odhlášení
   - Použití Flask-Login pro správu session

2. Registrace nových uživatelů:
   - Vytvoření formuláře pro registraci
   - Implementace routy pro registraci
   - Omezení registrace pouze pro adminy

3. Změna hesla:
   - Vytvoření formuláře pro změnu hesla
   - Implementace routy pro změnu hesla

## Implementace správy volna
1. Vytvoření žádosti o volno:
   - Vytvoření formuláře pro žádost o volno
   - Implementace routy pro vytvoření žádosti
   - Validace dat (datum začátku a konce)

2. Schvalování/zamítání žádostí:
   - Vytvoření formuláře pro schválení/zamítnutí žádosti
   - Implementace routy pro schválení/zamítnutí
   - Omezení schvalování pouze pro manažery

3. Přehled žádostí o volno:
   - Implementace routy pro zobrazení vlastních žádostí
   - Implementace routy pro zobrazení žádostí ke schválení (pro manažery)

4. Kalendářní zobrazení volna:
   - Implementace routy pro zobrazení kalendáře
   - Použití FullCalendar.js pro zobrazení kalendáře
   - Barevné odlišení typů volna a stavů žádostí

## Řešení problému s ambiguitou ve vztazích mezi tabulkami
1. Problém:
   ```
   sqlalchemy.exc.AmbiguousForeignKeysError: Can't determine join between 'leave_request' and 'user'; tables have more than one foreign key constraint relationship between them. Please specify the 'onclause' of this join explicitly.
   ```

2. Příčina:
   - Model `LeaveRequest` má dva cizí klíče na tabulku `user`:
     - `user_id` - odkazuje na zaměstnance, který žádá o volno
     - `manager_id` - odkazuje na manažera, který schvaluje žádost
   - Při použití `join(User)` bez specifikace, který z těchto dvou cizích klíčů má být použit pro spojení, SQLAlchemy neví, který vztah použít

3. Řešení:
   - Explicitní určení podmínky spojení v každém dotazu:
   ```python
   # Místo:
   leave_requests = LeaveRequest.query.join(User).filter(...)
   
   # Použít:
   leave_requests = LeaveRequest.query.join(User, LeaveRequest.user_id == User.id).filter(...)
   ```

4. Upravené soubory:
   - `app/routes/main.py` - metody `index()` a `calendar()`
   - `app/routes/leave.py` - metoda `pending_approvals()`

## Přidání údajů o dovolené k uživatelům
1. Aktualizace modelu uživatele:
   - Přidání atributů `previous_year_leave` (nečerpaná dovolená z minulého roku) a `current_year_leave` (nárok na dovolenou)
   - Implementace metody `get_remaining_leave()` pro výpočet zbývající dovolené

2. Vytvoření formuláře pro úpravu údajů uživatele:
   - Vytvoření formuláře `EditUserForm`
   - Implementace validace dat

3. Implementace správy uživatelů:
   - Vytvoření rout pro zobrazení seznamu uživatelů a úpravu uživatelů
   - Omezení přístupu - pouze manažeři mohou upravovat údaje svých podřízených
   - Aktualizace profilu uživatele pro zobrazení informací o dovolené

4. Řešení problému s přidáním nových sloupců do existující databáze:
   - Smazání staré databáze a vytvoření nové s aktualizovaným schématem
   - Poznámka o možnosti použití migračního nástroje jako Flask-Migrate pro produkční prostředí
