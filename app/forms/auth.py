from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    remember_me = BooleanField('Zapamatovat si mě')
    submit = SubmitField('Přihlásit se')

class RegistrationForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Jméno', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Příjmení', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Heslo', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Potvrdit heslo', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', coerce=int)
    manager = SelectField('Nadřízený', coerce=int)
    submit = SubmitField('Registrovat')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Toto uživatelské jméno je již obsazeno. Zvolte prosím jiné.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Tento email je již registrován. Zvolte prosím jiný.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Současné heslo', validators=[DataRequired()])
    new_password = PasswordField('Nové heslo', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Potvrdit nové heslo', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Změnit heslo')
