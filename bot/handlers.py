import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot.keyboards import main_kb,speciality_kb,start_kb,settings_kb,generate_group_keyboard,generete_notification_keyboard,show_shedule_kb
from bot.information import speciality_list
from config import token
import telebot,datetime
from sqlalchemy.orm import sessionmaker
from sql.database import engine, Base, SessionLocal
from sql.db_groups import get_groups_by_speciality,get_group_by_name
from sql.db_shedule import get_call_schedule,get_schedule_for_today,get_schedule_for_week,format_call_schedule,format_schedule,format_week_schedule,get_current_week_type
from sql.db_user import initialize_user, get_user_by_id,update_user_info
from sql.db_time import swap_weeks
from contextlib import contextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
import pytz

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bot = telebot.TeleBot(token)
timezone = pytz.timezone('Europe/Kiev')
scheduler = BackgroundScheduler(timezone = timezone)

def update_week():
    with get_db() as db:
        swap_weeks(db)


def initialize_scheduler():
    job_id = "update_week"
    if not scheduler.get_job(job_id):
        scheduler.add_job(update_week, trigger=CronTrigger(day_of_week='sun', hour=0, minute=0,timezone=timezone), id=job_id)
    elif scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        scheduler.add_job(update_week, trigger=CronTrigger(day_of_week='sun', hour=0, minute=0,timezone=timezone), id=job_id)
    scheduler.start()

def clear_scheduler():
    scheduler.remove_all_jobs()


def update_user_notification_schedule(user_id, reminding_time,message):
    job_id = f"notification_{user_id}"
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        pass
    scheduler.add_job(send_today_schedule, trigger=CronTrigger(timezone=timezone, hour=reminding_time.hour, minute=reminding_time.minute), args=[message], id=job_id)

def the_setting_group(message):
    if is_group_selection(message):
        set_the_group(message)
    else:
        bot.send_message(message.chat.id, 'Такої групи не знайдено! Будь ласка, повторіть процедуру!')
        bot.register_next_step_handler(message, the_setting_group)  

def the_setting_speciality(message):
    bot.send_message(message.chat.id, 'Оберіть, будь ласка, вашу спеціальність', reply_markup=speciality_kb)
    bot.register_next_step_handler(message, handle_speciality_selection) 

def handle_speciality_selection(message):
    if is_speciality_selection(message):
        set_the_speciality(message)
        bot.register_next_step_handler(message, the_setting_group)
    else:
        bot.send_message(message.chat.id, 'Такої спеціальності не знайдено! Будь ласка, повторіть процедуру!')
        bot.register_next_step_handler(message, handle_speciality_selection)

def is_speciality_selection(message):
    text = message.text
    return text in speciality_list

def is_group_selection(message):
    user_id = message.from_user.id
    text = message.text
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            user_speciality = user.speciality
            groups_by_speciality = get_groups_by_speciality(db, user_speciality)
            groups_by_speciality = [i.name_of_group for i in groups_by_speciality]
            return text in groups_by_speciality
    return False

#Даний фрагмент коду описує функцію /start, яка створює новий екземпляр класу User і продовжує його налаштування спеціальності та групи
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    with get_db() as db:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            initialize_user(db, user_id, user_name, None, None, False, "00:00:00")
        else:
            user = db_user
    bot.send_message(message.chat.id, f"Вітаю вас, {message.from_user.first_name}!")
    the_setting_speciality(message)

#Даний фрагмент коду діє на ряду з ф-ю /start і налаштовує спеціальність
@bot.message_handler(func=lambda message: message.text in speciality_list)
def set_the_speciality(message):
    user_id = message.from_user.id
    speciality = message.text.split(' ', 1)[1]
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            update_user_info(db, user_id, speciality=speciality)
            bot.send_message(message.chat.id, f'Вашу спеціальність обрано - {speciality}!\nБудь ласка, оберіть групу: ', reply_markup=generate_group_keyboard(get_groups_by_speciality(db,speciality)))
        else:
            bot.send_message(message.chat.id, 'Будь ласка, почніть з команди /start', reply_markup=start_kb)


@bot.message_handler(func=is_group_selection)
def set_the_group(message):
    user_id = message.from_user.id
    name_of_group = message.text
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            update_user_info(db, user_id, name_of_group=name_of_group)
            bot.send_message(message.chat.id, f'Ваша група вибрана - {name_of_group}!\nЩо ви бажаєте зробити:', reply_markup=main_kb)
        else: 
            bot.send_message(message.chat.id, 'Будь ласка, почніть з команди /start', reply_markup=start_kb)

