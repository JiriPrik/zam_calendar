from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from app.models import Holiday
from datetime import date

class HolidayForm(FlaskForm):
    """Formulář pro vytvoření a úpravu svátků"""
    name = StringField('Název svátku', validators=[DataRequired()])
    date = DateField('Datum', validators=[DataRequired()], format='%Y-%m-%d')
    description = TextAreaField('Popis')
    is_recurring = BooleanField('Opakuje se každý rok')
    submit = SubmitField('Uložit')
    
    def __init__(self, original_holiday=None, *args, **kwargs):
        super(HolidayForm, self).__init__(*args, **kwargs)
        self.original_holiday = original_holiday
    
    def validate_date(self, date_field):
        """Validace data - kontrola, zda na dané datum již neexistuje jiný svátek"""
        if self.original_holiday and self.original_holiday.date == date_field.data:
            # Pokud upravujeme existující svátek a datum se nezměnilo, přeskočíme validaci
            return
        
        # Kontrola, zda na dané datum již neexistuje jiný svátek
        existing_holiday = Holiday.query.filter_by(date=date_field.data).first()
        if existing_holiday:
            raise ValidationError(f'Na toto datum již existuje svátek: {existing_holiday.name}')
