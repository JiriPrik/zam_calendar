from app import db
from app.models import DashboardWidget

def init_dashboard_widgets():
    """Inicializace výchozích widgetů pro dashboard"""
    # Kontrola, zda již existují widgety
    if DashboardWidget.query.count() > 0:
        print("Widgety již existují, přeskakuji inicializaci.")
        return
    
    # Vytvoření výchozích widgetů
    widgets = [
        {
            'name': 'Přehled volna',
            'description': 'Zobrazuje přehled žádostí o volno pro aktuální měsíc.',
            'icon': 'fas fa-calendar-alt',
            'position': 0,
            'is_enabled': True
        },
        {
            'name': 'Moje žádosti',
            'description': 'Zobrazuje počet vašich žádostí o volno podle stavu.',
            'icon': 'fas fa-list-alt',
            'position': 1,
            'is_enabled': True
        },
        {
            'name': 'Ke schválení',
            'description': 'Zobrazuje počet žádostí čekajících na vaše schválení.',
            'icon': 'fas fa-check-circle',
            'position': 2,
            'is_enabled': True
        },
        {
            'name': 'Rychlé odkazy',
            'description': 'Poskytuje rychlý přístup k nejpoužívanějším funkcím.',
            'icon': 'fas fa-link',
            'position': 3,
            'is_enabled': True
        }
    ]
    
    for widget_data in widgets:
        widget = DashboardWidget(**widget_data)
        db.session.add(widget)
    
    db.session.commit()
    print(f"Úspěšně vytvořeno {len(widgets)} výchozích widgetů.")

if __name__ == '__main__':
    init_dashboard_widgets()
