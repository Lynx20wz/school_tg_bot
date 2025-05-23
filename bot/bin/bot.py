import asyncio
import sys
from datetime import datetime, timedelta

from aiogram import Bot, F, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import (
    Message,
    BufferedInputFile,
)

from bot.bin import (
    API_BOT,
    logger,
    parser,
    main_button,
    social_networks_button,
    make_setting_button,
    get_weekday,
    ExpiredToken,
    NoToken,
    ServerError,
)
from bot.classes import BaseDate, UserClass, Homework
from bot.classes.Homework import StudyDay
from bot.handlers import Handlers

bot = Bot(API_BOT)
dp = Dispatcher()
db = BaseDate()

MAX_WIDTH_MESSAGE = 33


async def _exception_handler(
    user: UserClass, message: Message, function: callable, **kwargs
):
    """Handles exceptions that may occur during the execution of a function.

    Args:
        user (UserClass): A user for which the function is called
        message (Message): A message for which the function is called
        function (callable): The function to be called.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Either notify the user that an exception has happened
        or return the result of the function completion
    """
    try:
        if not user.token:
            raise NoToken()
        if 'token' not in kwargs:
            kwargs['token'] = user.token
        result = function(**kwargs)
    except (ExpiredToken, NoToken, ServerError) as e:
        logger.warning(f'{function.__name__} | {user.username}: Произошла ошибка: {e}')
        await message.answer(e.args[0])
        return None
    return result


# START!
@dp.message(F.text, Command('start'))
@UserClass.get_user()
async def start(message: Message, user: UserClass):
    logger.info(f'Бота запустили ({message.from_user.username})')
    with open('bot/loging.png', 'rb') as file:
        await message.answer_photo(
            photo=BufferedInputFile(file.read(), filename='Логирование'),
            caption="""Привет. Этот бот создан для вашего удобства и комфорта! Здесь вы можете глянуть расписание, дз, и т.д. Найдёте ошибки сообщите: @Lynx20wz)
                \nP.S: Также должен сказать, что в целях отлова ошибок я веду логирование, то есть, я вижу какую функцию вы запустили и ваш никнейм в телеграм (на фото видно).""",
            reply_markup=main_button(user),
        )


@dp.message(F.text == 'Оценки 📝')
@UserClass.get_user()
async def marks(message: Message, user: UserClass):
    logger.info(f'Вызваны оценки ({message.from_user.username})')
    response = await _exception_handler(user, message, parser.get_marks, student_id = user.student_id)
    if not response:
        return

    if user.setting_dw:
        output = f'*Оценки за неделю ({response["date"]["begin_date"].strftime("%d.%m")} - {response["date"]["end_date"].strftime("%d.%m")}):*\n'

        if response['days']:
            for name_of_day, marks in response['days'].items():
                if not marks:
                    continue
                output += (
                    f'*{name_of_day}:*\n\t├ '
                    + '\n\t├ '.join(f'*{mark[0]}*: {mark[1]}' for mark in marks[:-1])
                    + f'\n\t└ *{marks[-1][0]}*: {marks[-1][1]}'
                    + '\n\n'
                )
        else:
            output += '\t└ Оценки за этот период отсутствуют'
    else:
        today = get_weekday(datetime.now().isoweekday())
        output = (
            f'*Оценки за сегодняшний день ({today}, {response["date"]["begin_date"].strftime("%d.%m")}):*\n'
        )

        if response['days']:
            output += '\t├ ' + '\n\t├ '.join(f'*{mark[0]}*: {mark[1]}' for mark in response['days'][today][:-1])
            output += f'\n\t└ *{response["days"][today][-1][0]}*: {response["days"][today][-1][1]}'
        else:
            output += '\t└ Оценки за сегодняшний день отсутствуют'

    await message.answer(
        output,
        reply_markup=main_button(user),
        disable_notification=user.setting_notification,
        parse_mode='Markdown',
    )


