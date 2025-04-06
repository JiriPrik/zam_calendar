from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nesprávné uživatelské jméno nebo heslo', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Přihlášení', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Pouze admin může registrovat nové uživatele
    if not current_user.is_admin():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    # Naplnění výběrových polí
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    form.manager.choices = [(user.id, f"{user.first_name} {user.last_name}") 
                           for user in User.query.filter(User.role.has(name='Manager')).all()]
    form.manager.choices.insert(0, (0, 'Žádný'))
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role_id=form.role.data
        )
        
        if form.manager.data != 0:
            user.manager_id = form.manager.data
            
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Uživatel {user.username} byl úspěšně vytvořen!', 'success')
        return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', title='Registrace uživatele', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Současné heslo je nesprávné', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Vaše heslo bylo úspěšně změněno', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/change_password.html', title='Změna hesla', form=form)
