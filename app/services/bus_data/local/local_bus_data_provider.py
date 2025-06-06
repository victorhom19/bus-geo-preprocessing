import time
from typing import List, Optional, Tuple

from haversine import haversine, Unit
from sqlalchemy.ext.asyncio import AsyncSession


from app.common_types import BBox
from app.database.daos.route_dao import RouteDAO
from app.database.daos.stop_dao import StopDAO
from app.database.models import Stop, Route, RouteGeometryNode, RouteObstacleNode, RouteStopPositionNode
from app.logger import logger
from app.schemas.enums import BusDataProvider, RouteGeometryNodeType
from app.schemas.route import RouteSchema
from app.schemas.route_geometry import RouteGeometryNodeSchema, RouteObstacleSchema, RouteStopPositionSchema
from app.schemas.route_segment import RouteSegmentSchema
from app.schemas.stop import StopSchema


class LocalBusDataProvider:
    """ Класс, предоставляющий информацию об автобусных маршрутах и остановках из локальной базы данных """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_bus_data_in_bbox(self, bbox: BBox) -> Tuple[List[StopSchema], List[RouteSchema]]:
        """ Получение данных об автобусных маршрутах, остановках и препятствиях в ограниченной рамкой области """

        logger.info(f"BUS DATA > LOCAL | FETCHING BUS DATA IN AREA {str(bbox)}")
        start = time.perf_counter()

        # Получение остановок
        stops = await self.get_stops_in_bbox(bbox)

        # Получение маршрутов
        routes = await self.get_routes_in_bbox(bbox)

        end = time.perf_counter()

        if bbox:
            lon_dist = haversine((bbox[0], bbox[1]), (bbox[0], bbox[3]), unit=Unit.KILOMETERS)
            lat_dist = haversine((bbox[0], bbox[1]), (bbox[2], bbox[1]), unit=Unit.KILOMETERS)

            area = lat_dist * lon_dist

            log_message = "\n".join([
                f"BUS DATA > LOCAL | Done:",
                f"BUS DATA > LOCAL | * Total stops: {len(stops)}",
                f"BUS DATA > LOCAL | * Total routes: {len(routes)}",
                f"BUS DATA > LOCAL | * Area: {area:3.2f} km^2 | Processing time: {end - start:3.2f} s"
            ])
        else:
            log_message = "\n".join([
                f"BUS DATA > LOCAL | Done:",
                f"BUS DATA > LOCAL | * Total stops: {len(stops)}",
                f"BUS DATA > LOCAL | * Total routes: {len(routes)}",
            ])
        logger.info(log_message)

        return stops, routes

    async def get_stops_in_bbox(self, bbox: Optional[BBox]) -> List[StopSchema]:
        """ Получение всех остановок внутри ограничивающей рамки """

        stops_in_bbox = []

        # Получение и обход всех остановок из базы данных
        all_db_stops = await StopDAO(self.session).get_all()
        for stop in all_db_stops:

            if bbox is not None:
                # Проверка принадлежности координат остановки к области ограничивающей рамки
                is_inside_bbox = (bbox[0] <= stop.lon <= bbox[2]) and (bbox[1] <= stop.lat <= bbox[3])

                # Если остановка находится внутри рамки, то она добавляется в выходной массив
                if is_inside_bbox:
                    stops_in_bbox.append(self.db_stop_as_schema(stop))
            else:
                stops_in_bbox.append(self.db_stop_as_schema(stop))

        return stops_in_bbox

    async def get_routes_in_bbox(self, bbox: BBox) -> List[RouteSchema]:
        """ Получение всех маршрутов внутри ограничивающей рамки """

        routes_in_bbox = []

        # Получение и обход всех маршрутов из базы данных
        all_db_routes = await RouteDAO(self.session).get_all()
        for route in all_db_routes:

            is_inside_bbox = True

            # Обход всех остановок маршрута: если хотя бы одна остановка находится вне
            # ограничивающей рамки, то маршрут не добавляется в выходной список
            for route_stop in route.stops:

                if bbox is None:
                    break

                # Проверка принадлежности координат остановки к области ограничивающей рамки
                lon = route_stop.stop.lon
                lat = route_stop.stop.lat
                is_inside_bbox = (bbox[0] <= lon <= bbox[2]) and (bbox[1] <= lat <= bbox[3])

                # Если остановка находится внутри рамки, то она добавляется в выходной массив
                if not is_inside_bbox:
                    is_inside_bbox = False
                    break

            if is_inside_bbox:
                routes_in_bbox.append(self.db_route_as_schema(route))

        return routes_in_bbox

    async def get_routes_by_ids(self, routes_ids: List[str]) -> List[RouteSchema]:
        db_routes = await RouteDAO(self.session).get_all_by_ids(routes_ids)
        return [self.db_route_as_schema(db_route) for db_route in db_routes]

    @staticmethod
    def db_stop_as_schema(db_stop: Stop) -> StopSchema:
        return StopSchema(
            id=str(db_stop.id),
            source=BusDataProvider.LOCAL,
            external_source_id=db_stop.external_source_id,
            name=db_stop.name,
            lon=db_stop.lon,
            lat=db_stop.lat
        )

    @classmethod
    def db_route_as_schema(cls, db_route: Route) -> RouteSchema:

        stops_schemas = [cls.db_stop_as_schema(route_stop.stop) for route_stop in db_route.stops]

        route_segments_schemas = []
        for route_segment in db_route.segments:
            route_segments_schemas.append(
                RouteSegmentSchema(
                    stop_from_id=str(route_segment.stop_from_id),
                    stop_to_id=str(route_segment.stop_to_id),
                    segment_order=route_segment.segment_order,
                    distance=route_segment.distance,
                    crossings=route_segment.crossings,
                    traffic_signals=route_segment.traffic_signals,
                    speedbumps=route_segment.speedbumps,
                    roundabouts=route_segment.roundabouts
                )
            )

        route_geometry_schemas = []
        for node in db_route.geometry:
            if type(node) is RouteGeometryNode:
                route_geometry_schemas.append(
                    RouteGeometryNodeSchema(
                        type=node.type,
                        lat=node.lat,
                        lon=node.lon
                    )
                )
            elif type(node) is RouteObstacleNode:
                route_geometry_schemas.append(
                    RouteObstacleSchema(
                        type=RouteGeometryNodeType.OBSTACLE,
                        lat=node.lat,
                        lon=node.lon,
                        obstacle_type=node.obstacle_type
                    )
                )
            elif type(node) is RouteStopPositionNode:
                route_geometry_schemas.append(
                    RouteStopPositionSchema(
                        type=RouteGeometryNodeType.STOP_POSITION,
                        lat=node.lat,
                        lon=node.lon,
                        corresponding_stop_id=str(node.corresponding_stop_id)
                    )
                )

        return RouteSchema(
            id=str(db_route.id),
            source=BusDataProvider.LOCAL,
            external_source_id=db_route.external_source_id,
            name=db_route.name,
            stops=stops_schemas,
            final_stop_order=db_route.final_stop_order,
            segments=route_segments_schemas,
            geometry=route_geometry_schemas
        )

    async def prepare_local_stops_mapping(self, bbox):
        stops_in_bbox = {}

        # Получение и обход всех остановок из базы данных
        all_db_stops = await StopDAO(self.session).get_all()
        for stop in all_db_stops:

            if stop.external_source_id is None:
                continue

            # Проверка принадлежности координат остановки к области ограничивающей рамки
            is_inside_bbox = (bbox[0] <= stop.lon <= bbox[2]) and (bbox[1] <= stop.lat <= bbox[3])

            # Если остановка находится внутри рамки, то она добавляется в выходной массив
            if is_inside_bbox:
                stops_in_bbox[stop.external_source_id] = self.db_stop_as_schema(stop)

        return stops_in_bbox

    async def prepare_local_routes_mapping(self, bbox):

        routes_in_bbox = {}

        # Получение и обход всех маршрутов из базы данных
        all_db_routes = await RouteDAO(self.session).get_all()
        for route in all_db_routes:

            if route.external_source_id is None:
                continue

            is_inside_bbox = True

            # Обход всех остановок маршрута: если хотя бы одна остановка находится вне
            # ограничивающей рамки, то маршрут не добавляется в выходной список
            for route_stop in route.stops:

                if bbox is None:
                    break

                # Проверка принадлежности координат остановки к области ограничивающей рамки
                lon = route_stop.stop.lon
                lat = route_stop.stop.lat
                is_inside_bbox = (bbox[0] <= lon <= bbox[2]) and (bbox[1] <= lat <= bbox[3])

                # Если остановка находится внутри рамки, то она добавляется в выходной массив
                if not is_inside_bbox:
                    is_inside_bbox = False
                    break

            if is_inside_bbox:
                routes_in_bbox[route.external_source_id] = self.db_route_as_schema(route)

        return routes_in_bbox
