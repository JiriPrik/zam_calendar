import os, stat
import sqlite3
import shutil
import json
import datetime
import time
import sys
import psutil
from flask import current_app
from app import db
import win32file
import win32con

def backup_database(backup_dir=None):
    """
    Vytvoří zálohu databáze

    Args:
        backup_dir: Adresář pro uložení zálohy

    Returns:
        dict: Informace o záloze (cesta, čas vytvoření)
    """
    # Nastavení absolutní cesty k adresáři backups v KOŘENI projektu (nad app)
    if backup_dir is None:
        project_root = os.path.dirname(current_app.root_path)
        backup_dir = os.path.join(project_root, 'backups')

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
        current_app.logger.info(f"=== ZAČÁTEK ZÁLOHOVÁNÍ ===")
        current_app.logger.info(f"Backup directory: {backup_dir}")
        current_app.logger.info(f"Database URI: {db_uri}")
        current_app.logger.info(f"Resolved database path: {db_path}")
        current_app.logger.info(f"Backup file path: {backup_path}")

        # Uzavření všech spojení s databází
        db.session.close()
        db.engine.dispose()
        current_app.logger.info("Spojení s databází uzavřena a engine dispose proveden.")

        # Kopírování souboru databáze
        try:
            shutil.copy2(db_path, backup_path)
            current_app.logger.info(f"Databáze úspěšně zkopírována do {backup_path}")
        except Exception as copy_error:
            current_app.logger.error(f"Chyba při kopírování databáze: {copy_error}")
            raise

        # Vytvoření metadat o záloze
        try:
            metadata = {
                'timestamp': timestamp,
                'filename': backup_filename,
                'path': backup_path,
                'created_at': datetime.datetime.now().isoformat(),
                'db_size': os.path.getsize(backup_path)
            }
            current_app.logger.info(f"Metadata vytvořena: {metadata}")
        except Exception as meta_error:
            current_app.logger.error(f"Chyba při vytváření metadat: {meta_error}")
            raise

        # Uložení metadat do JSON souboru
        try:
            metadata_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            current_app.logger.info(f"Metadata uložena do {metadata_path}")
        except Exception as json_error:
            current_app.logger.error(f"Chyba při ukládání metadat: {json_error}")
            raise

        current_app.logger.info(f"=== KONEC ZÁLOHOVÁNÍ ===")
        return metadata

    except Exception as e:
        current_app.logger.error(f"Chyba při zálohování databáze: {str(e)}")
        raise

# --- Funkce restore_database odstraněna ---
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

def delete_backup_file(backup_filename, logger, backup_dir='backups'):
    """
    Smaže zálohu

    Args:
        backup_filename: Název souboru zálohy
        logger: Instance loggeru pro logování
        backup_dir: Adresář se zálohami

    Returns:
        bool: True pokud byla záloha úspěšně smazána, jinak False
    """
    logger.info(f"--- Entering delete_backup_file for {backup_filename} ---")
    try:
        # Normalizace cest pro Windows
        backup_dir = os.path.abspath(backup_dir)
        backup_path = os.path.join(backup_dir, backup_filename)
        metadata_path = os.path.join(backup_dir, backup_filename.replace('.db', '.json'))

        logger.info(f"Attempting to delete backup: {backup_filename}")
        logger.info(f"Backup file path: {backup_path}")
        logger.info(f"Metadata file path: {metadata_path}")

        success = True

        # Zavřít všechna spojení s databází
        try:
            db.session.close()
            db.engine.dispose()
            logger.debug("Database connections closed and disposed.")
            time.sleep(1)  # Počkáme 1 sekundu na uvolnění spojení
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

        # Odstraněno problematické hledání a ukončování procesů
        # Spoléháme na time.sleep() po db.engine.dispose()

        # Smazání souboru zálohy
        if os.path.exists(backup_path):
            try:
                if sys.platform == 'win32':
                    # Windows: Zkusit win32file, pak os.remove
                    try:
                        logger.debug(f"Attempting to delete backup file using win32file: {backup_path}")
                        win32file.DeleteFile(backup_path)
                        logger.info(f"Backup file successfully deleted using win32file: {backup_path}")
                    except Exception as e_win:
                        logger.warning(f"win32file delete failed for {backup_path}: {e_win}. Falling back to os.remove.")
                        try:
                            os.remove(backup_path)
                            logger.info(f"Backup file successfully deleted using os.remove: {backup_path}")
                        except Exception as e_os:
                            logger.error(f"os.remove also failed for {backup_path}: {e_os}")
                            success = False
                else:
                    # Ostatní OS: Použít os.remove
                    logger.debug(f"Attempting to delete backup file using os.remove: {backup_path}")
                    os.remove(backup_path)
                    logger.info(f"Backup file successfully deleted using os.remove: {backup_path}")

            except Exception as e:
                logger.error(f"General error during backup file deletion for {backup_path}: {str(e)}")
                success = False
        else:
            logger.warning(f"Backup file does not exist: {backup_path}")

        # Smazání souboru metadat
        if os.path.exists(metadata_path):
            try:
                if sys.platform == 'win32':
                     # Windows: Zkusit win32file, pak os.remove
                    try:
                        logger.debug(f"Attempting to delete metadata file using win32file: {metadata_path}")
                        win32file.DeleteFile(metadata_path)
                        logger.info(f"Metadata file successfully deleted using win32file: {metadata_path}")
                    except Exception as e_win:
                        logger.warning(f"win32file delete failed for {metadata_path}: {e_win}. Falling back to os.remove.")
                        try:
                            os.remove(metadata_path)
                            logger.info(f"Metadata file successfully deleted using os.remove: {metadata_path}")
                        except Exception as e_os:
                            logger.error(f"os.remove also failed for {metadata_path}: {e_os}")
                            success = False
                else:
                    # Ostatní OS: Použít os.remove
                    logger.debug(f"Attempting to delete metadata file using os.remove: {metadata_path}")
                    os.remove(metadata_path)
                    logger.info(f"Metadata file successfully deleted using os.remove: {metadata_path}")

            except Exception as e:
                logger.error(f"General error during metadata file deletion for {metadata_path}: {str(e)}")
                success = False
        else:
            logger.warning(f"Metadata file does not exist: {metadata_path}")

        # Kontrola, zda byly soubory smazány
        logger.debug("Checking if files still exist after deletion attempts.")
        if os.path.exists(backup_path) or os.path.exists(metadata_path):
            logger.warning(f"Deletion failed. Backup file exists: {os.path.exists(backup_path)}, Metadata file exists: {os.path.exists(metadata_path)}")
            return False

        logger.info(f"Backup {backup_filename} successfully deleted.")
        return success

    except Exception as e:
        logger.error(f"Unhandled exception in delete_backup_file for {backup_filename}: {str(e)}", exc_info=True)
        return False
