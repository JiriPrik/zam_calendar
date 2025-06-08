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

### Základní nasazení s Gunicornem (Linux)

Pro nasazení aplikace na Linuxu v produkčním prostředí se doporučuje použít Gunicorn.

1. Nainstalujte Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Spusťte aplikaci pomocí Gunicornu:
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:5000 run:app
   ```
   - `--workers 4`: Nastaví počet worker procesů na 4. Upravte podle počtu jader vašeho CPU.
   - `--bind 0.0.0.0:5000`: Aplikace bude naslouchat na portu 5000 na všech síťových rozhraních.
   - `run:app`: Specifikuje, že Gunicorn má spustit Flask aplikaci (`app`) definovanou v souboru `run.py`.

### Pokročilé nasazení s Gunicornem, systemd a Nginx

Pro robustnější produkční nasazení na Linuxu je doporučeno Gunicorn spravovat pomocí systemd a předřadit mu Nginx jako reverzní proxy server. Nginx se postará o SSL terminaci, servírování statických souborů a další optimalizace. Komunikace mezi Nginx a Gunicornem může probíhat přes Unix socket (efektivnější na jednom serveru) nebo TCP/IP.

#### 1. Vytvoření souboru `wsgi.py` (volitelné, ale doporučené)

I když Gunicorn může být schopen najít vaši Flask `app` instanci přímo v `run.py` (pokud je tam definována globálně), je čistší praxí vytvořit soubor `wsgi.py` v kořenovém adresáři projektu (vedle `run.py`) s následujícím obsahem:

```python
from app import app

if __name__ == "__main__":
    app.run()
```
*Poznámka: Tento soubor zajišťuje, že Gunicorn má jasný vstupní bod k vaší Flask aplikaci. Pokud používáte aplikační továrnu (např. funkci `create_app()`), upravte `wsgi.py` následovně:*
```python
# from app import create_app
# app = create_app()
```

#### 2. Konfigurace systemd služby pro Gunicorn

Vytvořte konfigurační soubor pro systemd službu, například `/etc/systemd/system/servisnew.service`:

```ini
[Unit]
Description=Gunicorn instance to serve calendar_python
After=network.target

[Service]
User=root  # Nahraďte skutečným uživatelem, pod kterým má aplikace běžet
Group=www-data # Nahraďte skutečnou skupinou
WorkingDirectory=/opt/flask/calendar_python # Nahraďte cestou k vaší aplikaci
Environment="PATH=/opt/flask/calendar_python/venv/bin" # Nahraďte cestou k virtuálnímu prostředí
ExecStart=/opt/flask/calendar_python/venv/bin/gunicorn --workers 3 --bind unix:calendar_python.sock -m 007 wsgi:app
# Pro TCP/IP socket (pokud Nginx běží na jiném stroji nebo preferujete TCP):
# ExecStart=/opt/flask/calendar_python/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
# --log-level=debug # Ponechte pouze pro ladění

[Install]
WantedBy=multi-user.target
```

**Vysvětlivky:**
- `Description`: Popis služby.
- `After=network.target`: Služba se spustí až po dostupnosti sítě.
- `User`, `Group`: Uživatel a skupina, pod kterými Gunicorn poběží. **Důrazně se doporučuje nepoužívat `root` pro produkční aplikace.** Vytvořte specializovaného uživatele.
- `WorkingDirectory`: Absolutní cesta k adresáři vaší aplikace.
- `Environment`: Nastavení cesty k binárkám ve virtuálním prostředí.
- `ExecStart`: Příkaz pro spuštění Gunicornu.
    - `--workers 3`: Počet worker procesů. Upravte podle počtu CPU jader (doporučení: `2 * CPU_cores + 1`).
    - `--bind unix:calendar_python.sock`: Gunicorn bude naslouchat na Unix socketu `calendar_python.sock` vytvořeném v `WorkingDirectory`. Unix sockety jsou obecně rychlejší pro komunikaci na stejném stroji než TCP/IP.
    - `-m 007`: Nastaví umask, aby socket byl zapisovatelný pro Nginx (pokud běží pod jiným uživatelem, ale ve stejné skupině).
    - `wsgi:app`: Gunicorn spustí `app` instanci z `wsgi.py` souboru. Pokud nepoužíváte `wsgi.py` a `app` je globálně v `run.py`, použijte `run:app`.
    - `--log-level=debug`: Zvyšuje úroveň logování, vhodné pro ladění, pro produkci zvažte `info` nebo `warning`.

Po vytvoření souboru spusťte následující příkazy pro povolení a spuštění služby:
```bash
sudo systemctl daemon-reload
sudo systemctl start servisnew.service
sudo systemctl enable servisnew.service # Pro automatické spuštění po restartu
sudo systemctl status servisnew.service # Kontrola stavu
```

#### 3. Konfigurace Nginx jako reverzního proxy

Vytvořte nebo upravte konfigurační soubor Nginx pro vaši doménu, obvykle v `/etc/nginx/sites-available/your_domain`:

```nginx
server {
    listen 80; # Nebo 443 pokud používáte SSL
    server_name service.domain.cz www.service.domain.cz; # Nahraďte vaší doménou

    location /static {
        alias /opt/flask/calendar_python/app/static; # Cesta ke statickým souborům vaší aplikace
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/flask/calendar_python/calendar_python.sock;
        # Pokud Gunicorn naslouchá na TCP/IP (např. port 8000):
        # proxy_pass http://127.0.0.1:8000;
    }

    # Volitelné: Nastavení pro SSL (důrazně doporučeno pro produkci)
    # listen 443 ssl;
    # ssl_certificate /cesta/k/vasemu/certifikatu_fullchain.pem;
    # ssl_certificate_key /cesta/k/vasemu/privatnimu_klici.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf; # Pokud používáte Let's Encrypt
    # ssl_dhparam /cesta/k/dhparam.pem;
}
```

**Vysvětlivky:**
- `listen 80`: Nginx naslouchá na portu 80 (HTTP). Pro HTTPS použijte port 443 a SSL konfiguraci.
- `server_name`: Doménová jména, pro která tato konfigurace platí.
- `location /static`: Optimalizace pro servírování statických souborů přímo Nginxem. Upravte `alias` na správnou cestu k vašim statickým souborům.
- `location /`: Všechny ostatní požadavky jsou přesměrovány na Gunicorn.
    - `include proxy_params`: Standardní sada proxy parametrů.
    - `proxy_pass http://unix:/opt/flask/calendar_python/calendar_python.sock;`: Nginx předává požadavky na Unix socket Gunicornu. Ujistěte se, že cesta k `.sock` souboru odpovídá té v `ExecStart` Gunicorn služby a že Nginx má práva k němu přistupovat.

Po vytvoření/upravení konfiguračního souboru vytvořte symbolický link (pokud je potřeba) a otestujte konfiguraci Nginx a restartujte ho:
```bash
sudo ln -s /etc/nginx/sites-available/your_domain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
Ujistěte se, že název souboru `calendar_python.sock` a cesty (`/opt/flask/calendar_python/`) jsou konzistentní napříč konfiguracemi a odpovídají vaší skutečné struktuře projektu. Nahraďte `servisnew.service` a `your_domain` vašimi skutečnými názvy.

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
