import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Union, Tuple, Optional

import telebot
from dotenv import load_dotenv
from loguru import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message

import parser_school as ps

log_format = '{time:H:mm:ss} | "{function}" | {line} | <level>{level}</level> | {message}'

logger.remove()
logger.add(
        sink=sys.stdout,
        level='DEBUG',
        format=log_format,
)
logger.add(
        sink='..//temp//log.log',
        level='INFO',
        mode='a',
        format=log_format,
)

load_dotenv()

API_BOT = os.getenv('API_BOT')
ADMIN_ID = int(os.getenv('MY_ID'))

bot = telebot.TeleBot(API_BOT)


class user_class:
    users = []

    def __init__(self, username: str, userid: int, debug: bool = False, setting_dw: bool = False, setting_notification: bool = True):
        """
        Инициализирует объект user_class.

        :param username: Имя пользователя.
        :param userid: ID пользователя.
        :param debug: Флаг отладки.
        :param setting_dw: Флаг настройки уведомлений.
        :param setting_notification: Флаг уведомлений.
        """
        self.data = (username, userid, setting_dw, setting_notification, debug)
        self.username: str = username
        self.userid: int = userid
        self.debug: bool = debug
        self.setting_dw: bool = setting_dw
        self.setting_notification: bool = setting_notification

        # Следующий код проверяет есть ли данный пользователь в массиве, если есть обновляет настройки пользователя в массиве
        existing_user = self.get_user_from_massive(username, 2)
        if existing_user:
            existing_user.debug = debug
            existing_user.setting_dw = setting_dw
            existing_user.setting_notification = setting_notification
        else:
            self.users.append(self)

        # Вызов метода user_record для того чтобы записать пользователя в файл кэша
        db.add_user(self.data)
        # cache.user_record(self)

    @classmethod
    def get_user_from_massive(cls, username: str, mode: int = 1) -> Optional[Union[Tuple[str, int, bool, bool, bool], 'user_class', int]]:
        """
        Получает пользователя из списка пользователей.

        :param username: Имя пользователя.
        :param mode: Режим возвращаемых данных.
        :return: Возвращает данные пользователя из массива users в зависимости от режима.
         Если пользователь не найден в массиве, то None.
        """
        for i, user in enumerate(cls.users):
            if user.username == username:
                match mode:
                    case 1:
                        return user.data
                    case 2:
                        return user
                    case 3:
                        return i
        return None

    @staticmethod
    def get_user():
        """
        Возвращает пользователя из кэша.
        :return: Возвращает функцию-обёртку для получения пользователя.
        """

        def wrapper(func):
            def wrapped(message: Union[Message, user_class], *args, **kwargs):
                if type(message) is user_class:
                    user = message
                else:
                    existing_user = user_class.get_user_from_massive(message.from_user.username, 2)
                    if existing_user:
                        user = existing_user
                    else:
                        user_db = db.get_user(message.from_user.username)
                        user = None
                        if user_db:
                            user = user_class(
                                    message.from_user.username,
                                    message.from_user.id,
                                    user_db.get('debug', False),
                                    user_db.get('setting_dw', True),
                                    user_db.get('setting_notification', True)
                            )
                return func(message=message, user=user, *args, **kwargs)

            return wrapped

        return wrapper

    def save_settings(
        self, database: 'DataBase', setting_dw: bool = None, setting_notification: bool = None, debug: bool = None, save_cache: bool = False
        ):
        """
        Сохраняет настройки пользователя.

        :param database: База данных
        :param setting_dw: Флаг настройки уведомлений.
        :param setting_notification: Флаг уведомлений.
        :param debug: Флаг отладки.
        :param save_cache: Если True, то настройки будут обновленный не только в массиве пользователей,
        а также и в файле кэша.

        :return: Обновлённый файл кэша
        """
        if setting_dw is None:
            setting_dw = self.setting_dw
        if setting_notification is None:
            setting_notification = self.setting_notification
        if debug is None:
            debug = self.debug

        self.setting_dw = setting_dw
        self.setting_notification = setting_notification
        self.debug = debug

        user_index = user_class.get_user_from_massive(self.username, 3)
        if user_index is not None:
            user_class.users[user_index].setting_dw = setting_dw
            user_class.users[user_index].setting_notification = setting_notification
            user_class.users[user_index].debug = debug

        if save_cache:
            with sqlite3.connect(database.path) as db:
                cursor = db.cursor()
                cursor.execute(
                        'UPDATE users SET debug = ?, setting_dw = ?, setting_notification = ? WHERE username = ?',
                        (self.debug, self.setting_dw, self.setting_notification, self.username)
                    )

            logger.info(f'Новые настройки пользователя {self.username} сохранены!')

