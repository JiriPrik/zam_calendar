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
            # Přímé smazání souborů bez volání funkce
            if os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"Soubor zálohy smazán: {backup_path}")
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                print(f"Soubor metadat smazán: {metadata_path}")
            
            flash(f'Záloha {backup_filename} byla úspěšně smazána', 'success')
        except Exception as e:
            print(f"Chyba při mazání zálohy: {str(e)}")
            flash(f'Chyba při mazání zálohy: {str(e)}', 'danger')
    
    return redirect(url_for('backup.backup_settings'))
