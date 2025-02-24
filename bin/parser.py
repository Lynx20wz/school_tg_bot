import re
from datetime import datetime, timedelta
from typing import Union

import requests

from bin import ExpiredToken, ServerError, logger


def check_response(func:callable):
    """
    Wrapper for function, which check for token and status code in response

    Args:
        func (callable): Function, which need token for request and returns requests.Response
    Returns:
        Server response as a dictionary
    Raises:
        NoToken: when user doesn't have token
        ExpiredToken: when token is expired
        ServerError: when request failed for other reasons
    """

    def wrapped(*args, **kwargs):
        gen = func(*args, **kwargs)
        response = next(gen)

        if response.status_code == 401:
            logger.warning(f'Срок действия токена истёк!: {response.status_code}\n{response.text}')
            raise ExpiredToken()
        elif response.status_code >= 400:
            logger.warning(f'Произошла ошибка: {response.status_code}\n{response.text}')
            raise ServerError()
        else:
            return next(gen)
    return wrapped
def get_weekday(number: int = None) -> Union[str, list[str]]:
    weekdays = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    }
    if not number:
        return [name_day for name_day in weekdays.values()]
    else:
        return weekdays.get(number)

@check_response
def get_homework_from_website(
    token: str, student_id: int, date: datetime = datetime.now()
) -> dict:
    """
    Парсит данные со школьного портала и заносит их в файл в формате json.
    :param token: токен авторизации для парсинга с госулслуг
    :param student_id: id ученика
    :param date: текущая дата
    :return: Json-файл с домашним заданием.
    """
    date_in_str = datetime(datetime.now().year, date.month, date.day)

    day = date_in_str.isoweekday()
    monday = (
        date_in_str - timedelta(days=(day - 1))
        if day < 6
        else date_in_str - timedelta(days=(day - 8))
    )

    begin_date = monday.strftime('%Y-%m-%d')
    end_date = (monday + timedelta(days=4)).strftime('%Y-%m-%d')

    logger.info(f'{begin_date} - {end_date}')

    if student_id is None:
        student_id = get_student_id(token)

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + token,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
        'Referer': 'https://authedu.mosreg.ru/diary/homeworks/homeworks/',
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
    params = {'from': begin_date, 'to': end_date, 'student_id': student_id}
    cookie = {'aupd_token': token}

    response = requests.get(
        'https://authedu.mosreg.ru/api/family/web/v1/homeworks',
        params=params,
        cookies=cookie,
        headers=headers,
    )
    yield response

    output = response.json()
    output['date'] = {}
    output['date']['begin_date'] = datetime.isoformat(datetime.strptime(begin_date, '%Y-%m-%d'))
    output['date']['end_date'] = datetime.isoformat(datetime.strptime(end_date, '%Y-%m-%d'))
    yield output

