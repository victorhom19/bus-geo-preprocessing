from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.daos.base_dao import BaseDAO
from app.database.daos.route_dao import RouteDAO
from app.database.models import SpeedProfile, SegmentSpeed
from app.schemas.speed_profile_schema import RouteIdToWeekday


class SpeedProfileDAO(BaseDAO):
    """ DAO-класс для работы с объектами профилей скоростей """

    def __init__(self, session: AsyncSession):
        super().__init__(session, SpeedProfile)

    async def create(self, name: str, routes: RouteIdToWeekday, speed_data_id: str) -> SpeedProfile:
        """ Создание записи о профиле скорости """

        # Создание записи о профиле скорости
        _speed_profile = SpeedProfile(
            name=name,
            speed_data_id=UUID(speed_data_id)
        )
        self.session.add(_speed_profile)
        await self.session.flush()
        await self.session.refresh(_speed_profile)

        # Создание записей о скоростях сегментов маршрутов
        for route_id in routes:
            route = await RouteDAO(self.session).get_by_id(route_id)
            for i, route_segment in enumerate(route.segments):
                for j, weekday in enumerate(routes[route_id].keys()):
                    for hour in routes[route_id][weekday].keys():
                        _segment_speed = SegmentSpeed(
                            speed_profile_id=_speed_profile.id,
                            weekday=j,
                            hour_interval=hour,
                            route_segment_id=route.segments[i].id,
                            segment_order=i,
                            speed=routes[route_id][weekday][hour][i]
                        )
                        self.session.add(_segment_speed)

        await self.session.commit()
        await self.session.refresh(_speed_profile)
        return _speed_profile
