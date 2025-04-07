import os, stat
import sqlite3
import shutil
import json
import datetime
from flask import current_app
from app import db

def backup_database(backup_dir='backups'):
    """
    Vytvoří zálohu databáze

    Args:
        backup_dir: Adresář pro uložení zálohy

    Returns:
        dict: Informace o záloze (cesta, čas vytvoření)
    """
    # Vytvoření adresáře pro zálohy, pokud neexistuje
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Získání cesty k databázi
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']

    # Pokud je cesta relativní (např. 'sqlite:///app.db'), přidáme cestu k adresáři instance
    if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):  # Relativní cesta
        db_path = os.path.join(current_app.instance_path, db_uri.replace('sqlite:///', ''))
    else:  # Absolutní cesta
        db_path = db_uri.replace('sqlite:///', '')

    # Vytvoření názvu souboru zálohy s časovým razítkem
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)

    # Vytvoření zálohy
    try:
        # Uzavření všech spojení s databází
        db.session.close()
        db.engine.dispose()

        # Kopírování souboru databáze
        shutil.copy2(db_path, backup_path)

        # Vytvoření metadat o záloze
        metadata = {
            'timestamp': timestamp,
            'filename': backup_filename,
            'path': backup_path,
            'created_at': datetime.datetime.now().isoformat(),
            'db_size': os.path.getsize(backup_path)
        }

        # Uložení metadat do JSON souboru
        metadata_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        current_app.logger.info(f"Databáze byla úspěšně zálohována do {backup_path}")
        return metadata

    except Exception as e:
        current_app.logger.error(f"Chyba při zálohování databáze: {str(e)}")
        raise

def restore_database(backup_path):
    """
    Obnoví databázi ze zálohy

    Args:
        backup_path: Cesta k souboru zálohy

    Returns:
        bool: True pokud byla obnova úspěšná, jinak False
    """
    try:
        # Získání cesty k databázi
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']

        # Pokud je cesta relativní (např. 'sqlite:///app.db'), přidáme cestu k adresáři instance
        if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):  # Relativní cesta
            db_path = os.path.join(current_app.instance_path, db_uri.replace('sqlite:///', ''))
        else:  # Absolutní cesta
            db_path = db_uri.replace('sqlite:///', '')

        # Kontrola, zda soubor zálohy existuje
        if not os.path.exists(backup_path):
            current_app.logger.error(f"Soubor zálohy {backup_path} neexistuje")
            return False

        # Uzavření všech spojení s databází
        db.session.close()
        db.engine.dispose()

        # Vytvoření zálohy aktuální databáze před obnovením
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = f"pre_restore_{timestamp}.db"
        pre_restore_path = os.path.join('backups', pre_restore_backup)

        # Vytvoření adresáře pro zálohy, pokud neexistuje
        if not os.path.exists('backups'):
            os.makedirs('backups')

        # Kopírování aktuální databáze jako pojistka
        shutil.copy2(db_path, pre_restore_path)

        # Kopírování souboru zálohy do aktuální databáze
        shutil.copy2(backup_path, db_path)

        current_app.logger.info(f"Databáze byla úspěšně obnovena ze zálohy {backup_path}")
        return True

    except Exception as e:
        current_app.logger.error(f"Chyba při obnovení databáze: {str(e)}")
        return False