class DataBase:
    def __init__(self, path: str):
        self.path = path

    def add_user(self, user: tuple):
        with sqlite3.connect(self.path) as db:
            cursor = db.cursor()

            cursor.execute('SELECT userid FROM users WHERE userid = ?', (user[1],))
            if cursor.fetchone():
                return

            cursor.execute(
                    '''
                        INSERT INTO users 
                        (username, userid, debug, setting_dw, setting_notification) 
                        VALUES (?, ?, ?, ?, ?)
                        ''', (user[0], user[1], user[2], user[3], user[4])
            )

    def get_user(self, username: str = None) -> dict[str, bool | str | int] | list[dict[str, bool | str | int]]:
        with sqlite3.connect(self.path) as db:
            cursor = db.cursor()

            if username is not None:
                cursor.execute(
                        """
                        SELECT * FROM users WHERE username = ?
                        """, (username,)
                )

                user = cursor.fetchone()

                if user:
                    return dict(zip([column[0] for column in cursor.description], user))
            else:
                cursor.execute(
                        """
                        SELECT * FROM users
                        """, (username,)
                )

                users_db = cursor.fetchall()
                return [dict(zip([column[0] for column in cursor.description], user)) for user in users_db]

    def get_time_homework_cache(self, id_cache):
        with sqlite3.connect(self.path) as db:
            cursor = db.cursor()
            cursor.execute('SELECT ')


@user_class.get_user()
def main_button(user, message):
    murkup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Расписание 📅')
    button2 = KeyboardButton('Домашнее задание 📓')
    button3 = KeyboardButton('Соц. сети класса 💬')
    button4 = KeyboardButton('Настройки ⚙️')
    murkup.add(button1, button2, button3, button4)
    if user and user.debug:
        button5 = KeyboardButton('Команды дебага')
        murkup.add(button5)
    return murkup


def restart(database):
    """
    Перезапускает бота и отправка оповещение каждому пользователю из файла кэша
    """
    with sqlite3.connect(database.path) as db:
        cursor = db.cursor()
        cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    userid INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    debug INTEGER DEFAULT 0,
                    setting_dw INTEGER DEFAULT 0,
                    setting_notification INTEGER DEFAULT 0,
                    homework INTEGER, FOREIGN KEY (homework) REFERENCES homework_cache(id)
                );
                '''
        )

        cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS homework_cache (
                    id INTEGER PRIMARY KEY ,
                    cache TEXT 
                );
                '''
        )

        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        try:
            for user in users:
                user_dict = dict(zip([column[0] for column in cursor.description], user))
                # logger.debug(user_dict)
                user_r = user_class(
                        user_dict.get('username'), user_dict.get('user_id'),
                        setting_dw=user_dict.get('setting_dw'),
                        setting_notification=user_dict.get('setting_notification'),
                        debug=user_dict.get('debug')
                )
                murkup = ReplyKeyboardMarkup()
                button1 = KeyboardButton('/start')
                murkup.add(button1)
                # bot.send_message(user.get('chat_id'), 'Бот вновь запущен!\nДля лучшего опыта использования не будет лишним ввести команду /start', disable_notification=user.setting_notification, reply_markup=murkup)
        except AttributeError:
            pass


# СТАРТ!
@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f'Бота запустили ({message.from_user.username})')
    murkup = main_button(message=message)
    user_class(message.from_user.username, message.from_user.id)
    with open('../Логирование.png', 'rb') as file:
        bot.send_photo(
                message.chat.id,
                photo=file,
                caption='''
Привет. Этот бот создан для вашего удобства и комфорта! Здесь вы можете глянуть расписание, дз, и т.д.
Найдёте ошибки сообщите: @Lynx20wz )\n\nP.S: Также должен сказать, что в целях отлова ошибок я веду логирование, то есть,
я вижу какую функцию вы запустили и ваш никнейм в телеграм (на фото видно).
                ''',
                reply_markup=murkup
        )


