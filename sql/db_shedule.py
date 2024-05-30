import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from sql.db_models import Monday, Tuesday, Wednesday, Thursday, Friday, Time, Week
from sql.db_time import get_current_day_of_week

week = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця']

def get_current_week_type(db: Session):
    """
    Функція для отримання типу поточного тижня (верхній чи нижній).
    """
    week_info = db.query(Week).first()
    if week_info:
        if week_info.is_upper:
            return "верхній"
        elif week_info.is_lower:
            return "нижній"
    return None


def get_schedule_by_group_and_day(db: Session, group_id: int, day: str, is_upper: bool = None):
    """
    Функція для отримання розкладу для групи на конкретний день з урахуванням типу тижня.
    """
    query = None
    if day == 'Понеділок':
        query = db.query(Monday)
    elif day == 'Вівторок':
        query = db.query(Tuesday)
    elif day == 'Середа':
        query = db.query(Wednesday)
    elif day == 'Четвер':
        query = db.query(Thursday)
    elif day == 'П\'ятниця':
        query = db.query(Friday)

    if query is None:
        return []

    if is_upper is None:
        return query.filter_by(group_id=group_id).all()
    else:
        return query.filter(
            (query.column_descriptions[0]['entity'].group_id == group_id) & 
            ((query.column_descriptions[0]['entity'].is_upper == is_upper) | 
             (query.column_descriptions[0]['entity'].is_upper == None))
        ).all()

def get_schedule_for_today(db: Session, group_id: int):
    """
    Функція для отримання розкладу на сьогодні для конкретної групи.
    """
    day_of_week = get_current_day_of_week()
    if day_of_week > 5:
        return []
    today = week[day_of_week - 1]
    week_type = get_current_week_type(db)
    if week_type == 'верхній':
        is_upper = True
    elif week_type == 'нижній':
        is_upper = False
    else:
        is_upper = None
    return get_schedule_by_group_and_day(db, group_id, today, is_upper)

def get_schedule_for_week(db: Session, group_id: int):
    """
    Функція для отримання розкладу на тиждень для конкретної групи.
    """
    week_type = get_current_week_type(db)
    if week_type == 'верхній':
        is_upper = True
    elif week_type == 'нижній':
        is_upper = False
    else:
        is_upper = None
    schedule = {
        'Понеділок': get_schedule_by_group_and_day(db, group_id, 'Понеділок', is_upper),
        'Вівторок': get_schedule_by_group_and_day(db, group_id, 'Вівторок', is_upper),
        'Середа': get_schedule_by_group_and_day(db, group_id, 'Середа', is_upper),
        'Четвер': get_schedule_by_group_and_day(db, group_id, 'Четвер', is_upper),
        'П\'ятниця': get_schedule_by_group_and_day(db, group_id, 'П\'ятниця', is_upper),
    }
    return schedule

def get_call_schedule(db: Session):
    """
    Функція для отримання розкладу дзвінків.
    """
    return db.query(Time).all()

def format_schedule(db: Session, schedule):
    """
    Функція для форматування розкладу у читабельний формат.
    """
    if not schedule:
        return "Сьогодні пар немає, відпочивайте"

    formatted_schedule = []
    call_schedule = {entry.num_of_lesson: f"{entry.time_of_begin.strftime('%H:%M')} - {entry.time_of_end.strftime('%H:%M')}" for entry in get_call_schedule(db)}

    for lesson_number in sorted(call_schedule.keys()):
        lesson_entry = next((entry for entry in schedule if entry.num_of_lesson == lesson_number), None)
        if lesson_entry:
            subgroup_info = f"\n    Підгрупа: {lesson_entry.subgroup}" if lesson_entry.subgroup else ""
            formatted_schedule.append(
                f"Пара {lesson_number}: {lesson_entry.name_of_lesson}{subgroup_info}\n     Викладач: {lesson_entry.teacher_name}\n     Аудиторія: {lesson_entry.lesson_room}\n     Час: {call_schedule[lesson_number]}"
            )
        else:
            formatted_schedule.append(
                f"Пара {lesson_number}: Немає пари"
            )
    
    return "\n".join(formatted_schedule)

def format_week_schedule(db: Session, week_schedule):
    """
    Функція для форматування розкладу на тиждень у читабельний формат.
    """
    formatted_schedule = []
    for day, schedule in week_schedule.items():
        formatted_schedule.append(f"{day}:")
        formatted_schedule.append(format_schedule(db, schedule))
        formatted_schedule.append("\n")
    return "\n".join(formatted_schedule)

def format_call_schedule(call_schedule):
    """
    Функція для форматування розкладу дзвінків у читабельний формат.
    """
    formatted_schedule = []
    for entry in call_schedule:
        formatted_schedule.append(
            f"Урок {entry.num_of_lesson}: {entry.time_of_begin.strftime('%H:%M')} - {entry.time_of_end.strftime('%H:%M')}"
        )
    return "\n".join(formatted_schedule)
