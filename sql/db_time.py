import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from sql.db_models import Week

def get_current_day_of_week() -> int:
    """Повертає номер сьогоднішнього дня тижня (1-понеділок, 7-неділя)."""
    return datetime.today().isoweekday()

def swap_weeks(db):
    """Міняє місцями верхній та нижній тиждень."""
    # Отримуємо поточні значення верхнього та нижнього тижня з бази даних.
    week = db.query(Week).first()
    
    # Міняємо їх місцями.
    if week.is_upper == True and week.is_lower==False:
        week.is_upper = False
        week.is_lower = True
    elif week.is_upper == False and week.is_lower == True:
        week.is_upper = True
        week.is_lower = False
    else:
        pass
    
    # Зберігаємо зміни у базі даних.
    db.commit()