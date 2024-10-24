import json
import os
import sys
from datetime import datetime, timedelta
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
CACHE_FILE = '../temp/cache_school_bot.json'

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
        cache.user_record(self)

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
    def get_user(cache: 'cache_class'):
        """
        Возвращает пользователя из кэша.

        :param cache: Объект cache_class.
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
                        user = user_class(
                                message.from_user.username,
                                message.from_user.id,
                                cache.users.get(message.from_user.username).get('debug', False),
                                cache.users.get(message.from_user.username).get('settings').get('setting_dw', True),
                                cache.users.get(message.from_user.username).get('settings').get('setting_notification', True)
                        )
                return func(message=message, user=user, *args, **kwargs)

            return wrapped

        return wrapper

    def save_settings(self, setting_dw: bool = None, setting_notification: bool = None, debug: bool = None, save_cache: bool = False):
        """
        Сохраняет настройки пользователя.

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
            with open(CACHE_FILE, 'r') as file:
                settings_file = json.loads(file.read())
            settings_file.get(self.userid)
            settings_file['users'][self.username]['debug'] = self.debug
            settings_file['users'][self.username]['settings']['setting_dw'] = self.setting_dw
            settings_file['users'][self.username]['settings']['setting_notification'] = self.setting_notification
            with open(CACHE_FILE, 'w') as file:
                json.dump(settings_file, file, indent=4)
            logger.info(f'Новые настройки пользователя {self.username} сохранены!')


class cache_class():
    def __init__(self, cache_restart: bool = False):
        """
        :param cache_restart: если True, то номер запуска в кэше повыситься на один, и время обновиться.
        :return: Объект cache_class, который хранит в себе сам кэш, номер запуска,
         время обновления кэша, пользователей из файла кэша.
        """
        cache = cache_class.cache_read()

        #  методы класса
        self.cache = cache
        self.number_of_starts = cache.get('cache').get('number_of_starts')
        self.time = cache.get('cache').get('time')
        self.users = cache.get('users')

        try:
            self.homework = cache.get('homework')
        except AttributeError:
            self.homework = None

        if cache_restart:
            with open(CACHE_FILE, 'w') as cache_file:
                cache['cache']['number_of_starts'] = self.number_of_starts + 1
                cache['cache']['time'] = str(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
                json.dump(cache, cache_file, indent=4)
            cache_restart = False
            # logger.debug('Кэш обновлён')

    @classmethod
    def cache_read(cls) -> dict:
        """
        Читает файл кэша, если такого нет, то создаёт с базовым содержанием.
        :return: dict c кэшем заполненный из файла кэша или содержанием по умолчанию.
        """
        try:  # если файл кэша есть
            with open(CACHE_FILE, 'r', encoding='utf-8') as cache_file:
                cache = json.loads(cache_file.read())
        except (json.decoder.JSONDecodeError, FileNotFoundError):  # если файла кэша нет
            with open(CACHE_FILE, 'w') as cache_file:
                write_to_file = {'cache': {'number_of_starts': 1, 'time': str(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))}, 'users': {}}
                cache = write_to_file
                json.dump(write_to_file, cache_file, indent=4)

        # logger.info(f'Кэш прочитан {cache}')
        return cache

    @classmethod
    def user_record(cls, a_user: 'user_class') -> None:
        """
        Если пользователь существовал то ничего не происходит. Если не существовал, то заносит a_user в файл кэша

        :param a_user: объект класса user_class
        :return: None | Обновлённый файл кэша
        """
        with open(CACHE_FILE, 'r') as file:
            cache_json = json.loads(file.read())
            # logger.debug(f'{a_user.username} подгрузил файл кэша - {cache_json}')
        try:
            if cache_json.get('users').get(a_user.username) is None:
                raise KeyError
            else:
                logger.info(f'Пользователь {a_user.username} уже создан')
        except (KeyError, AttributeError):
            with open(CACHE_FILE, 'w') as file:
                cache_json['users'][a_user.username] = {'username': a_user.username, 'userid': a_user.userid, 'debug': a_user.debug,
                                                        'settings': {'setting_dw': a_user.setting_dw,
                                                                     'setting_notification': a_user.setting_notification}}
                json.dump(cache_json, file, indent=4)
                logger.info(f'Пользователь {a_user.username} был создан и занесён в кэш!')

    @classmethod
    def homework_record(cls, homework: dict) -> json:
        """
        Записывает домашнее задание в файл кэша

        :param homework: домашнее задание которое нужно записать в файл
        :return: Обновлённый файл кэша
        """
        logger.debug(homework)
        with open(CACHE_FILE, 'r', encoding='utf-8') as file:
            cache_json = json.loads(file.read())
        with open(CACHE_FILE, 'w', encoding='utf-8') as file:
            cache_json['homework'] = homework
            json.dump(cache_json, file, indent=4, ensure_ascii=False)


def main_button():
    murkup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Расписание 📅')
    button2 = KeyboardButton('Домашнее задание 📓')
    button3 = KeyboardButton('Соц. сети класса 💬')
    button4 = KeyboardButton('Настройки ⚙️')
    murkup.add(button1, button2, button3, button4)
    return murkup


