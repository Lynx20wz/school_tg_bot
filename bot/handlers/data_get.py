from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.types import Message

from bot.classes import UserClass, Homework, DataBase
from bot.classes.Homework import StudyDay
from bot.bin import logger, get_weekday
from bot.until import main_button
from datetime import datetime, timedelta

data_get_router = Router()
db = DataBase()

MAX_WIDTH_MESSAGE = 33


async def request_handler(func: callable, message: Message, *args, **kwargs) -> dict | None:
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(e)
        await message.answer(str(e))
        return None


@data_get_router.message(or_f(F.text == 'Оценки 📝', Command('marks')))
async def marks(message: Message, user: UserClass):
    response = await request_handler(user.parser.get_marks, message)
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
        output = f'*Оценки за сегодняшний день ({today}, {response["date"]["begin_date"].strftime("%d.%m")}):*\n'

        if response['days']:
            output += '\t├ ' + '\n\t├ '.join(
                f'*{mark[0]}*: {mark[1]}' for mark in response['days'][today][:-1]
            )
            output += f'\n\t└ *{response["days"][today][-1][0]}*: {response["days"][today][-1][1]}'
        else:
            output += '\t└ Оценки за сегодняшний день отсутствуют'

    await message.answer(
        output,
        reply_markup=main_button(user),
        disable_notification=user.setting_notification,
        parse_mode='Markdown',
    )


@data_get_router.message(or_f(F.text == 'Расписание 📅', Command('schedule')))
async def schedule(message: Message, user: UserClass):
    response = await request_handler(user.parser.get_schedule, message)
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


@data_get_router.message(or_f(F.text == 'Домашнее задание 📓', Command('homework')))
async def homework(message: Message, user: UserClass):
    """Sends the text of homework in accordance with the user settings.

    Args:
        message (Message): Received message.
        user (UserClass): User object.
    """
    msg = await message.answer('Ожидайте... ⌛')

    # Getting homework
    pre_hk = await db.get_homework(user.username)
    if pre_hk and (datetime.now() - pre_hk[1]) < timedelta(hours=1):
        hk: Homework = pre_hk[0]
    else:
        hk: Homework = await request_handler(user.parser.get_homework, message)
        if not hk:
            await msg.delete()
            return

        await db.save_homework(user.username, hk)

    async def get_output_for_day(day: StudyDay) -> str:
        output = f'*Домашка на {day.name} ({day.date.strftime("%d.%m")})*:\n'
        for lesson in day:
            if lesson.links:
                if user.setting_hide_link:
                    lesson_links = f'\t└ {"\n\t\t\t".join(f"[{exam.name}]({exam.link})" for exam in lesson.links)}\n'
                else:
                    lesson_links = f'\t└ {"\n\t\t\t".join(f"{exam[1].replace('_', r'\_')}" for exam in lesson.links)}\n'
            else:
                lesson_links = ''
            output += f'*• {lesson.name}:*\n\t{"├" if lesson_links else "└"} _{lesson.homework}_\n{lesson_links}'
        output += f'{r"-" * min(MAX_WIDTH_MESSAGE, len(max(output.split("\n"), key=len)))}\nВсего задано уроков: {len(day)}'
        return output

    await message.bot.delete_message(message.chat.id, msg.message_id)
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