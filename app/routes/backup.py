from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.utils.decorators import admin_required
from app.forms import BackupDatabaseForm, RestoreDatabaseForm, DeleteBackupForm
from app.utils.backup import backup_database as create_db_backup, restore_database as restore_db_backup, get_backups, delete_backup_file
import os
import shutil
import logging

# Nastavení logování
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='backup_debug.log',
                    filemode='a')
logger = logging.getLogger(__name__)

backup = Blueprint('backup', __name__)


@backup.route('/settings/backup', methods=['GET'])
@login_required
@admin_required
def backup_settings():
    """Stránka pro zálohování a obnovení databáze (pouze pro adminy)"""
    backup_form = BackupDatabaseForm()
    restore_form = RestoreDatabaseForm()
    delete_form = DeleteBackupForm()

    # Získání seznamu záloh
    backups = get_backups()

    return render_template('settings/backup.html',
                           title='Zálohování a obnovení databáze',
                           backup_form=backup_form,
                           restore_form=restore_form,
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

@backup.route('/settings/backup/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup():
    """Obnovení databáze ze zálohy (pouze pro adminy)"""
    form = RestoreDatabaseForm()

    if form.validate_on_submit():
        backup_filename = form.backup_file.data
        backup_path = os.path.join('backups', backup_filename)

        if not os.path.exists(backup_path):
            flash(f'Soubor zálohy {backup_filename} neexistuje', 'danger')
            return redirect(url_for('backup.backup_settings'))

        try:
            # Obnovení databáze ze zálohy
            success = restore_db_backup(backup_path)

            if success:
                flash(f'Databáze byla úspěšně obnovena ze zálohy {backup_filename}', 'success')
            else:
                flash('Nepodařilo se obnovit databázi ze zálohy', 'danger')
        except Exception as e:
            flash(f'Chyba při obnovení databáze: {str(e)}', 'danger')

    return redirect(url_for('backup.backup_settings'))

@backup.route('/settings/backup/delete', methods=['POST'])
@login_required
@admin_required
def delete_backup():
    """Smazání zálohy databáze (pouze pro adminy)"""
    print("=== FUNKCE delete_backup ====", flush=True)
    print(f"Request method: {request.method}", flush=True)
    print(f"Request form: {request.form}", flush=True)

    form = DeleteBackupForm()
    print(f"Form data: {form.data}", flush=True)
    print(f"Form errors: {form.errors}", flush=True)
    print(f"Form validate: {form.validate()}", flush=True)

    if form.validate_on_submit():
        backup_filename = form.backup_file.data

        print(f"Volaní funkce delete_backup_file pro zálohu: {backup_filename}", flush=True)

        # Zkontrolujeme, zda soubory existují
        backup_path = os.path.join('backups', backup_filename)
        metadata_path = os.path.join('backups', backup_filename.replace('.db', '.json'))
        print(f"Cesta k záloze: {backup_path}", flush=True)
        print(f"Cesta k metadatům: {metadata_path}", flush=True)
        print(f"Soubor zálohy existuje: {os.path.exists(backup_path)}", flush=True)
        print(f"Soubor metadat existuje: {os.path.exists(metadata_path)}", flush=True)

        try:
            # Použití funkce delete_backup_file
            print(f"Volaní funkce delete_backup_file pro zálohu: {backup_filename}", flush=True)

            # Vytvoření adresáře deleted, pokud neexistuje
            deleted_dir = os.path.join('backups', 'deleted')
            if not os.path.exists(deleted_dir):
                os.makedirs(deleted_dir)
                print(f"Vytvořen adresář pro smazání zálohy: {deleted_dir}", flush=True)

            # Přímé přesunutí souborů
            try:
                # Přesun souboru zálohy
                if os.path.exists(backup_path):
                    new_path = os.path.join(deleted_dir, backup_filename)
                    print(f"Přesouvám soubor zálohy z {backup_path} do {new_path}", flush=True)
                    print(f"Soubor zálohy existuje: {os.path.exists(backup_path)}", flush=True)
                    print(f"Cílový adresář existuje: {os.path.exists(os.path.dirname(new_path))}", flush=True)
                    print(f"Cílový soubor existuje: {os.path.exists(new_path)}", flush=True)

                    # Pokud cílový soubor existuje, nejprve ho smažeme
                    if os.path.exists(new_path):
                        print(f"Mažu existující cílový soubor: {new_path}", flush=True)
                        os.remove(new_path)

                    os.rename(backup_path, new_path)
                    print(f"Soubor zálohy úspěšně přesunut do: {new_path}", flush=True)

                # Přesun souboru metadat
                if os.path.exists(metadata_path):
                    new_path = os.path.join(deleted_dir, os.path.basename(metadata_path))
                    print(f"Přesouvám soubor metadat z {metadata_path} do {new_path}", flush=True)
                    print(f"Soubor metadat existuje: {os.path.exists(metadata_path)}", flush=True)
                    print(f"Cílový adresář existuje: {os.path.exists(os.path.dirname(new_path))}", flush=True)
                    print(f"Cílový soubor existuje: {os.path.exists(new_path)}", flush=True)

                    # Pokud cílový soubor existuje, nejprve ho smažeme
                    if os.path.exists(new_path):
                        print(f"Mažu existující cílový soubor: {new_path}", flush=True)
                        os.remove(new_path)

                    os.rename(metadata_path, new_path)
                    print(f"Soubor metadat úspěšně přesunut do: {new_path}", flush=True)

                success = True
                print(f"Záloha {backup_filename} byla úspěšně smazána", flush=True)
            except Exception as e:
                print(f"Chyba při přesunu souborů: {str(e)}", flush=True)
                success = False

            print(f"Výsledek mazání zálohy: {success}", flush=True)

            if success:
                flash(f'Záloha {backup_filename} byla úspěšně smazána', 'success')
            else:
                flash(f'Záloha {backup_filename} nebyla úplně smazána', 'warning')
        except Exception as e:
            print(f"Chyba při mazání zálohy: {str(e)}", flush=True)
            import traceback
            print(f"Traceback: {traceback.format_exc()}", flush=True)
            flash(f'Chyba při mazání zálohy: {str(e)}', 'danger')

    return redirect(url_for('backup.backup_settings'))

@backup.route('/settings/backup/download/<filename>', methods=['GET'])
@login_required
@admin_required
def download_backup(filename):
    """Stažení zálohy databáze (pouze pro adminy)"""
    backup_path = os.path.join('backups', filename)

    if not os.path.exists(backup_path):
        flash(f'Soubor zálohy {filename} neexistuje', 'danger')
        return redirect(url_for('backup.backup_settings'))

    try:
        return send_file(backup_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Chyba při stahování zálohy: {str(e)}', 'danger')
        return redirect(url_for('backup.backup_settings'))
