from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, IntegerField, ColorField
from wtforms.validators import DataRequired, ValidationError, NumberRange
from app.models import LeaveType

class LeaveTypeForm(FlaskForm):
    """Formulář pro vytvoření a úpravu typů volna"""
    name = StringField('Název typu volna', validators=[DataRequired()])
    description = TextAreaField('Popis')
    color_code = StringField('Barva (HEX kód)', validators=[DataRequired()], default="#3498db")
    auto_approve = BooleanField('Automatické schvalování')
    max_days = IntegerField('Maximální počet dní pro automatické schválení', 
                           validators=[NumberRange(min=0, message='Hodnota musí být kladné číslo nebo nula')],
                           default=0)
    submit = SubmitField('Uložit')
    
    def __init__(self, original_leave_type=None, *args, **kwargs):
        super(LeaveTypeForm, self).__init__(*args, **kwargs)
        self.original_leave_type = original_leave_type
    
    def validate_name(self, name):
        """Validace názvu - kontrola, zda již neexistuje typ volna se stejným názvem"""
        if self.original_leave_type and self.original_leave_type.name == name.data:
            # Pokud upravujeme existující typ volna a název se nezměnil, přeskočíme validaci
            return
        
        # Kontrola, zda již neexistuje typ volna se stejným názvem
        existing_leave_type = LeaveType.query.filter_by(name=name.data).first()
        if existing_leave_type:
            raise ValidationError(f'Typ volna s názvem "{name.data}" již existuje.')
