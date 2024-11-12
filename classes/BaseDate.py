import json
from datetime import datetime
from types import NoneType
from typing import Optional, Union

import aiosqlite
from bin.config import BD_PATH, logger


class BaseDate:
    def __init__(self, path: str):
        self.path = path

    async def add_user(self, user: tuple) -> dict[str, Union[str, int, bool]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            while True:
                async with db.execute('SELECT userid FROM users WHERE userid = ?', (user[1],)) as cursor:
                    res = await cursor.fetchone()
                    if res:
                        return dict(res)
                logger.info(f'{user[0]} был добавлен в базу данных')
                await db.execute(
                        '''
                        INSERT INTO users (username, userid, debug, setting_dw, setting_notification) 
                        VALUES (?, ?, ?, ?, ?)
                        ''', (*user,)
                )
                await db.commit()

    async def __call__(self, username: str = None) -> dict[str, Union[str, int, bool]]:
        return await self.get_user(username)

    async def get_user(self, username: str = None) -> Union[dict[str, Union[str, bool, int]], list[dict[str, Union[str, bool, int]]]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row

            if username:
                async with db.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
                    user = await cursor.fetchone()
                    return dict(user) if user else None
            else:
                async with db.execute("SELECT * FROM users") as cursor:
                    users = await cursor.fetchall()
                    return [dict(user) for user in users]

    async def restart_bot(self) -> list[dict[str, Union[str, bool, int]]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            await db.executescript(
                    '''
                    CREATE TABLE IF NOT EXISTS users (
                        userid INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        debug INTEGER DEFAULT 0,
                        setting_dw INTEGER DEFAULT 0,
                        setting_notification INTEGER DEFAULT 0,
                        token TEXT,
                        student_id INTEGER,
                        homework_id INTEGER REFERENCES homework_cache(id)
                    );
                    CREATE TABLE IF NOT EXISTS homework_cache (
                        id INTEGER PRIMARY KEY,
                        timestamp INTEGER,
                        cache TEXT
                    );
                    '''
            )
            async with db.execute('SELECT DISTINCT * FROM users') as cursor:
                return [dict(user) for user in await cursor.fetchall()]

    async def get_homework(self, username: 'str') -> Optional[Union[tuple[datetime, str], str]]:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                    '''
                    SELECT hc.timestamp, hc.cache
                    FROM users u
                    INNER JOIN homework_cache hc ON hc.id = u.homework_id
                    WHERE u.username = ?;
                    ''', (username,)
            ) as cursor:
                data = await cursor.fetchone()
                logger.debug(data)
                if data is not None:
                    return datetime.strptime(data[0], '%Y-%m-%d %H:%M'), data[1]

    async def update_user(self, user):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                    'UPDATE users SET debug = ?, setting_dw = ?, setting_notification = ?, token = ?, student_id = ? WHERE username = ?',
                    (user.debug, user.setting_dw, user.setting_notification, user.token, user.student_id, user.username,)
            )
            await db.commit()

    async def update_homework_cache(self, /, username: str, homework: dict):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                    'SELECT id FROM homework_cache WHERE id = (SELECT homework_id FROM users WHERE username = ?)', (username,)
            ) as cursor:
                result = await cursor.fetchone()
                logger.debug(result)
                # если result == None то привязываем пользователя к новой ячейке таблицы в которую заносим токен, если result != None, то проверяем что такокого кэша нет в таблице, если есть удаляем запись с токеном и привязывыям пользователя туда
                if result is None:
                    await self.set_homework_id(username, homework)
                else:
                    await db.execute(
                            '''
                                UPDATE homework_cache SET timestamp = ?, cache = ? WHERE id = (SELECT homework_id FROM users WHERE username = ?)
                                ''',
                            (
                                datetime.now().strftime('%Y-%m-%d %H:%M'),
                                json.dumps(homework, ensure_ascii=False),
                                username,)
                    )

    async def set_homework_id(self, username: str, homework: dict):
        async with aiosqlite.connect(self.path) as db:
            homework_str = json.dumps(homework, ensure_ascii=False)
            async with db.execute('SELECT id FROM homework_cache WHERE cache = ?', (homework_str,)) as cursor:
                result = await cursor.fetchone()
                logger.debug(f'{result=}, {homework_str=}')
                if result:
                    await db.execute('UPDATE users SET homework_id = ? WHERE username = ?', (result[0], username))
                else:
                    await db.execute(
                            f'INSERT INTO homework_cache (timestamp,  cache) VALUES (?, ?)',
                            (datetime.now().strftime('%Y-%m-%d %H:%M'), homework_str)
                    )
                    last_row_id = await db.execute('SELECT last_insert_rowid()')
                    homework_id = (await last_row_id.fetchone())[0]
                    await db.execute('UPDATE users SET homework_id = ? WHERE username = ?', (homework_id, username))
                await db.commit()

    async def get_token(self, username: str) -> str:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute('SELECT token FROM users WHERE username = ?', (username,)) as result:
                token = await result.fetchone()
                if token:
                    return token[0]

    async def custom_command(self, command: str, args = None) -> list | dict[str, Union[str, int, bool]]:
        # logger.debug(f"{command=}\n{args=}")
        async with aiosqlite.connect(self.path) as db:
            if args is not None:
                res = await db.execute(command, tuple(args))
            else:
                res = await db.execute(command)
            await db.commit()
            return await res.fetchall()


db = BaseDate(BD_PATH)

__all__ = ['db', 'BaseDate']