@dp.message(F.text == 'Расписание 📅')
@UserClass.get_user()
async def schedule(message: Message, user: UserClass):
    logger.info(f'Вызвано расписание ({message.from_user.username})')
    response = await _exception_handler(user, message, parser.get_schedule)
    if not response:
        return
    schedule = response.get('days')

    if user.setting_dw:
        output = f'*Расписание на неделю ({response["date"]["begin_date"].strftime("%d.%m")} - {response["date"]["end_date"].strftime("%d.%m")}):*'
        for name_of_day, day in schedule.items():
            output += f'\n\n*{name_of_day}:*\n' + '\n'.join(
                f'\t{"├└"[i == len(day)]} {lesson["subject_name"]} ({lesson["room_number"]})'
                for i, lesson in enumerate(day, start=1)
            )
        output += f'\n{"-" * min(MAX_WIDTH_MESSAGE, len(output))}\nВсего уроков: {response["total_count"]}\n'
    else:
        today = datetime.now().isoweekday()
        if today in [5, 6, 7]:
            name_of_day = get_weekday(1)
        else:
            name_of_day = get_weekday(today + 1)

        day = schedule[name_of_day]

        output = (
            f'*Расписание на {name_of_day} ({datetime.fromisoformat(day[0]["start_at"]).strftime("%d.%m")}):*\n'
            + '\n'.join(
                f'\t{"├└"[i == len(day)]} {lesson["subject_name"]} ({lesson["room_number"]})'
                for i, lesson in enumerate(day, start=1)
            )
        )

        output += f'\n{"-" * min(MAX_WIDTH_MESSAGE, len(output))}\nВсего уроков: {len(day)}\n'
    await message.answer(output, parse_mode='Markdown')


@dp.message(F.text == 'Домашнее задание 📓')
@UserClass.get_user()
async def homework(message: Message, user: UserClass):
    """Sends the text of homework in accordance with the user settings.

    Args:
        message (Message): Received message.
        user (UserClass): User object.
    """
    logger.info(f'Вызвана домашка ({message.from_user.username})')

    msg = await message.answer('Ожидайте... ⌛')

    # Getting homework
    pre_hk = await db.get_homework(user.username)
    if pre_hk and (datetime.now() - pre_hk[1]) < timedelta(hours=1):
        hk: Homework = pre_hk[0]
    else:
        hk: Homework = await _exception_handler(user, message, parser.get_homework_from_website, student_id = user.student_id)
        if not hk:
            await msg.delete()
            return

        await db.save_homework(user.username, hk)

    async def get_output_for_day(day: StudyDay) -> str:
        output = f'*Домашка на {day.name} ({day.date.strftime("%d.%m")})*:\n'
        for lesson in day:
            if lesson.links:
                if user.setting_hide_link:
                    lesson_links = (
                        f'\t└ {"\n\t\t\t".join(f"[{exam.name}]({exam.link})" for exam in lesson.links)}\n'
                    )
                else:
                    lesson_links = (
                        f'\t└ {"\n\t\t\t".join(f"{exam[1].replace('_', r'\_')}" for exam in lesson.links)}\n'
                    )
            else:
                lesson_links = ''
            output += f'*• {lesson.name}:*\n\t{"├" if lesson_links else "└"} _{lesson.homework}_\n{lesson_links}'
        output += f'{r"-" * min(MAX_WIDTH_MESSAGE, len(max(output.split("\n"), key=len)))}\nВсего задано уроков: {len(day)}'
        return output

    await bot.delete_message(message.chat.id, msg.message_id)
    if user.setting_dw:  # if setting_dw is True, print for 5 days
        output = ''
        for day in hk:
            output += await get_output_for_day(day) + '\n\n\n'
    else:  # if False, for one day.
        today_index = datetime.now().isoweekday() if datetime.now().weekday() < 5 else 0
        output = await get_output_for_day(hk[today_index])

    await message.answer(
        output,
        parse_mode='Markdown',
        disable_notification=user.setting_notification,
    )


@dp.message(F.text == 'Соц. сети класса 💬')
async def social_networks(message):
    await message.answer(
        text=r"""
Конечно\! Держи:

[Официальная группа в WhatsApp](https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg) \(создатель @Lynx20wz\)
[Подпольная группа в WhatsApp](https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo) \(создатель @Juggernaut\_45\)

Если ссылки не работают обратиться к @Lynx20wz\} 
""",
        reply_markup=social_networks_button(),
        parse_mode='MarkdownV2',
    )