#Даний фрагмент коду показує інформацію про розклад користувача
@bot.message_handler(func=lambda message: message.text == 'Показати розклад')
def choose_showing_shedule(message):
    bot.send_message(message.chat.id,'Що хочете подивитись:',reply_markup=show_shedule_kb)

@bot.message_handler(func=lambda message: message.text == 'Показати розклад на сьогоднішній день')
def send_today_schedule(message):
    user_id = message.from_user.id
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            group = get_group_by_name(db, user.name_of_group)
            if group is not None:
                today_schedule = get_schedule_for_today(db, group.id)
                formatted_schedule = format_schedule(db, today_schedule)
                if not today_schedule:
                    bot.send_message(message.chat.id, "Сьогодні пар немає, відпочивайте!")
                else:
                    bot.send_message(message.chat.id, f"Розклад на сьогодні:\n{formatted_schedule}")
            else:
                bot.send_message(message.chat.id, 'Групу не знайдено. Будь ласка, налаштуйте групу.', reply_markup=settings_kb)
        else:
            bot.send_message(message.chat.id, 'Будь ласка, почніть з команди /start', reply_markup=start_kb)

@bot.message_handler(func=lambda message: message.text == 'Показати розклад дзвінків')
def send_call_schedule(message):
    with get_db() as db:
        call_schedule = get_call_schedule(db)
        formatted_schedule = format_call_schedule(call_schedule)
        send_long_message(message.chat.id, f"Розклад дзвінків:\n{formatted_schedule}")

@bot.message_handler(func=lambda message: message.text == 'Показати розклад на тиждень')
def send_week_schedule(message):
    user_id = message.from_user.id
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            group_name = user.name_of_group
            week_schedule = get_schedule_for_week(db, get_group_by_name(db,group_name).id)
            formatted_schedule = format_week_schedule(db, week_schedule)
            send_long_message(message.chat.id, f"Розклад на тиждень:\n{formatted_schedule}")
        else:
            bot.send_message(message.chat.id, 'Будь ласка, почніть з команди /start', reply_markup=start_kb)

def send_long_message(chat_id, message):
    max_length = 4096
    for i in range(0, len(message), max_length):
        bot.send_message(chat_id, message[i:i+max_length])


@bot.message_handler(func=lambda message: message.text == 'Показати який тиждень')
def send_current_week_type(message):
    with get_db() as db:
        week_type = get_current_week_type(db)
        if week_type:
            bot.send_message(message.chat.id, f"Зараз {week_type} тиждень.",reply_markup=show_shedule_kb)
        else:
            bot.send_message(message.chat.id, "Не вдалося визначити тип тижня. Будь ласка, спробуйте пізніше.",reply_markup=show_shedule_kb)


@bot.message_handler(func=lambda message: message.text == 'Назад')
def back(message):
    bot.send_message(message.chat.id, 'Що ви бажаєте зробити:', reply_markup=main_kb)



#Даний фрагмент коду показує інфомацію про користувача
@bot.message_handler(func=lambda message: message.text == 'Показати мою інформацію')
@bot.message_handler(commands=['my_info'])
def my_info(message):
    user_id = message.from_user.id
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user:
            remind_info = 'Чи увімкнуте сповіщення - НІ!' if not user.is_get_reminds else f'Чи увімкнуте сповіщення - Так!\n\nВаш час сповіщення - {user.reminding_time}'
            bot.send_message(message.chat.id, f'''Ваша інформація:
                             \nВаша спеціальність - {user.speciality}!
                             \nВаша група - {user.name_of_group}!
        \n{remind_info}''')
        else:
            bot.send_message(message.chat.id, 'Будь ласка, почніть з команди /start', reply_markup=start_kb)

#Даний фрагмент коду буде дозволяти користувачам змінювати їх налаштування
@bot.message_handler(func=lambda message: message.text == 'Налаштування')
@bot.message_handler(commands=['settings'])
def my_settings(message):
    bot.send_message(message.chat.id, 'Вітаю! Що ви бажаєте налаштувати?', reply_markup=settings_kb)

