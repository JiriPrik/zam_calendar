import sqlite3
import os
from datetime import datetime

def run_migration():
    """
    Přidá nové sloupce do tabulky app_settings pro podporu mazání zrušených žádostí
    """
    # Cesta k databázi
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')
    
    # Připojení k databázi
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kontrola, zda tabulka app_settings existuje
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'")
    if not cursor.fetchone():
        print("Tabulka app_settings neexistuje. Vytvoření nové tabulky...")
        cursor.execute('''
        CREATE TABLE app_settings (
            id INTEGER PRIMARY KEY,
            allow_weekend_leave BOOLEAN DEFAULT 0,
            allow_holiday_leave BOOLEAN DEFAULT 0,
            auto_delete_cancelled BOOLEAN DEFAULT 0,
            delete_cancelled_period VARCHAR(20) DEFAULT 'month',
            last_cancelled_cleanup DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        # Vložení výchozího záznamu
        cursor.execute('''
        INSERT INTO app_settings (allow_weekend_leave, allow_holiday_leave, auto_delete_cancelled, delete_cancelled_period)
        VALUES (0, 0, 0, 'month')
        ''')
        print("Tabulka app_settings byla vytvořena a inicializována.")
    else:
        # Kontrola, zda sloupce již existují
        cursor.execute("PRAGMA table_info(app_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Přidání chybějících sloupců
        if 'auto_delete_cancelled' not in columns:
            print("Přidávám sloupec auto_delete_cancelled...")
            cursor.execute("ALTER TABLE app_settings ADD COLUMN auto_delete_cancelled BOOLEAN DEFAULT 0")
        
        if 'delete_cancelled_period' not in columns:
            print("Přidávám sloupec delete_cancelled_period...")
            cursor.execute("ALTER TABLE app_settings ADD COLUMN delete_cancelled_period VARCHAR(20) DEFAULT 'month'")
        
        if 'last_cancelled_cleanup' not in columns:
            print("Přidávám sloupec last_cancelled_cleanup...")
            cursor.execute("ALTER TABLE app_settings ADD COLUMN last_cancelled_cleanup DATETIME")
        
        print("Migrace tabulky app_settings byla dokončena.")
    
    # Uložení změn a uzavření spojení
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
