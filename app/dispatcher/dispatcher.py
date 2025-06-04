import ast
import json
import os
from typing import Optional, List

from fastapi import File
from sqlalchemy import select, asc

from app.api.api_schemas import GetBusDataResponse, TruncatedSpeedProfile, ApplyClusteringResponse
from app.common_types import BBox
from app.database.daos.base_dao import BaseDAO
from app.database.daos.clustering_profile_dao import ClusteringProfileDAO
from app.database.daos.route_dao import RouteDAO
from app.database.daos.speed_profile_dao import SpeedProfileDAO
from app.database.daos.stop_dao import StopDAO
from app.database.models import RouteSegment, SegmentSpeed, SpeedData, ClusteringData
from app.schemas.clustering_profile_schema import ClusteringDataSchema, ClusteringProfileSchema, \
    TruncatedClusteringProfileSchema, ClusteredStopSchema
from app.schemas.enums import BusDataProvider, Weekday
from app.schemas.route import RouteSchema
from app.schemas.speed_profile_schema import SpeedProfileSchema, SpeedDataSchema
from app.schemas.stop import StopSchema
from app.schemas.stops_clustering import StopsClusteringParams, CorrespondenceNode, CorrespondenceEntry, \
    ClusteredCorrespondenceEntry
from app.services.bus_data.local.local_bus_data_provider import LocalBusDataProvider
from app.services.bus_data.osm.osm_bus_data_provider import OSMBusDataProvider
from app.services.stops_clustering.stops_clustering_provider import StopsClusteringProvider
from app.services.traffic_flow.tomtom.tomtom_traffic_flow_provider import TomtomTrafficFlowProvider
from config import SRC_PATH


