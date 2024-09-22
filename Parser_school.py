import json
import sys
from copy import deepcopy
from datetime import datetime, timedelta

import requests
from loguru import logger

logger.remove()
logger.add(
        sink=sys.stdout,
        level='INFO',
        format='{time:H:mm:ss}:{line}| <level>{level}</level> | {message}',
)

is_friday = False
is_weekend = False


def get_weekday(number):
    weekdays = {1: 'Понедельник',
                2: 'Вторник',
                3: 'Среда',
                4: 'Четверг',
                5: 'Пятница',
                6: 'Суббота',
                7: 'Воскресенье'}
    return weekdays.get(number)


class lesson_class():
    def __init__(self, day, name, cabinet_number, homework, /) -> None:
        self.day = day
        self.name = name
        self.cabinet_number = cabinet_number
        self.homework = homework

    def get_lesson_info(self):
        return (self.name, self.day, self.cabinet_number, self.homework)


def get_homework_from_website(date: datetime = datetime.now()) -> json:
    """
    Парсит данные со школьного портала и заносит их в файл в формате json.

    :param date: Любое число от 1 до 31.
    :return: Json-файл с домашним заданием.
    """
    date_in_str = date.replace(year=datetime.now().year, month=datetime.now().month)
    Monday = (date_in_str + timedelta(days=7 + (1 - date_in_str.isoweekday()) if (1 - date_in_str.isoweekday()) != 0 else 0))
    begin_date = Monday.strftime('%Y-%m-%d')
    end_date = (Monday + timedelta(days=4)).strftime('%Y-%m-%d')

    logger.info(f'{begin_date} - {end_date}:')

    cookies = {
        'auth_flag': 'region',
        'user_login': 'prokopishinmn',
        'obr_id': '3617590',
        'subsystem_id': '2',
        'cluster': '',
        'aupd_current_role': '2:1',
        'auth_token': 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzNjE3NTkwIiwic2NwIjoib3BlbmlkIHByb2ZpbGUiLCJtc2giOiJkZDBlNjA0NC0xMzhjLTRlNTItODlhYi1mMmEwZGE5YzliN2MiLCJpc3MiOiJodHRwczpcL1wvYXV0aGVkdS5tb3NyZWcucnUiLCJyb2wiOiIiLCJzc28iOiIxMDkxMDQwNjYwIiwiYXVkIjoiMjoxIiwibmJmIjoxNzI2MjAzMzcwLCJhdGgiOiJlc2lhIiwicmxzIjoiezE6WzE4MzoxNjpbXSwzMDo0OltdLDQwOjE6W10sMjExOjE5OltdLDUzMzo0ODpbXSwyMDoyOltdXX0iLCJyZ24iOiI1MCIsImV4cCI6MTcyNzA2NzM3MCwiaWF0IjoxNzI2MjAzMzcwLCJqdGkiOiJiNWIwZDQwYi1kMWJkLTQ1OTctYjBkNC0wYmQxYmQ4NTk3ZjgifQ.jgPc-vdmofCrkP2zbFfA3GxLTqtLEHSxVG0KN0RuBMhxPs-XXc83Lj1ztxrNcDEZ7W3KleaSFjmq3prvdIfE13PjG3LPQY9IskyBH4DHNIQZZKvERojHM6s8jYISwVZf8edq0XCzRBJb1AkvTnxtqCfyR6DI3tRJDTe0V3qrr2jgKvbF2zT5MY88xeL4oAJah4QQmEn85jt5tjKua2Jtu5HTt2rHz1UonByjJ5fwdUAE4weIvvRGdZawnreJB4opJDDJTf9g-Vw2ur1Yp4pu-WDjnPjqFYz0O23uZO4ovWriUkmKV-mXJqCwXaScHHoO2NsRwHNBazPWcVkgUPG2xQ',
        'active_student': '1530640',
        'aupd_token': 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzNjE3NTkwIiwic2NwIjoib3BlbmlkIHByb2ZpbGUiLCJtc2giOiJkZDBlNjA0NC0xMzhjLTRlNTItODlhYi1mMmEwZGE5YzliN2MiLCJpc3MiOiJodHRwczpcL1wvYXV0aGVkdS5tb3NyZWcucnUiLCJyb2wiOiIiLCJzc28iOiIxMDkxMDQwNjYwIiwiYXVkIjoiMjoxIiwibmJmIjoxNzI2MjMzNDQ1LCJhdGgiOiJlc2lhIiwicmxzIjoiezE6WzE4MzoxNjpbXSwzMDo0OltdLDQwOjE6W10sMjExOjE5OltdLDUzMzo0ODpbXSwyMDoyOltdXX0iLCJyZ24iOiI1MCIsImV4cCI6MTcyNzA5NzQ0NSwiaWF0IjoxNzI2MjMzNDQ1LCJqdGkiOiI0OWVlNDZjYy03MGU5LTQ1NWYtYWU0Ni1jYzcwZTk3NTVmNmMifQ.Ey3KYZyh6t9aykUNGfkipIujnvSWT4D7GZ6XsNIdDuhoYcaHYAIxuu1CLFbxsowPJrY5rnPN9JDdBij4MLWGm2FSO2xr-tRVfmx64ITL3WOwCClBRE4hN0ch4BXIc71g2Kw6hYYacdY3cfovTXgNhX8ABTUvkhogHKN9gDV-XJkgyENmZyywOPjgfyhdTRMU43uMOmWsahS5zalnMHz72inWe22MInd_t77F2eO8WK6mFXW2dg3r9UweU5qW4wJagEdbU_V8oNp0WQa1Jnf89G-NWg7OjIvds1RXGfrmQXgj1EUOzKj-VXynWT3Q94d2CwormY-3dbcSj68YpMWxVw',
        'JSESSIONID': 'node01trhzupz9owd5130dxxytr0mik27269143.node0',
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzNjE3NTkwIiwic2NwIjoib3BlbmlkIHByb2ZpbGUiLCJtc2giOiJkZDBlNjA0NC0xMzhjLTRlNTItODlhYi1mMmEwZGE5YzliN2MiLCJpc3MiOiJodHRwczpcL1wvYXV0aGVkdS5tb3NyZWcucnUiLCJyb2wiOiIiLCJzc28iOiIxMDkxMDQwNjYwIiwiYXVkIjoiMjoxIiwibmJmIjoxNzI2MjAzMzcwLCJhdGgiOiJlc2lhIiwicmxzIjoiezE6WzE4MzoxNjpbXSwzMDo0OltdLDQwOjE6W10sMjExOjE5OltdLDUzMzo0ODpbXSwyMDoyOltdXX0iLCJyZ24iOiI1MCIsImV4cCI6MTcyNzA2NzM3MCwiaWF0IjoxNzI2MjAzMzcwLCJqdGkiOiJiNWIwZDQwYi1kMWJkLTQ1OTctYjBkNC0wYmQxYmQ4NTk3ZjgifQ.jgPc-vdmofCrkP2zbFfA3GxLTqtLEHSxVG0KN0RuBMhxPs-XXc83Lj1ztxrNcDEZ7W3KleaSFjmq3prvdIfE13PjG3LPQY9IskyBH4DHNIQZZKvERojHM6s8jYISwVZf8edq0XCzRBJb1AkvTnxtqCfyR6DI3tRJDTe0V3qrr2jgKvbF2zT5MY88xeL4oAJah4QQmEn85jt5tjKua2Jtu5HTt2rHz1UonByjJ5fwdUAE4weIvvRGdZawnreJB4opJDDJTf9g-Vw2ur1Yp4pu-WDjnPjqFYz0O23uZO4ovWriUkmKV-mXJqCwXaScHHoO2NsRwHNBazPWcVkgUPG2xQ',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
        'Profile-Id': '1530640',
        'Profile-Type': 'student',
        'Referer': 'https://authedu.mosreg.ru/diary/schedules/schedule/?date=13-09-2024',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'X-Mes-Role': 'student',
        'X-mes-subsystem': 'familyweb',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    params = {
        'person_ids': 'dd0e6044-138c-4e52-89ab-f2a0da9c9b7c',
        'begin_date': begin_date,
        'end_date': end_date,
        'expand': 'marks,homework',
    }

    response = requests.get(
            'https://authedu.mosreg.ru/api/eventcalendar/v1/api/events',
            params=params,
            cookies=cookies,
            headers=headers,
    ).json()

    with open('school.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)


def split_day(response: dict) -> dict:
    """
    Делит уроки из response по дням.

    :param response: Принимает в себя dict с домашним заданием.
    """
    dow = 0  # day of week
    lessons = []  # все уроки за день
    lessons_dict = {'дни': []}  # задаю конечный словарь
    for i, lesson in enumerate(response['response'], start=1):
        date_lesson = datetime.strptime(lesson['start_at'][:10], '%Y-%m-%d').isoweekday()
        date_weekday = get_weekday(date_lesson)
        lessons.append(lesson)
        if i == 1:
            get_weekday(1)
        if i % 7 == 0:
            dow += 1
            lessons_dict['дни'].append({date_weekday: deepcopy(lessons)})
            lessons.clear()
    if lessons != []:
        dow += 1
        lessons_dict['дни'].append({date_weekday: deepcopy(lessons)})
        lessons.clear()
    return lessons_dict


def homework_output(dict_hk: dict = None, need_output: bool = False) -> dict:
    """
    Функция для вывода домашнего задания.

    :param dict_hk: Словарь с информацией о домашних заданиях.
    :return: Возвращает строку с информацией о домашнем задании.
    """
    output = {}
    if dict_hk == None:
        with open('school.json', 'r', encoding='utf-8') as file:
            response = json.load(file)
            lessons_dict = split_day(response)
    else:
        lessons_dict = dict_hk
    for i in range(0, len(lessons_dict['дни'])):  # задаю на каждой итерации новое значение i что значит день недели
        for day in lessons_dict['дни'][i].values():  # забираю информацию по дню согласно переменной i
            day_masiv = []
            for lid in day:  # (lesson in day) прохожусь по урокам в дне (day)

                name = lid.get('subject_name')
                if name == 'Труд (технология)': name = 'Технология'
                if name == 'Музыка': name = 'МХК'

                cabinet_number = lid.get('room_number')
                homework = ', '.join(lid.get('homework').get('descriptions'))
                if homework in ['.', ''] or 'Не задано' in homework:
                    pass
                else:
                    # lesson_class(get_weekday(i + 1), name, cabinet_number, homework)
                    # print(f'{name} ({cabinet_number}) - {homework}')
                    day_masiv.append((name, cabinet_number, homework))
                output[get_weekday(i + 1)] = day_masiv
    if not need_output:
        return output
    else:
        return_output = ''
        for i, one_day in enumerate(output.values(), start=1):
            day_of_week = get_weekday(i)
            return_output += f'\n*{day_of_week}*:\n'
            for number_lesson, lesson in enumerate(one_day, start=1):
                return_output += f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
        return_output += f'-------------------------------\nВсего задано уроков: {sum(len(day) for day in output.values())}'
        return return_output


def full_parse(date: datetime = datetime.now()) -> str:
    """
    Функция для полного анализа расписания.

    :param date: Дата, для которой нужно произвести анализ. По умолчанию - сегодняшняя дата.
    """
    get_homework_from_website(date)
    with open('school.json', 'r', encoding='utf-8') as file:
        response = json.load(file)
    return homework_output(split_day(response))


if __name__ == '__main__':
    while True:
        try:
            mode = int(input("Введите режим: "))
            break
        except ValueError:
            print("Некорректный ввод")
    if mode == 1:
        while True:
            try:
                d_date = datetime.strptime(input('Введите день: ') or datetime.now().strftime('%d'), '%d').replace(
                        year=datetime.now().year, month=datetime.now().month
                )
                if d_date.isoweekday() in [5, 6, 7]:
                    is_weekend = True
                break
            except ValueError:
                print("Некорректный формат даты. Попробуйте снова.")
        full_parse(d_date)
    elif mode == 2:
        print(homework_output(need_output=True))
    else:
        print("Режим не найден!")
