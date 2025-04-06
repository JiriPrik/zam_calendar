from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import LeaveType
from app.forms import LeaveTypeForm
from datetime import datetime

leave_type = Blueprint('leave_type', __name__)

@leave_type.route('/leave-types')
@login_required
def list_leave_types():
    """Seznam typů volna"""
    # Pouze manažeři a admini mají přístup ke správě typů volna
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    # Získání všech typů volna
    leave_types = LeaveType.query.order_by(LeaveType.name).all()
    
    return render_template('leave_type/list.html', 
                          title='Typy volna',
                          leave_types=leave_types)

@leave_type.route('/leave-types/add', methods=['GET', 'POST'])
@login_required
def add_leave_type():
    """Přidání nového typu volna"""
    # Pouze manažeři a admini mají přístup ke správě typů volna
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    form = LeaveTypeForm()
    
    if form.validate_on_submit():
        leave_type = LeaveType(
            name=form.name.data,
            description=form.description.data,
            color_code=form.color_code.data,
            auto_approve=form.auto_approve.data,
            max_days=form.max_days.data
        )
        
        db.session.add(leave_type)
        db.session.commit()
        
        flash(f'Typ volna {leave_type.name} byl úspěšně přidán', 'success')
        return redirect(url_for('leave_type.list_leave_types'))
    
    return render_template('leave_type/edit.html', 
                          title='Přidat typ volna',
                          form=form,
                          is_edit=False)

@leave_type.route('/leave-types/edit/<int:leave_type_id>', methods=['GET', 'POST'])
@login_required
def edit_leave_type(leave_type_id):
    """Úprava existujícího typu volna"""
    # Pouze manažeři a admini mají přístup ke správě typů volna
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    leave_type_to_edit = LeaveType.query.get_or_404(leave_type_id)
    form = LeaveTypeForm(original_leave_type=leave_type_to_edit)
    
    if request.method == 'GET':
        form.name.data = leave_type_to_edit.name
        form.description.data = leave_type_to_edit.description
        form.color_code.data = leave_type_to_edit.color_code
        form.auto_approve.data = leave_type_to_edit.auto_approve
        form.max_days.data = leave_type_to_edit.max_days
    
    if form.validate_on_submit():
        leave_type_to_edit.name = form.name.data
        leave_type_to_edit.description = form.description.data
        leave_type_to_edit.color_code = form.color_code.data
        leave_type_to_edit.auto_approve = form.auto_approve.data
        leave_type_to_edit.max_days = form.max_days.data
        leave_type_to_edit.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Typ volna {leave_type_to_edit.name} byl úspěšně aktualizován', 'success')
        return redirect(url_for('leave_type.list_leave_types'))
    
    return render_template('leave_type/edit.html', 
                          title='Upravit typ volna',
                          form=form,
                          leave_type=leave_type_to_edit,
                          is_edit=True)

@leave_type.route('/leave-types/delete/<int:leave_type_id>')
@login_required
def delete_leave_type(leave_type_id):
    """Smazání typu volna"""
    # Pouze manažeři a admini mají přístup ke správě typů volna
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    leave_type_to_delete = LeaveType.query.get_or_404(leave_type_id)
    
    # Kontrola, zda typ volna není používán v žádostech o volno
    if leave_type_to_delete.leave_requests.count() > 0:
        flash(f'Typ volna {leave_type_to_delete.name} nelze smazat, protože je používán v žádostech o volno', 'danger')
        return redirect(url_for('leave_type.list_leave_types'))
    
    db.session.delete(leave_type_to_delete)
    db.session.commit()
    
    flash(f'Typ volna {leave_type_to_delete.name} byl úspěšně smazán', 'success')
    return redirect(url_for('leave_type.list_leave_types'))
