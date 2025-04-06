# Dokumentace aplikace pro registraci dovolených

Tato složka obsahuje kompletní dokumentaci k aplikaci pro registraci dovolených vyvinuté pomocí Pythonu, Flasku a SQLite.

## Obsah dokumentace

1. [Historie brainstormingu](01_historie_brainstormingu.md) - Základní přehled celého projektu, implementované funkce, technické detaily a řešené problémy.

2. [Nastavení prostředí a základní struktura](02_nastaveni_prostredi.md) - Nastavení virtuálního prostředí, vytvoření adresářové struktury, implementace základních modelů a rout, databázový model.

3. [Správa uživatelů a volna](03_sprava_uzivatelu_a_volna.md) - Implementace autentizace a autorizace, implementace správy volna, řešení problému s ambiguitou ve vztazích mezi tabulkami, přidání údajů o dovolené k uživatelům.

4. [Reporting a pokročilé funkce](04_reporting_a_pokrocile_funkce.md) - Implementace reportingu, kontrola překrývajících se žádostí o volno, úprava zobrazení v kalendáři, výhody implementovaných funkcí.

5. [Shrnutí a budoucí vylepšení](05_shrnuti_a_budouci_vylepseni.md) - Shrnutí celého projektu, klíčové funkce aplikace, technické aspekty, návrhy na budoucí vylepšení.

6. [Odkazy na použité technologie](06_odkazy_na_pouzite_technologie.md) - Seznam všech použitých technologií s odkazy.

## Jak používat aplikaci

### Instalace a spuštění

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

### Výchozí přihlašovací údaje

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
