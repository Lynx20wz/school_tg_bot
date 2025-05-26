import re
from datetime import datetime, timedelta
from typing import Iterator
from collections import namedtuple

from pydantic import BaseModel, Field
from requests import Response

from bot.bin import get_weekday

LinkInfo = namedtuple('LinkInfo', ['name', 'link'])


class Lesson(BaseModel):
    name: str
    homework: str = Field(frozen=True)
    links: list[LinkInfo] = Field(examples=[LinkInfo('name', 'link')])


class StudyDay(BaseModel):
    name: str
    date: datetime = Field(frozen=True)
    lessons: list[Lesson]

    def __iter__(self) -> Iterator[Lesson]:
        return iter(self.lessons)

    def __len__(self) -> int:
        return len(self.lessons)


class Homework:
    def __init__(
        self,
        id_: int,
        begin: datetime,
        end: datetime,
        response: Response = None,
        days: list[StudyDay] = None,
    ):
        # Date
        self.id_: int = id_
        self._begin: datetime = begin
        self._end: datetime = end
        self.date: tuple[datetime, datetime] = (begin, end)

        # Data
        if days:
            self.__days: list[StudyDay] = days
        elif response:
            self.__days: list[StudyDay] = self.__get_ready_homework(response)
        else:
            raise ValueError('Either response or days must be provided.')

    def __iter__(self) -> Iterator[StudyDay]:
        return iter(self.__days)

    def __getitem__(self, item) -> StudyDay:
        return self.__days[item]

    # Properties
    @property
    def begin(self) -> datetime:
        return self._begin

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def days(self) -> list[StudyDay]:
        return self.__days

    def __get_ready_homework(self, raw_response: dict) -> list[StudyDay]:
        """Collect ready homework data from raw response."""
        days = [
            StudyDay(name=day, date=datetime.now() + timedelta(days=i), lessons=[])
            for i, day in enumerate(get_weekday()[:5])
        ]

        for lesson in raw_response['payload']:
            date = datetime.strptime(lesson['date'], '%Y-%m-%d')
            if add_materials := lesson.get('additional_materials'):
                links = [
                    self.__process_material_item(item)
                    for mat in add_materials
                    for item in mat.get('items')
                ]
            else:
                links = []
            if lesson['homework'].lower() not in [None, '.', 'не задано'] or links:
                days[date.weekday()].lessons.append(
                    Lesson(
                        name=lesson.get('subject_name'),
                        homework=lesson.get('homework').strip(),
                        links=links,
                    )
                )

        return days

    @staticmethod
    def __process_material_item(item: dict) -> tuple[str, str]:
        """Processes the individual material and returns the reference information.

        Returns:
            A dictionary which contains links for each lesson
        """
        # FIXME: links doesn't work
        if re.search(r'\.(?:png|jpg|docx|pptx)$', item.get('title', ''), re.MULTILINE):
            return item.get('title'), item.get('link')
        else:
            return item.get('title'), item['urls'][2]['url']
