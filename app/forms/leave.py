from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateField, BooleanField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from datetime import date
from flask_login import current_user
from app.models import LeaveRequest

class LeaveRequestForm(FlaskForm):
    leave_type = SelectField('Typ volna', coerce=int, validators=[DataRequired()])
    start_date = DateField('Datum začátku', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('Datum konce', validators=[DataRequired()], format='%Y-%m-%d')
    half_day = BooleanField('Půldenní volno')
    reason = TextAreaField('Důvod')
    request_id = HiddenField()  # Pro případ úpravy existující žádosti
    submit = SubmitField('Odeslat žádost')

    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError('Datum konce nemůže být dříve než datum začátku.')

    def validate_start_date(self, start_date):
        if start_date.data and start_date.data < date.today():
            raise ValidationError('Datum začátku nemůže být v minulosti.')

    def validate_overlapping(self):
        """Validace překrývajících se žádostí o volno"""
        if self.start_date.data and self.end_date.data:
            request_id = int(self.request_id.data) if self.request_id.data else None
            overlapping_requests = LeaveRequest.check_overlapping_leave(
                user_id=current_user.id,
                start_date=self.start_date.data,
                end_date=self.end_date.data,
                request_id=request_id
            )

            if overlapping_requests:
                dates_info = ', '.join([f"{r.start_date.strftime('%d.%m.%Y')} - {r.end_date.strftime('%d.%m.%Y')}" for r in overlapping_requests])
                status_info = ', '.join(["schváleno" if r.status == 'approved' else "čeká na schválení" for r in overlapping_requests])
                raise ValidationError(f'Na toto období již máte existující žádost o volno: {dates_info} ({status_info}).')

class LeaveApprovalForm(FlaskForm):
    status = SelectField('Stav', choices=[
        ('approved', 'Schválit'),
        ('rejected', 'Zamítnout')
    ])
    comment = TextAreaField('Komentář')
    submit = SubmitField('Potvrdit')
