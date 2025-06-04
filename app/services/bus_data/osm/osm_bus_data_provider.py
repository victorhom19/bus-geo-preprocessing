import dataclasses
import time
import uuid
from typing import List, Dict, Tuple, Any

import utm
from haversine import haversine, Unit
from overpy import Overpass, Relation as OSMRelation, Node as OSMNode, RelationNode, RelationWay, Relation
from overpy.exception import OverPyException

from app.common_types import BBox
from app.logger import logger
from app.schemas.enums import BusDataProvider, RouteGeometryNodeType, RouteObstacleType
from app.schemas.route import RouteSchema
from app.schemas.route_geometry import RouteGeometryNodeSchema, RouteStopPositionSchema, RouteObstacleSchema
from app.schemas.route_segment import RouteSegmentSchema
from app.schemas.stop import StopSchema
from app.services.bus_data.osm.wrappers import OSMWayWrapper, KDTreeWrapper
from app.utils import utm_point_from_latlon, project_point_on_segment, frechet_distance


class OSMBusDataProvider:
    """ Класс, предоставляющий информацию об автобусных маршрутах и остановках посредством OpenStreetMaps API """

    # Документация Overpass API: https://dev.overpass-api.de/overpass-doc/en/
    # Веб-приложение для выполнения запросов: https://overpass-turbo.eu/#

    def __init__(self, local_stops_mapping: Dict[str, StopSchema] | None = None,
                 local_routes_mapping: Dict[str, RouteSchema] | None = None,
                 overpass_api_mock=None):
        if overpass_api_mock is None:
            self.api = Overpass()
        else:
            self.api = overpass_api_mock
        self.local_stops_mapping = local_stops_mapping or {}
        self.local_routes_mapping = local_routes_mapping or {}

    async def get_bus_data_in_bbox(self, bbox: BBox) -> Tuple[List[StopSchema], List[RouteSchema]]:
        """ Получение данных об автобусных маршрутах, остановках и препятствиях в ограниченной рамкой области """

        logger.info(f"BUS DATA > OSM | FETCHING BUS DATA IN AREA {str(bbox)}")
        start = time.perf_counter()

        # Получение остановок
        stops = await self.get_stops_in_bbox(bbox)

        # Получение маршрутов
        routes = await self.get_routes_in_bbox(bbox)

        end = time.perf_counter()

        lon_dist = haversine((bbox[0], bbox[1]), (bbox[0], bbox[3]), unit=Unit.KILOMETERS)
        lat_dist = haversine((bbox[0], bbox[1]), (bbox[2], bbox[1]), unit=Unit.KILOMETERS)

        area = lat_dist * lon_dist

        log_message = "\n".join([
            f"BUS DATA > OSM | Done:",
            f"BUS DATA > OSM | * Total stops: {len(stops)}",
            f"BUS DATA > OSM | * Total routes: {len(routes)}",
            f"BUS DATA > OSM | * Area: {area:3.2f} km^2 | Processing time: {end - start:3.2f} s"
        ])
        logger.info(log_message)

        return stops, routes

    async def get_stops_in_bbox(self, bbox: BBox) -> List[StopSchema]:
        """ Получение всех остановок внутри ограничивающей рамки """

        # Преобразование ограничивающей рамки в формат OSM
        formatted_bbox = self.as_osm_bbox(bbox)

        # Формирование строки запроса
        query_string = f"node[highway=bus_stop]{str(formatted_bbox)};out;"

        # Отправка запроса к Overpass API
        try:
            logger.debug("BUS DATA > OSM | Fetching get stops in bbox...")
            start = time.perf_counter()
            response = self.api.query(query_string)
            end = time.perf_counter()
            logger.debug(f"BUS DATA > OSM | Done in {end - start:3.2f} s!")
        except OverPyException:
            logger.debug(f"BUS DATA > OSM | Failed to fetch route stops data!")
            return []

        # Формирование выходного списка остановок
        stops = []
        for node in response.nodes:
            if str(node.id) in self.local_stops_mapping:
                db_stop = self.local_stops_mapping[str(node.id)]
                stops.append(db_stop)
            else:
                stops.append(StopSchema(
                    id=str(node.id),
                    source=BusDataProvider.OSM,
                    name=(node.tags.get('name') or 'Безымянная остановка'),
                    lat=node.lat,
                    lon=node.lon
                ))

        return stops

    @dataclasses.dataclass
    class RouteRawData:
        """ Класс-контейнер для группировки данных, необходимых для построения маршрута OSM """
        # При построении маршрута часто требуется прокидывать много аргументов, из-за чего сигнатуры методов
        # становятся громоздкими и нечитаемыми
        node_by_id: Dict[int, OSMNode]
        way_by_id: Dict[int, OSMWayWrapper]
        global_stop_positions: List[OSMNode]
        global_stop_positions_kd_tree: KDTreeWrapper

    async def get_routes_in_bbox(self, bbox: BBox) -> List[RouteSchema]:
        """ Получение всех маршрутов внутри ограничивающей рамки """

        # Преобразование ограничивающей рамки в формат OSM
        formatted_bbox = self.as_osm_bbox(bbox)

        # Формирование строки запроса
        query_string = f"""
            // Автобусные и троллейбусные маршруты
            (
              relation[route=bus]{str(formatted_bbox)};
              relation[route=trolleybus]{str(formatted_bbox)};
            ) -> .routes;
            .routes out geom;

            // Платформы и места остановок
            node[highway=bus_stop][public_transport=stop_position]{str(formatted_bbox)}; out;
            node[highway=bus_stop][public_transport=platform]{str(formatted_bbox)}; out;

            // Дороги
            .routes >; way._ -> .roads;
            .roads out;

            // Узлы геометрии дорог
            .roads >; node._; out;
        """

        # Отправка запроса к Overpass API
        try:
            logger.debug("GP > BUS DATA > OSM | Fetching get routes in bbox...")
            start = time.perf_counter()
            response = self.api.query(query_string)
            end = time.perf_counter()
            logger.debug(f"GP > BUS DATA > OSM | Done in {end - start:3.2f} s!")
        except OverPyException:
            logger.debug(f"GP > BUS DATA > OSM | Failed to fetch routes data!")
            return []

        # Формирование соответствий id -> узел
        node_by_id = {}
        for node in response.nodes:
            node_by_id[node.id] = node

        # Формирование соответствий id -> дорога
        way_by_id = {}
        for way in response.ways:
            way_by_id[way.id] = OSMWayWrapper(id=way.id, nodes=way.nodes, tags=way.tags)

        # Парсинг найденных в границах рамки мест остановки общественного транспорта, построение kd-дерева
        # (необходимо для разрешения ситуаций с отсутствующими в объекте маршрута данными)
        global_stop_positions = []
        for node in node_by_id.values():
            if node.tags.get('public_transport') == 'stop_position':
                global_stop_positions.append(node)
        global_stop_positions_as_utm_points = [utm.from_latlon(float(node.lat), float(node.lon))[:2] for node in
                                               global_stop_positions]
        global_stop_positions_kd_tree = KDTreeWrapper(global_stop_positions_as_utm_points)

        # Группировка данных после парсинга
        route_raw_data = self.RouteRawData(node_by_id, way_by_id, global_stop_positions, global_stop_positions_kd_tree)

        # Фильтрация маршрутов, находящихся за пределами ограничивающей рамки
        bbox_route_relations = await self.__filter_exceeding_routes(response.relations, node_by_id, bbox)

        # Фильтрация "плохих" маршрутов (пр. не содержащих дороги или остановки)
        filtered_route_relations = await self.__filter_bad_routes(bbox_route_relations)

        # Парсинг маршрутов с их разбором на набор остановок и геометрию
        routes = {}
        for route_relation in filtered_route_relations:
            try:
                stops, geometry = await self.__extract_route_stops_and_geometry(route_relation, route_raw_data)
                routes[route_relation.id] = (stops, geometry, route_relation)
            except Exception as e:
                logger.debug(f"Failed to build route <OSM #({route_relation.id})>")

        # Инициализация словаря для кэширования расстояний между маршрутами
        self.cached_distances = {}

        # Инициализация списка обработанных маршрутов
        processed_route_ids = []

        # Инициализация выходного списка маршрутов
        routes_out = []

        # Обход всех маршрутов (с целью определения парного маршрута)
        for route_id, (stops, geometry, rel) in routes.items():

            # Маршруты, которые уже были определены как пара для другого маршрута, отбрасываются
            if route_id in processed_route_ids:
                continue

            # Проверка, является ли маршрут круговым
            is_cyclic = await self.__is_route_cyclic(stops)

            if is_cyclic:
                # Добавление кругового маршрута (особой обработки не требуется)
                processed_route_ids.append(rel.id)
                final_stop_order = None
            else:
                # Если маршрут не является круговым, то производится попытка найти парный маршрут
                has_pair, pair_route_id = await self.__find_matching_route(route_id, routes, processed_route_ids)

                if has_pair:
                    # Если парный маршрут найден

                    # Получение параметров парного маршрута
                    paired_stops, paired_geometry, paired_rel = routes[pair_route_id]

                    # Объединение пары маршрутов
                    stops, geometry, final_stop_order = await self.__join_route_pair(
                        stops, geometry,
                        paired_stops, paired_geometry
                    )

                    # Отметка маршрутов как уже обработанных
                    processed_route_ids.append(rel.id)
                    processed_route_ids.append(pair_route_id)
                else:
                    # Иначе считается, что у маршрута нет пары
                    final_stop_order = None

            route_segments = self.construct_route_segments(stops, geometry)

            if str(route_id) in self.local_routes_mapping:
                routes_out.append(self.local_routes_mapping[str(route_id)])
            else:
                # Создание объекта маршрута и добавление в общий список маршрутов
                route = RouteSchema(
                    id=str(rel.id),
                    source=BusDataProvider.OSM,
                    name=(rel.tags.get('name') or 'Безымянный маршрут'),
                    stops=stops,
                    final_stop_order=final_stop_order,
                    geometry=geometry,
                    segments=route_segments
                )
                routes_out.append(route)

        return routes_out

    @staticmethod
    async def __bind_platforms_to_stop_positions(route_relation: OSMRelation, route_raw_data: RouteRawData)\
            -> Tuple[List[OSMNode], List[OSMNode]]:
        """
        Связывание платформ и мест остановок транспорта

        В качестве результата работы функция возвращает кортеж из двух списков: список платформ и список мест остановки
        транспорта. Списки при этом имеют одинаковую длину, i-ая платформа соответствует i-ому месту остановки.

        * Примечание: маршрут OSM содержит данные и о платформах, и о местах остановки транспорта. Однако, для некоторых
          маршрутов может отсутствовать информация о каком-либо месте остановки или платформе. На практике чаще
          встречается ситуация, когда для маршрута указаны все платформы, но некоторые места остановки отсутствуют.
          По этой причине при попытке восстановить данные приоритет отдаётся именно платформам.

        Работа функции производится в несколько этапов:
        1) Попытка связывания платформ и мест остановок по локальным данным, содержащимся в объекте маршрута
        2) Попытка связывания платформ и мест остановок по глобальным данным, полученным от OSM
        3) Попытка связывания данных "вручную" путём создания новых мест остановки
        """

        # Распаковка сгруппированных данных маршрута
        node_by_id = route_raw_data.node_by_id
        way_by_id = route_raw_data.way_by_id
        global_stop_positions = route_raw_data.global_stop_positions
        global_stop_positions_kd_tree = route_raw_data.global_stop_positions_kd_tree

        # Подготовка локальных данных платформ
        platforms = []
        for m in route_relation.members:
            if type(m) is RelationNode and m.role.startswith('platform'):
                platforms.append(node_by_id[m.ref])
        platforms_as_utm_points = [utm_point_from_latlon(node.lat, node.lon) for node in platforms]

        # Подготовка локальных данных мест остановок
        raw_stop_positions = []
        for m in route_relation.members:
            if type(m) is RelationNode and m.role.startswith('stop'):
                raw_stop_positions.append(node_by_id[m.ref])
        stop_positions_as_utm_points = [utm_point_from_latlon(node.lat, node.lon) for node in raw_stop_positions]
        stop_positions_kd_tree = KDTreeWrapper(stop_positions_as_utm_points)

        # Определение для каждой платформы ближайшего места остановки (на основе локальных данных)
        platforms_closest_stop_position_indices, _ = stop_positions_kd_tree.query_radius(
            platforms_as_utm_points, return_distance=True, sort_results=True, r=30
        )
        stop_positions = []
        for i, platform in enumerate(platforms_closest_stop_position_indices):
            closest_stop_position_indices = platforms_closest_stop_position_indices[i]
            if len(closest_stop_position_indices) == 0:
                stop_positions.append(None)
            else:
                closest_stop_positions = [raw_stop_positions[j] for j in closest_stop_position_indices]
                closest_stop_position = closest_stop_positions[0]
                stop_positions.append(closest_stop_position)

        # Если каждой платформе было сопоставлено место остановки - выход из функции
        if None not in stop_positions:
            return platforms, stop_positions

        # Определение для каждой платформы ближайшего места остановки (на основе глобальных данных)
        for i, (platform, stop_position) in enumerate(zip(platforms, stop_positions)):
            if stop_position is None:
                closest_stop_position_indices, _ = global_stop_positions_kd_tree.query_radius(
                    [platforms_as_utm_points[i]], return_distance=True, sort_results=True, r=30
                )

                if len(closest_stop_position_indices[0]) > 0:
                    closest_stop_positions = [global_stop_positions[j] for j in closest_stop_position_indices[0]]
                    closest_stop_position = closest_stop_positions[0]
                    stop_positions[i] = closest_stop_position

        # Если каждой платформе было сопоставлено место остановки - выход из функции
        if None not in stop_positions:
            return platforms, stop_positions

        # Определение для каждой платформы ближайшего места остановки (вручную)

        # Извлечение всех дорог маршрута
        route_ways = []
        for m in route_relation.members:
            if type(m) is RelationWay:
                route_ways.append(way_by_id[m.ref])

        # Преобразование дорог в набор отрезков
        way_segments = []
        way_segments_as_utm_points = []
        for way in route_ways:
            for i, (node1, node2) in enumerate(zip(way.nodes, way.nodes[1:])):
                way_segments.append((node1, node2, i, way.id))
                way_segments_as_utm_points.append(utm.from_latlon(float(node1.lat), float(node1.lon))[:2])
                way_segments_as_utm_points.append(utm.from_latlon(float(node2.lat), float(node2.lon))[:2])
        way_segment_kd_tree = KDTreeWrapper(way_segments_as_utm_points, leaf_size=40)

        # Обход всех платформ, для которых не было найдено место остановки
        for i, (platform, stop_position) in enumerate(zip(platforms, stop_positions)):
            if stop_position is None:

                # Определение ближайших отрезков дороги
                closest_way_segments_indices = way_segment_kd_tree.query_radius([platforms_as_utm_points[i]], r=50)[0]
                if len(closest_way_segments_indices) == 0:
                    break
                closest_way_segments = [way_segments[i // 2] for i in closest_way_segments_indices]

                best_segment = None
                best_position = None
                best_distance = None
                best_position_type = None

                # Определение ближайшей к платформе точки на дороге.
                # Для каждого сегмента определяется расстояние от платформы до его начальной и конечной точки,
                # а также проекционное расстояние. В качестве лучшей выбирается ближайшая к платформе точка между
                # всеми сегментами маршрута.
                for segment in closest_way_segments:

                    node1, node2, segment_index, way_id = segment

                    # Расстояние между началом сегмента и платформой
                    dist_to_node1 = haversine((node1.lat, node1.lon), (platform.lat, platform.lon),
                                              unit=Unit.METERS)

                    # Расстояние между концом сегмента и платформой
                    dist_to_node2 = haversine((node2.lat, node2.lon), (platform.lat, platform.lon),
                                              unit=Unit.METERS)

                    # Расчёт проекции платформы на отрезок и проекционного расстояния
                    projected_position, projection_distance = project_point_on_segment(
                        ((node1.lat, node1.lon), (node2.lat, node2.lon)),
                        (platform.lat, platform.lon),
                        0.1
                    )

                    # Группировка рассчитанных точек и расстояний для выбора лучшей
                    candidates = list(zip(
                        ((node1.lat, node1.lon), projected_position, (node2.lat, node2.lon)),
                        (dist_to_node1, projection_distance, dist_to_node2),
                        (0, 1, 2)
                    ))

                    # Выбор ближайшей точки отрезка
                    segment_best_candidate = list(sorted(candidates, key=lambda c: c[1]))[0]
                    segment_best_position, segment_best_distance, position_type = segment_best_candidate

                    # Сравнение с лучшей найденной точкой
                    if best_segment is None or segment_best_distance < best_distance:
                        best_segment = segment
                        best_position = segment_best_position
                        best_distance = segment_best_distance
                        best_position_type = position_type

                if best_position_type == 1:
                    # Если ближайшей оказалась спроецированная точка - необходимо создать новый узел

                    # Создание нового "фиктивного" OSM узла
                    lat, lon = best_position
                    new_stop_position_node = OSMNode(node_id=uuid.uuid4().int, lat=lat, lon=lon, attributes={}, tags={
                        'public_transport': 'stop_position'
                    })

                    # Добавление нового узла в геометрию дороги
                    _, _, j, way_id = best_segment
                    old_nodes = way_by_id[way_id].nodes
                    way_by_id[way_id].nodes = [
                        *old_nodes[:j + 1],
                        new_stop_position_node,
                        *old_nodes[j + 1:]
                    ]
                    node_by_id[new_stop_position_node.id] = new_stop_position_node

                    # Добавление места остановки
                    stop_positions[i] = new_stop_position_node

                elif best_position_type == 0:
                    # Если ближайшей оказалась первая точка сегмента - в качестве места остановки будет
                    # использован уже существующий узел

                    # Добавление начальному узлу тега места остановки общественного транспорта
                    _, _, j, way_id = best_segment
                    stop_position_node = route_raw_data.way_by_id[way_id].nodes[j]
                    stop_position_node.tags['public_transport'] = 'stop_position'

                    stop_positions[i] = stop_position_node

                else:
                    # Если ближайшей оказалась первая точка сегмента - в качестве места остановки будет
                    # использован уже существующий узел

                    # Добавление конечному узлу тега места остановки общественного транспорта
                    _, _, j, way_id = best_segment
                    stop_position_node = route_raw_data.way_by_id[way_id].nodes[j + 1]
                    stop_position_node.tags['public_transport'] = 'stop_position'

                    # Добавление места остановки
                    stop_positions[i] = stop_position_node

        if None not in stop_positions:
            return platforms, stop_positions

        raise ValueError(f"Cannot resolve stop position for route #({route_relation.id})")

    async def __extract_route_stops_and_geometry(self, route_relation: OSMRelation, route_raw_data: RouteRawData) \
            -> Tuple[List[StopSchema], List[RouteGeometryNodeSchema]]:
        """
        Извлечение информации об остановках и геометрии маршрута

        Данная функция создаёт список остановок маршрута в порядке их следования, а также список узлов геометрии
        маршрута. Работа функции производится в несколько этапов:

        1) Подготовка: получение пар [платформа <-> место остановки], а также извлечение всех дорог, по которым проходит
           автобусный маршрут.
        2) Обход всех дорог маршрута с формированием геометрии:
            2.1) Определение направления движения по дороге.
            2.2) Формирование списка узлов геометрии, которые необходимо "пройти".
            2.3) Парсинг и добавление соответствующих узлов (место остановки, препятствие, узел геометрии) в список
                 геометрии маршрута.
        3) Конвертация списка остановок в формат pydantic-схемы.

        """

        # Связывание платформ и мест остановок транспорта
        # (с разрешением конфликтов при отсутствии места остановки)
        platforms, stop_positions = await self.__bind_platforms_to_stop_positions(route_relation, route_raw_data)
        assert len(stop_positions) == len(platforms)

        # Получение объектов дорог, по которым проходит маршрут
        route_ways_members = [m for m in route_relation.members if type(m) is RelationWay]
        ways = [route_raw_data.way_by_id[m.ref] for m in route_ways_members]

        # Инициализация списка для сохранения пройденных узлов.
        # Первый узел - место первой остановки автобуса
        first_stop_node = stop_positions[0]
        route_nodes = [
            RouteStopPositionSchema(
                type=RouteGeometryNodeType.STOP_POSITION,
                lat=first_stop_node.lat,
                lon=first_stop_node.lon,
                corresponding_stop_id=str(platforms[0].id)
            )
        ]

        # Курсор для отслеживания индекса следующей по ходу движения остановки
        next_stop_position_index = 1

        # Инициализация переменной для сохранения идентификатора последнего посещённого узла
        last_node_id = first_stop_node.id

        last_was_roundabout = False

        # Последовательный обход всех дорог маршрута
        for i, way in enumerate(ways):

            # Получение идентификаторов всех узлов текущей дороги
            way_node_ids = [node.id for node in way.nodes]

            # Определение индекса текущего узла в пределах дороги
            # (необходим для выбора направления)
            current_node_index = way_node_ids.index(last_node_id)

            is_last_way = (i + 1) == len(ways)

            if is_last_way:
                # Если текущая дорога является последней в маршруте, то это означает, что последняя остановка
                # также находится в её пределах. В качестве конца сегмента выбирается конечная остановка.
                traverse_to_node_id = stop_positions[-1].id
            else:
                # Если текущая дорога не является последней в маршруте, то в качестве конца сегмента выбирается узел,
                # являющийся общим для текущего и следующего объекта дороги

                # Получение идентификаторов всех узлов следующей дороги
                next_way = ways[i + 1]
                next_way_node_ids = [node.id for node in next_way.nodes]

                # При совпадении текущей и следующей дороги - переход к следующей итерации цикла
                # (некоторые маршруты OSM содержат ошибочное дублирование дорог)
                if way.id == next_way.id:
                    continue

                # Получение идентификаторов общих узлов
                common_node_ids = set(way_node_ids) & set(next_way_node_ids)

                # В подавляющем большинстве случаев общий узел будет только один, однако некоторые кольцевые дороги
                # состоят из нескольких сегментов (например двух половин) - в таком случае общих узлов будет два.
                # Для таких особых случаев необходимо выбирать последний по ходу движения общий узел.
                assert 1 <= len(common_node_ids) <= 2
                if len(common_node_ids) == 1:
                    common_node_id, = common_node_ids
                else:
                    first_common_node_id, second_common_node_id = common_node_ids
                    first_common_node_index = way_node_ids.index(first_common_node_id)
                    second_common_node_index = way_node_ids.index(second_common_node_id)
                    if first_common_node_index < second_common_node_index:
                        common_node_id = second_common_node_id
                    else:
                        common_node_id = first_common_node_id

                # Выбор общего узла в качестве конца сегмента
                traverse_to_node_id = common_node_id

            # Создание списков узлов сегментов
            if way.tags.get('junction') == 'roundabout':
                # Особой обработки требуют кольцевые дороги, так как почти всегда транспорт будет въезжать на них
                # через общий узел, не являющийся началом этой кольцевой дороги. В таком случае может оказаться, что
                # следующий общий узел может оказаться "позади" транспорта (учитывая что движение по кольцу может быть
                # только в одну сторону).
                #
                # Поэтому список узлов кольцевой дороги искусственно дублируется, а для выбора индекса конца сегмента
                # не рассматриваются узлы, расположенные в направлении против движения по кольцу.

                # Дублирование узлов кольцевой дороги
                expanded = way.nodes + way.nodes
                expanded_node_ids = way_node_ids + way_node_ids

                # Определение конечного индекса сегмента дороги
                traverse_to_node_index = expanded_node_ids.index(traverse_to_node_id, current_node_index + 1)

                # Для кольцевой дороги порядок хранения узлов всегда соответствует направлению движения
                direction = 1

                # Заполнение списка узлов, которые необходимо пройти
                nodes_to_traverse = []
                for j in range(current_node_index, traverse_to_node_index + direction, direction):
                    nodes_to_traverse.append(expanded[j])

            else:
                # Если дорога не является кольцевой, то конечный узел сегмента ищется в исходном наборе узлов дороги

                # Определение конечного индекса сегмента дороги
                traverse_to_node_index = way_node_ids.index(traverse_to_node_id)

                # Определение направления движения: порядок хранения узлов в объекте дороги может не соответствовать
                # порядку их прохождения транспортом
                direction = 1 if current_node_index < traverse_to_node_index else -1

                # Заполнение списка узлов, которые необходимо пройти
                nodes_to_traverse = []
                for j in range(current_node_index, traverse_to_node_index + direction, direction):
                    nodes_to_traverse.append(way.nodes[j])

            # Обход узлов сегмента и формирование геометрии маршрута
            for node in nodes_to_traverse:

                # Отбрасывание повторяющихся узлов
                if node.id == last_node_id:
                    continue

                if node.id == stop_positions[next_stop_position_index].id:
                    # Добавление очередного места остановки
                    route_nodes.append(RouteStopPositionSchema(
                        type=RouteGeometryNodeType.STOP_POSITION,
                        lat=node.lat,
                        lon=node.lon,
                        corresponding_stop_id=str(platforms[next_stop_position_index].id)
                    ))
                    next_stop_position_index += 1
                elif node.tags.get('highway') == 'crossing':
                    # Добавление пешеходного перехода
                    route_nodes.append(RouteObstacleSchema(
                        type=RouteGeometryNodeType.OBSTACLE,
                        obstacle_type=RouteObstacleType.CROSSING,
                        lat=node.lat,
                        lon=node.lon
                    ))
                elif node.tags.get('highway') == 'traffic_signals':
                    # Добавление светофора
                    route_nodes.append(RouteObstacleSchema(
                        type=RouteGeometryNodeType.OBSTACLE,
                        obstacle_type=RouteObstacleType.TRAFFIC_SIGNALS,
                        lat=node.lat,
                        lon=node.lon
                    ))
                elif node.tags.get('traffic_calming') in ('bump', 'hump', 'table'):
                    # Добавление лежачего полицейского
                    route_nodes.append(RouteObstacleSchema(
                        type=RouteGeometryNodeType.OBSTACLE,
                        obstacle_type=RouteObstacleType.SPEEDBUMP,
                        lat=node.lat,
                        lon=node.lon
                    ))
                elif way.tags.get('junction') == 'roundabout' and not last_was_roundabout:
                    route_nodes.append(RouteObstacleSchema(
                        type=RouteGeometryNodeType.OBSTACLE,
                        obstacle_type=RouteObstacleType.ROUNDABOUT,
                        lat=node.lat,
                        lon=node.lon
                    ))
                else:
                    # Добавление узла геометрии
                    route_nodes.append(RouteGeometryNodeSchema(
                        type=RouteGeometryNodeType.GEOMETRY,
                        lat=node.lat,
                        lon=node.lon
                    ))

                # Обновление последнего посещённого узла
                last_node_id = node.id
                last_was_roundabout = way.tags.get('junction') == 'roundabout'

                # Если была обработана последняя остановка - выход из цикла
                # (последняя остановка может быть расположена в "середине" объекта дороги)
                if next_stop_position_index == len(stop_positions):
                    break

            # Если была обработана последняя остановка - выход из цикла
            # (маршрут может содержать некоторое количество дорог и после конечной остановки)
            if next_stop_position_index == len(stop_positions):
                break

        for node in route_nodes:
            if node.type != RouteGeometryNodeType.STOP_POSITION:
                continue
            if node.corresponding_stop_id in self.local_stops_mapping:
                node.corresponding_stop_id = self.local_stops_mapping[str(node.corresponding_stop_id)].id

        # Формирование отдельного списка платформ
        stops = []
        for node in platforms:
            if str(node.id) in self.local_stops_mapping:
                db_stop = self.local_stops_mapping[str(node.id)]
                stops.append(db_stop)
            else:
                stops.append(
                    StopSchema(
                        id=str(node.id),
                        source=BusDataProvider.OSM,
                        name=(node.tags.get('name') or 'Безымянная остановка'),
                        lat=node.lat,
                        lon=node.lon,
                    )
                )

        # Проверка совпадения количества платформ и остановок, а также их соответствия друг другу
        stop_positions = [n for n in route_nodes if n.type == RouteGeometryNodeType.STOP_POSITION]
        for stop_position, platform_node in zip(stop_positions, stops):
            assert str(stop_position.corresponding_stop_id) == str(platform_node.id)
        assert len(platforms) == len(stop_positions)

        return stops, route_nodes

    @staticmethod
    async def __filter_exceeding_routes(route_relations: List[Relation], node_by_id: Dict[int, OSMNode], bbox: BBox):
        """ Фильтрация маршрутов по вхождению в ограничивающую рамку """

        # Инициализация списка отфильтрованных маршрутов
        filtered_route_relations = []

        # Обход всех маршрутов
        for rel in route_relations:

            # Вхождение маршрута в ограничивающую рамку определяется по факту вхождения всех его остановок в эту же
            # ограничивающую рамку
            route_is_inside_bbox = True
            for m in rel.members:
                if type(m) is RelationNode:
                    if m.ref not in node_by_id:
                        route_is_inside_bbox = False
                        break
                    node = node_by_id[m.ref]
                    route_is_inside_bbox = bbox[0] <= node.lon <= bbox[2] and bbox[1] <= node.lat <= bbox[3]
                    if not route_is_inside_bbox:
                        break

            # Проверка выполнения условия
            if route_is_inside_bbox:
                filtered_route_relations.append(rel)

        return filtered_route_relations

    @staticmethod
    async def __filter_bad_routes(route_relations: List[Relation]):
        """ Фильтрация некорректных маршрутов """

        # В базе данных OSM могут встречаться пустые маршруты, маршруты без остановок или с одной остановкой,
        # маршруты без дорог. Данная функция отфильтровывает такие объекты.

        # Инициализация списка отфильтрованных маршрутов
        filtered_route_relations = []

        # Обход всех маршрутов
        for rel in route_relations:

            # Корректным считается маршрут с не менее чем двумя остановками и не менее чем одной дорогой
            platforms_count = 0
            ways_count = 0
            for m in rel.members:
                if type(m) is RelationNode and m.role and m.role.startswith('platform'):
                    platforms_count += 1
                elif type(m) is RelationWay:
                    ways_count += 1

            # Проверка выполнения условия
            if platforms_count >= 2 and ways_count >= 1:
                filtered_route_relations.append(rel)

        return filtered_route_relations

    @staticmethod
    async def __is_route_cyclic(route_stops: List[StopSchema], tolerance=1000):
        """ Проверка того, является ли маршрут круговым """

        # Определение по расстоянию между первой и последней остановкой
        # (для круговых маршрутов оно должно быть небольшим)
        distance_between_first_and_last_stop = haversine(
            (route_stops[0].lat, route_stops[0].lon),
            (route_stops[-1].lat, route_stops[-1].lon),
            unit=Unit.METERS
        )

        return distance_between_first_and_last_stop < tolerance

    async def __find_matching_route(self, route_id: int, all_routes: Any, processed_route_ids,
                                    tolerance: float = 3000) -> Tuple[bool, int | None]:
        """ Определение маршрута со схожей геометрией """

        # Извлечение остановок интересующего маршрута
        stops, _, _ = all_routes[route_id]

        # Инициализация переменных для хранения ближайшего маршрута и минимального расстояния Фреше
        closest_route_id = None
        min_frechet_dist = 0
        has_pair = False

        # Обход всех маршрутов
        for other_id, (other_stops, _, _) in all_routes.items():

            # Тот же самый маршрут и уже обработанные маршруты не рассматриваются
            if route_id == other_id or other_id in processed_route_ids:
                continue

            # Проверка того, было ли уже рассчитано расстояния между двумя маршрутами
            cache_key = frozenset((route_id, other_id))
            cached_value = self.cached_distances.get(cache_key)
            if cached_value:
                # Получение кэшированного расстояния Фреше
                dist = cached_value
            else:
                # Расчёт расстояния Фреше и кэширование результата
                stops_as_points = [(stop.lat, stop.lon) for stop in stops]
                other_stops_as_points = [(stop.lat, stop.lon) for stop in other_stops]
                dist = frechet_distance(stops_as_points, other_stops_as_points[::-1])
                self.cached_distances[cache_key] = dist

            # Определение ближайшего маршрута
            if dist < tolerance and (closest_route_id is None or dist < min_frechet_dist):
                closest_route_id = other_id
                min_frechet_dist = dist
                has_pair = True

        return has_pair, closest_route_id

    @staticmethod
    async def __join_route_pair(first_route_stops, first_route_geometry, second_route_stops, second_route_geometry):
        """ Объединение пары маршрутов """

        # В OSM противоположные направления движения по одному и тому же маршруту
        # считаются различными сущностями. Данная функция "склеивает" два парных маршрута
        # по одной из конечных остановок.

        # Определение расстояния от конца первого маршрута до начала второго
        first_end_to_second_start = haversine(
            (first_route_stops[-1].lat, first_route_stops[-1].lon),
            (second_route_stops[0].lat, second_route_stops[0].lon),
            unit=Unit.METERS
        )

        # Определение расстояния от конца второго маршрута до начала первого
        second_end_to_first_start = haversine(
            (second_route_stops[-1].lat, second_route_stops[-1].lon),
            (first_route_stops[0].lat, first_route_stops[0].lon),
            unit=Unit.METERS
        )

        # Выбор порядка "сборки" пары маршрутов с объединением остановок и геометрии
        if first_end_to_second_start < second_end_to_first_start:
            final_stop_order = len(first_route_stops) - 1
            stops = first_route_stops + second_route_stops
            geometry = first_route_geometry + second_route_geometry
        else:
            final_stop_order = len(second_route_stops) - 1
            stops = second_route_stops + first_route_stops
            geometry = second_route_geometry + first_route_geometry

        return stops, geometry, final_stop_order

    @staticmethod
    def construct_route_segments(stops: List[StopSchema], geometry: List[RouteGeometryNodeSchema]) -> List[RouteSegmentSchema]:
        geometry_cursor = 1

        stop_cursor = 0
        distance = 0
        crossings = 0
        traffic_signals = 0
        speedbumps = 0
        roundabouts = 0

        last_node = None

        route_segments = []

        while geometry_cursor < len(geometry):

            geometry_node = geometry[geometry_cursor]

            if last_node is None:
                last_node = geometry_node
                continue

            distance += haversine(
                (last_node.lat, last_node.lon),
                (geometry_node.lat, geometry_node.lon),
                unit=Unit.METERS
            )

            if type(geometry_node) is RouteStopPositionSchema:
                if str(stops[stop_cursor].id) != str(stops[stop_cursor+1].id):
                    route_segments.append(RouteSegmentSchema(
                        stop_from_id=str(stops[stop_cursor].id),
                        stop_to_id=str(stops[stop_cursor+1].id),
                        segment_order=stop_cursor,
                        distance=distance,
                        crossings=crossings,
                        traffic_signals=traffic_signals,
                        speedbumps=speedbumps,
                        roundabouts=roundabouts
                    ))
                stop_cursor += 1
                distance = 0
                crossings = 0
                traffic_signals = 0
                speedbumps = 0
                roundabouts = 0
            elif type(geometry_node) is RouteObstacleSchema:
                if geometry_node.obstacle_type is RouteObstacleType.CROSSING:
                    crossings += 1
                elif geometry_node.obstacle_type is RouteObstacleType.TRAFFIC_SIGNALS:
                    traffic_signals += 1
                elif geometry_node.obstacle_type is RouteObstacleType.SPEEDBUMP:
                    speedbumps += 1
                elif geometry_node.obstacle_type is RouteObstacleType.ROUNDABOUT:
                    roundabouts += 1

            last_node = geometry_node
            geometry_cursor += 1

        return route_segments

    @staticmethod
    def as_osm_bbox(bbox):
        """ Конвертация bbox в формат OSM"""
        # (lon1, lat1, lon2, lat2) -> (lat1, lon1, lat2, lon2)
        return bbox[1], bbox[0], bbox[3], bbox[2]
