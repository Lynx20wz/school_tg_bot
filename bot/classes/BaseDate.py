import json
import os
from datetime import datetime
from typing import Optional, Union

import aiosqlite

from bot.bin import logger, BD_PATH, BD_BACKUP_PATH
from bot.classes.Homework import Lesson, StudyDay, Homework


class BaseDate:
    _instance = None

    def __new__(cls, *args, **kwargs):  # Singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug('An instance of BaseDate class was created')
        return cls._instance

    def __init__(self, path: str = BD_PATH, backup_path: str = BD_BACKUP_PATH):
        self.path = path
        self.backup_path = backup_path

    async def __call__(self, username: str = None) -> dict[str, Union[str, int, bool]]:
        return await self.get_user(username)

    async def restart_bot(self, load_backup: bool = True):
        exists = os.path.exists(self.path)
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    userid INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    debug INTEGER DEFAULT 0,
                    setting_dw INTEGER DEFAULT 0,
                    setting_notification INTEGER DEFAULT 0,
                    setting_hide_link INTEGER DEFAULT 0,
                    token TEXT,
                    student_id INTEGER,
                    homework_id INTEGER REFERENCES homework_cache(id)
                );
                CREATE TABLE IF NOT EXISTS homework_cache (
                    id INTEGER PRIMARY KEY,
                    begin TEXT NOT NULL,
                    end TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS study_days (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    homework_id INTEGER,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (homework_id) REFERENCES homework_cache(id) ON DELETE CASCADE
                );      
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_day_id INTEGER,
                    name TEXT NOT NULL,
                    homework TEXT,
                    links TEXT,
                    FOREIGN KEY (study_day_id) REFERENCES study_days(id) ON DELETE CASCADE
                );
                """
            )

            if load_backup and not exists and os.path.exists(self.backup_path):
                await self.backup_load()

    # User
    async def add_user(self, user: tuple) -> dict[str, Union[str, int, bool]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            while True:
                async with db.execute(
                    'SELECT userid FROM users WHERE userid = ?', (user[1],)
                ) as cursor:
                    res = await cursor.fetchone()
                    if res:
                        return dict(res)
                logger.info(f'{user[0]} was added in the database')
                await db.execute(
                    """
                    INSERT INTO users (username, userid, debug, setting_dw, setting_notification, setting_hide_link) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (*user,),
                )
                await db.commit()

    async def get_user(
        self, username: str = None
    ) -> Union[dict[str, Union[str, bool, int]], list[dict[str, Union[str, bool, int]]]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row

            if username:
                async with db.execute(
                    'SELECT * FROM users WHERE username = ?', (username,)
                ) as cursor:
                    user = await cursor.fetchone()
                    return dict(user) if user else None
            else:
                async with db.execute('SELECT * FROM users') as cursor:
                    users = await cursor.fetchall()
                    return [dict(user) for user in users]

    async def update_user(self, user):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET debug = ?,
                    setting_dw = ?,
                    setting_notification = ?,
                    setting_hide_link = ?,
                    token = ?,
                    student_id = ?
                WHERE username = ?
                """,
                (
                    user.debug,
                    user.setting_dw,
                    user.setting_notification,
                    user.setting_hide_link,
                    user.token,
                    user.student_id,
                    user.username,
                ),
            )
            await db.commit()

    async def delete_user(self, userid: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute('DELETE FROM users WHERE userid = ?', (userid,))
            await db.execute(
                """
                    DELETE FROM homework_cache
                    WHERE id IN (
                        SELECT homework_id 
                        FROM users 
                        WHERE userid = ?
                    )
                    AND NOT EXISTS (
                        SELECT 1
                        FROM users
                        WHERE homework_id = homework_cache.id
                    )
                    """,
                (userid, userid),
            )
            await db.commit()

    async def set_homework_id(self, username: str, homework: dict):
        async with aiosqlite.connect(self.path) as db:
            logger.debug(homework['date'])
            homework['date']['timestamp'] = datetime.now().timestamp()
            logger.debug(homework['date'])
            homework_str = json.dumps(homework, ensure_ascii=False)
            async with db.execute(
                'SELECT id FROM homework_cache WHERE cache = ?', (homework_str,)
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    await db.execute(
                        'UPDATE users SET homework_id = ? WHERE username = ?',
                        (result[0], username),
                    )
                else:
                    await db.execute(
                        f'INSERT INTO homework_cache (cache) VALUES (?)',
                        (homework_str,),
                    )
                    last_row_id = await db.execute('SELECT last_insert_rowid()')
                    homework_id = (await last_row_id.fetchone())[0]
                    await db.execute(
                        'UPDATE users SET homework_id = ? WHERE username = ?',
                        (homework_id, username),
                    )
                await db.commit()

    async def get_token(self, username: str) -> str:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                'SELECT token FROM users WHERE username = ?', (username,)
            ) as result:
                token = await result.fetchone()
                if token:
                    return token[0]
                return None

    # Homework
    async def save_homework(self, username: str, homework: Homework):
        async with aiosqlite.connect(self.path) as db:
            # Check if there is a homework_id for the user
            async with db.execute(
                """
                SELECT homework_id
                FROM users
                WHERE username = ?
                """,
                (username,),
            ) as cursor:
                result = await cursor.fetchone()

            if not result[0]:
                # If there is no homework_id, create a new record
                async with db.execute(
                    """
                    INSERT INTO homework_cache (begin, end, timestamp)
                    VALUES (?, ?, ?)
                    """,
                    (
                        homework.begin.isoformat(),
                        homework.end.isoformat(),
                        datetime.now().isoformat(),
                    ),
                ) as cursor:
                    homework_id = cursor.lastrowid
                await db.execute(
                    """
                    UPDATE users
                    SET homework_id = ?
                    WHERE username = ?
                    """,
                    (homework_id, username),
                )
            else:
                # If homework_id exists, update timestamp
                homework_id = result[0]
                await db.execute(
                    """
                    UPDATE homework_cache
                    SET timestamp = ?
                    WHERE id = ?
                    """,
                    (datetime.now().isoformat(), homework_id),
                )
                # Clear old data
                await db.execute(
                    """
                    DELETE FROM study_days
                    WHERE homework_id = ?
                    """,
                    (homework_id,),
                )

            # Save study_days and lessons from homework
            for i, day in enumerate(homework):
                async with db.execute(
                    """
                    INSERT INTO study_days (homework_id, name, date)
                    VALUES (?, ?, ?)
                    """,
                    (homework_id, day.name, day.date.isoformat()),
                ) as cursor:
                    study_day_id = cursor.lastrowid

                # Save lessons
                for lesson in day.lessons:
                    await db.execute(
                        """
                        INSERT INTO lessons (study_day_id, name, homework, links)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            study_day_id,
                            lesson.name,
                            lesson.homework,
                            json.dumps(lesson.links, ensure_ascii=False),
                        ),
                    )

            await db.commit()

    async def get_homework(self, username: str) -> Optional[tuple[Homework, datetime]]:
        async with aiosqlite.connect(self.path) as db:
            # Get homework_id, begin, end, and timestamp
            async with db.execute(
                """
                    SELECT hc.id, hc.begin, hc.end, hc.timestamp
                    FROM users u
                             INNER JOIN homework_cache hc ON hc.id = u.homework_id
                    WHERE u.username = ?
                    """,
                (username,),
            ) as cursor:
                result = await cursor.fetchone()
                if not result:
                    return None
                homework_id, begin, end, timestamp = result
                begin = datetime.fromisoformat(begin)
                end = datetime.fromisoformat(end)
                timestamp = datetime.fromisoformat(timestamp)

            # Get study_days
            days = []
            async with db.execute(
                """
                    SELECT id, name, date
                    FROM study_days
                    WHERE homework_id = ?
                    ORDER BY date
                    """,
                (homework_id,),
            ) as cursor:
                async for day_row in cursor:
                    day_id, name, date = day_row
                    date = datetime.fromisoformat(date)

                    # Get lessons for study_day
                    lessons = []
                    async with db.execute(
                        """
                            SELECT name, homework, links
                            FROM lessons
                            WHERE study_day_id = ?
                            """,
                        (day_id,),
                    ) as lesson_cursor:
                        async for lesson_row in lesson_cursor:
                            lesson_name, lesson_homework, lesson_links = lesson_row
                            lessons.append(
                                Lesson(
                                    name=lesson_name,
                                    homework=lesson_homework,
                                    links=json.loads(lesson_links) if lesson_links else [],
                                )
                            )

                    days.append(StudyDay(name=name, date=date, lessons=lessons))

            # Create Homework object
            homework = Homework(id_=homework_id, begin=begin, end=end, days=days)
            return homework, timestamp

    # Other
    async def custom_command(
        self, command: str, args=None
    ) -> list | dict[str, Union[str, int, bool]]:
        async with aiosqlite.connect(self.path) as db:
            if args is not None:
                res = await db.execute(command, tuple(args))
            else:
                res = await db.execute(command)
            await db.commit()
            return await res.fetchall()

    async def backup_create(self):
        """The function creates a backup of the database."""
        if os.path.exists(self.path):
            logger.debug('Создание бэкапа')
            async with aiosqlite.connect(self.path) as db:
                async with aiosqlite.connect(self.backup_path) as backup_db:
                    await db.backup(backup_db)
        else:
            logger.debug('Бэкап не создан, так как база данных не существует')

    async def backup_load(self):
        """The function loads a backup of the database if "-back" isn't in arguments."""
        logger.debug('Загрузка бэкапа')
        async with aiosqlite.connect(self.backup_path) as backup_db:
            async with aiosqlite.connect(self.path) as db:
                await backup_db.backup(db)
