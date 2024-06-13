import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from sqlalchemy.orm import Session
from sql.db_models import Monday, Tuesday,Wednesday,Thursday,Friday,Time,Group

subjects = [
    {'name_of_lesson': 'Математика', 'teacher_name': 'Др. Смирнов', 'lesson_room': 101},
    {'name_of_lesson': 'Фізика', 'teacher_name': 'Проф. Іваненко', 'lesson_room': 102},
    {'name_of_lesson': 'Хімія', 'teacher_name': 'Др. Петров', 'lesson_room': 103},
    {'name_of_lesson': 'Біологія', 'teacher_name': 'Др. Сидоренко', 'lesson_room': 104},
    {'name_of_lesson': 'Історія', 'teacher_name': 'Др. Мельник', 'lesson_room': 105},
    {'name_of_lesson': 'Географія', 'teacher_name': 'Проф. Коваленко', 'lesson_room': 106},
    {'name_of_lesson': 'Англійська мова', 'teacher_name': 'Панянка Шевченко', 'lesson_room': 107},
    {'name_of_lesson': 'Українська мова', 'teacher_name': 'Пан Андрійчук', 'lesson_room': 108},
    {'name_of_lesson': 'Інформатика', 'teacher_name': 'Др. Гончаренко', 'lesson_room': 109},
    {'name_of_lesson': 'Фізична культура', 'teacher_name': 'Пан Кравчук', 'lesson_room': 110},
    {'name_of_lesson': 'Мистецтво', 'teacher_name': 'Панянка Лопушанська', 'lesson_room': 111},
    {'name_of_lesson': 'Література', 'teacher_name': 'Пан Олійник', 'lesson_room': 112},
    {'name_of_lesson': 'Філософія', 'teacher_name': 'Др. Марченко', 'lesson_room': 113},
    {'name_of_lesson': 'Соціологія', 'teacher_name': 'Проф. Гриценко', 'lesson_room': 114},
    {'name_of_lesson': 'Економіка', 'teacher_name': 'Др. Тимченко', 'lesson_room': 115},
    {'name_of_lesson': 'Правознавство', 'teacher_name': 'Пан Дорошенко', 'lesson_room': 116},
    {'name_of_lesson': 'Музика', 'teacher_name': 'Панянка Лисенко', 'lesson_room': 117},
    {'name_of_lesson': 'Хореографія', 'teacher_name': 'Панянка Скрипка', 'lesson_room': 118},
    {'name_of_lesson': 'Психологія', 'teacher_name': 'Др. Рубан', 'lesson_room': 119},
    {'name_of_lesson': 'Політологія', 'teacher_name': 'Пан Радченко', 'lesson_room': 120},
]

# Розклад дзвінків
time_schedule = [
    {'num_of_lesson': 1, 'time_of_begin': '08:00', 'time_of_end': '09:00'},
    {'num_of_lesson': 2, 'time_of_begin': '09:10', 'time_of_end': '10:10'},
    {'num_of_lesson': 3, 'time_of_begin': '11:20', 'time_of_end': '12:20'},
    {'num_of_lesson': 4, 'time_of_begin': '12:30', 'time_of_end': '13:30'},
    {'num_of_lesson': 5, 'time_of_begin': '13:40', 'time_of_end': '14:40'},
    {'num_of_lesson': 6, 'time_of_begin': '14:50', 'time_of_end': '15:50'},
    {'num_of_lesson': 7, 'time_of_begin': '16:00', 'time_of_end': '17:00'},
    {'num_of_lesson': 8, 'time_of_begin': '17:10', 'time_of_end': '18:10'},
]


def random_schedule():
    schedule = []
    for i in range(1, 9):  # 8 пар на день
        if random.randint(1,10)==5:  # випадковий пропуск пари
            schedule.append(None)
        else:
            subject = random.choice(subjects)
            schedule.append(subject)
    return schedule

def fill_schedule_for_day(session: Session, day_model, group):
    for is_upper in [True, False]:  # Два варіанти: верхній і нижній тиждень
        schedule = random_schedule()
        for i, lesson in enumerate(schedule, start=1):
            if lesson is not None:
                entry = day_model(
                    num_of_lesson=i,
                    name_of_lesson=lesson['name_of_lesson'],
                    lesson_room=lesson['lesson_room'],
                    teacher_name=lesson['teacher_name'],
                    group_id=group.id,
                    is_upper=is_upper,
                    subgroup='Основна'
                )
                session.add(entry)
        session.commit()

def fill_schedule(session: Session):
    groups = session.query(Group).all()
    for group in groups:
        for day_model in [Monday, Tuesday, Wednesday, Thursday, Friday]:
            if random.randint(1,20)==13:  # Випадковий вихідний день
                continue
            fill_schedule_for_day(session, day_model, group)

def fill_time_schedule(session: Session):
    for lesson in time_schedule:
        entry = Time(
            num_of_lesson=lesson['num_of_lesson'],
            time_of_begin=lesson['time_of_begin'],
            time_of_end=lesson['time_of_end']
        )
        session.add(entry)
    session.commit()

def clear_week_days(session: Session):
    session.query(Monday).delete()
    session.query(Tuesday).delete()
    session.query(Wednesday).delete()
    session.query(Thursday).delete()
    session.query(Friday).delete()
    session.query(Time).delete()
    session.commit()


if __name__ == "__main__":
    from sql.database import SessionLocal
    session = SessionLocal()
    clear_week_days(session)
    fill_time_schedule(session)
    fill_schedule(session)
    print('All done!')