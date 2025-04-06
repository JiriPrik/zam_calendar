from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import LeaveRequest, User, LeaveStatus, Holiday, DashboardWidget, UserDashboardSetting
from datetime import datetime, date
import json

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Získání aktuálního měsíce a roku
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Získání žádostí o volno pro aktuální měsíc
    if current_user.is_manager():
        # Manažeři vidí žádosti svých podřízených
        leave_requests = LeaveRequest.query.join(User, LeaveRequest.user_id == User.id).filter(
            User.manager_id == current_user.id,
            LeaveRequest.start_date.between(
                datetime(current_year, current_month, 1),
                datetime(current_year, current_month + 1 if current_month < 12 else 1, 1)
            )
        ).all()

        # Získání počtu žádostí ke schválení pro manažery
        pending_approvals_count = LeaveRequest.query.join(User, LeaveRequest.user_id == User.id).filter(
            User.manager_id == current_user.id,
            LeaveRequest.status == LeaveStatus.PENDING
        ).count()
    else:
        # Běžní uživatelé vidí jen své žádosti
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.user_id == current_user.id,
            LeaveRequest.start_date.between(
                datetime(current_year, current_month, 1),
                datetime(current_year, current_month + 1 if current_month < 12 else 1, 1)
            )
        ).all()

        # Běžní uživatelé nemají žádné žádosti ke schválení
        pending_approvals_count = 0

    # Získání počtu žádostí o dovolenou pro přihlášeného uživatele
    pending_requests_count = LeaveRequest.query.filter_by(user_id=current_user.id, status=LeaveStatus.PENDING).count()
    approved_requests_count = LeaveRequest.query.filter_by(user_id=current_user.id, status=LeaveStatus.APPROVED).count()

    # Získání nastavení dashboardu pro uživatele
    # Získání všech dostupných widgetů
    available_widgets = DashboardWidget.query.filter_by(is_enabled=True).all()

    # Získání nastavení uživatele
    user_settings = UserDashboardSetting.query.filter_by(user_id=current_user.id).all()

    # Vytvoření slovníku pro rychlý přístup k nastavení
    user_settings_dict = {setting.widget_id: setting for setting in user_settings}

    # Vytvoření seznamu widgetů pro zobrazení
    dashboard_widgets = []
    for widget in available_widgets:
        # Kontrola, zda existuje nastavení pro tento widget
        if widget.id in user_settings_dict:
            setting = user_settings_dict[widget.id]
            # Přidání widgetu pouze pokud je viditelný
            if setting.is_visible:
                dashboard_widgets.append({
                    'widget': widget,
                    'position': setting.position
                })
        else:
            # Pokud neexistuje nastavení, přidáme widget s výchozím nastavením
            dashboard_widgets.append({
                'widget': widget,
                'position': widget.position
            })

    # Seřazení widgetů podle pozice
    dashboard_widgets.sort(key=lambda x: x['position'])

    return render_template('main/index.html',
                          title='Přehled',
                          leave_requests=leave_requests,
                          current_month=current_month,
                          current_year=current_year,
                          dashboard_widgets=dashboard_widgets,
                          pending_requests_count=pending_requests_count,
                          approved_requests_count=approved_requests_count,
                          pending_approvals_count=pending_approvals_count)

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', title='Můj profil')

@main.route('/calendar')
@login_required
def calendar():
    # Získání všech žádostí o volno pro zobrazení v kalendáři
    if current_user.is_manager():
        # Manažeři vidí žádosti svých podřízených (kromě zamítnutých)
        leave_requests = LeaveRequest.query.join(User, LeaveRequest.user_id == User.id).filter(
            User.manager_id == current_user.id,
            LeaveRequest.status != LeaveStatus.REJECTED
        ).all()
    else:
        # Běžní uživatelé vidí jen své žádosti (kromě zamítnutých)
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.user_id == current_user.id,
            LeaveRequest.status != LeaveStatus.REJECTED
        ).all()

    # Získání svátků pro aktuální rok
    current_year = datetime.now().year
    holidays = Holiday.query.all()

    # Příprava svátků pro JavaScript
    holiday_dates = []
    for holiday in holidays:
        if holiday.is_recurring:
            # Pro opakující se svátky použijeme aktuální rok
            holiday_date = date(current_year, holiday.date.month, holiday.date.day)
            holiday_dates.append({
                'date': holiday_date.strftime('%Y-%m-%d'),
                'name': holiday.name
            })
        elif holiday.date.year == current_year:
            # Pro jednorázové svátky v aktuálním roce
            holiday_dates.append({
                'date': holiday.date.strftime('%Y-%m-%d'),
                'name': holiday.name
            })

    return render_template('main/calendar.html',
                          title='Kalendář',
                          leave_requests=leave_requests,
                          holidays=json.dumps(holiday_dates))
