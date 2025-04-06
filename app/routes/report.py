from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, LeaveRequest, LeaveType, LeaveStatus
from datetime import datetime, timedelta
from sqlalchemy import extract, func
import calendar

report = Blueprint('report', __name__)

@report.route('/reports')
@login_required
def index():
    """Hlavní stránka reportů - přehled dostupných reportů"""
    # Pouze manažeři a admini mají přístup k reportům
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('report/index.html', title='Reporty')

@report.route('/reports/leave-summary')
@login_required
def leave_summary():
    """Report se shrnutím volna zaměstnanců"""
    # Pouze manažeři a admini mají přístup k reportům
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    # Získání seznamu zaměstnanců
    if current_user.is_admin():
        # Admin vidí všechny zaměstnance
        employees = User.query.all()
    else:
        # Manažer vidí pouze své podřízené
        employees = User.query.filter_by(manager_id=current_user.id).all()
    
    # Aktuální rok
    current_year = datetime.now().year
    
    # Získání statistik pro každého zaměstnance
    employee_stats = []
    for employee in employees:
        # Základní údaje o zaměstnanci
        stats = {
            'id': employee.id,
            'name': f"{employee.first_name} {employee.last_name}",
            'username': employee.username,
            'role': employee.role.name,
            'previous_year_leave': employee.previous_year_leave,
            'current_year_leave': employee.current_year_leave,
            'total_leave': employee.previous_year_leave + employee.current_year_leave,
            'remaining_leave': employee.get_remaining_leave(),
            'leave_by_type': {},
            'leave_by_month': [0] * 12  # Seznam pro každý měsíc v roce
        }
        
        # Získání všech schválených žádostí o volno v aktuálním roce
        leave_requests = LeaveRequest.query.join(LeaveType).filter(
            LeaveRequest.user_id == employee.id,
            LeaveRequest.status == LeaveStatus.APPROVED,
            extract('year', LeaveRequest.start_date) == current_year
        ).all()
        
        # Počítání volna podle typu
        for leave_type in LeaveType.query.all():
            stats['leave_by_type'][leave_type.name] = 0
        
        # Zpracování žádostí o volno
        for request in leave_requests:
            # Přidání dnů podle typu volna
            leave_type_name = request.leave_type.name
            days = request.duration_days()
            
            if leave_type_name in stats['leave_by_type']:
                stats['leave_by_type'][leave_type_name] += days
            
            # Přidání dnů podle měsíce
            # Pro zjednodušení předpokládáme, že celé volno patří do měsíce začátku
            month_index = request.start_date.month - 1  # 0-indexed
            stats['leave_by_month'][month_index] += days
        
        employee_stats.append(stats)
    
    # Názvy měsíců pro zobrazení v grafu
    months = [calendar.month_name[i] for i in range(1, 13)]
    
    # Získání všech typů volna pro zobrazení v tabulce
    leave_types = LeaveType.query.all()
    
    return render_template('report/leave_summary.html', 
                          title='Shrnutí volna zaměstnanců',
                          employee_stats=employee_stats,
                          months=months,
                          leave_types=leave_types,
                          current_year=current_year)

@report.route('/reports/employee/<int:employee_id>')
@login_required
def employee_detail(employee_id):
    """Detailní report o volnu konkrétního zaměstnance"""
    # Pouze manažeři a admini mají přístup k reportům
    if not current_user.is_manager():
        flash('Nemáte oprávnění k této akci', 'danger')
        return redirect(url_for('main.index'))
    
    # Získání zaměstnance
    employee = User.query.get_or_404(employee_id)
    
    # Kontrola oprávnění - pouze manažer daného zaměstnance nebo admin může vidět jeho detail
    if not current_user.is_admin() and employee.manager_id != current_user.id:
        flash('Nemáte oprávnění zobrazit detail tohoto zaměstnance', 'danger')
        return redirect(url_for('report.leave_summary'))
    
    # Aktuální rok
    current_year = datetime.now().year
    
    # Získání všech žádostí o volno v aktuálním roce
    leave_requests = LeaveRequest.query.join(LeaveType).filter(
        LeaveRequest.user_id == employee.id,
        extract('year', LeaveRequest.start_date) == current_year
    ).order_by(LeaveRequest.start_date).all()
    
    # Statistiky podle typu volna
    leave_by_type = {}
    for leave_type in LeaveType.query.all():
        leave_by_type[leave_type.name] = {
            'approved': 0,
            'pending': 0,
            'rejected': 0,
            'cancelled': 0,
            'color': leave_type.color_code
        }
    
    # Zpracování žádostí o volno
    for request in leave_requests:
        leave_type_name = request.leave_type.name
        days = request.duration_days()
        
        if leave_type_name in leave_by_type:
            if request.status == LeaveStatus.APPROVED:
                leave_by_type[leave_type_name]['approved'] += days
            elif request.status == LeaveStatus.PENDING:
                leave_by_type[leave_type_name]['pending'] += days
            elif request.status == LeaveStatus.REJECTED:
                leave_by_type[leave_type_name]['rejected'] += days
            elif request.status == LeaveStatus.CANCELLED:
                leave_by_type[leave_type_name]['cancelled'] += days
    
    # Názvy měsíců pro zobrazení v grafu
    months = [calendar.month_name[i] for i in range(1, 13)]
    
    # Data pro graf podle měsíců
    leave_by_month = [0] * 12
    for request in leave_requests:
        if request.status == LeaveStatus.APPROVED:
            month_index = request.start_date.month - 1  # 0-indexed
            leave_by_month[month_index] += request.duration_days()
    
    return render_template('report/employee_detail.html',
                          title=f'Detail zaměstnance - {employee.first_name} {employee.last_name}',
                          employee=employee,
                          leave_requests=leave_requests,
                          leave_by_type=leave_by_type,
                          leave_by_month=leave_by_month,
                          months=months,
                          current_year=current_year)