@bot.message_handler(func=lambda message: message.text in ['Налаштувати спеціальність', 'Налаштувати групу', 'Налаштувати сповіщення', 'Назад до налаштувань', 'Назад'])
def set_settings(message):
    if message.text == 'Налаштувати спеціальність':
        the_setting_speciality(message)
    elif message.text == 'Налаштувати групу':
        with get_db() as db:
            user = get_user_by_id(db, message.from_user.id)
            bot.send_message(message.chat.id, 'Будь ласка, оберіть групу:', reply_markup=generate_group_keyboard(get_groups_by_speciality(db, user.speciality)))
            bot.register_next_step_handler(message, handle_group_selection)
    elif message.text == 'Налаштувати сповіщення':
        set_notification(message)
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Що ви бажаєте зробити:', reply_markup=main_kb)
    elif message.text == 'Назад до налаштувань':
        my_settings(message)

def handle_group_selection(message):
    if is_group_selection(message):
        def set_the_group1(message):
            user_id = message.from_user.id
            name_of_group = message.text
            with get_db() as db:
                user = get_user_by_id(db, user_id)
                if user is not None:
                    update_user_info(db, user_id, name_of_group=name_of_group)
                    bot.send_message(message.chat.id, f'Ваша група вибрана - {name_of_group}!\n', reply_markup=main_kb)
                else: 
                    bot.send_message(message.chat.id, 'Будь ласка, почніть з команди /start', reply_markup=start_kb)
        set_the_group1(message)
        bot.send_message(message.chat.id, 'Групу налаштовано успішно!', reply_markup=main_kb)
    else:
        bot.send_message(message.chat.id, 'Такої групи не знайдено! Будь ласка, повторіть процедуру!')
        bot.register_next_step_handler(message, handle_group_selection)

def set_notification(message):
    user_id = message.from_user.id
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            if not user.is_get_reminds:
                bot.send_message(message.chat.id, 'Ваше сповіщення вимкнуте!', reply_markup=generete_notification_keyboard(user.is_get_reminds))
                bot.register_next_step_handler(message, handle_notification_settings)
            else:
                reminding_time_formatted = user.reminding_time.strftime('%H:%M')
                bot.send_message(message.chat.id, f'Ваше сповіщення увімкнене!\nВаший час сповіщення - {reminding_time_formatted}', reply_markup=generete_notification_keyboard(user.is_get_reminds))
                bot.register_next_step_handler(message, handle_notification_settings)

def handle_notification_settings(message):
    user_id = message.from_user.id
    with get_db() as db:
        user = get_user_by_id(db, user_id)
        if user is not None:
            if message.text == 'Увімкнути сповіщення':
                update_user_info(db, user_id, is_get_reminds=True)
                bot.send_message(message.chat.id, f'Ваше сповіщення увімкнене!\nВаший час сповіщення - {user.reminding_time}', reply_markup=generete_notification_keyboard(user.is_get_reminds))
                if user.reminding_time:
                    reminding_time = user.reminding_time
                    update_user_notification_schedule(user_id, reminding_time, message)
                    bot.register_next_step_handler(message, handle_notification_settings)
            elif message.text == 'Вимкнути сповіщення':
                update_user_info(db, user_id, is_get_reminds=False)
                bot.send_message(message.chat.id, 'Ваше сповіщення вимкнуте!', reply_markup=generete_notification_keyboard(user.is_get_reminds))
                job_id = f"notification_{user_id}"
                if scheduler.get_job(job_id):
                    scheduler.remove_job(job_id)
                bot.register_next_step_handler(message, handle_notification_settings)
            elif message.text == 'Налаштувати час сповіщення':
                bot.send_message(message.chat.id, 'Будь ласка, вкажіть час сповіщення у форматі HH:MM(година:хвилина)')
                bot.register_next_step_handler(message, set_reminding_time)
            elif message.text == 'Назад до налаштувань':
                my_settings(message)

def set_reminding_time(message):
    user_id = message.from_user.id
    try:
        reminding_time = message.text
        reminding_time_obj = datetime.datetime.strptime(reminding_time, '%H:%M').time()
        with get_db() as db:
            update_user_info(db, user_id, reminding_time=reminding_time_obj)
            bot.send_message(message.chat.id, f'Час сповіщення встановлено на {reminding_time}', reply_markup=settings_kb)
            update_user_notification_schedule(user_id, reminding_time_obj,message)
    except ValueError:
        bot.send_message(message.chat.id, 'Невірний формат часу. Будь ласка, спробуйте ще раз.')


#Даний фрагмент коду буде повідомляти користувачів, що їх повідомлення, яке не буде у форматі тексту, буде незрозуміле ботові
@bot.message_handler(content_types=['audio','document','photo','pass','video','video_note','voice','location','contact'])
def unsupported_messages(message):
    bot.send_message(message.chat.id,'Ваше повідомлення не зрозуміле!')