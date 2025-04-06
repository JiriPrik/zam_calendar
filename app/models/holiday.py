from app import db
from datetime import datetime

class Holiday(db.Model):
    """Model pro státní svátky a jiné nepracovní dny"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    is_recurring = db.Column(db.Boolean, default=True)  # Opakuje se každý rok?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Holiday {self.name} - {self.date}>'
    
    @staticmethod
    def is_holiday(date):
        """Kontroluje, zda je zadané datum svátek"""
        # Kontrola přesného data
        exact_match = Holiday.query.filter_by(date=date).first()
        if exact_match:
            return True
        
        # Kontrola opakujících se svátků (stejný den a měsíc)
        recurring_match = Holiday.query.filter(
            Holiday.is_recurring == True,
            db.extract('month', Holiday.date) == date.month,
            db.extract('day', Holiday.date) == date.day
        ).first()
        
        return recurring_match is not None
    
    @staticmethod
    def is_weekend(date):
        """Kontroluje, zda je zadané datum víkend (sobota nebo neděle)"""
        return date.weekday() >= 5  # 5 = sobota, 6 = neděle
    
    @staticmethod
    def is_non_working_day(date):
        """Kontroluje, zda je zadané datum nepracovní den (víkend nebo svátek)"""
        return Holiday.is_weekend(date) or Holiday.is_holiday(date)
