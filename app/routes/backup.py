from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.utils.decorators import admin_required
from app.forms.settings import BackupDatabaseForm, DeleteBackupForm # Odstraněn RestoreDatabaseForm
from app.utils.backup import backup_database as create_db_backup, get_backups, delete_backup_file # Odstraněn restore_database
import os
import shutil
import logging

# Nastavení logování
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='backup_debug.log',
                    filemode='a')
logger = logging.getLogger(__name__)
# print("--- DEBUG: Loading app/routes/backup.py module ---", flush=True) # Odstraněno

backup = Blueprint('backup', __name__)


@backup.route('/settings/backup', methods=['GET'])
@login_required
@admin_required
def backup_settings():
    """Stránka pro zálohování a obnovení databáze (pouze pro adminy)"""
    backup_form = BackupDatabaseForm()
    delete_form = DeleteBackupForm()

    # Získání seznamu záloh
    backups = get_backups()

    return render_template('settings/backup.html',
                           title='Zálohování a obnovení databáze',
                           backup_form=backup_form,
                           # restore_form=restore_form, # Odstraněno
                           delete_form=delete_form,
                           backups=backups)

@backup.route('/settings/backup/create', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """Vytvoření zálohy databáze (pouze pro adminy)"""
    form = BackupDatabaseForm()

    if form.validate_on_submit():
        try:
            # Vytvoření zálohy
            metadata = create_db_backup()
            flash(f'Záloha databáze byla úspěšně vytvořena: {metadata["filename"]}', 'success')
        except Exception as e:
            flash(f'Chyba při vytváření zálohy databáze: {str(e)}', 'danger')

    return redirect(url_for('backup.backup_settings'))

# --- Funkce restore_backup odstraněna ---
@backup.route('/settings/backup/delete', methods=['POST'])
@login_required
@admin_required # Vráceno zpět
def delete_backup():
    """Smazání zálohy databáze (pouze pro adminy)"""
    form = DeleteBackupForm()
    logger.debug(f"--- Entering delete_backup route for file: {request.form.get('backup_file')} ---")

    # Explicitní kontrola metody a validace
    if request.method == 'POST':
        logger.debug("Request method is POST. Proceeding to validation.")
        if form.validate():
            logger.info("Form validation successful (form.validate() returned True).")
            backup_filename = form.backup_file.data
            logger.info(f"Attempting to delete backup: {backup_filename}")
            try:
                # Použití funkce delete_backup_file pro skutečné smazání
                logger.debug(f"Calling delete_backup_file for: {backup_filename}")
                success = delete_backup_file(backup_filename, logger) # Předáme logger

                logger.info(f"delete_backup_file returned: {success}")
                if success:
                    flash(f'Záloha {backup_filename} byla úspěšně smazána', 'success')
                    logger.info(f"Flash message: Backup {backup_filename} successfully deleted.")
                else:
                    flash(f'Záloha {backup_filename} nebyla úplně smazána', 'warning')
                    logger.warning(f"Flash message: Backup {backup_filename} not completely deleted.")
            except Exception as e:
                logger.error(f"Exception during backup deletion: {str(e)}", exc_info=True)
                flash(f'Chyba při mazání zálohy: {str(e)}', 'danger')
        else:
            # form.validate() selhalo
            logger.warning(f"Form validation failed (form.validate() returned False). Errors: {form.errors}")
            error_message = "Formulář pro smazání zálohy neprošel validací. "
            if 'csrf_token' in form.errors:
                error_message += "Chyba CSRF tokenu. Zkuste obnovit stránku a odeslat formulář znovu."
            else:
                # Přidáme detailnější výpis chyb
                error_details = "; ".join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
                error_message += f"Detaily: {error_details}"
                logger.warning(f"Validation error details: {error_details}")
            flash(error_message, 'danger')
    else:
        # Toto by nemělo nastat pro POST route, ale pro jistotu
        logger.warning(f"Request method was not POST ({request.method}). Redirecting.")


    # Přesměrování je vždy na konci
    return redirect(url_for('backup.backup_settings'))


@backup.route('/settings/backup/delete_all', methods=['POST'])
@login_required
@admin_required
def delete_all_backups():
    """Smazání všech záloh databáze (pouze pro adminy)"""
    logger.info("--- Entering delete_all_backups route ---")
    backup_dir = 'backups'
    deleted_count = 0
    failed_count = 0
    failed_files = []

    try:
        if not os.path.exists(backup_dir):
            flash('Adresář se zálohami neexistuje.', 'warning')
            logger.warning(f"Backup directory '{backup_dir}' does not exist.")
            return redirect(url_for('backup.backup_settings'))

        # Získání všech souborů k smazání (kromě adresáře 'deleted')
        files_to_delete = []
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isfile(item_path) and (item.endswith('.db') or item.endswith('.json')):
                 files_to_delete.append(item)

        logger.info(f"Found {len(files_to_delete)} files to delete: {files_to_delete}")

        if not files_to_delete:
            flash('Nebyly nalezeny žádné zálohy ke smazání.', 'info')
            return redirect(url_for('backup.backup_settings'))

        # Mazání souborů
        for filename in files_to_delete:
            try:
                logger.debug(f"Attempting to delete file: {filename}")
                success = delete_backup_file(filename, logger, backup_dir)
                if success:
                    deleted_count += 1
                    logger.info(f"Successfully deleted: {filename}")
                else:
                    failed_count += 1
                    failed_files.append(filename)
                    logger.warning(f"Failed to delete: {filename}")
            except Exception as e:
                failed_count += 1
                failed_files.append(filename)
                logger.error(f"Exception while deleting {filename}: {str(e)}", exc_info=True)

        # Zobrazení výsledku
        if failed_count == 0:
            flash(f'Všech {deleted_count} záloh bylo úspěšně smazáno.', 'success')
            logger.info(f"Successfully deleted all {deleted_count} backups.")
        else:
            flash(f'Podařilo se smazat {deleted_count} záloh. Nepodařilo se smazat {failed_count} souborů: {", ".join(failed_files)}', 'warning')
            logger.warning(f"Deleted {deleted_count} backups, failed to delete {failed_count}: {failed_files}")

    except Exception as e:
        logger.error(f"Error during delete_all_backups: {str(e)}", exc_info=True)
        flash(f'Při mazání všech záloh došlo k chybě: {str(e)}', 'danger')

    return redirect(url_for('backup.backup_settings'))


@backup.route('/settings/backup/download/<filename>', methods=['GET'])
@login_required
@admin_required
def download_backup(filename):
    """Stažení zálohy databáze (pouze pro adminy)"""
    # Cesta k adresáři backups
    # Zjištění absolutní cesty k adresáři backups
    # Nejprve získáme cestu k adresáři, kde je umístěn soubor __file__ (app/routes)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Pak získáme cestu k adresáři app
    app_dir = os.path.dirname(current_dir)
    # Pak získáme cestu k kořenovému adresáři projektu
    project_root = os.path.dirname(app_dir)
    # A nakonec sestavíme cestu k adresáři backups
    backup_dir = os.path.join(project_root, 'backups')
    backup_path = os.path.join(backup_dir, filename)

    print(f"Aktuální adresář: {current_dir}", flush=True)
    print(f"Adresář app: {app_dir}", flush=True)
    print(f"Kořenový adresář projektu: {project_root}", flush=True)
    print(f"Adresář backups: {backup_dir}", flush=True)
    print(f"Cesta k souboru zálohy: {backup_path}", flush=True)
    print(f"Soubor existuje: {os.path.exists(backup_path)}", flush=True)

    if not os.path.exists(backup_path):
        flash(f'Soubor zálohy {filename} neexistuje', 'danger')
        return redirect(url_for('backup.backup_settings'))

    try:
        print(f"Pokus o odeslání souboru: {backup_path}", flush=True)
        # Použití send_from_directory místo send_file
        # Rozdělíme cestu na adresář a název souboru
        directory = os.path.dirname(backup_path)
        file_name = os.path.basename(backup_path)
        print(f"Adresář: {directory}", flush=True)
        print(f"Název souboru: {file_name}", flush=True)
        response = send_from_directory(directory, file_name, as_attachment=True)
        print(f"Soubor úspěšně odeslán", flush=True)
        return response
    except Exception as e:
        import traceback
        print(f"Chyba při stahování zálohy: {str(e)}", flush=True)
        print(f"Traceback: {traceback.format_exc()}", flush=True)
        flash(f'Chyba při stahování zálohy: {str(e)}', 'danger')
        return redirect(url_for('backup.backup_settings'))

