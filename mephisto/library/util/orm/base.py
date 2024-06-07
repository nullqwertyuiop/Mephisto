from asyncio import Semaphore
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy import Executable, Result, update, insert, select, delete, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatabaseEngine:
    engine: AsyncEngine
    mutex: Semaphore | None

    def __init__(self, link: str, mutex: Semaphore | None = None, **adapter):
        self.engine = create_async_engine(link, **adapter, echo=False)
        self.mutex = mutex

    @asynccontextmanager
    async def __lock(self):
        try:
            if self.mutex:
                await self.mutex.acquire()
            yield
        finally:
            if self.mutex:
                self.mutex.release()

    async def execute(self, sql: Executable, **kwargs) -> Result:
        async with self.__lock():
            async with AsyncSession(self.engine) as session:
                try:
                    result = await session.execute(sql, **kwargs)
                    await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    raise e

    async def all(self, table, *where):
        return (await self.execute(select(table).where(*where))).all()

    async def first(self, table, *where):
        return (await self.execute(select(table).where(*where))).first()

    async def scalar(self, table, *where):
        return (await self.execute(select(table).where(*where))).scalar()

    async def fetchone(self, table, *where):
        return (await self.execute(select(table).where(*where))).fetchone()

    async def fetchmany(self, table, *where, size: int | None):
        return (await self.execute(select(table).where(*where))).fetchmany(size)

    async def insert(self, table, **values):
        return await self.execute(insert(table).values(**values))

    async def update(self, table, *where, **values):
        return await self.execute(update(table).where(*where).values(**values))

    async def insert_or_update(self, table, *where, **values):
        if not await self.scalar(table, *where):
            return await self.execute(insert(table).values(**values))
        return await self.execute(update(table).where(*where).values(**values))

    async def insert_or_ignore(self, table, *where, **values):
        if not await self.scalar(table, *where):
            return await self.execute(insert(table).values(**values))

    async def delete(self, table, *where):
        return await self.execute(delete(table).where(*where))

    async def create(self, table):
        async with self.__lock():
            async with self.engine.begin() as conn:
                if await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn).has_table(table.__tablename__)
                ):
                    logger.debug(
                        f"[DatabaseEngine] Table {table.__tablename__!r} already exists, skipping..."
                    )
                else:
                    await conn.run_sync(table.__table__.create)

    async def drop(self, table):
        async with self.__lock():
            async with self.engine.begin() as conn:
                await conn.run_sync(table.__table__.drop)

    async def create_all(self):
        async with self.__lock():
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self.__lock():
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

    async def close(self):
        async with self.__lock():
            await self.engine.dispose()
