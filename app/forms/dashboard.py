from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class DashboardWidgetForm(FlaskForm):
    """Formulář pro správu widgetů dashboardu"""
    name = StringField('Název', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Popis', validators=[Optional(), Length(max=500)])
    icon = StringField('Ikona (Font Awesome)', validators=[DataRequired(), Length(max=50)])
    is_enabled = BooleanField('Aktivní', default=True)
    position = IntegerField('Pozice', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Uložit')

class UserDashboardSettingForm(FlaskForm):
    """Formulář pro uživatelská nastavení dashboardu"""
    widgets = SelectField('Widgety', coerce=int)
    is_visible = BooleanField('Viditelný', default=True)
    position = IntegerField('Pozice', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Uložit nastavení')