@check_response
def get_student_id(token: str) -> int:
    """
    :param token: токен авторизации для "Моя школа"
    :return: student_id с "Моя школа"
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'zip, deflate, br',
        'Connection': 'keep-alive',
        'Auth-Token': token,
        'Authorization': token,
    }

    response = requests.get(
        'https://myschool.mosreg.ru/acl/api/users/profile_info', headers=headers
    )
    yield response

    yield response.json()[0]['id']

@check_response
def get_person_id(token: str) -> str:
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + token,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
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

    json_data = {'auth_token': token}

    response = requests.post(
        'https://authedu.mosreg.ru/api/ej/acl/v1/sessions',
        headers=headers,
        json=json_data,
    )
    yield response

    yield response.json()['person_id']

@check_response
def get_marks(
    student_id: int, token: str, date: datetime = datetime.now()
) -> tuple[tuple[datetime], dict]:
    """
    :param student_id: id ученика
    :param date: текущая дата
    :param token: токен авторизации для "Моя школа"
    :return: оценки ученика
    """

    date_in_str = datetime(datetime.now().year, date.month, date.day)

    day = date_in_str.isoweekday()
    monday = date_in_str - timedelta(days=(day - 1))

    begin_date = monday.strftime('%Y-%m-%d')
    end_date = (monday + timedelta(days=4)).strftime('%Y-%m-%d')

    # logger.debug(f'{begin_date} - {end_date}')

    cookie = {'aupd_token': token}

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + token,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
        'Referer': 'https://authedu.mosreg.ru/diary/marks/current-marks/',
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

    params = {'from': begin_date, 'to': end_date, 'student_id': student_id}

    response = requests.get(
        'https://authedu.mosreg.ru/api/family/web/v1/marks',
        params=params,
        cookies=cookie,
        headers=headers,
    )
    yield response

    yield (monday, monday + timedelta(days=4)), response.json()

@check_response
def get_schedule(token: str) -> tuple[datetime, dict]:
    """
    :param token: токен авторизации для "Моя школа"
    :return: расписание для ученика
    """

    person_id = get_person_id(token)

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + token,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
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

    today = datetime.now().isoweekday()
    if today in [5, 6, 7]:
        schedule_day = 1
        date = datetime.now() + timedelta(days=7 - today + 1)
    else:
        schedule_day = today + 1
        date = datetime.now() + timedelta(days=1)
    date_str = date.strftime('%Y-%m-%d')

    logger.debug(f'{date} - {schedule_day}')

    params = {'person_ids': person_id, 'begin_date': date_str, 'end_date': date_str}

    response = requests.get(
        'https://authedu.mosreg.ru/api/eventcalendar/v1/api/events',
        headers=headers,
        params=params,
    )
    yield response

    yield date, response.json()


def get_links_in_lesson(response: dict[str, dict]) -> dict:
    """
    :param response: словарь который содержит в себе домашнее задание
    :type response: dict
    :return: изначальный словарь, но ключом links в каждом уроке будет подробная информация об уроке
    :rtype: dict
    """

    links = {day: {} for day in get_weekday()[:5]}
    for day_name, day in response.get('дни').items():
        for lesson in day:
            add_mat: dict | None = lesson.get('additional_materials')
            if add_mat:
                for mat in add_mat:
                    if re.match('test_.*', mat.get('type')):
                        links[day_name][lesson.get('subject_name')] = [
                            item.get('urls')[2].get('url')
                            for i, item in enumerate(mat.get('items'), start=1)
                        ]

    response['links'] = links
    return response


def split_day(response: dict[str, dict]) -> dict:
    """
    Делит уроки из response по дням.

    :param response: Принимает в себя dict с домашним заданием.
    """
    lessons_dict = {
        'дни': {day: [] for day in get_weekday()[:5]},
        'date': response['date'],
    }
    for i, lesson in enumerate(response['payload'], start=1):
        date_lesson = datetime.strptime(lesson['date'], '%Y-%m-%d').isoweekday()
        date_weekday = get_weekday(date_lesson)
        lessons_dict['дни'][date_weekday].append(lesson)
    return lessons_dict


def homework_output(
    dict_hk: dict = None, need_output: bool = False
) -> Union[dict, str]:
    """
    Функция для вывода домашнего задания.

    :param dict_hk: Словарь с информацией о домашних заданиях.
    :param need_output: Нужен ли вывод строки или вернуть словарь.
    :return: Возвращает строку с информацией о домашнем задании.
    """
    output = {}
    for day_name, day in dict_hk['дни'].items():  # прохожу по всем дням
        day_list = []
        for lid in day:  # (lesson in day) прохожусь по урокам в дне (day)
            name = lid.get('subject_name')
            if name == 'Труд (технология)':
                name = 'Технология'
            if name == 'Музыка':
                name = 'МХК'

            links = dict_hk['links'][day_name].get(name)
            homework = lid.get('homework')
            if homework in ['.', ''] or 'Не задано' in homework:
                pass
            else:
                lesson_info = {'name': name, 'links': links, 'homework': homework}
                day_list.append(lesson_info)
            output[day_name] = day_list
    output['date'] = dict_hk['date']

    if not need_output:
        return output
    else:
        return_output = ''
        for i, one_day in enumerate(output.values(), start=1):
            day_of_week = get_weekday(i)
            return_output += f'\n*{day_of_week}*:\n'
            for number_lesson, lesson in enumerate(one_day, start=1):
                return_output += (
                    f'{number_lesson}) {lesson[0]} ({lesson[1]}) - {lesson[2]}\n'
                )
        return_output += f'-------------------------------\nВсего задано уроков: {sum(len(day) for day in output.values())}'
        return return_output


def full_parse(
    *,
    token=None,
    student_id: int = None,
    date: datetime = datetime.now(),
    output: bool = False,
) -> dict:
    """
    Функция для полного анализа расписания.

    :param token: токен авторизации для парсинга с госулслуг
    :param student_id: id ученика
    :param date: Дата, для которой нужно произвести анализ. По умолчанию - сегодняшняя дата.
    :param output: Нужен ли вывод строки или вернуть словарь.
    """

    response = get_homework_from_website(token, student_id, date)
    ready_for_output = get_links_in_lesson(split_day(response))
    return homework_output(ready_for_output, output)


if __name__ == '__main__':
    while True:
        try:
            mode = int(input('Введите режим: '))
            break
        except ValueError:
            print('Некорректный ввод')
    if mode == 1:
        while True:
            try:
                d_date = int(input('Введите день: ')) or datetime.now().strftime('%d')
                m_date = int(input('Введите месяц: ')) or datetime.now().strftime('%m')
                f_date = datetime(datetime.now().year, m_date, d_date)
                token = input('Введите токен: ')
                break
            except ValueError:
                print('Некорректный формат даты. Попробуйте снова.')
        print(full_parse(token=token, date=f_date, output=True))
    elif mode == 2:
        print(full_parse(date=datetime.now(), output=True))
    else:
        print('Режим не найден!')
