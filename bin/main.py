import asyncio
import json
from datetime import datetime, timedelta

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile

import parser as ps
from bin import (UserClass, API_BOT, logger, db,
                 main_button, social_networks_button, make_setting_button,
                 NoHomeworkError)
from handlers import Handlers

bot = Bot(API_BOT)
dp = Dispatcher()


async def restart():
    """
    Перезапускает бота и создаёт всех пользователей из БД
    """
    users = await db.restart_bot()
    for user in users:
        UserClass(
                user.get('username'),
                user.get('userid'),
                bool(user.get('debug')),
                bool(user.get('setting_dw')),
                bool(user.get('setting_notification')),
                user.get('token'),
                user.get('student_id'),
                user.get('homework_id'),
        )
    logger.debug('Бот рестарт!')


# СТАРТ!
@dp.message(F.text, Command("start"))
@UserClass.get_user()
async def start(message: Message, user: UserClass):
    logger.info(f'Бота запустили ({message.from_user.username})')
    with open('../Логирование.png', 'rb') as file:
        await message.answer_photo(
                photo=BufferedInputFile(file.read(), filename='Логирование'),
                caption='''Привет. Этот бот создан для вашего удобства и комфорта! Здесь вы можете глянуть расписание, дз, и т.д. Найдёте ошибки сообщите: @Lynx20wz)
                \nP.S: Также должен сказать, что в целях отлова ошибок я веду логирование, то есть, я вижу какую функцию вы запустили и ваш никнейм в телеграм (на фото видно).''',
                reply_markup=main_button(user)
        )


@dp.message(F.text == 'Оценки 📝')
@UserClass.get_user()
async def marks(message: Message, user: UserClass):
    if not user.check_token():
        await message.answer('У вас отсутствует токен, пожалуйста введите команду /token, чтобы получить его!')
        return
    logger.info(f'Вызваны оценки ({message.from_user.username})')
    response = ps.get_marks(user.student_id, user.token)
    output = ''
    for lesson in response['payload']:
        day_of_week = ps.get_weekday(datetime.strptime(lesson['date'], '%Y-%m-%d').isoweekday())
        if day_of_week not in output:
            output += f'*{day_of_week}:*\n'
        output += f'\t- {lesson["subject_name"]}: {lesson["value"]}\n'

    await message.answer(output, reply_markup=main_button(user), disable_notification=user.setting_notification, parse_mode='Markdown')


@dp.message(F.text, Command("schedule"))
@dp.message(F.text == 'Расписание 📅')
@UserClass.get_user()
async def schedule(message: Message, user: UserClass, command: CommandObject = None):
    if not user.check_token():
        await message.answer('У вас отсутствует токен, пожалуйста введите команду /token, чтобы получить его!')
        return
    command_args = command.args if command else None
    name_of_day, schedule = ps.get_schedule(user.token, command_args)
    output = f'*{name_of_day}:*\n'
    for lesson in schedule['response']:
        output += f'\t- {lesson['subject_name']} ({lesson["room_number"]})\n'
    output += f'-------------------------------\nВсего уроков: {schedule['total_count']}\n'
    logger.info(f'Вызвано расписание ({message.from_user.username})')
    await message.answer(output, parse_mode='Markdown')


@dp.message(F.text == 'Домашнее задание 📓')
@UserClass.get_user()
async def homework(message: Message, user: UserClass) -> None:
    """
    Высылает текст домашнего задания в соответствии с настройками пользователя.

    :param message: Полученное сообщение.
    :param user: Объект пользователя.
    """

    logger.info(f'Вызвана домашка ({message.from_user.username})')
    link: bool = False

    # Получаем токен
    msg = await message.answer('Ожидайте... ⌛')
    if not user.check_token():
        await message.answer('У вас отсутствует токен, пожалуйста введите команду /token, чтобы получить его!')
        return

    # Получаем домашку
    pre_hk = await db.get_homework(user.username)
    if pre_hk is not None and (datetime.now() - pre_hk[0]) < timedelta(hours=1):
        hk = json.loads(pre_hk[1])
    else:  # Если домашка не была обновлена в последний час/не была обнаружена в бд
        async def update_homework():
            await db.update_homework_cache(user.username, homework=hk)
            logger.info('Домашка была обновлена')
        try:
            hk = ps.full_parse(token=user.token, student_id=user.student_id, parsing=True)
            await update_homework()
        except NoHomeworkError as e:
            logger.error(f'{user.username} - {e.ready_message(user.setting_dw)}')
            await msg.edit_text(e.ready_message(user.setting_dw))
            return

    # Анализируем домашку
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

        # logger.debug(f'{next_day_index} - {today_index}) {one_day}')
        for number_lesson, lesson in enumerate(one_day, start=1):
            output += f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
            if 'https://' in lesson[2]:
                link = True
        output += f'-------------------------------\nВсего задано уроков: {len(one_day)}'
    await bot.delete_message(message.chat.id, msg.message_id)
    if link:
        murkup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Бот для решения ЦДЗ', url='https://t.me/solving_CDZ_tests_bot')]])
        await message.answer(output, parse_mode="Markdown", reply_markup=murkup, disable_notification=user.setting_notification)
    else:
        await message.answer(output, parse_mode="Markdown", disable_notification=user.setting_notification)


@dp.message(F.text == 'Соц. сети класса 💬')
async def social_networks(message):
    await message.answer(
            text=
            r"""
Конечно! Держи:

[Официальная группа в WhatsApp](https://chat.whatsapp.com/Dz9xYMsfWoy3E7smQHimDg) (создатель @Lynx20wz)
[Подпольная группа в WhatsApp](https://chat.whatsapp.com/GvkRfG5W5JoApXrnu4T9Yo) (создатель @Juggernaut\_45)

Если ссылки не работают обратиться к @Lynx20wz)
""",
            reply_markup=social_networks_button(),
            parse_mode='Markdown'
    )


# Settings
@dp.message(F.text == 'Настройки ⚙️')
@UserClass.get_user()
async def settings(message: Message, user: UserClass):
    logger.info(f'Вызваны настройки ({message.from_user.username})')
    murkup = make_setting_button(user)
    await message.answer(
            text=r'''
Настройки:

*Выдача на день\неделю:*
    1) *"Выдача на день":* будет высылаться домашнее задание только на завтра.
В пятницу, субботу и воскресенье будет высылаться домашнее задание на понедельник.
    2) *"Выдача на неделю":* Будет высылаться домашнее задание на все оставшиеся дни недели.
    
*Уведомления:*
    1) *"Уведомления вкл.":* включает звук уведомлений для каждого сообщения.
    2) *"Уведомления выкл.":* отключает звук уведомления для каждого сообщения.
            ''',
            reply_markup=murkup, parse_mode='Markdown',
            disable_notification=user.setting_notification
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
            disable_notification=user.setting_notification
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
            disable_notification=user.setting_notification
    )


@dp.message(F.text == 'Назад')
@UserClass.get_user()
async def exit_settings(message: Message, user: UserClass):
    logger.info(f'Вышел из настроек ({message.from_user.username})')
    await user.save_settings(setting_dw=user.setting_dw, setting_notification=user.setting_notification, debug=user.debug, save_db=True)
    await message.answer(
            'Главное меню',
            reply_markup=main_button(user),
            disable_notification=user.setting_notification
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
    await restart()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())