@bot.message_handler(func=lambda message: message.text == 'Расписание 📅')
def timetable(message):
    day_of_week = datetime.now().isoweekday()
    if day_of_week in [5, 6, 7]:
        name_of_day = ps.get_weekday(1)
    else:
        name_of_day = ps.get_weekday(day_of_week + 1)
    output = f'*{name_of_day} расписание*:\n'
    logger.debug(name_of_day)
    for i, lesson in enumerate(timetable_dict.get('schedule').get(name_of_day), 1):
        lesson_subject = timetable_dict.get('subjects').get(lesson[0])
        lesson_subjects = ', '.join(lesson_subject)
        if lesson_subjects == '':
            lesson_subjects = 'Предметы не нужны!'
        output += f'{i}) {lesson[0]} ({lesson[1]}) - {lesson_subjects}\n'
    logger.info(f'Вызвано расписание ({message.from_user.username})')
    output += f'-------------------------------\nИтого:\nТетрадей: {output.count('тетрадь')}\nУчебников: {output.count('учебник')}'
    with open('D:\\System folder\\Pictures\\Расписание 8 класс.png', 'rb') as file:
        bot.send_photo(message.chat.id, file, caption=output, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Домашнее задание 📓')
@user_class.get_user()
def homework(message: Message, user: user_class) -> None:
    """
    Высылает текст домашнего задания в соответствии с настройками пользователя.

    :param message: Полученное сообщение.
    :param user: Объект пользователя.
    """
    # TODO: Убрать строку снизу
    bot.send_message(message.chat.id, 'Временно это функция не работает 😥(')

    logger.info(f'Вызвана домашка ({message.from_user.username})')
    # link: bool = False

    # if datetime.now() - datetime.strptime(cache.time, '%Y-%m-%d-%H:%M:%S') < timedelta(minutes=45) and cache.cache.get('homework'):
    #
    # else:
    #     logger.info('Домашка была обновлена')
    #     hk = ps.full_parse()
    #     cache.homework_record(hk)
#
#     output = ''
#     if user.setting_dw:  # Если setting_dw равен True, выводим на всю неделю
#         for i, one_day in enumerate(hk.values(), start=1):
#             day_of_week = ps.get_weekday(i)
#             output += f'\n*{day_of_week}*:\n'
#             for number_lesson, lesson in enumerate(one_day, start=1):
#                 output += f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
#                 if 'https://' in lesson[2]:
#                     link = True
#         output += f'-------------------------------\nВсего задано уроков: {sum(len(day) for day in hk.values())}'
#     else:  # Если False то на один день
#         today_index = datetime.now().isoweekday()
#
#         if today_index in [5, 6, 7]:
#             next_day_index = 1
#         else:
#             next_day_index = today_index + 1
#
#         day_of_week = ps.get_weekday(next_day_index)
#         output += f'\n*{day_of_week}*:\n'
#         one_day = hk.get(day_of_week)
#
#         logger.debug(f'{next_day_index} - {today_index}) {one_day}')
#         for number_lesson, lesson in enumerate(one_day, start=1):
#             output += f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
#             if 'https://' in lesson[2]:
#                 link = True
#         output += f'-------------------------------\nВсего задано уроков: {len(one_day)}'
#     if link:
#         murkup = InlineKeyboardMarkup()
#         button1 = InlineKeyboardButton(text='Бот для решения ЦДЗ', url='https://t.me/CDZ_AnswersBot')
#         murkup.add(button1)
#         bot.send_message(message.chat.id, output, parse_mode="Markdown", reply_markup=murkup, disable_notification=user.setting_notification)
#     else:
#         bot.send_message(message.chat.id, output, parse_mode="Markdown", disable_notification=user.setting_notification)


@bot.message_handler(func=lambda message: message.text == 'Соц. сети класса 💬')
def social_networks(message):
    murkup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton('Оф. группа', 'https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg')
    button2 = InlineKeyboardButton('Подполка', 'https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo')
    murkup.add(button1, button2)
    bot.send_message(
        message.chat.id,
            'Конечно! Держи:\n\nОфициальная группа в WhatsApp: https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg (создатель @Lynx20wz)\nПодпольная группа в WhatsApp: https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo (создатель @Juggernaut_45)\n\n Если ссылки не работают обратиться к @Lynx20wz)',
        reply_markup=murkup
        )


# Settings
def make_setting_button(user):
    murkup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Назад')
    button2 = KeyboardButton('Выдача на неделю' if user.setting_dw else 'Выдача на день')
    button3 = KeyboardButton('Уведомления вкл.' if user.setting_notification else 'Уведомления выкл.')
    murkup.add(button1, button2, button3)
    return murkup


@bot.message_handler(func=lambda message: message.text == 'Настройки ⚙️')
@user_class.get_user()
def settings(message, user):
    logger.info(f'Вызваны настройки ({message.from_user.username})')
    murkup = make_setting_button(user)
    bot.send_message(
        message.chat.id,
            '''
    Настройки:\n\n*Выдача на день\\неделю:*\n\t1) *"Выдача на день":* будет высылаться домашнее задание только на завтра.
    В пятницу, субботу и воскресенье будет высылаться домашнее задание на понедельник.\n\t
    2) *"Выдача на неделю":* Будет высылаться домашнее задание на все оставшиеся дни недели.\n\n*Уведомления:*\n\t
    1) *"Уведомления вкл.":* включает звук уведомлений для каждого сообщения.\n\t
    2) *"Уведомления выкл.":* отключает звук уведомления для каждого сообщения.
             ''',
        reply_markup=murkup, parse_mode='Markdown', disable_notification=user.setting_notification
        )


@bot.message_handler(func=lambda message: message.text in ['Выдача на неделю', 'Выдача на день'])
@user_class.get_user()
def change_delivery(message, user):
    if message.text == 'Выдача на неделю':
        user.setting_dw = False
    elif message.text == 'Выдача на день':
        user.setting_dw = True
    murkup = make_setting_button(user)
    user.save_settings(setting_dw=user.setting_dw)
    logger.info(f'Изменены настройки выдачи ({message.from_user.username} - {user.setting_dw} ({user.data}))')
    bot.send_message(message.chat.id, 'Настройки успешно изменены!', reply_markup=murkup, disable_notification=user.setting_notification)


@bot.message_handler(func=lambda message: message.text in ['Уведомления вкл.', 'Уведомления выкл.'])
@user_class.get_user()
def change_notification(message, user):
    if message.text == 'Уведомления вкл.':
        user.setting_notification = False
    elif message.text == 'Уведомления выкл.':
        user.setting_notification = True
    murkup = make_setting_button(user)
    user.save_settings(setting_notification=user.setting_notification)
    logger.info(f'Изменены настройки уведомлений ({message.from_user.username} - {user.setting_notification} ({user.data}))')
    bot.send_message(message.chat.id, 'Настройки успешно изменены!', reply_markup=murkup, disable_notification=user.setting_notification)


@bot.message_handler(func=lambda message: message.text == 'Назад')
@user_class.get_user()
def exit_settings(message, user):
    logger.debug(f'{user.setting_dw} - {user.setting_notification}')
    logger.info(f'Вышел из настроек ({message.from_user.username})')
    user.save_settings(user.setting_dw, user.setting_notification, True)
    bot.send_message(message.chat.id, 'Главное меню', reply_markup=main_button(message=message), disable_notification=user.setting_notification)


# Debug
@bot.message_handler(func=lambda message: message.text == 'Debug')
@user_class.get_user()
def developer(message, user):
    if message.from_user.id == ADMIN_ID:
        user.debug = True
        user.save_settings(debug=user.debug, save_cache=True, database=db)
        bot.send_message(message.chat.id, f'Удачной разработки, {user.username}! 😉', reply_markup=main_button(message))
        logger.warning(f'{user.username} получил роль разработчика!')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь разработчиком! 😑', reply_markup=main_button(message))
        logger.warning(f'{user.username} пытался получить разработчика')


def make_debug_button():
    murkup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Назад')
    button2 = KeyboardButton('Запрос пользователя')
    button3 = KeyboardButton('Выкл. дебаг')
    murkup.add(button1, button2, button3)
    return murkup


@bot.message_handler(func=lambda message: message.text == 'Команды дебага')
def command_debug(message):
    bot.send_message(message.chat.id, f'Добро пожаловать разработчик, тут все нужные для тебя команды!', reply_markup=make_debug_button())


@bot.message_handler(func=lambda message: message.text == 'Запрос пользователя')
def get_user(message):
    bot.send_message(message.chat.id, f'{db.get_user(message.from_user.username)}')


@bot.message_handler(func=lambda message: message.text == 'Выкл. дебага')
@user_class.get_user()
def remove_debug(message, user):
    user.debug = False
    user.save_settings(debug=user.debug, save_cache=True, database=db)
    bot.send_message(message.chat.id, f'Выключаю дебаг...', reply_markup=main_button(message))
    logger.debug(f'{user.username} отключил роль разработчика.')


@bot.message_handler(func=lambda message: message.text == 'Назад')
@user_class.get_user()
def exit_settings(message, user):
    logger.debug(f'{user.setting_dw} - {user.setting_notification}')
    logger.info(f'Вышел из команд дебага ({message.from_user.username})')
    bot.send_message(message.chat.id, 'Главное меню', reply_markup=main_button(message=message), disable_notification=user.setting_notification)

@bot.message_handler(func=lambda message: message.text)
@user_class.get_user()
def unknown_command(message, user):
    logger.error(f'Вызвана несуществующая команда! ({message.from_user.username}):\n"{message.text}"')
    bot.send_message(
            message.chat.id, "Извините, нет такой команды. Пожалуйста, используйте доступные кнопки или команды.",
            disable_notification=user.setting_notification
        )



# Запуск бота
if __name__ == '__main__':
    db = DataBase('../temp/DataBase.db')
    with open('../schedule.json', 'r', encoding='utf-8') as file:
        timetable_dict = json.load(file)
    restart(database=db)
    bot.polling(none_stop=True)