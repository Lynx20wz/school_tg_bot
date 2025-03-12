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
    UserClass,
    API_BOT,
    logger,
    db,
    parser,
    main_button,
    social_networks_button,
    make_setting_button,
    ExpiredToken,
    NoToken,
    ServerError
)
from bot.bin.parser import get_weekday
from bot.handlers import Handlers

bot = Bot(API_BOT)
dp = Dispatcher()

MAX_WIDTH_MESSAGE = 33

async def _exception_handler(user: UserClass, message: Message, function: callable, *args, **kwargs):
    """

    Args:
        user (UserClass): A user for which the function is called
        message (Message): A message for which the function is called
        function (callable): The function to be called

    Returns:
        Either notify the user that an exception has happened
        or return the result of the function completion
    """
    try:
        if not user.token:
            raise NoToken()
        result = function(token=user.token, *args, **kwargs)
    except (ExpiredToken, NoToken, ServerError) as e:
        logger.warning(f'{function.__name__} | {user.username}: Произошла ошибка: {e}')
        await message.answer(e.args[0])
        return
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
    response = await _exception_handler(user, message, parser.get_marks, user.student_id)
    if not response:
        return

    if user.setting_dw:
        output = f'*Оценки за неделю ({response['date']['begin_date'].strftime("%d.%m")} - {response['date']['end_date'].strftime("%d.%m")}):*\n'

        if response['days']:
            for name_of_day, marks in response['days'].items():
                output += f'*{name_of_day}:*\n\t└ ' + '\n\t└ '.join(f'*{mark[0]}*: {mark[1]}' for mark in marks)
        else:
            output += '\t└ Оценки за этот период отсутствуют'
    else:
        output = f'*Оценки за сегодняшний день ({response["date"]["begin_date"].strftime("%d.%m")}):*\n'

        today = get_weekday(datetime.now().isoweekday())

        if response['days']:
            output += f'*{today}:*\n\t└ ' + '\n\t└ '.join(f'*{mark[0]}*: {mark[1]}' for mark in response['days'][today])
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
        output = f'*Расписание на неделю ({response['date']['begin_date'].strftime("%d.%m")} - {response['date']['end_date'].strftime("%d.%m")}):*'
        for name_of_day, day in schedule.items():
            output += (
            f'\n\n*{name_of_day}:*\n'
            + '\n'.join(
                f'\t{"├└"[i == len(day)]} {lesson["subject_name"]} ({lesson["room_number"]})'
                for i, lesson in enumerate(day, start=1)
            ))
        output += f'\n{'-' * min(MAX_WIDTH_MESSAGE, len(output))}\nВсего уроков: {response["total_count"]}\n'
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

        output += f'\n{'-' * min(MAX_WIDTH_MESSAGE, len(output))}\nВсего уроков: {len(day)}\n'
    await message.answer(output, parse_mode='Markdown')


@dp.message(F.text == 'Домашнее задание 📓')
@UserClass.get_user()
async def homework(message: Message, user: UserClass):
    """
    Sends the text of homework in accordance with the user settings.

    Args:
        message (Message): Received message.
        user (UserClass): User object.
    """

    logger.info(f'Вызвана домашка ({message.from_user.username})')

    msg = await message.answer('Ожидайте... ⌛')

    # Getting homework
    pre_hk = await db.get_homework(user.username)
    if pre_hk and (datetime.now() - datetime.fromisoformat(pre_hk['date']['timestamp'])) < timedelta(hours=1):
        hk = pre_hk
    else:
        hk = await _exception_handler(user, message, parser.full_parse)
        if not hk:
            await msg.delete()
            return

        await db.save_homework(user.username, hk)

    async def get_output_for_day(day_name: str) -> str:
        one_day = hk['days'].get(day_name)
        begin_date, end_date, _ = map(
                lambda x: datetime.fromisoformat(x).strftime('%d.%m'),
                hk.get('date', {}).values(),
        )

        output = f'*Домашка на {day_name} ({begin_date + r"-" + end_date if user.setting_dw else begin_date})*:\n'
        for lesson in one_day:
            if lesson['links']:
                logger.debug(f'{user.setting_hide_link=}')
                if user.setting_hide_link:
                    lesson['links'] = (
                        f'\t└ {"\n\t\t\t".join(f"[{(exam['title'])}]({exam['link']})" for  exam in lesson["links"])}\n'
                    )
                else:
                    lesson['links'] = (
                        f'\t└ {"\n\t\t\t".join(f"{exam['link'].replace('_', r'\_')}" for exam in lesson["links"])}\n'
                    )
            else:
                lesson['links'] = ''
            output += f'*• {lesson["name"]}:*\n\t{"├" if lesson["links"] else "└"} _{lesson["homework"].strip()}_\n{lesson["links"]}'
        output += f'{r"-" * min(MAX_WIDTH_MESSAGE, len(max(output.split("\n"), key=len)))}\nВсего задано уроков: {len(one_day)}'
        return output

    await bot.delete_message(message.chat.id, msg.message_id)
    if user.setting_dw:  # if setting_dw is True, print for 5 days
        output = ''
        for i in range(1, 6):
            output += await get_output_for_day(parser.get_weekday(i)) + '\n'
    else:  # if False, for one day.
        today_index = datetime.now().isoweekday()

        # if today is Saturday or Sunday, print for next Monday
        if today_index in [5, 6, 7]:
            next_day_index = 1
        else:
            next_day_index = today_index + 1

        day_name = parser.get_weekday(next_day_index)
        output = await get_output_for_day(day_name)

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
    murkup = make_setting_button(user)
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
            reply_markup=murkup,
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
    murkup = make_setting_button(user)
    await user.save_settings(setting_dw=user.setting_dw)
    logger.info(f'Изменены настройки выдачи ({message.from_user.username} - {user.setting_dw} ({user.data}))')
    await message.answer(
            'Настройки успешно изменены!',
            reply_markup=murkup,
            disable_notification=user.setting_notification,
    )


@dp.message(F.text.in_(['Уведомления вкл.', 'Уведомления выкл.']))
@UserClass.get_user()
async def change_notification(message: Message, user: UserClass):
    if message.text == 'Уведомления вкл.':
        user.setting_notification = False
    elif message.text == 'Уведомления выкл.':
        user.setting_notification = True
    murkup = make_setting_button(user)
    await user.save_settings(setting_notification=user.setting_notification)
    logger.info(f'Изменены настройки уведомлений ({message.from_user.username} - {user.setting_notification} ({user.data}))')
    await message.answer(
            'Настройки успешно изменены!',
            reply_markup=murkup,
            disable_notification=user.setting_notification,
    )


@dp.message(F.text.in_(['Скрыть ссылки', 'Показать ссылки']))
@UserClass.get_user()
async def change_link(message: Message, user: UserClass):
    if message.text == 'Скрыть ссылки':
        user.setting_hide_link = True
    elif message.text == 'Показать ссылки':
        user.setting_hide_link = False
    murkup = make_setting_button(user)
    await user.save_settings(setting_hide_link=user.setting_hide_link)
    logger.info(
            f'Изменены настройки ссылок ({message.from_user.username} - {user.setting_hide_link} ({user.data}))'
    )
    await message.answer(
            'Настройки успешно изменены!',
            reply_markup=murkup,
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
    """
    Complete deletion of a user

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
