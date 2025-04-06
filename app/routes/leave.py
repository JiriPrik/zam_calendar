from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import LeaveRequest, LeaveType, LeaveStatus, User
from app.forms import LeaveRequestForm, LeaveApprovalForm
from datetime import datetime
from wtforms.validators import ValidationError

leave = Blueprint('leave', __name__)

@leave.route('/leave/request', methods=['GET', 'POST'])
@login_required
def request_leave():
    form = LeaveRequestForm()

    # Naplnění výběrového pole typů volna
    form.leave_type.choices = [(lt.id, lt.name) for lt in LeaveType.query.all()]

    if form.validate_on_submit():
        try:
            # Kontrola překrývajících se žádostí
            form.validate_overlapping()

            # Získání typu volna
            leave_type = LeaveType.query.get(form.leave_type.data)

            # Vytvoření žádosti o volno
            leave_request = LeaveRequest(
                user_id=current_user.id,
                leave_type_id=form.leave_type.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                half_day=form.half_day.data,
                reason=form.reason.data,
                manager_id=current_user.manager_id
            )

            # Kontrola, zda má být žádost automaticky schválena
            if leave_type.auto_approve:
                # Výpočet počtu dní volna
                days = leave_request.duration_days()

                # Kontrola maximálního počtu dní pro automatické schválení
                if leave_type.max_days == 0 or days <= leave_type.max_days:
                    leave_request.status = LeaveStatus.APPROVED
                    success_message = 'Vaše žádost o volno byla automaticky schválena'
                else:
                    success_message = 'Vaše žádost o volno byla odeslána ke schválení (překročen limit pro automatické schválení)'
            else:
                success_message = 'Vaše žádost o volno byla odeslána ke schválení'

            db.session.add(leave_request)
            db.session.commit()

            flash(success_message, 'success')
            return redirect(url_for('main.index'))
        except ValidationError as e:
            flash(str(e), 'danger')

    return render_template('leave/request.html', title='Žádost o volno', form=form)

@leave.route('/leave/my-requests')
@login_required
def my_requests():
    leave_requests = LeaveRequest.query.filter_by(user_id=current_user.id).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('leave/my_requests.html', title='Moje žádosti', leave_requests=leave_requests)

@leave.route('/leave/pending-approvals')
@login_required
def pending_approvals():
    # Pouze manažeři mohou schvalovat žádosti
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))

    # Získání čekajících žádostí od podřízených
    pending_requests = LeaveRequest.query.join(User, LeaveRequest.user_id == User.id).filter(
        User.manager_id == current_user.id,
        LeaveRequest.status == LeaveStatus.PENDING
    ).order_by(LeaveRequest.created_at.asc()).all()

    return render_template('leave/pending_approvals.html',
                          title='Čekající žádosti',
                          pending_requests=pending_requests)

@leave.route('/leave/approve/<int:request_id>', methods=['GET', 'POST'])
@login_required
def approve_request(request_id):
    # Pouze manažeři mohou schvalovat žádosti
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))

    leave_request = LeaveRequest.query.get_or_404(request_id)

    # Ověření, že manažer schvaluje žádost svého podřízeného
    if leave_request.employee.manager_id != current_user.id:
        flash('Nemáte oprávnění schvalovat tuto žádost', 'danger')
        return redirect(url_for('leave.pending_approvals'))

    form = LeaveApprovalForm()

    if form.validate_on_submit():
        leave_request.status = form.status.data
        leave_request.manager_comment = form.comment.data
        leave_request.updated_at = datetime.utcnow()

        db.session.commit()

        status_text = 'schválena' if form.status.data == LeaveStatus.APPROVED else 'zamítnuta'
        flash(f'Žádost byla úspěšně {status_text}', 'success')
        return redirect(url_for('leave.pending_approvals'))

    return render_template('leave/approve.html',
                          title='Schválení žádosti',
                          leave_request=leave_request,
                          form=form)

@leave.route('/leave/cancel/<int:request_id>')
@login_required
def cancel_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)

    # Ověření, že uživatel ruší svou vlastní žádost
    if leave_request.user_id != current_user.id:
        flash('Nemáte oprávnění zrušit tuto žádost', 'danger')
        return redirect(url_for('leave.my_requests'))

    # Žádost lze zrušit pouze pokud je ve stavu čekající
    if leave_request.status != LeaveStatus.PENDING:
        flash('Tuto žádost již nelze zrušit', 'danger')
        return redirect(url_for('leave.my_requests'))

    leave_request.status = LeaveStatus.CANCELLED
    leave_request.updated_at = datetime.utcnow()

    db.session.commit()

    flash('Vaše žádost byla úspěšně zrušena', 'success')
    return redirect(url_for('leave.my_requests'))
