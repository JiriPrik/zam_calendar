from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.utils.decorators import admin_required
from app.forms import BackupDatabaseForm, RestoreDatabaseForm, DeleteBackupForm
from app.utils.backup import backup_database as create_db_backup, restore_database as restore_db_backup, get_backups
import os
import shutil

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
    form = DeleteBackupForm()

    if form.validate_on_submit():
        backup_filename = form.backup_file.data
        backup_path = os.path.join('backups', backup_filename)
        metadata_path = os.path.join('backups', backup_filename.replace('.db', '.json'))

        try:
            import time
            import subprocess
            import sys

            print(f"Pokus o smazání zálohy: {backup_filename}")
            print(f"Cesta k záloze: {backup_path}")
            print(f"Cesta k metadatům: {metadata_path}")

            # Zkontrolujeme, zda soubory existují
            backup_exists = os.path.exists(backup_path)
            metadata_exists = os.path.exists(metadata_path)

            print(f"Soubor zálohy existuje: {backup_exists}")
            print(f"Soubor metadat existuje: {metadata_exists}")

            # Pokus o smazání souborů pomocí různých metod
            success = True

            # Metoda 1: Standardní os.remove
            if backup_exists:
                try:
                    os.remove(backup_path)
                    print(f"Metoda 1: Soubor zálohy úspěšně smazán pomocí os.remove")
                except Exception as e:
                    print(f"Metoda 1: Chyba při mazání souboru zálohy: {str(e)}")
                    success = False

            if metadata_exists:
                try:
                    os.remove(metadata_path)
                    print(f"Metoda 1: Soubor metadat úspěšně smazán pomocí os.remove")
                except Exception as e:
                    print(f"Metoda 1: Chyba při mazání souboru metadat: {str(e)}")
                    success = False

            # Pokud metoda 1 selhala, zkusíme metodu 2: os.unlink
            if not success:
                if backup_exists and os.path.exists(backup_path):
                    try:
                        os.unlink(backup_path)
                        print(f"Metoda 2: Soubor zálohy úspěšně smazán pomocí os.unlink")
                        success = True
                    except Exception as e:
                        print(f"Metoda 2: Chyba při mazání souboru zálohy: {str(e)}")
                        success = False

                if metadata_exists and os.path.exists(metadata_path):
                    try:
                        os.unlink(metadata_path)
                        print(f"Metoda 2: Soubor metadat úspěšně smazán pomocí os.unlink")
                        success = True
                    except Exception as e:
                        print(f"Metoda 2: Chyba při mazání souboru metadat: {str(e)}")
                        success = False

            # Pokud metoda 2 selhala, zkusíme metodu 3: dávkový soubor
            if not success:
                try:
                    # Vytvoření dávkového souboru pro mazání
                    batch_file = os.path.join('backups', 'delete_backup.bat')
                    with open(batch_file, 'w') as f:
                        f.write('@echo off\n')
                        if backup_exists and os.path.exists(backup_path):
                            f.write(f'del /F /Q "{os.path.abspath(backup_path)}"\n')
                        if metadata_exists and os.path.exists(metadata_path):
                            f.write(f'del /F /Q "{os.path.abspath(metadata_path)}"\n')
                        f.write('del "%~f0"\n')  # Smazat sám sebe

                    # Spustit dávkový soubor
                    subprocess.Popen(batch_file, shell=True)
                    print(f"Metoda 3: Dávkový soubor pro mazání vytvořen a spuštěn")

                    # Počkat chvíli, aby se dávkový soubor stihl spustit
                    time.sleep(1)

                    success = True
                except Exception as e:
                    print(f"Metoda 3: Chyba při vytváření dávkového souboru: {str(e)}")
                    success = False

            # Kontrola, zda byly soubory úspěšně smazány
            if (not backup_exists or not os.path.exists(backup_path)) and \
               (not metadata_exists or not os.path.exists(metadata_path)):
                flash(f'Záloha {backup_filename} byla úspěšně smazána', 'success')
            else:
                flash(f'Záloha {backup_filename} nebyla úplně smazána', 'warning')
        except Exception as e:
            print(f"Chyba při mazání zálohy: {str(e)}")
            flash(f'Chyba při mazání zálohy: {str(e)}', 'danger')

    return redirect(url_for('backup.backup_settings'))
