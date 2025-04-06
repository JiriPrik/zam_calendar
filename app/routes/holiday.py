from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Holiday
from app.forms import HolidayForm
from datetime import datetime

holiday = Blueprint('holiday', __name__)

@holiday.route('/holidays')
@login_required
def list_holidays():
    """Seznam svátků a nepracovních dnů"""
    # Pouze manažeři a admini mají přístup ke správě svátků
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    # Získání všech svátků seřazených podle data
    holidays = Holiday.query.order_by(Holiday.date).all()
    
    # Rozdělení svátků na aktuální rok a budoucí
    current_year = datetime.now().year
    current_year_holidays = []
    future_holidays = []
    past_holidays = []
    
    for h in holidays:
        # Pro opakující se svátky použijeme aktuální rok
        if h.is_recurring:
            holiday_date = datetime(current_year, h.date.month, h.date.day).date()
        else:
            holiday_date = h.date
        
        if holiday_date.year == current_year:
            current_year_holidays.append(h)
        elif holiday_date.year > current_year:
            future_holidays.append(h)
        else:
            past_holidays.append(h)
    
    return render_template('holiday/list.html', 
                          title='Svátky a nepracovní dny',
                          current_year_holidays=current_year_holidays,
                          future_holidays=future_holidays,
                          past_holidays=past_holidays,
                          current_year=current_year)

@holiday.route('/holidays/add', methods=['GET', 'POST'])
@login_required
def add_holiday():
    """Přidání nového svátku"""
    # Pouze manažeři a admini mají přístup ke správě svátků
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    form = HolidayForm()
    
    if form.validate_on_submit():
        holiday = Holiday(
            name=form.name.data,
            date=form.date.data,
            description=form.description.data,
            is_recurring=form.is_recurring.data
        )
        
        db.session.add(holiday)
        db.session.commit()
        
        flash(f'Svátek {holiday.name} byl úspěšně přidán', 'success')
        return redirect(url_for('holiday.list_holidays'))
    
    return render_template('holiday/edit.html', 
                          title='Přidat svátek',
                          form=form,
                          is_edit=False)

@holiday.route('/holidays/edit/<int:holiday_id>', methods=['GET', 'POST'])
@login_required
def edit_holiday(holiday_id):
    """Úprava existujícího svátku"""
    # Pouze manažeři a admini mají přístup ke správě svátků
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    holiday_to_edit = Holiday.query.get_or_404(holiday_id)
    form = HolidayForm(original_holiday=holiday_to_edit)
    
    if request.method == 'GET':
        form.name.data = holiday_to_edit.name
        form.date.data = holiday_to_edit.date
        form.description.data = holiday_to_edit.description
        form.is_recurring.data = holiday_to_edit.is_recurring
    
    if form.validate_on_submit():
        holiday_to_edit.name = form.name.data
        holiday_to_edit.date = form.date.data
        holiday_to_edit.description = form.description.data
        holiday_to_edit.is_recurring = form.is_recurring.data
        holiday_to_edit.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Svátek {holiday_to_edit.name} byl úspěšně aktualizován', 'success')
        return redirect(url_for('holiday.list_holidays'))
    
    return render_template('holiday/edit.html', 
                          title='Upravit svátek',
                          form=form,
                          holiday=holiday_to_edit,
                          is_edit=True)

@holiday.route('/holidays/delete/<int:holiday_id>')
@login_required
def delete_holiday(holiday_id):
    """Smazání svátku"""
    # Pouze manažeři a admini mají přístup ke správě svátků
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    holiday_to_delete = Holiday.query.get_or_404(holiday_id)
    
    db.session.delete(holiday_to_delete)
    db.session.commit()
    
    flash(f'Svátek {holiday_to_delete.name} byl úspěšně smazán', 'success')
    return redirect(url_for('holiday.list_holidays'))
