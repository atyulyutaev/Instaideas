from abc import ABC, abstractmethod
from collections.abc import Iterable

import asyncpg

import config

speech_styles = {
    1: {"name": "Ироничный", "link": "https://www.instagram.com/reel/C3xjy9_oLJj/?igsh=djd6OXJnYTNhNXNj"},
    2: {"name": "Легкомысленный", "link": "https://www.instagram.com/reel/C2J9k2tiovT/?igsh=MTQyNW1mbTVwejh1aA=="},
    3: {"name": "Серьёзный", "link": "https://www.instagram.com/reel/C4YM2tkvu30/?igsh=Y3k1Y2s4bjV5ZTdj"},
    4: {"name": "Вдохновляющий", "link": "https://www.instagram.com/reel/C4nFHaXtv5q/?igsh=dXk2MHVrNWViY2V0"},
    5: {"name": "Саркастический", "link": "https://www.instagram.com/reel/C4kfud3owB8/?igsh=OWxiNjNxcWh0bW1x"},
    6: {"name": "Учебный", "link": "https://www.instagram.com/reel/C4nFHaXtv5q/?igsh=dXk2MHVrNWViY2V0"},
    7: {"name": "Юмористический", "link": "https://www.instagram.com/reel/C4FvnsYIwqr/?igsh=MW83NGtycmdwc2Q2MQ=="},
    8: {"name": "Мотивирующий", "link": "https://www.instagram.com/reel/CnjqaGkKDAS/?igsh=cXV1bmIycTJvcTE5"},
}


class Author:
    def __init__(self, id: int, gender_id: int = None, age: int = None, preferred_speech_styles=None):
        if preferred_speech_styles is None:
            preferred_speech_styles = []

        self.id = id
        self.gender_id = gender_id
        self.age = age
        self.preferred_speech_styles = preferred_speech_styles

    @property
    def gender(self) -> str:
        return 'Мужчина' if self.gender_id == 0 else 'Женщина'

    def has_info(self):
        if not self.gender and not self.age and not self.preferred_speech_styles:
            return False
        return True

    def set_age(self, age: str) -> str | None:
        if not age.strip().isdigit():
            return "Возраст должен быть числом"

        self.age = int(age)

    def set_gender(self, gender: str) -> str | None:
        gender = gender.strip()
        if gender.lower() in ['м', 'муж', 'мужчина']:
            self.gender_id = 0
        elif gender.lower() in ['ж', 'жен', 'женщина']:
            self.gender_id = 1
        else:
            return "Напишите либо М, либо Ж"

    def toggle_speech_style(self, preferred_speech_style: int):
        if preferred_speech_style not in self.preferred_speech_styles:
            self.preferred_speech_styles.append(preferred_speech_style)
        else:
            self.preferred_speech_styles.remove(preferred_speech_style)

    def add_preferred_speech_styles(self, preferred_speech_styles: list[int]):
        self.preferred_speech_styles = preferred_speech_styles


class AuthorRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Author:
        pass

    @abstractmethod
    async def get_all(self) -> Iterable[Author]:
        pass

    @abstractmethod
    async def save(self, author: Author) -> None:
        pass

    @abstractmethod
    async def update(self, author: Author) -> None:
        pass


class PostgresAuthorRepository(AuthorRepository):
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def close(self):
        await self.pool.close()

    async def get_by_id(self, id: int) -> Author:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow('SELECT * FROM authors WHERE id = $1', id)
            if row:
                return Author(
                    id=row['id'],
                    gender_id=row['gender_id'],
                    age=row['age'],
                    preferred_speech_styles=row['preferred_speech_styles'],
                )
            return None

    async def get_all(self) -> Iterable[Author]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch('SELECT * FROM authors')
            return [
                Author(
                    id=row['id'],
                    gender_id=row['gender_id'],
                    age=row['age'],
                    preferred_speech_styles=row['preferred_speech_styles'],
                ) for row in rows
            ]

    async def save(self, author: Author) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                'INSERT INTO authors(id, gender_id, age, preferred_speech_styles) VALUES($1, $2, $3, $4)',
                author.id, author.gender_id, author.age, author.preferred_speech_styles
            )

    async def update(self, author: Author) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                'UPDATE authors SET gender_id = $2, age = $3, preferred_speech_styles = $4 WHERE id = $1',
                author.id, author.gender_id, author.age, author.preferred_speech_styles
            )

    async def update_or_create(self, author: Author) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO authors(id, gender_id, age, preferred_speech_styles) VALUES($1, $2, $3, $4)
                    ON CONFLICT (id)
                    DO UPDATE SET
                    gender_id = EXCLUDED.gender_id,
                    age = EXCLUDED.age,
                    preferred_speech_styles = EXCLUDED.preferred_speech_styles;
                ''', author.id, author.gender_id, author.age, author.preferred_speech_styles
                                     )


class DumpAuthorRepository(AuthorRepository):
    authors: dict[int, Author] = {}

    async def get_by_id(self, id: int) -> Author:
        return self.authors.get(id)

    async def get_all(self) -> Iterable[Author]:
        return self.authors.values()

    async def save(self, author: Author) -> None:
        self.authors[author.id] = author

    async def update(self, author: Author) -> None:
        self.authors[author.id] = author


author_repository = PostgresAuthorRepository(config.DATABASE_URL)