class Dispatcher:
    """ Класс узла диспетчеризации """

    def __init__(self, session):
        self.session = session

    async def get_bus_data(self, source: BusDataProvider, bbox: Optional[BBox]) -> GetBusDataResponse:
        """ Получение данных об остановках и маршрутах """

        if source is BusDataProvider.LOCAL:  # Провайдер данных - локальная база данных
            stops, routes = await LocalBusDataProvider(self.session).get_bus_data_in_bbox(bbox)
        elif source is BusDataProvider.OSM:  # Провайдер данных - интерфейс Overpass API
            # Подготовка данных о заранее синхронизированных остановках и маршрутах
            db_stops_mapping = await LocalBusDataProvider(self.session).prepare_local_stops_mapping(bbox)
            db_routes_mapping = await LocalBusDataProvider(self.session).prepare_local_routes_mapping(bbox)
            # Запрос данных
            stops, routes = await OSMBusDataProvider(db_stops_mapping, db_routes_mapping).get_bus_data_in_bbox(bbox)
        else:
            raise ValueError('Non-existing bus data source!')

        return GetBusDataResponse(stops=stops, routes=routes)

    async def get_bus_stops(self, source: BusDataProvider, bbox: Optional[BBox]) -> List[StopSchema]:
        """ Получение данных об остановках """
        if source is BusDataProvider.LOCAL:  # Провайдер данных - локальная база данных
            return await LocalBusDataProvider(self.session).get_stops_in_bbox(bbox)
        elif source is BusDataProvider.OSM:  # Провайдер данных - интерфейс Overpass API
            # Подготовка данных о заранее синхронизированных остановках
            db_stops_mapping = await LocalBusDataProvider(self.session).prepare_local_stops_mapping(bbox)
            # Запрос данных
            return await OSMBusDataProvider(db_stops_mapping).get_stops_in_bbox(bbox)
        else:
            raise ValueError('Non-existing bus data source!')

    async def create_bus_stops(self, stop_schemas: List[StopSchema]) -> List[StopSchema]:
        """ Создание записей об остановках """
        db_stops = await StopDAO(self.session).create_all(stop_schemas)
        out_stops_schemas = [LocalBusDataProvider.db_stop_as_schema(db_stop) for db_stop in db_stops]
        return out_stops_schemas

    async def delete_bus_stops(self, stops_ids: List[str]) -> List[StopSchema]:
        """ Удаление записей об остановках """
        db_stops = await StopDAO(self.session).delete_all(stops_ids)
        out_stops_schemas = [LocalBusDataProvider.db_stop_as_schema(db_stop) for db_stop in db_stops]
        return out_stops_schemas

    async def get_bus_routes(self, source: BusDataProvider, bbox: Optional[BBox]) -> List[RouteSchema]:
        """ Получение данных о маршрутах """
        if source is BusDataProvider.LOCAL:  # Провайдер данных - локальная база данных
            return await LocalBusDataProvider(self.session).get_routes_in_bbox(bbox)
        elif source is BusDataProvider.OSM:  # Провайдер данных - интерфейс Overpass API
            # Подготовка данных о заранее синхронизированных остановках и маршрутах
            db_stops_mapping = await LocalBusDataProvider(self.session).prepare_local_stops_mapping(bbox)
            db_routes_mapping = await LocalBusDataProvider(self.session).prepare_local_routes_mapping(bbox)
            # Запрос данных
            return await OSMBusDataProvider(db_stops_mapping, db_routes_mapping).get_routes_in_bbox(bbox)
        else:
            raise ValueError('Non-existing bus data source!')

    async def create_bus_routes(self, route_schemas: List[RouteSchema]) -> List[RouteSchema]:
        """ Создание записей об маршрутах """
        db_routes = await RouteDAO(self.session).create_all(route_schemas)
        out_routes_schemas = [LocalBusDataProvider.db_route_as_schema(db_route) for db_route in db_routes]
        return out_routes_schemas

    async def delete_bus_routes(self, routes_ids: List[str]) -> List[RouteSchema]:
        """ Удаление записей о маршрутах """
        db_routes = await RouteDAO(self.session).delete_all(routes_ids)
        out_routes_schemas = [LocalBusDataProvider.db_route_as_schema(db_route) for db_route in db_routes]
        return out_routes_schemas

    async def upload_speed_data(self, speed_data_files: List[File], name: str) -> SpeedDataSchema | None:
        """ Загрузка файлов с данными о загруженности дорожных сегментов """

        # Проверка количества файлов
        if len(speed_data_files) != len(Weekday):
            return None

        # Определение директории для сохранения файлов
        file_storage_path = os.path.join(SRC_PATH, 'services/traffic_flow/files')
        if not os.path.exists(file_storage_path):
            os.mkdir(file_storage_path)

        # Создание записи в локальной базе данных
        db_speed_data = await BaseDAO(self.session, SpeedData).create(name=name)

        # Сохранение файлов
        for speed_data_file, weekday in zip(speed_data_files, Weekday):
            file_path = os.path.join(file_storage_path, f"{str(db_speed_data.id)}_{weekday.value}.json")
            with open(file_path, "w", encoding='utf-8') as file:
                binary_data = await speed_data_file.read()
                data = json.loads(binary_data)
                json.dump(data, file, ensure_ascii=False)

        return SpeedDataSchema(id=str(db_speed_data.id), name=name)

    async def get_speed_data_list(self) -> List[SpeedDataSchema]:
        """ Получение списка данных о загруженности дорожных сегментов """
        db_speed_data_entries = await BaseDAO(self.session, SpeedData).get_all()
        return [
            SpeedDataSchema(
                id=str(db_speed_data.id),
                name=db_speed_data.name)
            for db_speed_data in db_speed_data_entries
        ]

    async def delete_speed_data(self, speed_data_id: str) -> SpeedDataSchema:
        """ Удаление записи о данных загруженности дорожных сегментов """

        # Удаление файлов
        file_storage_path = os.path.join(SRC_PATH, 'services/traffic_flow/files')
        for weekday in Weekday:
            file_path = os.path.join(file_storage_path, f"{speed_data_id}_{weekday.value}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

        # Удаление записи из базы данных
        db_speed_data = await BaseDAO(self.session, SpeedData).get_by_id(speed_data_id)
        await BaseDAO(self.session, SpeedData).delete_by_id(speed_data_id)
        return SpeedDataSchema(id=str(db_speed_data.id), name=db_speed_data.name)

    async def generate_speed_profile(self, profile_name: str, routes_ids: List[str],
                                     speed_data_id: str) -> SpeedProfileSchema:
        """ Генерация профиля скорости для выбранных маршрутов """

        # Получение записей о маршрутах из локальной базы данных
        routes = [
            LocalBusDataProvider.db_route_as_schema(
                await RouteDAO(self.session).get_by_id(route_id)
            ) for route_id in routes_ids
        ]

        # Создание записи о профиле скорости
        routes_speed_mapping = await TomtomTrafficFlowProvider(self.session).create_speed_profile(routes, speed_data_id)
        _speed_profile = await SpeedProfileDAO(self.session).create(profile_name, routes_speed_mapping, speed_data_id)
        return SpeedProfileSchema(
            id=str(_speed_profile.id),
            name=profile_name,
            routes=routes_speed_mapping,
            speed_data_id=speed_data_id
        )

    async def get_speed_profiles_list(self) -> List[TruncatedSpeedProfile]:
        """ Получение списка сгенерированных профилей скорости """
        db_speed_profiles = await SpeedProfileDAO(self.session).get_all()
        return [
            TruncatedSpeedProfile(
                id=str(speed_profile.id),
                name=speed_profile.name
            ) for speed_profile in db_speed_profiles
        ]

    async def get_speed_profile(self, profile_id: str) -> SpeedProfileSchema | None:
        """ Получение полных данных профиля скорости """

        # Проверка на существование искомой записи
        db_speed_profile = await SpeedProfileDAO(self.session).get_by_id(profile_id)
        if db_speed_profile is None:
            return None

        # Получение данных смежных таблиц
        stmt = (
            select(SegmentSpeed, RouteSegment)
            .where(SegmentSpeed.speed_profile_id == db_speed_profile.id)
            .join(SegmentSpeed, SegmentSpeed.route_segment_id == RouteSegment.id)
            .order_by(asc(RouteSegment.segment_order))
        )
        res = (await self.session.execute(stmt)).all()

        # Реконструкция вложенной структуры данных, описывающей скорости сегментов маршрутов для выбранного профиля
        route_id_to_weekday = {}
        for segment_speed, route_segment in res:
            route_id = str(route_segment.route_id)
            weekday = list(Weekday)[segment_speed.weekday].value
            hour = segment_speed.hour_interval
            speed = segment_speed.speed
            if route_id not in route_id_to_weekday:
                route_id_to_weekday[route_id] = {}
            if weekday not in route_id_to_weekday[route_id]:
                route_id_to_weekday[route_id][weekday] = {}
            if hour not in route_id_to_weekday[route_id][weekday]:
                route_id_to_weekday[route_id][weekday][hour] = []
            route_id_to_weekday[route_id][weekday][hour].append(speed)

        return SpeedProfileSchema(
            id=str(db_speed_profile.id),
            name=db_speed_profile.name,
            routes=route_id_to_weekday,
            speed_data_id=str(db_speed_profile.speed_data_id)
        )

    async def delete_speed_profile(self, profile_id: str) -> SpeedProfileSchema | None:
        """ Удаление профиля скорости """
        speed_profile = await self.get_speed_profile(profile_id)
        if speed_profile is None:
            return None
        await SpeedProfileDAO(self.session).delete_by_id(profile_id)
        return speed_profile

    async def upload_clustering_data(self, clustering_data_file: File, name: str) -> ClusteringDataSchema:
        """ Загрузка исходных данных кластеризации """

        # Определение директории для сохранения файлов
        file_storage_path = os.path.join(SRC_PATH, 'services/stops_clustering/files')
        if not os.path.exists(file_storage_path):
            os.mkdir(file_storage_path)

        # Создание записи в локальной базе данных
        db_clustering_data = await BaseDAO(self.session, ClusteringData).create(name=name)

        # Сохранение файла
        file_path = os.path.join(file_storage_path, f"{str(db_clustering_data.id)}.json")
        with open(file_path, "w", encoding='utf-8') as file:
            binary_data = await clustering_data_file.read()
            data = json.loads(binary_data)
            json.dump(data, file, ensure_ascii=False)

        return ClusteringDataSchema(id=str(db_clustering_data.id), name=name)

    async def get_clustering_data_list(self) -> List[ClusteringDataSchema]:
        """ Получение списка данных кластеризации """
        db_clustering_data_entries = await BaseDAO(self.session, ClusteringData).get_all()
        return [
            ClusteringDataSchema(
                id=str(db_clustering_data.id),
                name=db_clustering_data.name)
            for db_clustering_data in db_clustering_data_entries
        ]

    async def delete_clustering_data(self, clustering_data_id: str) -> ClusteringDataSchema:
        """ Удаление записи о данных кластеризации """
        file_storage_path = os.path.join(SRC_PATH, 'services/stops_clustering/files')
        file_path = os.path.join(file_storage_path, f"{clustering_data_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

        db_clustering_data = await BaseDAO(self.session, ClusteringData).get_by_id(clustering_data_id)
        await BaseDAO(self.session, ClusteringData).delete_by_id(clustering_data_id)
        return ClusteringDataSchema(id=str(db_clustering_data.id), name=db_clustering_data.name)

    @staticmethod
    async def generate_clustering_profile(params: StopsClusteringParams) -> List[TruncatedClusteringProfileSchema]:
        """ Генерация вариантов профиля кластеризации (поиск по сетке параметров) """
        return await StopsClusteringProvider().grid_search(params)

    async def realize_clustering_profile(self, clustering_profile: TruncatedClusteringProfileSchema)\
            -> ClusteringProfileSchema:
        """ Создание записи профиля кластеризации на основе одного из сгенерированных вариантов """

        # Кластеризация на основе сгенерированного варианта профиля (получение кластеризованных узлов и пересчёт
        # матрицы корреспонденций)
        clustered_nodes, clustered_correspondence, = await StopsClusteringProvider().realize_clustering_profile(
            clustering_profile.clustering_params)

        # Создание записи в локальной базе данных
        db_clustering_profile = await ClusteringProfileDAO(self.session).create(
            clustering_profile=clustering_profile,
            nodes=clustered_nodes,
            correspondence=clustered_correspondence,
        )

        return ClusteringProfileSchema(
            id=str(db_clustering_profile.id),
            name=clustering_profile.name,
            clustering_params=clustering_profile.clustering_params,
            clusters_count=clustering_profile.clusters_count,
            clustering_score=clustering_profile.clustering_score
        )

    async def get_clustering_profiles_list(self) -> List[ClusteringProfileSchema]:
        """ Получение списка сгенерированных профилей кластеризации """
        db_clustering_profiles = await ClusteringProfileDAO(self.session).get_all()
        return [
            ClusteringProfileSchema(
                id=str(db_clustering_profile.id),
                name=db_clustering_profile.name,
                clustering_params=StopsClusteringParams(**ast.literal_eval(db_clustering_profile.clustering_params)),
                clusters_count=db_clustering_profile.clusters_count,
                clustering_score=db_clustering_profile.clustering_score
            ) for db_clustering_profile in db_clustering_profiles
        ]

    async def apply_clustering(self, clustering_profile_id: str, stops_ids: List[str]) -> ApplyClusteringResponse:
        """ Применение профиля кластеризации для кластеризации автобусных остановок """

        # Получение профиля кластеризации из базы данных
        db_clustering_profile = await ClusteringProfileDAO(self.session).get_by_id(clustering_profile_id)

        # Определение опорных точек кластеризации
        anchor_nodes = [
            CorrespondenceNode(
                id=str(node.id),
                lat=node.lat,
                lon=node.lon
            )
            for node in db_clustering_profile.clustering_anchors
        ]
        anchor_labels = [node.cluster_index for node in db_clustering_profile.clustering_anchors]

        # Получение объектов остановок из локальной базы данных
        db_stops = await StopDAO(self.session).get_all_by_ids(stops_ids)
        stops_as_orphan_nodes = [
            CorrespondenceNode(
                id=str(node.id),
                lat=node.lat,
                lon=node.lon
            )
            for node in db_stops
        ]

        # Подготовка параметров кластеризации
        params = StopsClusteringParams(**ast.literal_eval(db_clustering_profile.clustering_params))

        # Сопоставление остановок и индексов кластеров
        orphan_labels = StopsClusteringProvider().fill_orphan(
            anchor_nodes,
            anchor_labels,
            stops_as_orphan_nodes,
            params
        )

        # Формирование выходных схем данных для кластеризованных остановок
        clustered_stops = [
            ClusteredStopSchema(
                id=str(stop.id),
                source=stop.source,
                name=stop.name,
                lat=stop.lat,
                lon=stop.lon,
                cluster_index=cluster_index
            ) for stop, cluster_index in zip(db_stops, orphan_labels)
        ]

        # Формирование выходных схем данных для обновлённой матрицы корреспонденций
        clustered_correspondence = [
            ClusteredCorrespondenceEntry(
                cluster_from_index=db_clustered_correspondence.cluster_from_index,
                cluster_to_index=db_clustered_correspondence.cluster_to_index,
                weekday=db_clustered_correspondence.weekday,
                hour_interval=db_clustered_correspondence.hour_interval,
                transitions=db_clustered_correspondence.transitions
            ) for db_clustered_correspondence in db_clustering_profile.clustering_correspondence
        ]

        return ApplyClusteringResponse(
            clustered_stops=clustered_stops,
            clustered_correspondence=clustered_correspondence
        )

    async def delete_clustering_profile(self, profile_id: str) -> ClusteringProfileSchema | None:
        """ Удаление профиля кластеризации """
        db_clustering_profile = await self.get_speed_profile(profile_id)
        if db_clustering_profile is None:
            return None
        await ClusteringProfileDAO(self.session).delete_by_id(profile_id)
        return ClusteringProfileSchema(
            id=str(db_clustering_profile.id),
            name=db_clustering_profile.name,
            clustering_params=StopsClusteringParams(**ast.literal_eval(db_clustering_profile.clustering_params)),
            clusters_count=db_clustering_profile.clusters_count,
            clustering_score=db_clustering_profile.clustering_score
        )