# Settings
@dp.message(F.text == 'Настройки ⚙️')
@UserClass.get_user()
async def settings(message: Message, user: UserClass):
    logger.info(f'Вызваны настройки ({message.from_user.username})')
    markup = make_setting_button(user)
    await message.answer(
        text=r"""
Настройки:

*Выдача на день\неделю:*
    1) *"Выдача на день":* будет высылаться домашнее задание только на завтра.
В пятницу, субботу и воскресенье будет высылаться домашнее задание на понедельник.
    2) *"Выдача на неделю":* Будет высылаться домашнее задание на все оставшиеся дни недели.

*Уведомления:*
    1) *"Уведомления вкл.":* включает звук уведомлений для каждого сообщения.
    2) *"Уведомления выкл.":* отключает звук уведомления для каждого сообщения.

*Скрытие ссылок:*
    1) *"Скрыть ссылки":* ссылки будут замаскированны под "ЦДЗ".
    2) *"Показать ссылки":* ссылки будут выведены напрямую.
            """,
        reply_markup=markup,
        parse_mode='Markdown',
        disable_notification=user.setting_notification,
    )


@dp.message(F.text.in_(['Выдача на неделю', 'Выдача на день']))
@UserClass.get_user()
async def change_delivery(message: Message, user: UserClass):
    if message.text == 'Выдача на неделю':
        user.setting_dw = False
    elif message.text == 'Выдача на день':
        user.setting_dw = True
    markup = make_setting_button(user)
    await user.save_settings(setting_dw=user.setting_dw)
    logger.info(
        f'Изменены настройки выдачи ({message.from_user.username} - {user.setting_dw} ({user.data}))'
    )
    await message.answer(
        'Настройки успешно изменены!',
        reply_markup=markup,
        disable_notification=user.setting_notification,
    )


@dp.message(F.text.in_(['Уведомления вкл.', 'Уведомления выкл.']))
@UserClass.get_user()
async def change_notification(message: Message, user: UserClass):
    if message.text == 'Уведомления вкл.':
        user.setting_notification = False
    elif message.text == 'Уведомления выкл.':
        user.setting_notification = True
    markup = make_setting_button(user)
    await user.save_settings(setting_notification=user.setting_notification)
    logger.info(
        f'Изменены настройки уведомлений ({message.from_user.username} - {user.setting_notification} ({user.data}))'
    )
    await message.answer(
        'Настройки успешно изменены!',
        reply_markup=markup,
        disable_notification=user.setting_notification,
    )


@dp.message(F.text.in_(['Скрыть ссылки', 'Показать ссылки']))
@UserClass.get_user()
async def change_link(message: Message, user: UserClass):
    if message.text == 'Скрыть ссылки':
        user.setting_hide_link = True
    elif message.text == 'Показать ссылки':
        user.setting_hide_link = False
    markup = make_setting_button(user)
    await user.save_settings(setting_hide_link=user.setting_hide_link)
    logger.info(
        f'Изменены настройки ссылок ({message.from_user.username} - {user.setting_hide_link} ({user.data}))'
    )
    await message.answer(
        'Настройки успешно изменены!',
        reply_markup=markup,
        disable_notification=user.setting_notification,
    )


@dp.message(F.text == 'Назад')
@UserClass.get_user()
async def exit_settings(message: Message, user: UserClass):
    logger.info(f'Вышел из настроек ({message.from_user.username})')
    await user.save_settings(
        setting_dw=user.setting_dw,
        setting_notification=user.setting_notification,
        setting_hide_link=user.setting_hide_link,
        debug=user.debug,
    )
    await message.answer(
        'Главное меню',
        reply_markup=main_button(user),
        disable_notification=user.setting_notification,
    )


@dp.message(F.text == 'Удалить аккаунт')
@UserClass.get_user()
async def delete_user(message: Message, user: UserClass):
    """Complete deletion of a user.

    Args:
        message (Message): Received message
        user (UserClass): User object
    """
    await db.delete_user(user.username)
    await message.answer('Аккаунт успешно удален!')


async def main():
    Handlers(dp).register_all()
    await bot.delete_webhook(drop_pending_updates=True)
    await db.restart_bot(False if '-back' in sys.argv else True)
    logger.debug('Бот рестарт!')
    try:
        await dp.start_polling(bot)
    finally:
        await db.backup_create()
        await bot.close()


# Starting the bot
if __name__ == '__main__':
    asyncio.run(main())
