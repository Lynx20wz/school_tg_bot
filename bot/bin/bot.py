import asyncio
import re
import sys
from datetime import datetime, timedelta

from aiogram import Bot, F, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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


# СТАРТ!
@dp.message(F.text, Command('start'))
@UserClass.get_user()
async def start(message: Message, user: UserClass):
    logger.info(f'Бота запустили ({message.from_user.username})')
    with open('../loging.png', 'rb') as file:
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
    date, response = response
    output = f'Оценки за неделю {date[0].strftime("%d.%m")} - {date[1].strftime("%d.%m")}:\n'

    if response['payload']:
        for lesson in response['payload']:
            day_of_week = parser.get_weekday(datetime.strptime(lesson['date'], '%Y-%m-%d').isoweekday())
            if day_of_week not in output:
                output += f'\t*{day_of_week}:*\n'
            output += f'\t\t- _{lesson["subject_name"]}: *{lesson["value"]}*_\n'
    else:
        output += '\t└ Оценки за этот период отсутствуют'

    output = re.sub(r'([\[(.\])-])', r'\\\1', output)
    await message.answer(
            output,
            reply_markup=main_button(user),
            disable_notification=user.setting_notification,
            parse_mode='MarkdownV2',
    )


@dp.message(F.text == 'Расписание 📅')
@UserClass.get_user()
async def schedule(message: Message, user: UserClass):
    logger.info(f'Вызвано расписание ({message.from_user.username})')
    response = await _exception_handler(user, message, parser.get_schedule)
    if not response:
        return
    date, schedule = response

    output = (
            f'*Расписание на {parser.get_weekday(date.isoweekday())} ({date.strftime("%d.%m")}):*\n'
            + '\n'.join(
            f'\t{"├└"[i == len(schedule["response"]) - 1]} {lesson["subject_name"]} ({lesson["room_number"]})'
            for i, lesson in enumerate(schedule['response'])
    )
    )

    output += f'\n{'-' * min(MAX_WIDTH_MESSAGE, len(output))}\nВсего уроков: {schedule["total_count"]}\n'
    await message.answer(re.sub(r'([\[(.\])-])', r'\\\1', output), parse_mode='MarkdownV2')


@dp.message(F.text == 'Домашнее задание 📓')
@UserClass.get_user()
async def homework(message: Message, user: UserClass):
    """
    Sends the text of homework in accordance with the user settings.

    : Param Message: received message.
    : Param User: User Object.
    """

    logger.info(f'Вызвана домашка ({message.from_user.username})')
    link: bool = False

    msg = await message.answer('Ожидайте... ⌛')

    # Получаем домашку
    pre_hk = await db.get_homework(user.username)
    if all(pre_hk) and (datetime.now() - pre_hk[0]) < timedelta(hours=1):
        hk = pre_hk[1]
    else:
        hk = await _exception_handler(user, message, parser.full_parse)
        if not hk:
            await msg.delete()
            return

        await db.save_homework(user.username, hk)
        await message.answer('Домашка успешно обновлена!')

    async def get_output_for_day(link: bool, day_name: str) -> str:
        one_day = hk.get(day_name)
        begin_date, end_date = map(
                lambda x: datetime.fromisoformat(x).strftime('%d.%m'),
                hk.get('date', {}).values(),
        )
        output = re.escape(f'*Домашка на {day_name} ({begin_date + "-" + end_date if user.setting_dw else begin_date})*:\n')
        for lesson in one_day:
            if lesson['links']:
                logger.debug(f'{user.setting_hide_link=}')
                if user.setting_hide_link:
                    lesson['links'] = (
                        f'\t└ {"\n\t\t\t".join(f"[{re.escape(exam['title'])}]({exam['link']})" for i, exam in enumerate(lesson["links"], start=1))}\n'
                    )
                else:
                    lesson['links'] = (
                        f'\t└ {"\n\t\t\t".join(f"{re.escape(exam['link'])}" for i, exam in enumerate(lesson["links"], start=1))}\n'
                    )
            else:
                lesson['links'] = ''
            if not link and 'https://' in lesson['homework']:
                link = True
            output += f'*• {re.escape(lesson["name"])}:*\n\t{"├" if lesson["links"] else "└"} _{re.escape(lesson["homework"].strip())}_\n{lesson["links"]}'
        output += f'{r"\-" * min(MAX_WIDTH_MESSAGE, len(max(output.split("\n"), key=len)))}\nВсего задано уроков: {len(one_day)}'
        return output

    await bot.delete_message(message.chat.id, msg.message_id)
    # Анализируем домашку
    if user.setting_dw:  # Если setting_dw равен True, выводим на всю неделю
        output = ''
        for i in range(1, 6):
            output += await get_output_for_day(link, parser.get_weekday(i)) + '\n'
    else:  # Если False то на один день
        today_index = datetime.now().isoweekday()

        # Если сегодня суббота или воскресенье, то выводим на следующий понедельник
        if today_index in [5, 6, 7]:
            next_day_index = 1
        else:
            next_day_index = today_index + 1

        day_name = parser.get_weekday(next_day_index)
        output = await get_output_for_day(link, day_name)

    logger.debug(output)

    if link:
        murkup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                                text='Бот для решения ЦДЗ',
                                url='https://t.me/solving_CDZ_tests_bot',
                        )
                    ]
                ]
        )
        await message.answer(
                output,
                parse_mode='MarkdownV2',
                reply_markup=murkup,
                disable_notification=user.setting_notification,
        )
    else:
        await message.answer(
                output,
                parse_mode='MarkdownV2',
                disable_notification=user.setting_notification,
        )


@dp.message(F.text == 'Соц. сети класса 💬')
async def social_networks(message):
    await message.answer(
            text=r"""
Конечно! Держи:

[Официальная группа в WhatsApp](https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg) (создатель @Lynx20wz)
[Подпольная группа в WhatsApp](https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo) (создатель @Juggernaut\_45)

Если ссылки не работают обратиться к @Lynx20wz)
""",
            reply_markup=social_networks_button(),
            parse_mode='Markdown',
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
            save_db=True,
    )
    await message.answer(
            'Главное меню',
            reply_markup=main_button(user),
            disable_notification=user.setting_notification,
    )


# полное удаления пользователя
@dp.message(F.text == 'Удалить аккаунт')
@UserClass.get_user()
async def delete_user(message: Message, user: UserClass):
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


# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())