def get_backups(backup_dir='backups'):
    """
    Získá seznam všech záloh

    Args:
        backup_dir: Adresář se zálohami

    Returns:
        list: Seznam metadat o zálohách
    """
    backups = []

    # Kontrola, zda adresář existuje
    if not os.path.exists(backup_dir):
        return backups

    # Procházení všech JSON souborů s metadaty
    for filename in os.listdir(backup_dir):
        if filename.endswith('.json') and filename.startswith('backup_'):
            try:
                with open(os.path.join(backup_dir, filename), 'r') as f:
                    metadata = json.load(f)

                # Kontrola, zda existuje soubor zálohy
                if os.path.exists(os.path.join(backup_dir, metadata['filename'])):
                    # Přidání informace o velikosti souboru v MB
                    metadata['size_mb'] = round(metadata['db_size'] / (1024 * 1024), 2)

                    # Přidání formátovaného data a času
                    created_at = datetime.datetime.fromisoformat(metadata['created_at'])
                    metadata['created_at_formatted'] = created_at.strftime('%d.%m.%Y %H:%M:%S')

                    backups.append(metadata)
            except Exception as e:
                current_app.logger.error(f"Chyba při načítání metadat zálohy {filename}: {str(e)}")

    # Seřazení záloh podle času vytvoření (nejnovější první)
    backups.sort(key=lambda x: x['created_at'], reverse=True)

    return backups

def delete_backup_file(backup_filename, backup_dir='backups'):
    """
    Smaže zálohu

    Args:
        backup_filename: Název souboru zálohy
        backup_dir: Adresář se zálohami

    Returns:
        bool: True pokud byla záloha úspěšně smazána, jinak False
    """
    print("=== FUNKCE delete_backup_file ====")
    print(f"Budeme mazat zálohu: {backup_filename}")
    print(f"Adresář se zálohami: {backup_dir}")
    try:
        # Cesty k souborům
        backup_path = os.path.join(backup_dir, backup_filename)
        metadata_path = os.path.join(backup_dir, backup_filename.replace('.db', '.json'))

        current_app.logger.info(f"Mazání zálohy: {backup_filename}")
        current_app.logger.info(f"Cesta k záloze: {backup_path}")
        current_app.logger.info(f"Cesta k metadatům: {metadata_path}")

        # Pokus o přesun souborů do adresáře deleted
        success = True

        # Vytvoření adresáře deleted, pokud neexistuje
        deleted_dir = os.path.join(backup_dir, 'deleted')
        if not os.path.exists(deleted_dir):
            os.makedirs(deleted_dir)
            current_app.logger.info(f"Vytvořen adresář pro smazání zálohy: {deleted_dir}")

        # Přesun souboru zálohy
        if os.path.exists(backup_path):
            try:
                # Zavřít všechna spojení s databází
                db.session.close()
                db.engine.dispose()

                # Zkusit přesunout soubor
                new_path = os.path.join(deleted_dir, backup_filename)
                print(f"Přesouvám soubor zálohy z {backup_path} do {new_path}")
                shutil.move(backup_path, new_path)
                current_app.logger.info(f"Soubor zálohy úspěšně přesunut do: {new_path}")
            except Exception as e:
                current_app.logger.error(f"Chyba při přesunu souboru zálohy: {str(e)}")
                success = False
        else:
            current_app.logger.warning(f"Soubor zálohy neexistuje: {backup_path}")

        # Přesun souboru metadat
        if os.path.exists(metadata_path):
            try:
                new_path = os.path.join(deleted_dir, os.path.basename(metadata_path))
                print(f"Přesouvám soubor metadat z {metadata_path} do {new_path}")
                shutil.move(metadata_path, new_path)
                current_app.logger.info(f"Soubor metadat úspěšně přesunut do: {new_path}")
            except Exception as e:
                current_app.logger.error(f"Chyba při přesunu souboru metadat: {str(e)}")
                success = False
        else:
            current_app.logger.warning(f"Soubor metadat neexistuje: {metadata_path}")

        # Kontrola, zda byly soubory přesunuty
        if os.path.exists(backup_path) or os.path.exists(metadata_path):
            current_app.logger.warning(f"Některé soubory nebyly přesunuty: záloha existuje: {os.path.exists(backup_path)}, metadata existují: {os.path.exists(metadata_path)}")
            return False

        current_app.logger.info(f"Záloha {backup_filename} byla úspěšně smazána")
        return success

    except Exception as e:
        current_app.logger.error(f"Chyba při mazání zálohy {backup_filename}: {str(e)}")
        return False
