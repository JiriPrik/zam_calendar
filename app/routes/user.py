from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Role
from app.forms import EditUserForm

user = Blueprint('user', __name__)

@user.route('/users')
@login_required
def list_users():
    """Seznam uživatelů pro manažery"""
    # Pouze manažeři mohou vidět seznam uživatelů
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    if current_user.is_admin():
        # Admin vidí všechny uživatele
        users = User.query.all()
    else:
        # Manažer vidí pouze své podřízené
        users = User.query.filter_by(manager_id=current_user.id).all()
    
    return render_template('user/list.html', title='Seznam uživatelů', users=users)

@user.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Úprava údajů uživatele (pouze pro manažery a adminy)"""
    # Získání uživatele
    user_to_edit = User.query.get_or_404(user_id)
    
    # Kontrola oprávnění - pouze manažer daného uživatele nebo admin může upravovat údaje
    if not current_user.is_admin() and user_to_edit.manager_id != current_user.id:
        flash('Nemáte oprávnění upravovat tohoto uživatele', 'danger')
        return redirect(url_for('main.index'))
    
    form = EditUserForm(user_to_edit)
    
    # Naplnění výběrových polí
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    form.manager.choices = [(user.id, f"{user.first_name} {user.last_name}") 
                           for user in User.query.filter(User.role.has(name='Manager')).all()]
    form.manager.choices.insert(0, (0, 'Žádný'))
    
    if request.method == 'GET':
        # Předvyplnění formuláře
        form.first_name.data = user_to_edit.first_name
        form.last_name.data = user_to_edit.last_name
        form.email.data = user_to_edit.email
        form.role.data = user_to_edit.role_id
        form.manager.data = user_to_edit.manager_id or 0
        form.previous_year_leave.data = user_to_edit.previous_year_leave
        form.current_year_leave.data = user_to_edit.current_year_leave
    
    if form.validate_on_submit():
        # Aktualizace údajů
        user_to_edit.first_name = form.first_name.data
        user_to_edit.last_name = form.last_name.data
        user_to_edit.email = form.email.data
        user_to_edit.role_id = form.role.data
        user_to_edit.manager_id = form.manager.data if form.manager.data != 0 else None
        user_to_edit.previous_year_leave = form.previous_year_leave.data
        user_to_edit.current_year_leave = form.current_year_leave.data
        
        db.session.commit()
        flash(f'Údaje uživatele {user_to_edit.username} byly úspěšně aktualizovány', 'success')
        return redirect(url_for('user.list_users'))
    
    return render_template('user/edit.html', title='Úprava uživatele', form=form, user=user_to_edit)
