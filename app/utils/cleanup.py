from app import db
from app.models import LeaveRequest, LeaveStatus, AppSettings
from datetime import datetime, timedelta
from sqlalchemy import and_

def delete_cancelled_requests(period='month'):
    """
    Smaže zrušené žádosti o volno za určité období
    
    Args:
        period: Období pro mazání ('month', 'year', 'all')
    
    Returns:
        int: Počet smazaných žádostí
    """
    # Vytvoření filtru podle období
    filter_conditions = [LeaveRequest.status == LeaveStatus.CANCELLED]
    
    if period == 'month':
        # Žádosti starší než 1 měsíc
        one_month_ago = datetime.now() - timedelta(days=30)
        filter_conditions.append(LeaveRequest.updated_at < one_month_ago)
    elif period == 'year':
        # Žádosti starší než 1 rok
        one_year_ago = datetime.now() - timedelta(days=365)
        filter_conditions.append(LeaveRequest.updated_at < one_year_ago)
    # Pro 'all' nepřidáváme žádnou další podmínku
    
    # Získání žádostí ke smazání
    requests_to_delete = LeaveRequest.query.filter(and_(*filter_conditions)).all()
    
    # Smazání žádostí
    count = len(requests_to_delete)
    for request in requests_to_delete:
        db.session.delete(request)
    
    # Aktualizace času posledního čištění
    app_settings = AppSettings.query.first()
    if app_settings:
        app_settings.last_cancelled_cleanup = datetime.now()
        
    db.session.commit()
    
    return count
