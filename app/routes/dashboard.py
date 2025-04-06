from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import DashboardWidget, UserDashboardSetting
from app.forms import DashboardWidgetForm, UserDashboardSettingForm
from app.utils.decorators import admin_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Nastavení dashboardu pro přihlášeného uživatele"""
    # Získání všech dostupných widgetů
    available_widgets = DashboardWidget.query.filter_by(is_enabled=True).all()
    
    # Získání nastavení uživatele
    user_settings = UserDashboardSetting.query.filter_by(user_id=current_user.id).all()
    
    # Vytvoření slovníku pro rychlý přístup k nastavení
    user_settings_dict = {setting.widget_id: setting for setting in user_settings}
    
    # Zpracování formuláře pro uložení nastavení
    if request.method == 'POST':
        # Zpracování dat z formuláře
        widget_settings = request.form.getlist('widget_settings')
        
        for widget_data in widget_settings:
            widget_id, is_visible, position = widget_data.split('|')
            widget_id = int(widget_id)
            is_visible = is_visible == 'true'
            position = int(position)
            
            # Kontrola, zda již existuje nastavení pro tento widget
            if widget_id in user_settings_dict:
                # Aktualizace existujícího nastavení
                setting = user_settings_dict[widget_id]
                setting.is_visible = is_visible
                setting.position = position
            else:
                # Vytvoření nového nastavení
                setting = UserDashboardSetting(
                    user_id=current_user.id,
                    widget_id=widget_id,
                    is_visible=is_visible,
                    position=position
                )
                db.session.add(setting)
        
        db.session.commit()
        flash('Nastavení dashboardu bylo úspěšně uloženo.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('dashboard/settings.html', 
                          available_widgets=available_widgets,
                          user_settings_dict=user_settings_dict)

@dashboard.route('/dashboard/widgets', methods=['GET'])
@login_required
@admin_required
def list_widgets():
    """Seznam všech widgetů dashboardu (pouze pro adminy)"""
    widgets = DashboardWidget.query.order_by(DashboardWidget.position).all()
    return render_template('dashboard/widgets.html', widgets=widgets)

@dashboard.route('/dashboard/widgets/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_widget():
    """Přidání nového widgetu (pouze pro adminy)"""
    form = DashboardWidgetForm()
    
    if form.validate_on_submit():
        widget = DashboardWidget(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data,
            is_enabled=form.is_enabled.data,
            position=form.position.data
        )
        db.session.add(widget)
        db.session.commit()
        
        flash('Widget byl úspěšně přidán.', 'success')
        return redirect(url_for('dashboard.list_widgets'))
    
    return render_template('dashboard/widget_form.html', form=form, title='Přidat widget')

@dashboard.route('/dashboard/widgets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_widget(id):
    """Úprava widgetu (pouze pro adminy)"""
    widget = DashboardWidget.query.get_or_404(id)
    form = DashboardWidgetForm(obj=widget)
    
    if form.validate_on_submit():
        widget.name = form.name.data
        widget.description = form.description.data
        widget.icon = form.icon.data
        widget.is_enabled = form.is_enabled.data
        widget.position = form.position.data
        
        db.session.commit()
        
        flash('Widget byl úspěšně upraven.', 'success')
        return redirect(url_for('dashboard.list_widgets'))
    
    return render_template('dashboard/widget_form.html', form=form, title='Upravit widget')

@dashboard.route('/dashboard/widgets/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_widget(id):
    """Smazání widgetu (pouze pro adminy)"""
    widget = DashboardWidget.query.get_or_404(id)
    
    # Smazání všech uživatelských nastavení pro tento widget
    UserDashboardSetting.query.filter_by(widget_id=widget.id).delete()
    
    db.session.delete(widget)
    db.session.commit()
    
    flash('Widget byl úspěšně smazán.', 'success')
    return redirect(url_for('dashboard.list_widgets'))

@dashboard.route('/dashboard/widgets/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_widget(id):
    """Přepnutí stavu widgetu (pouze pro adminy)"""
    widget = DashboardWidget.query.get_or_404(id)
    widget.is_enabled = not widget.is_enabled
    db.session.commit()
    
    return jsonify({'success': True, 'is_enabled': widget.is_enabled})
