from datetime import datetime, timedelta

import requests

from bot.bin import logger, get_weekday
from bot.classes import Homework

def _get_header(token: str) -> dict:
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': f'Bearer {token}',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'DNT': '1',
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


def get_monday_date(date: datetime) -> datetime:
    name_of_day = date.isoweekday()
    return (
        date - timedelta(days=(name_of_day - 1))
        if name_of_day < 6
        else date - timedelta(days=(name_of_day - 8))
    )


def get_homework_from_website(token: str, student_id: int, date: datetime = datetime.now()) -> Homework:
    """The function is parsing homework from "Моя школа".

    Args:
        token (str): Authorization token for parsing from "Моя школа"
        student_id (int): Student id
        date (datetime): Date for which you need to analyze. By default - today's date
    Returns:
        A response from "Моя школа" with homework as dictionary
    """
    monday = get_monday_date(date)

    date_start = monday
    date_end = monday + timedelta(days=4)

    logger.debug(f'{date_start} - {date_end}')

    if student_id is None:
        student_id = get_student_id(token)

    params = {
        'from': date_start.strftime('%Y-%m-%d'),
        'to': date_end.strftime('%Y-%m-%d'),
        'student_id': student_id,
    }
    cookie = {'aupd_token': token}

    response = requests.get(
        'https://authedu.mosreg.ru/api/family/web/v1/homeworks',
        params=params,
        cookies=cookie,
        headers=_get_header(token),
    )

    return Homework(student_id, date_start, date_end, response)


def get_student_id(token: str) -> int:
    """The function for getting student id.

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
    return response.json()[0]['id']


def get_person_id(token: str) -> str:
    json_data = {'auth_token': token}

    response = requests.post(
        'https://authedu.mosreg.ru/api/ej/acl/v1/sessions',
        headers=_get_header(token),
        json=json_data,
    )
    return response.json()['person_id']


def get_marks(
    student_id: int, token: str, date: datetime = datetime.now(), split: bool = True
) -> tuple[tuple[datetime], dict]:
    """He function for getting marks.

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
    date_end = monday + timedelta(days=4)

    cookie = {'aupd_token': token}

    params = {
        'from': date_start.strftime('%Y-%m-%d'),
        'to': date_end.strftime('%Y-%m-%d'),
        'student_id': student_id,
    }

    response = requests.get(
        'https://authedu.mosreg.ru/api/family/web/v1/marks',
        params=params,
        cookies=cookie,
        headers=_get_header(token),
    )

    output = response.json()
    output['date'] = {
        'begin_date': date_start,
        'end_date': date_end,
    }

    if split:
        return split_day(output, 'marks')
    else:
        return output


def get_schedule(token: str, split: bool = True) -> tuple[datetime, dict]:
    """The function for getting the schedule.

    Args:
        token (str): Authorization token for parsing from "Моя школа"
        split (bool): Split the schedule into days
    Returns:
        Tuple of date and schedule
    """
    person_id = get_person_id(token)

    monday = get_monday_date(datetime.now())
    date_start = monday
    date_end = monday + timedelta(days=4)

    logger.info(f'{date_start} - {date_end}')

    params = {
        'person_ids': person_id,
        'begin_date': date_start.strftime('%Y-%m-%d'),
        'end_date': date_end.strftime('%Y-%m-%d'),
    }

    response = requests.get(
        'https://authedu.mosreg.ru/api/eventcalendar/v1/api/events',
        headers=_get_header(token),
        params=params,
    )

    output = response.json()
    output['date'] = {
        'begin_date': date_start,
        'end_date': date_end,
    }

    if split:
        return split_day(output, 'schedule')
    else:
        return output

#TODO Cut to the appropriate class
def split_day(response: dict[str, dict], func_name: str) -> dict[str, dict]:
    """Split the lessons or marks or schedule from response by days.

    Args:
        response (dict[str, dict]): Takes in dict with homework
        func_name (str): What needs to be split up
    """
    lessons_dict = {'date': response['date'], 'days': {day: [] for day in get_weekday()[:5]}}

    if func_name == 'schedule':
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
