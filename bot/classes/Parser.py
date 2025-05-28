from datetime import datetime, timedelta
from typing import Optional, Literal

from requests import HTTPError, get, post

from bot.bin import logger, get_weekday

from bot.classes import Homework
from bot.until import ExpiredToken, ServerError


class Parser:
    def __init__(self, token: Optional[str] = None, student_id: Optional[int] = None):
        self.token = token
        if student_id:
            self.student_id = student_id
        elif token:
            self.student_id = self.get_student_id()
        else:
            self.student_id = None

    # TODO Cut to the appropriate class
    @staticmethod
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

    def _request(
        self,
        url: str,
        method: Literal['GET', 'POST'] = 'GET',
        headers: dict | None = None,
        params: dict | None = None,
        cookies: dict | None = None,
    ) -> dict:
        """Send HTTP request and return JSON response.

        Args:
            url: Target URL.
            method: HTTP method ('GET' or 'POST').
            headers: Optional request headers.
            params: Optional query or body parameters.
            cookies: Optional cookies.

        Returns:
            JSON response as a dictionary.

        Raises:
            ServerError: If server returns 400 status code.
            ExpiredToken: If server returns 401 status code.
            HTTPError: For other HTTP errors.
        """
        headers = headers or self._headers
        cookies = cookies or {}
        params = params or {}

        try:
            response = {'GET': get, 'POST': post}[method](
                url,
                headers=headers,
                params=params,
                cookies=cookies,
                json=params if method == 'POST' else None,
            )
            response.raise_for_status()
        except KeyError:
            raise ValueError(f'Unsupported method: {method}')
        except HTTPError as e:
            if e.response.status_code == 400:
                raise ServerError
            if e.response.status_code == 401:
                raise ExpiredToken
            raise

        return response.json()

    @staticmethod
    def _get_monday_date(date: datetime) -> datetime:
        name_of_day = date.isoweekday()
        return (
            date - timedelta(days=(name_of_day - 1))
            if name_of_day < 6
            else date - timedelta(days=(name_of_day - 8))
        )

    @property
    def _headers(self) -> dict:
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Authorization': f'Bearer {self.token}',
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

    def _get_person_id(self) -> str:
        json_data = {'auth_token': self.token}

        response = self._request(
            'https://authedu.mosreg.ru/api/ej/acl/v1/sessions', params=json_data, method='POST'
        )
        return response['person_id']

    # Methods for obtaining data
    def get_homework(self, date: datetime = datetime.now()) -> Homework:
        """The function is parsing homework from "Моя школа".

        Args:
            date (datetime): Date for which you need to analyze. By default - today's date
        Returns:
            A response from "Моя школа" with homework as dictionary
        """
        monday = self._get_monday_date(date)

        date_start = monday
        date_end = monday + timedelta(days=4)

        logger.debug(f'{date_start} - {date_end}')

        if self.student_id is None:
            self.student_id = self.get_student_id()

        params = {
            'from': date_start.strftime('%Y-%m-%d'),
            'to': date_end.strftime('%Y-%m-%d'),
            'student_id': self.student_id,
        }

        response = self._request(
            'https://authedu.mosreg.ru/api/family/web/v1/homeworks',
            params=params,
            # cookies=cookie,
        )

        return Homework(self.student_id, date_start, date_end, response)

    def get_marks(
        self, date: datetime = datetime.now(), split: bool = True
    ) -> tuple[tuple[datetime], dict]:
        """He function for getting marks.

        Args:
            date (datetime): Date for which you need to analyze. By default - today's date
            split(bool): Should be divided by days
        Returns:
            Tuple of date and marks
        """
        monday = self._get_monday_date(date)

        date_start = monday
        date_end = monday + timedelta(days=4)

        cookie = {'aupd_token': self.token}

        params = {
            'from': date_start.strftime('%Y-%m-%d'),
            'to': date_end.strftime('%Y-%m-%d'),
            'student_id': self.student_id,
        }

        response = self._request(
            'https://authedu.mosreg.ru/api/family/web/v1/marks',
            params=params,
            cookies=cookie,
        )

        response['date'] = {
            'begin_date': date_start,
            'end_date': date_end,
        }

        if split:
            return self.split_day(response, 'marks')
        else:
            return response

    def get_schedule(self, split: bool = True) -> dict:
        """The function for getting the schedule.

        Args:
            split (bool): Split the schedule into days
        Returns:
             A response from "Моя школа" with schedule as dictionary
        """
        person_id = self._get_person_id()

        monday = self._get_monday_date(datetime.now())
        date_start = monday
        date_end = monday + timedelta(days=4)

        logger.debug(f'{date_start} - {date_end}')

        params = {
            'person_ids': person_id,
            'begin_date': date_start.strftime('%Y-%m-%d'),
            'end_date': date_end.strftime('%Y-%m-%d'),
        }

        response = self._request(
            'https://authedu.mosreg.ru/api/eventcalendar/v1/api/events',
            params=params,
        )

        response['date'] = {
            'begin_date': date_start,
            'end_date': date_end,
        }

        if split:
            return self.split_day(response, 'schedule')
        else:
            return response

    def get_student_id(self) -> int:
        """The function for getting student id.

        Returns:
            student_id for "Моя школа"
        """
        headers = self._headers
        headers['Auth-Token'] = self.token

        return self._request('https://myschool.mosreg.ru/acl/api/users/profile_info', headers=headers)[0]['id']
