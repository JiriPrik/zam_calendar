from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import SmtpSettings, AppSettings, LeaveRequest, LeaveStatus
from app.forms import SmtpSettingsForm, AppSettingsForm
from app.utils.decorators import admin_required
from app.utils.email import send_email
from app.utils.cleanup import delete_cancelled_requests

settings = Blueprint('settings', __name__)

@settings.route('/settings/app', methods=['GET', 'POST'])
@login_required
@admin_required
def app_settings():
    """Obecné nastavení aplikace (pouze pro adminy)"""
    # Získání aktuálního nastavení nebo vytvoření nového
    app_settings = AppSettings.query.first()

    if not app_settings:
        app_settings = AppSettings(
            allow_weekend_leave=False,
            allow_holiday_leave=False,
            auto_delete_cancelled=False,
            delete_cancelled_period='month'
        )
        db.session.add(app_settings)
        db.session.commit()

    form = AppSettingsForm(obj=app_settings)

    # Získání statistik o zrušených žádostech
    cancelled_count = LeaveRequest.query.filter_by(status=LeaveStatus.CANCELLED).count()

    # Zpracování formuláře
    if form.validate_on_submit():
        # Kontrola, zda bylo stisknuto tlačítko pro ruční mazání
        if 'manual_delete' in request.form:
            # Mazání zrušených žádostí
            period = form.delete_cancelled_period.data
            deleted_count = delete_cancelled_requests(period)

            if deleted_count > 0:
                flash(f'Bylo smazáno {deleted_count} zrušených žádostí o volno.', 'success')
            else:
                flash('Nebyly nalezeny žádné zrušené žádosti o volno ke smazání.', 'info')

            return redirect(url_for('settings.app_settings'))
        else:
            # Aktualizace nastavení
            form.populate_obj(app_settings)
            db.session.commit()

            flash('Nastavení aplikace bylo úspěšně uloženo.', 'success')
            return redirect(url_for('settings.app_settings'))

    return render_template('settings/app.html', form=form, title='Nastavení aplikace', cancelled_count=cancelled_count)

@settings.route('/settings/smtp', methods=['GET', 'POST'])
@login_required
@admin_required
def smtp_settings():
    """Nastavení SMTP serveru (pouze pro adminy)"""
    # Získání aktuálního nastavení nebo vytvoření nového
    smtp_settings = SmtpSettings.query.first()

    if not smtp_settings:
        smtp_settings = SmtpSettings(
            server='',
            port=587,
            username='',
            password='',
            use_tls=True,
            use_ssl=False,
            default_sender='',
            is_enabled=False
        )
        db.session.add(smtp_settings)
        db.session.commit()

    form = SmtpSettingsForm(obj=smtp_settings)

    if form.validate_on_submit():
        # Aktualizace nastavení
        form.populate_obj(smtp_settings)
        db.session.commit()

        flash('Nastavení SMTP serveru bylo úspěšně uloženo.', 'success')

        # Pokud je odesílání emailů povoleno, zkusíme odeslat testovací email
        if smtp_settings.is_enabled and request.form.get('send_test_email'):
            # Kontrola, zda email uživatele není na doméně example.com
            if '@example.com' in current_user.email:
                flash('Nelze odeslat testovací email na adresu s doménou example.com. Tato doména je rezervována podle RFC 2606 a nelze na ni odesílat emaily. Prosím, upravte svůj email v profilu.', 'warning')
            else:
                success = send_email(
                    to=current_user.email,
                    subject='Testovací email ze Systému pro správu dovolených',
                    template='test_email',
                    user=current_user
                )

                if success:
                    flash('Testovací email byl úspěšně odeslán.', 'success')
                else:
                    flash('Nepodařilo se odeslat testovací email. Zkontrolujte nastavení SMTP serveru.', 'danger')

        return redirect(url_for('settings.smtp_settings'))

    return render_template('settings/smtp.html', form=form, title='Nastavení SMTP serveru')
