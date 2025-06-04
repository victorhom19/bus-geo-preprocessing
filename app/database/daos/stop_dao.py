from typing import List, Dict, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.daos.base_dao import BaseDAO
from app.database.models import Stop
from app.schemas.enums import BusDataProvider
from app.schemas.stop import StopSchema


class StopDAO(BaseDAO):
    """ DAO-класс для работы с объектами остановок """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Stop)

    async def create(self, stop_data: StopSchema, commit=True) -> Stop:
        """ Создание записи об остановке """
        _stop = Stop(
            name=stop_data.name,
            source=stop_data.source.value,
            external_source_id=str(stop_data.id),
            lon=stop_data.lon,
            lat=stop_data.lat,
        )
        self.session.add(_stop)
        if commit:
            await self.session.commit()
        return _stop

    async def create_all(self, stops_data: List[StopSchema]) -> List[Stop]:
        """ Создание записей для всех остановок из списка """
        _stops = []
        for stop_data in stops_data:
            _stop = await self.create(stop_data, commit=False)
            _stops.append(_stop)
        await self.session.commit()
        for _stop in _stops:
            await self.session.refresh(_stop)
        return _stops

    async def delete_all(self, stops_ids: List[str]) -> List[Stop]:
        """ Удаление всех остановок из списка """
        _stops = []
        for stop_id in stops_ids:
            _stop = await self.delete_by_id(stop_id)
            _stops.append(_stop)
        return _stops

    async def get_all_by_ids(self, stops_ids: List[str]) -> Sequence[Stop]:
        """ Получение нескольких остановок по списку идентификаторов """
        stops_ids = [UUID(stop_id) for stop_id in stops_ids]
        stmt = select(Stop).where(Stop.id.in_(stops_ids))
        res = await self.session.execute(stmt)
        return res.scalars().all()
