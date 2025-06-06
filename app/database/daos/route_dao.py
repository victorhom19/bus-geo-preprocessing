from typing import List, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.daos.base_dao import BaseDAO
from app.database.daos.stop_dao import StopDAO
from app.database.models import Route, RouteStop, RouteSegment, RouteGeometryNode, RouteObstacleNode, \
    RouteStopPositionNode
from app.schemas.enums import BusDataProvider
from app.schemas.route import RouteSchema
from app.schemas.route_geometry import RouteGeometryNodeSchema, RouteObstacleSchema, RouteStopPositionSchema


class RouteDAO(BaseDAO):
    """ DAO-класс для работы с объектами маршрутов """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Route)

    async def create(self, route_data: RouteSchema, commit=True) -> Route:
        """ Создание записи о маршруте """

        # Создание записи о маршруте
        _route = Route(
            name=route_data.name,
            source=route_data.source.value,
            external_source_id=str(route_data.id),
            final_stop_order=route_data.final_stop_order
        )
        self.session.add(_route)

        # Создание остановок
        db_stops = []
        matched_stops = {}
        for i, stop in enumerate(route_data.stops):
            if stop.source is BusDataProvider.LOCAL:
                _stop = await StopDAO(self.session).get_by_id(stop.id)
            else:
                _stop = await StopDAO(self.session).create(stop, commit=False)
            db_stops.append(_stop)
            matched_stops[str(stop.id)] = _stop
        await self.session.flush()
        await self.session.refresh(_route)
        for _stop in db_stops:
            await self.session.refresh(_stop)

        # Создание сопоставлений маршрут - остановки
        for i, _stop in enumerate(db_stops):
            _route_stop = RouteStop(
                route_id=_route.id,
                stop_id=_stop.id,
                stop_order=i
            )
            self.session.add(_route_stop)

        # Создание сегментов маршрута
        for i, route_segment in enumerate(route_data.segments):
            _stop_from = matched_stops[route_segment.stop_from_id]
            _stop_to = matched_stops[route_segment.stop_to_id]
            _route_segment = RouteSegment(
                route_id=_route.id,
                stop_from_id=_stop_from.id,
                stop_to_id=_stop_to.id,
                segment_order=i,
                distance=route_segment.distance,
                crossings=route_segment.crossings,
                traffic_signals=route_segment.traffic_signals,
                speedbumps=route_segment.speedbumps,
                roundabouts=route_segment.roundabouts
            )
            self.session.add(_route_segment)

        # Создание геометрии маршрута
        for i, node in enumerate(route_data.geometry):
            if type(node) is RouteGeometryNodeSchema:
                _node = RouteGeometryNode(
                    route_id=_route.id,
                    node_order=i,
                    lon=node.lon,
                    lat=node.lat,
                )
                self.session.add(_node)
            elif type(node) is RouteObstacleSchema:
                _node = RouteObstacleNode(
                    route_id=_route.id,
                    node_order=i,
                    lon=node.lon,
                    lat=node.lat,
                    obstacle_type=node.obstacle_type.value
                )
                self.session.add(_node)
            elif type(node) is RouteStopPositionSchema:
                _stop = matched_stops[node.corresponding_stop_id]
                _node = RouteStopPositionNode(
                    route_id=_route.id,
                    node_order=i,
                    lon=node.lon,
                    lat=node.lat,
                    corresponding_stop_id=_stop.id
                )
                self.session.add(_node)

        if commit:
            await self.session.commit()
        else:
            await self.session.flush()
        await self.session.refresh(_route)
        return _route

    async def create_all(self, routes_data: List[RouteSchema]) -> List[Route]:
        """ Создание нескольких маршрутов """
        _routes = []
        for route_data in routes_data:
            _route = await self.create(route_data, commit=False)
            _routes.append(_route)
        await self.session.commit()
        for _route in _routes:
            await self.session.refresh(_route)
        return _routes

    async def delete_all(self, routes_ids: List[str]) -> List[Route]:
        """ Удаление всех маршрутов из списка """
        _routes = []
        for route_id in routes_ids:
            _route = await self.delete_by_id(route_id)
            _routes.append(_route)
        return _routes

    async def get_all_by_ids(self, routes_ids: List[str]) -> Sequence[Route]:
        """ Получение нескольких маршрутов по списку идентификаторов """
        routes_ids = [UUID(route_id) for route_id in routes_ids]
        stmt = select(Route).where(Route.id.in_(routes_ids))
        res = await self.session.execute(stmt)
        return res.scalars().all()
