import json
import os
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Union

import requests
from dotenv import load_dotenv

from bin import logger

load_dotenv()

def get_weekday(number):
    weekdays = {1: 'Понедельник',
                2: 'Вторник',
                3: 'Среда',
                4: 'Четверг',
                5: 'Пятница',
                6: 'Суббота',
                7: 'Воскресенье'}
    return weekdays.get(number)


class lesson_class:
    def __init__(self, day, name, cabinet_number, homework, /) -> None:
        self.day = day
        self.name = name
        self.cabinet_number = cabinet_number
        self.homework = homework

    def get_lesson_info(self):
        return self.name, self.day, self.cabinet_number, self.homework


def get_homework_from_website(login: str, date: datetime = datetime.now()) -> dict:
    """
    Парсит данные со школьного портала и заносит их в файл в формате json.
    :param login: логин для парсинга с госулслуг
    :param date: текущая дата
    :return: Json-файл с домашним заданием.
    """
    date_in_str = datetime(datetime.now().year, date.month, date.day)
    monday = (date_in_str + timedelta(days=7 + (1 - date_in_str.isoweekday()) if (1 - date_in_str.isoweekday()) != 0 else 0))
    begin_date = monday.strftime('%Y-%m-%d')
    end_date = (monday + timedelta(days=4)).strftime('%Y-%m-%d')

    logger.info(f'{begin_date} - {end_date}')



    def req(cookie):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Authorization': cookie.get('aupd_token'),
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'DNT': '1',
            'Profile-Id': '1530640',
            'Profile-Type': 'student',
            'Referer': 'https://authedu.mosreg.ru/diary/schedules/schedule',
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

        return requests.get(
                'https://authedu.mosreg.ru/api/eventcalendar/v1/api/events',
                params=params,
                cookies=cookie,
                headers=headers,
        )

    # if req(cookie)
    # cookies = get_token(login, password)
    # response = req(cookies)
    # if response.status_code > 400:
    #     logger.debug(response.text)
    #     raise ValueError('Пароль или логин неверный!')
    #
    # with open('../temp/school.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4)
    #
    # return cookies


def get_links_in_lesson(response: dict, cookies: dict) -> dict:
    """
    :param response: словарь который содержит в себе домашнее задание
    :param cookies: словарь с cookies
    :type response: dict
    :return: изначальный словарь, но ключом links в каждом уроке будет подробная информация об уроке
    :rtype: dict
    """
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': cookies.get('aupd_token'),
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
        'Profile-Id': '1530640',
        'Profile-Type': 'student',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'X-mes-subsystem': 'familyweb',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    params = (
        ('plan_id', '2751477'),
        ('school_id', '347'),
        ('ignore_owner', 'true'),
        ('with_modules', 'true'),
        ('with_topics', 'true'),
        ('with_lessons', 'true'),
        ('status', 'for_calendar_plan'),
    )

    # for lesson in response.get('response'):
    lesson = response.get('response')[8]
    try:
        lid, hid = lesson.get('id'), lesson.get('homework').get('entries')[0].get('homework_entry_id')
        headers['Referer'] = f'https://authedu.mosreg.ru/diary/schedules/lesson/{lid}_normal?active_tab=homework&sidebar=homeworks_{hid}'
        response_with_lesson_id = requests.get(
                'https://authedu.mosreg.ru/api/ej/plan/family/v1/lesson_plans', headers=headers, params=params, cookies=cookies
        ).text
        lesson['response_data'] = response_with_lesson_id
    except TypeError as e:
        logger.debug(f'Поймано исключение {lesson} - {e}')

    with open('../temp/school.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)
    return response


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
    if lessons:
        dow += 1
        lessons_dict['дни'].append({date_weekday: deepcopy(lessons)})
        lessons.clear()
    return lessons_dict


def homework_output(dict_hk: dict = None, need_output: bool = False) -> Union[dict, str]:
    """
    Функция для вывода домашнего задания.

    :param dict_hk: Словарь с информацией о домашних заданиях.
    :param need_output: Нужен ли вывод строки или вернуть словарь.
    :return: Возвращает строку с информацией о домашнем задании.
    """
    output = {}
    if dict_hk is None:
        with open('../temp/school.json', 'r', encoding='utf-8') as file:
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


def full_parse(login, date: datetime = datetime.now()) -> dict:
    """
    Функция для полного анализа расписания.

    :param login: логин для парсинга с госулслуг
    :param date: Дата, для которой нужно произвести анализ. По умолчанию - сегодняшняя дата.
    """
    cookies = get_homework_from_website(login, date)
    with open('../temp/school.json', 'r', encoding='utf-8') as file:
        response = json.loads(file.read())
    # get_links_in_lesson(response, cookies)
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
                d_date = int(input('Введите день: ')) or datetime.now().strftime('%d')
                m_date = int(input('Введите месяц: ')) or datetime.now().strftime('%m')
                f_date = datetime(datetime.now().year, m_date, d_date)
                break
            except ValueError:
                print("Некорректный формат даты. Попробуйте снова.")
        full_parse(os.getenv('GMAIL'), os.getenv('PASSWORD'), f_date)
    elif mode == 2:
        print(homework_output(need_output=True))
    else:
        print("Режим не найден!")
