import asyncio
import json
from datetime import datetime, timedelta

from aiogram import Dispatcher, Bot, F, types
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile

import parser_school as ps
from KeyBoards import main_button, make_setting_button
from bin import BD_PATH, ADMIN_ID, API_BOT, logger, BaseDate, UserClass
from debug_handlers import debug_router
from registration import auth_router

bot = Bot(API_BOT)
dp = Dispatcher()


async def restart():
    """
    Перезапускает бота и отправка оповещение каждому пользователю из файла кэша
    """
    users = await db.restart_bot()
    # if users:
    #     for user in users:
    #         murkup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')]])
    # await bot.send_message(
    #         chat_id=user.get('userid'), text='Бот вновь запущен!\nДля лучшего опыта использования не будет лишним ввести команду /start',
    #         disable_notification=user.get('setting_notification'), reply_markup=murkup
    # )

    logger.debug('Бот рестарт!')

# СТАРТ!
@dp.message(F.text, Command("start"))
@UserClass.get_user()
async def start(message: types.Message, user, **kwargs):
    logger.info(f'Бота запустили ({message.from_user.username})')
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
@UserClass.get_user()
async def homework(message: Message, user: UserClass, **kwargs) -> None:
    """
    Высылает текст домашнего задания в соответствии с настройками пользователя.

    :param message: Полученное сообщение.
    :param user: Объект пользователя.
    """

    logger.info(f'Вызвана домашка ({message.from_user.username})')
    link: bool = False

    msg = await message.answer('Ожидайте... ⌛')
    result = await db.get_login(user.username)
    if not result:
        await msg.edit_text('Чтобы получить данные о домaшнем задании, нужно зарегистрироваться. Чтобы пройти регистрацию введите: /reg')
        return
    else:
        login = result

    pre_hk = await db.get_homework(user.username)
    if pre_hk is not None and datetime.now() - pre_hk[0] < timedelta(hours=1):
        hk = json.loads(pre_hk[1])
    elif pre_hk is not None:
        try:
            hk = ps.full_parse(login)
        except ValueError as e:
            logger.warning(f'Произошла ошибка при получении дз: {e}')
            await msg.edit_text('Данные для входа в госуслуги неверные! Повторите регистрацию с помощью /reg')
            return
        await db.update_homework_cache(user.username, hk)
        logger.info('Домашка была обновлена')
    else:
        await msg.edit_text('Данные для входа в госуслуги неверные! Повторите регистрацию с помощью /reg')
        return

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
    await bot.delete_message(message.chat.id, msg.message_id)
    if link:
        murkup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Бот для решения ЦДЗ', url='https://t.me/CDZ_AnswersBot')]])
        await message.answer(output, parse_mode="Markdown", reply_markup=murkup, disable_notification=user.setting_notification)
    else:
        await message.answer(output, parse_mode="Markdown", disable_notification=user.setting_notification)

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
@dp.message(F.text == 'Настройки ⚙️')
@UserClass.get_user()
async def settings(message: Message, user, **kwargs):
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
@UserClass.get_user()
async def change_delivery(message, user, **kwargs):
    if message.text == 'Выдача на неделю':
        user.setting_dw = False
    elif message.text == 'Выдача на день':
        user.setting_dw = True
    murkup = make_setting_button(user)
    user.save_settings(db, setting_dw=user.setting_dw)
    logger.info(f'Изменены настройки выдачи ({message.from_user.username} - {user.setting_dw} ({user.data}))')
    await message.answer('Настройки успешно изменены!', reply_markup=murkup, disable_notification=user.setting_notification)


@dp.message(F.text.in_(['Уведомления вкл.', 'Уведомления выкл.']))
@UserClass.get_user()
async def change_notification(message, user, **kwargs):
    if message.text == 'Уведомления вкл.':
        user.setting_notification = False
    elif message.text == 'Уведомления выкл.':
        user.setting_notification = True
    murkup = make_setting_button(user)
    user.save_settings(db, setting_notification=user.setting_notification)
    logger.info(f'Изменены настройки уведомлений ({message.from_user.username} - {user.setting_notification} ({user.data}))')
    await message.answer('Настройки успешно изменены!', reply_markup=murkup, disable_notification=user.setting_notification)


@dp.message(F.text == 'Назад')
@UserClass.get_user()
async def exit_settings(message, user, **kwargs):
    logger.debug(f'{user.setting_dw} - {user.setting_notification}')
    logger.info(f'Вышел из настроек ({message.from_user.username})')
    user.save_settings(db, user.setting_dw, user.setting_notification, user.debug, True)
    await message.answer('Главное меню', reply_markup=main_button(user), disable_notification=user.setting_notification)


async def main():
    debug_router.message.filter(F.chat.id == ADMIN_ID)
    dp.include_routers(debug_router, auth_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await restart()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


# @dp.message(F.text)
# @UserClass.get_user()
# async def unknown_command(message, user):
#     logger.error(f'Вызвана несуществующая команда! ({message.from_user.username}):\n"{message.text}"')
#     await message.answer(
#             "Извините, нет такой команды. Пожалуйста, используйте доступные кнопки или команды.",
#             disable_notification=user.setting_notification
#         )

# Запуск бота
if __name__ == '__main__':
    db = BaseDate(BD_PATH)
    with open('../schedule.json', 'r', encoding='utf-8') as file:
        timetable_dict = json.load(file)
    asyncio.run(main())
