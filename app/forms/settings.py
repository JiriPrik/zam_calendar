from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, NumberRange, Optional

class AppSettingsForm(FlaskForm):
    """Formulář pro obecné nastavení aplikace"""
    allow_weekend_leave = BooleanField('Povolit žádosti o volno na víkendy', default=False)
    allow_holiday_leave = BooleanField('Povolit žádosti o volno na svátky', default=False)

    # Nastavení pro mazání zrušených žádostí
    auto_delete_cancelled = BooleanField('Automaticky mazat zrušené žádosti', default=False)
    delete_cancelled_period = SelectField('Období pro mazání', choices=[
        ('month', 'Za poslední měsíc'),
        ('year', 'Za poslední rok'),
        ('all', 'Všechny zrušené žádosti')
    ], default='month')

    # Tlačítko pro ruční mazání
    manual_delete = SubmitField('Smazat zrušené žádosti nyní')

    submit = SubmitField('Uložit nastavení')

class BackupDatabaseForm(FlaskForm):
    """Formulář pro zálohování databáze"""
    submit = SubmitField('Vytvořit zálohu')

class RestoreDatabaseForm(FlaskForm):
    """Formulář pro obnovení databáze ze zálohy"""
    backup_file = HiddenField('Soubor zálohy', validators=[DataRequired()])
    confirm = BooleanField('Potvrzuji, že chci obnovit databázi ze zálohy. Všechna aktuální data budou nahrazena.', validators=[DataRequired()])
    submit = SubmitField('Obnovit databázi')

class DeleteBackupForm(FlaskForm):
    """Formulář pro smazání zálohy"""
    backup_file = HiddenField('Soubor zálohy', validators=[DataRequired()])
    submit = SubmitField('Smazat zálohu')

class SmtpSettingsForm(FlaskForm):
    """Formulář pro nastavení SMTP serveru"""
    server = StringField('SMTP Server', validators=[DataRequired()])
    port = IntegerField('Port', validators=[DataRequired(), NumberRange(min=1, max=65535)], default=587)
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    use_tls = BooleanField('Použít TLS', default=True)
    use_ssl = BooleanField('Použít SSL', default=False)
    default_sender = StringField('Výchozí odesílatel', validators=[DataRequired(), Email()])
    is_enabled = BooleanField('Povolit odesílání emailů', default=True)
    submit = SubmitField('Uložit nastavení')
