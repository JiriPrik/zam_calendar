from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email, ValidationError, Length, NumberRange
from app.models import User

class EditUserForm(FlaskForm):
    first_name = StringField('Jméno', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Příjmení', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', coerce=int)
    manager = SelectField('Nadřízený', coerce=int)
    previous_year_leave = FloatField('Nečerpaná dovolená z minulého roku',
                                    validators=[NumberRange(min=0, message='Hodnota musí být kladné číslo')],
                                    default=0.0)
    current_year_leave = FloatField('Nárok na dovolenou v aktuálním roce',
                                   validators=[NumberRange(min=0, message='Hodnota musí být kladné číslo')],
                                   default=20.0)
    submit = SubmitField('Uložit změny')

    def __init__(self, original_user, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_email(self, email):
        if email.data != self.original_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Tento email je již registrován. Zvolte prosím jiný.')
