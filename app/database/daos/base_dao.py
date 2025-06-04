from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """ Базовый DAO-класс для работы с объектами базы данных """

    def __init__(self, session: AsyncSession, table):
        self.session = session
        self.table = table

    async def create(self, **kwargs):
        """ Создание записи об объекте """
        _obj = self.table(**kwargs)
        self.session.add(_obj)
        await self.session.commit()
        return _obj

    async def get_by_id(self, object_id: str):
        """ Получение записи об объекте по id  """
        statement = select(self.table).where(self.table.id == UUID(object_id))
        _obj = await self.session.scalar(statement)
        return _obj

    async def get_all(self):
        """ Получение всех записей об объектах из базы данных """
        statement = select(self.table)
        query_result = await self.session.execute(statement)
        return query_result.scalars().all()

    async def delete_by_id(self, object_id: str):
        """ Удаление записи об объекте по id """
        _obj = await self.get_by_id(object_id)
        if _obj is not None:
            statement = delete(self.table).where(self.table.id == UUID(object_id))
            await self.session.execute(statement)
            await self.session.commit()
        return _obj
