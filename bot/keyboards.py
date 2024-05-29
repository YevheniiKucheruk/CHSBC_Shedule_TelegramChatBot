import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telebot.types as types
from bot.information import speciality_list
main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(types.KeyboardButton(text='Показати розклад'),types.KeyboardButton(text='Показати мою інформацію'),types.KeyboardButton(text='Налаштування'))

speciality_kb = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=3)
for i in range(0,len(speciality_list),2):
    if i + 1 < len(speciality_list):
        speciality_kb.add(types.KeyboardButton(text=f'{speciality_list[i]}'), types.KeyboardButton(text=f'{speciality_list[i+1]}'))
    else:
        speciality_kb.add(types.KeyboardButton(text=f'{speciality_list[i]}'))

start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='/start'))

settings_kb = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=3)
settings_kb.add(types.KeyboardButton(text='Налаштувати спеціальність'),types.KeyboardButton(text='Налаштувати групу'),types.KeyboardButton(text='Налаштувати сповіщення'))
settings_kb.add(types.KeyboardButton(text='Назад'))
def generate_group_keyboard(List):
    groups = List
    group_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for group in groups:
        group_kb.add(types.KeyboardButton(text=group.name_of_group))
    return group_kb

def generete_notification_keyboard(is_notificated):
    notification_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_notificated == True:
        notification_kb.add(types.KeyboardButton(text='Вимкнути сповіщення'),types.KeyboardButton(text='Налаштувати час сповіщення'))
        notification_kb.add(types.KeyboardButton(text='Назад до налаштувань'))
    elif is_notificated == False:
        notification_kb.add(types.KeyboardButton(text='Увімкнути сповіщення'))
        notification_kb.add(types.KeyboardButton(text='Назад до налаштувань'))
    return notification_kb

show_shedule_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
show_shedule_kb.add(types.KeyboardButton(text='Показати розклад на сьогоднішній день'),types.KeyboardButton(text='Показати розклад на тиждень'),types.KeyboardButton(text='Показати розклад дзвінків'),types.KeyboardButton(text='Показати який тиждень'))
show_shedule_kb.add(types.KeyboardButton(text='Назад'))