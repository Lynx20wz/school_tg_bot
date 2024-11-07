import json
from datetime import datetime
from typing import Optional, Union

import aiosqlite


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
                await db.execute(
                        '''
                        INSERT INTO users (username, userid, debug, setting_dw, setting_notification) 
                        VALUES (?, ?, ?, ?, ?)
                        ''', (*user,)
                )
                await db.commit()

    async def __call__(self, username: str) -> dict[str, Union[str, int, bool]]:
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

    async def restart_bot(self) -> list[int]:
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(
                    '''
                    CREATE TABLE IF NOT EXISTS users (
                        userid INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        debug INTEGER DEFAULT 0,
                        setting_dw INTEGER DEFAULT 0,
                        setting_notification INTEGER DEFAULT 0,
                        login TEXT,
                        homework_id INTEGER REFERENCES homework_cache(id)
                    );
                    CREATE TABLE IF NOT EXISTS homework_cache (
                        id INTEGER PRIMARY KEY,
                        timestamp INTEGER,
                        token TEXT,
                        cache TEXT
                    );
                    '''
            )
            async with db.execute('SELECT userid FROM users') as cursor:
                return [row[0] for row in await cursor.fetchall()]

    async def get_homework(self, username: 'str') -> Optional[tuple[datetime, str]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    '''
                    SELECT hc.timestamp, hc.cache
                    FROM users u
                    INNER JOIN homework_cache hc ON hc.id = u.homework_id
                    WHERE u.username = ?;
                    ''', (username,)
            ) as cursor:
                data = cursor.fetchone()
                data[0] = datetime.strptime(data[0], '%Y-%m-%d %H:%M')
                return await data

    async def update_homework_cache(self, username: str, homework: dict, token: str = None):
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            if token:
                await db.execute(
                    '''
                                        UPDATE homework_cache
                                        SET timestamp = ?, token = ?, cache = ?
                                        WHERE id = (
                                            SELECT u.homework_id
                                            FROM users u
                                            WHERE u.username = ?
                                        )
                                    ''', (datetime.now().strftime('%Y-%m-%d %H:%M'), token, json.dumps(homework), username)
                    )
            else:
                await db.execute(
                        '''
                        UPDATE homework_cache
                        SET timestamp = ?, cache = ?
                        WHERE id = (
                            SELECT u.homework_id
                            FROM users u
                            WHERE u.username = ?
                        )
                    ''', (datetime.now().strftime('%Y-%m-%d %H:%M'), json.dumps(homework), username)
                )
            await db.commit()

    async def set_homework_id(self, username: str, homework: dict, token: str):
        async with aiosqlite.connect(self.path) as db:
            homework_str = json.dumps(homework, ensure_ascii=False)
            async with db.execute('SELECT id FROM homework_cache WHERE cache = ?', (homework_str,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    await db.execute('UPDATE users SET homework_id = ? WHERE username = ?', (result[0], username))
                else:
                    await db.execute(
                            'INSERT INTO homework_cache (timestamp, token, cache) VALUES (?, ?)',
                            (datetime.now().strftime('%Y-%m-%d %H:%M'), token, homework_str)
                    )
                    lastrowid = await db.execute('SELECT last_insert_rowid()')
                    homework_id = (await lastrowid.fetchone())[0]
                    await db.execute('UPDATE users SET homework_id = ? WHERE username = ?', (homework_id, username))
                await db.commit()

    async def update_login(self, username: str, login: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                    '''
                    UPDATE users SET login = ? WHERE username = ?
                    ''', (login, username)
            )
            await db.commit()

    async def get_login(self, username) -> Optional[tuple[str]]:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT login FROM users WHERE username = ?", (username,)) as cursor:
                result = await cursor.fetchone()

                if result is not None:
                    return result[0]

    async def get_homework_token(self, username):
        pass
