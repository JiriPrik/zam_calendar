import sqlite3
import os

def fix_db():
    """
    Opraví databázi - vytvoří tabulku app_settings s novými sloupci
    """
    # Cesta k databázi
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
    
    # Připojení k databázi
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Odstranění tabulky app_settings, pokud existuje
    cursor.execute("DROP TABLE IF EXISTS app_settings")
    
    # Vytvoření nové tabulky app_settings
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
    
    # Uložení změn a uzavření spojení
    conn.commit()
    conn.close()
    
    print("Tabulka app_settings byla úspěšně opravena.")

if __name__ == "__main__":
    fix_db()
