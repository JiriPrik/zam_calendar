from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SubmitField, SelectField
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
