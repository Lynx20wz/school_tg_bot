import asyncio
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from typing import Union, Tuple, Optional

from aiogram import Dispatcher, Bot, F, types
from aiogram.filters.command import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from dotenv import load_dotenv
from loguru import logger

import parser_school as ps

log_format = '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'

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

DB_PATH = '../temp/DataBase.db'

bot = Bot(os.getenv('API_BOT'))
dp = Dispatcher()

class user_class:
    users = []

    def __init__(
        self, username: str, userid: int, debug: bool = False, setting_dw: bool = False, setting_notification: bool = True, homework_id: int = None
        ):
        """
        Инициализирует объект user_class.

        :param username: Имя пользователя.
        :param userid: ID пользователя.
        :param debug: Флаг отладки.
        :param setting_dw: Флаг настройки уведомлений.
        :param setting_notification: Флаг уведомлений.
        """
        self.username: str = username
        self.userid: int = userid
        with sqlite3.connect(db.path) as database:
            database.row_factory = sqlite3.Row
            cursor = database.cursor()
            while True:
                cursor.execute('SELECT * FROM users WHERE userid = ?', (self.userid,))
                result = dict(cursor.fetchone())
                if result is not None:
                    debug = result.get('debug')
                    setting_dw = result.get('setting_dw')
                    setting_notification = result.get('setting_notification')
                    break
                else:
                    db.add_user((username, userid, setting_dw, setting_notification, debug))

        self.debug: bool = debug
        self.setting_dw: bool = setting_dw
        self.setting_notification: bool = setting_notification
        self.data = (username, userid, setting_dw, setting_notification, debug)

        # Следующий код проверяет есть ли данный пользователь в массиве, если есть обновляет настройки пользователя в массиве
        existing_user = self.get_user_from_massive(username, 2)
        if existing_user:
            existing_user.debug = debug
            existing_user.setting_dw = setting_dw
            existing_user.setting_notification = setting_notification
        else:
            self.users.append(self)


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
            async def wrapped(message: Union[Message, user_class], *args):
                if isinstance(message, user_class):
                    user = message
                else:
                    existing_user = user_class.get_user_from_massive(message.from_user.username, 2)
                    if existing_user:
                        user = existing_user
                    else:
                        user_db = db.get_user(message.from_user.username)
                        logger.debug(f'{user_db} - {func.__name__}')
                        user = None
                        if user_db:
                            user = user_class(
                                    message.from_user.username,
                                    message.from_user.id,
                                    user_db.get('debug', False),
                                    user_db.get('setting_dw', True),
                                    user_db.get('setting_notification', True),
                                    user_db.get('homework')
                            )

                return await func(message=message, user=user, *args)
            return wrapped
        return wrapper

    def save_settings(
        self, database: 'BaseDate', setting_dw: bool = None, setting_notification: bool = None, debug: bool = None, save_db: bool = False
        ):
        """
        Сохраняет настройки пользователя.

        :param database: База данных
        :param setting_dw: Флаг настройки уведомлений.
        :param setting_notification: Флаг уведомлений.
        :param debug: Флаг отладки.
        :param save_db: Если True, то настройки будут обновленный не только в массиве пользователей,
        а также и в БД.

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

        if save_db:
            with sqlite3.connect(database.path) as db:
                cursor = db.cursor()
                cursor.execute(
                        'UPDATE users SET debug = ?, setting_dw = ?, setting_notification = ? WHERE username = ?',
                        (self.debug, self.setting_dw, self.setting_notification, self.username)
                    )

            logger.info(f'Новые настройки пользователя {self.username} сохранены!')


class BaseDate:
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
            db.row_factory = sqlite3.Row
            cursor = db.cursor()

            if username is not None:
                cursor.execute(
                        """
                        SELECT * FROM users WHERE username = ?
                        """, (username,)
                )
                user = cursor.fetchone()

                if user: return dict(user)
            else:
                cursor.execute(
                        """
                        SELECT * FROM users
                        """, (username,)
                )

                users = cursor.fetchall()
                return [dict(user) for user in users]

    def get_homework(self, user) -> tuple:
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()

            cursor.execute(
                '''
                            SELECT hc.timestamp, hc.cache
                            FROM users u
                            INNER JOIN homework_cache hc ON hc.id = u.homework_id
                            WHERE u.username = ?;
                            ''', (user.username,)
                )

            return cursor.fetchone() if cursor is not None else None

    def set_homework(self, user: 'user_class', homework: dict):
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            homework_str = json.dumps(homework, ensure_ascii=False)
            cursor.execute('SELECT * FROM homework_cache WHERE cache = ?', (homework_str,))
            result = cursor.fetchone()
            if result:
                cursor.execute('UPDATE users SET homework_id = ? WHERE username = ?', (result.get('id'), user.username))
            else:
                cursor.execute(
                    'INSERT INTO homework_cache (timestamp, cache) VALUES (?, ?)',
                    (datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M'), homework_str)
                    )
                cursor.execute('UPDATE users SET homework_id = ? WHERE username = ?', (cursor.lastrowid, user.username))


def main_button(user):
    btns = [
        [
            KeyboardButton(text='Расписание 📅'),
            KeyboardButton(text='Домашнее задание 📓')
        ],
        [
            KeyboardButton(text='Соц. сети класса 💬'),
            KeyboardButton(text='Настройки ⚙️')
        ],
    ]
    if user and user.debug:
        btns.append([KeyboardButton(text='Команды дебага')])
    murkup = ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)
    logger.debug('Вызываю кнопки клавиатуры')
    return murkup


async def restart(database):
    """
    Перезапускает бота и отправка оповещение каждому пользователю из файла кэша
    """
    with sqlite3.connect(database.path) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.executescript(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    userid INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    debug INTEGER(1) DEFAULT 0,
                    setting_dw INTEGER(1) DEFAULT 0,
                    setting_notification INTEGER(1) DEFAULT 0,
                    login VARCHAR,
                    password VARCHAR,
                    homework_id INTEGER, FOREIGN KEY (homework_id) REFERENCES homework_cache(id)
                );
                CREATE TABLE IF NOT EXISTS homework_cache (
                    id INTEGER PRIMARY KEY,
                    timestamp INTEGER,
                    cache TEXT 
                );
                '''
        )

        cursor.execute('SELECT * FROM users')
        # noinspection PyTypeChecker
        users = list(map(dict, cursor.fetchall()))

        if users:
            for user in users:
                murkup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')]])
        await bot.send_message(
                chat_id=user.get('userid'), text='Бот вновь запущен!\nДля лучшего опыта использования не будет лишним ввести команду /start',
                disable_notification=user.get('setting_notification'), reply_markup=murkup
        )

        logger.debug('Бот рестарт!')



# СТАРТ!
@dp.message(F.text, Command("start"))
@user_class.get_user()
async def start(message: types.Message, user):
    logger.info(f'Бота запустили ({message.from_user.username})')
    # user_class(db, message.from_user.username, message.from_user.id)
    with open('../Логирование.png', 'rb') as file:
        await message.answer_photo(
                photo=BufferedInputFile(file.read(), filename='Логирование'),
                caption='''Привет. Этот бот создан для вашего удобства и комфорта! Здесь вы можете глянуть расписание, дз, и т.д. Найдёте ошибки сообщите: @Lynx20wz)
                \nP.S: Также должен сказать, что в целях отлова ошибок я веду логирование, то есть, я вижу какую функцию вы запустили и ваш никнейм в телеграм (на фото видно).''',
                reply_markup=main_button(user)
        )


@dp.message(F.text == 'Расписание 📅')
async def timetable(message):
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
        await bot.send_photo(message.chat.id, BufferedInputFile(file.read(), filename='Расписание'), caption=output, parse_mode='Markdown')


@dp.message(F.text == 'Домашнее задание 📓')
@user_class.get_user()
async def homework(message: Message, user: user_class) -> None:
    """
    Высылает текст домашнего задания в соответствии с настройками пользователя.

    :param message: Полученное сообщение.
    :param user: Объект пользователя.
    """

    logger.info(f'Вызвана домашка ({message.from_user.username})')
    link: bool = False

    msg = message.answer('Ожидайте... ⌛')
    with sqlite3.connect(db.path) as db_con:
        cursor = db_con.cursor()
        result = cursor.execute('SELECT login, password FROM users WHERE username = ?', (user.username,)).fetchone()
        if all(value is None for value in result):
            await registration_user(message, user)
            return
        else:
            login, password = result

    pre_hk = db.get_homework(user)
    if pre_hk is not None and datetime.now() - datetime.strptime(pre_hk[0], '%Y-%m-%d %H:%M') < timedelta(hours=1):
        hk = json.loads(pre_hk[1])
    elif pre_hk is None:
        try:
            hk = ps.full_parse(login, password)
        except ValueError as e:
            logger.info('Произошла ошибка!')
            await message.answer(text=f'{e}')
            await registration_user(message, user)
            return
        db.set_homework(user, hk)
        logger.info('Домашка была обновлена')

    output = ''
    if user.setting_dw:  # Если setting_dw равен True, выводим на всю неделю
        for i, one_day in enumerate(hk.values(), start=1):
            day_of_week = ps.get_weekday(i)
            output += f'\n*{day_of_week}*:\n'
            for number_lesson, lesson in enumerate(one_day, start=1):
                output += f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
                if 'https://' in lesson[2]:
                    link = True
        output += f'-------------------------------\nВсего задано уроков: {sum(len(day) for day in hk.values())}'
    else:  # Если False то на один день
        today_index = datetime.now().isoweekday()

        if today_index in [5, 6, 7]:
            next_day_index = 1
        else:
            next_day_index = today_index + 1

        day_of_week = ps.get_weekday(next_day_index)
        output += f'\n*{day_of_week}*:\n'
        one_day = hk.get(day_of_week)

        logger.debug(f'{next_day_index} - {today_index}) {one_day}')
        for number_lesson, lesson in enumerate(one_day, start=1):
            output += f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
            if 'https://' in lesson[2]:
                link = True
        output += f'-------------------------------\nВсего задано уроков: {len(one_day)}'
    await bot.delete_message(message.chat.id, msg.id)
    if link:
        murkup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Бот для решения ЦДЗ', url='https://t.me/CDZ_AnswersBot')]])
        await message.answer(output, parse_mode="Markdown", reply_markup=murkup, disable_notification=user.setting_notification)
    else:
        await message.answer(output, parse_mode="Markdown", disable_notification=user.setting_notification)


async def registration_user(message, user):
    await message.answer(
            message.chat.id,
            'Для доступа к домашнему заданию нужно зарегистрироваться! Введите пожалуйста свой логин для входа в школьный портал (госуслуги)'
    )
    # dp.register_next_step_handler(message, get_password, user)


async def get_password(message, user):
    login = message.text
    if login and re.match(r'^[\w.-]+@[\w.-]+$', login):
        await message.answer(
                message.chat.id,
                'Теперь введите свой пароль'
        )
        # dp.register_next_step_handler(message, end_registration, user, login)
    else:
        await message.answer(
                message.chat.id,
                'Некорректный логин. Пожалуйста, введите ваш логин снова.'
        )
        await registration_user(message, user)


async def end_registration(message, user, login):
    password = message.text
    # Здесь можно добавить логику для проверки логина и пароля
    # Например, сохранить их в базе данных или проверить их действительность
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            '''
                    UPDATE users SET login = ?, password = ? WHERE username = ?
                    ''', (login, password, user.username)
            )
    await message.answer(
            message.chat.id,
            f'Спасибо, {user.username}, вы зарегистрированы! Ваш пароль сохранён.',
            reply_markup=main_button(user)
    )


@dp.message(F.text == 'Соц. сети класса 💬')
async def social_networks(message):
    murkup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Оф. группа', url='https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg'),
                    InlineKeyboardButton(text='Подполка', url='https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo')
                ],
            ]
    )
    await message.answer(
            text='Конечно! Держи:\n\nОфициальная группа в WhatsApp: https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg (создатель @Lynx20wz)\nПодпольная группа в WhatsApp: https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo (создатель @Juggernaut_45)\n\n Если ссылки не работают обратиться к @Lynx20wz)',
            reply_markup=murkup
        )


# Settings
def make_setting_button(user):
    return ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[
                [
                    KeyboardButton(text='Выдача на неделю' if user.setting_dw else 'Выдача на день'),
                    KeyboardButton(text='Уведомления вкл.' if user.setting_notification else 'Уведомления выкл.')
                ],
                [KeyboardButton(text='Назад')],
            ]
    )


@dp.message(F.text == 'Настройки ⚙️')
@user_class.get_user()
async def settings(message: Message, user):
    logger.info(f'Вызваны настройки ({message.from_user.username})')
    murkup = make_setting_button(user)
    await message.answer(
            text='''
Настройки:\n\n*Выдача на день\\неделю:*\n\t1) *"Выдача на день":* будет высылаться домашнее задание только на завтра.
В пятницу, субботу и воскресенье будет высылаться домашнее задание на понедельник.\n\t
2) *"Выдача на неделю":* Будет высылаться домашнее задание на все оставшиеся дни недели.\n\n*Уведомления:*\n\t
1) *"Уведомления вкл.":* включает звук уведомлений для каждого сообщения.\n\t
2) *"Уведомления выкл.":* отключает звук уведомления для каждого сообщения.
        ''',
        reply_markup=murkup, parse_mode='Markdown', disable_notification=user.setting_notification
    )


@dp.message(F.text.in_(['Выдача на неделю', 'Выдача на день']))
@user_class.get_user()
async def change_delivery(message, user):
    if message.text == 'Выдача на неделю':
        user.setting_dw = False
    elif message.text == 'Выдача на день':
        user.setting_dw = True
    murkup = make_setting_button(user)
    user.save_settings(db, setting_dw=user.setting_dw)
    logger.info(f'Изменены настройки выдачи ({message.from_user.username} - {user.setting_dw} ({user.data}))')
    await message.answer('Настройки успешно изменены!', reply_markup=murkup, disable_notification=user.setting_notification)


@dp.message(F.text.in_(['Уведомления вкл.', 'Уведомления выкл.']))
@user_class.get_user()
async def change_notification(message, user):
    if message.text == 'Уведомления вкл.':
        user.setting_notification = False
    elif message.text == 'Уведомления выкл.':
        user.setting_notification = True
    murkup = make_setting_button(user)
    user.save_settings(db, setting_notification=user.setting_notification)
    logger.info(f'Изменены настройки уведомлений ({message.from_user.username} - {user.setting_notification} ({user.data}))')
    await message.answer('Настройки успешно изменены!', reply_markup=murkup, disable_notification=user.setting_notification)


@dp.message(F.text == 'Назад')
@user_class.get_user()
async def exit_settings(message, user):
    logger.debug(f'{user.setting_dw} - {user.setting_notification}')
    logger.info(f'Вышел из настроек ({message.from_user.username})')
    user.save_settings(db, user.setting_dw, user.setting_notification, user.debug, True)
    await message.answer('Главное меню', reply_markup=main_button(user), disable_notification=user.setting_notification)


# @dp.message(F.text)
# @user_class.get_user()
# async def unknown_command(message, user):
#     logger.error(f'Вызвана несуществующая команда! ({message.from_user.username}):\n"{message.text}"')
#     await message.answer(
#             "Извините, нет такой команды. Пожалуйста, используйте доступные кнопки или команды.",
#             disable_notification=user.setting_notification
#         )

async def main():
    from debug_handlers import debug_router
    debug_router.message.filter(F.chat.id == ADMIN_ID)
    dp.include_router(debug_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await restart(database=db)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()

# Запуск бота
db = BaseDate(DB_PATH)
if __name__ == '__main__':
    with open('../schedule.json', 'r', encoding='utf-8') as file:
        timetable_dict = json.load(file)
    asyncio.run(main())