def restart():
    """
    Перезапускает бота и отправка оповещение каждому пользователю из файла кэша
    """
    try:
        for user_overkill in cache.cache.get('users').values():
            user = user_class(
                    user_overkill.get('username'), user_overkill.get('user_id'),
                    setting_dw=user_overkill.get('settings').get('setting_dw'),
                    setting_notification=user_overkill.get('settings').get('setting_notification'),
                    debug=user_overkill.get('settings').get('debug')
            )
            murkup = ReplyKeyboardMarkup()
            button1 = KeyboardButton('/start')
            murkup.add(button1)
            # bot.send_message(user_overkill.get('chat_id'), 'Бот вновь запущен!\nДля лучшего опыта использования не будет лишним ввести команду /start', disable_notification=user.setting_notification, reply_markup=murkup)
    except AttributeError:
        pass


# СТАРТ!
@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f'Бота запустили ({message.from_user.username})')
    murkup = main_button()
    user_class(message.from_user.username, message.from_user.id)
    with open('../Логирование.png', 'rb') as file:
        bot.send_photo(
                message.chat.id,
                photo=file,
                caption='Привет. Этот бот создан для вашего удобства и комфорта! Здесь вы можете глянуть расписание, дз, и т.д. Найдёте ошибки сообщите: @Lynx20wz )\n\nP.S: Также должен сказать, что в целях отлова ошибок я веду логирование, то есть, я вижу какую функцию вы запустили и ваш никнейм в телеграм (на фото видно).',
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
@user_class.get_user(cache_class())
def homework(message: Message, user: user_class) -> None:
    """
    Высылает текст домашнего задания в соответствии с настройками пользователя.

    :param message: Полученное сообщение.
    :param user: Объект пользователя.
    """
    logger.info(f'Вызвана домашка ({message.from_user.username})')
    link: bool = False

    if datetime.now() - datetime.strptime(cache.time, '%Y-%m-%d-%H:%M:%S') < timedelta(minutes=45) and cache.cache.get('homework'):
        hk = cache.homework
    else:
        logger.info('Домашка была обновлена')
        hk = ps.full_parse()
        cache.homework_record(hk)

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
    if link:
        murkup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton(text='Бот для решения ЦДЗ', url='https://t.me/CDZ_AnswersBot')
        murkup.add(button1)
        bot.send_message(message.chat.id, output, parse_mode="Markdown", reply_markup=murkup, disable_notification=user.setting_notification)
    else:
        bot.send_message(message.chat.id, output, parse_mode="Markdown", disable_notification=user.setting_notification)


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


@bot.message_handler(func=lambda message: message.text == 'Debug')
@user_class.get_user(cache_class())
def developer(message, user):
    if message.from_user.id == ADMIN_ID:
        user.debug = True
        user.save_settings(debug=user.debug, save_cache=True)
        bot.send_message(message.chat.id, f'Удачной разработки, {user.username}')
        logger.warning(f'{user.username} получил роль разработчика!')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь разработчиком!')
        logger.warning(f'{user.username} пытался получить разработчика')


# Settings
@user_class.get_user(cache_class())
def make_setting_button(user):
    murkup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Назад')
    button2 = KeyboardButton('Выдача на неделю' if user.setting_dw else 'Выдача на день')
    button3 = KeyboardButton('Уведомления вкл.' if user.setting_notification else 'Уведомления выкл.')
    murkup.add(button1, button2, button3)
    return murkup


@bot.message_handler(func=lambda message: message.text == 'Настройки ⚙️')
@user_class.get_user(cache_class())
def settings(message, user):
    logger.info(f'Вызваны настройки ({message.from_user.username})')
    murkup = make_setting_button()
    bot.send_message(
        message.chat.id,
        'Настройки:\n\n*Выдача на день\\неделю:*\n\t1) *"Выдача на день":* будет высылаться домашнее задание только на завтра. В пятницу, субботу и воскресенье будет высылаться домашнее задание на понедельник.\n\t2) *"Выдача на неделю":* Будет высылаться домашнее задание на все оставшиеся дни недели.\n\n*Уведомления:*\n\t1) *"Уведомления вкл.":* включает звук уведомлений для каждого сообщения.\n\t2) *"Уведомления выкл.":* отключает звук уведомления для каждого сообщения.',
        reply_markup=murkup, parse_mode='Markdown', disable_notification=user.setting_notification
        )


@bot.message_handler(func=lambda message: message.text in ['Выдача на неделю', 'Выдача на день'])
@user_class.get_user(cache_class())
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
@user_class.get_user(cache_class())
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
@user_class.get_user(cache_class())
def exit_settings(message, user):
    logger.debug(f'{user.setting_dw} - {user.setting_notification}')
    logger.info(f'Вышел из настроек ({message.from_user.username})')
    user.save_settings(user.setting_dw, user.setting_notification, True)
    bot.send_message(message.chat.id, 'Главное меню', reply_markup=main_button(), disable_notification=user.setting_notification)


@bot.message_handler(func=lambda message: message.text)
@user_class.get_user(cache_class())
def unknown_command(message, user):
    logger.error(f'Вызвана несуществующая команда! ({message.from_user.username})')
    bot.send_message(
        message.chat.id, "Извините, нет такой команды. Пожалуйста, используйте доступные кнопки или команды.",
        disable_notification=user.setting_notification
        )


# Запуск бота
if __name__ == '__main__':
    cache = cache_class(True)
    with open('../schedule.json', 'r', encoding='utf-8') as file:
        timetable_dict = json.load(file)
    restart()
    logger.info(f'------------- Запуск номер: {cache.number_of_starts} -------------')
    bot.polling(none_stop=True)