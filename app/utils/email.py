import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
from app.models import SmtpSettings

def get_smtp_settings():
    """Získá aktivní nastavení SMTP serveru"""
    return SmtpSettings.query.filter_by(is_enabled=True).first()

def send_email(to, subject, template, **kwargs):
    """
    Odešle email pomocí SMTP serveru

    Args:
        to: Příjemce emailu (string nebo list)
        subject: Předmět emailu
        template: Název šablony pro tělo emailu (bez přípony .html)
        **kwargs: Proměnné pro šablonu

    Returns:
        bool: True pokud byl email úspěšně odeslán, jinak False
    """
    settings = get_smtp_settings()

    if not settings:
        current_app.logger.warning("Nelze odeslat email: Chybí nastavení SMTP serveru")
        return False

    if not settings.is_enabled:
        current_app.logger.info("Odesílání emailů je zakázáno v nastavení")
        return False

    # Kontrola, zda příjemce není example.com (RFC 2606 rezervovaná doména)
    if isinstance(to, str) and '@example.com' in to:
        current_app.logger.warning(f"Nelze odeslat email na rezervovanou doménu example.com: {to}")
        return False
    elif isinstance(to, list):
        # Odstranění všech adres s example.com
        to = [addr for addr in to if '@example.com' not in addr]
        if not to:  # Pokud po filtrování nezbyla žádná adresa
            current_app.logger.warning("Nelze odeslat email: Všechny adresy příjemce jsou na rezervované doméně example.com")
            return False

    # Vytvoření zprávy
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.default_sender

    # Pokud je 'to' string, převedeme ho na list
    recipients = [to] if isinstance(to, str) else to
    msg['To'] = ', '.join(recipients)

    # Vytvoření HTML těla emailu ze šablony
    html = render_template(f'emails/{template}.html', **kwargs)
    msg.attach(MIMEText(html, 'html'))

    try:
        # Připojení k SMTP serveru
        if settings.use_ssl:
            server = smtplib.SMTP_SSL(settings.server, settings.port)
        else:
            server = smtplib.SMTP(settings.server, settings.port)

        if settings.use_tls:
            server.starttls()

        # Přihlášení k SMTP serveru
        server.login(settings.username, settings.password)

        # Odeslání emailu
        server.sendmail(settings.default_sender, recipients, msg.as_string())

        # Ukončení spojení
        server.quit()

        current_app.logger.info(f"Email úspěšně odeslán: {subject} -> {recipients}")
        return True

    except Exception as e:
        current_app.logger.error(f"Chyba při odesílání emailu: {str(e)}")
        return False

def send_new_leave_request_notification(leave_request):
    """Odešle notifikaci o nové žádosti o volno manažerovi"""
    if not leave_request.manager:
        current_app.logger.warning(f"Nelze odeslat notifikaci: Žádost ID {leave_request.id} nemá přiřazeného manažera")
        return False

    # Kontrola, zda email manažera není na doméně example.com
    if '@example.com' in leave_request.manager.email:
        current_app.logger.warning(f"Nelze odeslat notifikaci: Email manažera {leave_request.manager.email} je na rezervované doméně example.com")
        return False

    return send_email(
        to=leave_request.manager.email,
        subject=f"Nová žádost o volno od {leave_request.employee.first_name} {leave_request.employee.last_name}",
        template='new_leave_request',
        leave_request=leave_request,
        employee=leave_request.employee,
        manager=leave_request.manager
    )

def send_leave_request_status_notification(leave_request):
    """Odešle notifikaci o změně stavu žádosti o volno zaměstnanci"""
    # Kontrola, zda email zaměstnance není na doméně example.com
    if '@example.com' in leave_request.employee.email:
        current_app.logger.warning(f"Nelze odeslat notifikaci: Email zaměstnance {leave_request.employee.email} je na rezervované doméně example.com")
        return False

    return send_email(
        to=leave_request.employee.email,
        subject=f"Aktualizace stavu vaší žádosti o volno",
        template='leave_request_status',
        leave_request=leave_request,
        employee=leave_request.employee,
        manager=leave_request.manager
    )
