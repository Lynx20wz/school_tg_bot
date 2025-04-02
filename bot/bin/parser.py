import re
from datetime import datetime, timedelta
from typing import Union

import requests

from bot.bin import ExpiredToken, ServerError, logger


def check_response(func: callable):
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

def get_monday_date(date: datetime) -> datetime:
    name_of_day = date.isoweekday()
    return (
        date - timedelta(days=(name_of_day - 1))
        if name_of_day < 6
        else date - timedelta(days=(name_of_day - 8))
    )


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
    The function is parsing homework from "Моя школа"

    Args:
        token (str): Authorization token for parsing from "Моя школа"
        student_id (int): Student id
        date (datetime): Date for which you need to analyze. By default - today's date
    Returns:
        A response from "Моя школа" with homework as dictionary
    """

    monday = get_monday_date(date)

    date_start = monday
    date_end = (monday + timedelta(days=4))

    logger.info(f'{date_start} - {date_end}')

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
    params = {
        'from': date_start.strftime('%Y-%m-%d'),
        'to': date_end.strftime('%Y-%m-%d'),
        'student_id': student_id
    }
    cookie = {'aupd_token': token}

    response = requests.get(
            'https://authedu.mosreg.ru/api/family/web/v1/homeworks',
            params=params,
            cookies=cookie,
            headers=headers,
    )
    yield response

    output = response.json()
    output['date'] = {
        'begin_date': datetime.isoformat(date_start),
        'end_date': datetime.isoformat(date_end),
    }
    yield output


@check_response
def get_student_id(token: str) -> int:
    """
    The function for getting student id

    Args:
        token (str): Authorization token for parsing from "Моя школа"
    Returns:
        student_id for "Моя школа"
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
    student_id: int,
    token: str,
    date: datetime = datetime.now(),
    split: bool = True
) -> tuple[tuple[datetime], dict]:
    """
    The function for getting marks

    Args:
        student_id (int): Student id
        date (datetime): Date for which you need to analyze. By default - today's date
        token (str): Authorization token for parsing from "Моя школа"
        split(bool): Should be divided by days
    Returns:
        Tuple of date and marks
    """
    monday = get_monday_date(date)

    date_start = monday
    date_end = (monday + timedelta(days=4))

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

    params = {
        'from': date_start.strftime('%Y-%m-%d'),
        'to': date_end.strftime('%Y-%m-%d'),
        'student_id': student_id
    }

    response = requests.get(
            'https://authedu.mosreg.ru/api/family/web/v1/marks',
            params=params,
            cookies=cookie,
            headers=headers,
    )
    yield response

    output = response.json()
    output['date'] = {
        'begin_date': date_start,
        'end_date': date_end,
    }

    if split:
        yield split_day(output, 'marks')
    else:
        yield output


@check_response
def get_schedule(token: str, split: bool=True) -> tuple[datetime, dict]:
    """
    The function for getting the schedule

    Args:
        token (str): Authorization token for parsing from "Моя школа"
        split (bool): Split the schedule into days
    Returns:
        Tuple of date and schedule
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

    monday = get_monday_date(datetime.now())
    date_start = monday
    date_end = (monday + timedelta(days=4))

    logger.debug(f'{date_start} - {date_end}')

    params = {
        'person_ids': person_id,
        'begin_date': date_start.strftime('%Y-%m-%d'),
        'end_date': date_end.strftime('%Y-%m-%d')
    }

    response = requests.get(
            'https://authedu.mosreg.ru/api/eventcalendar/v1/api/events',
            headers=headers,
            params=params,
    )
    yield response

    output = response.json()
    output['date'] = {
        'begin_date': date_start,
        'end_date': date_end,
    }

    if split:
        yield split_day(output, 'schedule')
    else:
        yield output

def get_links_in_lesson(response: dict[str, dict]) -> dict:
    """
    Gets the links in each lesson for themselves

    Args:
        response (dict[str, dict]): dictionary which contains homework
    Returns:
        Initial dictionary, but the key links in each lesson will be all links for the lesson
    """
    links = {day: {} for day in get_weekday()[:5]}
    for day_name, day in response['days'].items():
        for lesson in day:
            add_mat: dict | None = lesson.get('additional_materials')
            if add_mat:
                for mat in add_mat:
                    if re.search(r'\.(?:png|jpg|docx)$', mat.get('items')[0].get('title') , re.MULTILINE):
                        links[day_name][lesson.get('subject_name')] = [
                            {
                                'link': item.get('link'),
                                'title': item.get('title')
                            }
                            for item in mat.get('items')
                        ]
                    else:
                        links[day_name][lesson.get('subject_name')] = [
                            {
                                'link': item.get('urls')[2].get('url'),
                                'title': item.get('title')
                            }
                            for item in mat.get('items')
                        ]

    response['links'] = links
    return response


def split_day(response: dict[str, dict], func_name: str) -> dict[str, dict]:
    """
    Split the lessons or marks or schedule from response by days.

    Args:
        response (dict[str, dict]): Takes in dict with homework
        func_name (str): What needs to be split up
    """

    lessons_dict = {
            'date': response['date'],
            'days': {day: [] for day in get_weekday()[:5]}
        }

    if func_name == 'homework':
        for lesson in response['payload']:
            date = datetime.strptime(lesson['date'], '%Y-%m-%d')
            name_of_day = get_weekday(date.isoweekday())
            lessons_dict['days'][name_of_day].append(lesson)

    elif func_name == 'schedule':
        lessons_dict['total_count'] = response['total_count']
        for lesson in response['response']:
            date = datetime.fromisoformat(lesson['start_at'])
            name_of_day = get_weekday(date.isoweekday())
            lessons_dict['days'][name_of_day].append(lesson)

    elif func_name == 'marks':
        if response['payload']:
            for mark in response['payload']:
                date = datetime.strptime(mark['date'], '%Y-%m-%d')
                name_of_day = get_weekday(date.isoweekday())
                lessons_dict['days'][name_of_day].append((mark['subject_name'], mark['value']))
        else:
            lessons_dict['days'] = None

    else:
        raise ValueError('Имя функции неверное!')

    return lessons_dict


def homework_output(
    dict_hk: dict = None
) -> Union[dict, str]:
    """
    The function for outputs homework

    Args:
        dict_hk (dict): Dictionary with information about homework
    Returns:
        Return string with information about homework
    """
    output = {'days': {}, 'date': dict_hk['date']}
    for day_name, day in dict_hk['days'].items():
        day_list = []
        for lid in day:  # (lesson in day) going over the lessons of the day
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
            output['days'][day_name] = day_list

    return output



def full_parse(
    *,
    token:str=None,
    student_id: int = None,
    date: datetime = datetime.now(),
) -> dict:
    """
    The function for full analysis of the schedule

    Args
        token (str): Authorization token for parsing from the "госуслуги"
        student_id (int): Student id
        date (datetime): Date for which you need to analyze. Defaults to today's date.
    """

    response = get_homework_from_website(token, student_id, date)
    ready_for_output = get_links_in_lesson(split_day(response, 'homework'))
    return homework_output(ready_for_output)