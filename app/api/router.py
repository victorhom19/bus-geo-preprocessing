from typing import List

from fastapi import APIRouter, Depends, Query, UploadFile, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_schemas import GetBusDataRequest, GetBusDataResponse, TruncatedSpeedProfile, \
    GenerateSpeedProfileRequest, GenerateClusteringProfileRequest, ApplyClusteringResponse
from app.database.database import get_session
from app.dispatcher.dispatcher import Dispatcher
from app.schemas.clustering_profile_schema import ClusteringDataSchema, ClusteringProfileSchema, \
    TruncatedClusteringProfileSchema
from app.schemas.route import RouteSchema
from app.schemas.speed_profile_schema import SpeedProfileSchema, SpeedDataSchema
from app.schemas.stop import StopSchema

# Группа конечных точек API для блока обработки данных остановок и маршрутов
bus_data_router = APIRouter(tags=['BusData'], prefix='/bus_data')

@bus_data_router.get('/')
async def get_bus_data(data_request: GetBusDataRequest = Query(),
                       session: AsyncSession = Depends(get_session)) -> GetBusDataResponse:
    """ Получение данных об остановках """
    return await Dispatcher(session).get_bus_data(data_request.source, data_request.bbox)

@bus_data_router.get('/stops')
async def get_bus_stops(data_request: GetBusDataRequest = Query(),
                        session: AsyncSession = Depends(get_session)) -> List[StopSchema]:
    """ Получение данных об остановках """
    return await Dispatcher(session).get_bus_stops(data_request.source, data_request.bbox)

@bus_data_router.post('/stops')
async def create_bus_stops(stops: List[StopSchema], session: AsyncSession = Depends(get_session)) -> List[StopSchema]:
    """ Создание записей об остановках в локальной базе данных """
    return await Dispatcher(session).create_bus_stops(stops)

@bus_data_router.delete('/stops')
async def delete_bus_stops(stops_ids: List[str], session: AsyncSession = Depends(get_session)) -> List[StopSchema]:
    """ Удаление записей об остановках в локальной базе данных """
    return await Dispatcher(session).delete_bus_stops(stops_ids)

@bus_data_router.get('/routes')
async def get_bus_routes(data_request: GetBusDataRequest = Query(),
                         session: AsyncSession = Depends(get_session)) -> List[RouteSchema]:
    """ Получение данных о маршрутах """
    return await Dispatcher(session).get_bus_routes(data_request.source, data_request.bbox)

@bus_data_router.post('/routes')
async def create_bus_routes(routes: List[RouteSchema],
                            session: AsyncSession = Depends(get_session)) -> List[RouteSchema]:
    """ Создание записей о маршрутах в локальной базе данных """
    return await Dispatcher(session).create_bus_routes(routes)

@bus_data_router.delete('/routes')
async def delete_bus_routes(routes_ids: List[str], session: AsyncSession = Depends(get_session)) -> List[RouteSchema]:
    """ Удаление записей о маршрутах в локальной базе данных """
    return await Dispatcher(session).delete_bus_routes(routes_ids)


# Группа конечных точек API для блока обработки данных загруженности дорог
traffic_flow_router = APIRouter(tags=['TrafficFlow'], prefix='/traffic_flow')

@traffic_flow_router.post('/data')
async def upload_speed_data(speed_data_files: List[UploadFile], name: str = Body(),
                            session: AsyncSession = Depends(get_session)) -> SpeedDataSchema | None:
    """ Загрузка исходных данных о скоростях транспортных сегментов """
    return await Dispatcher(session).upload_speed_data(speed_data_files, name)

@traffic_flow_router.get('/data/list')
async def get_speed_data_list(session: AsyncSession = Depends(get_session)) -> List[SpeedDataSchema]:
    """ Получение списка данных о скоростях транспортных сегментов """
    return await Dispatcher(session).get_speed_data_list()

@traffic_flow_router.delete('/data/{speed_data_id}')
async def delete_speed_data(speed_data_id: str, session: AsyncSession = Depends(get_session)) -> SpeedDataSchema:
    """ Удаление исходных данных о скоростях транспортных сегментов по идентификатору """
    return await Dispatcher(session).delete_speed_data(speed_data_id)

@traffic_flow_router.post('/')
async def generate_speed_profile(data_request: GenerateSpeedProfileRequest,
                                 session: AsyncSession = Depends(get_session)) -> SpeedProfileSchema:
    """ Генерация профиля скорости """
    return await Dispatcher(session).generate_speed_profile(data_request.name, data_request.routes_ids,
                                                            data_request.speed_data_id)

@traffic_flow_router.get('/list')
async def get_speed_profile_list(session: AsyncSession = Depends(get_session)) -> List[TruncatedSpeedProfile]:
    """ Получение списка профилей скорости """
    return await Dispatcher(session).get_speed_profiles_list()

@traffic_flow_router.get('/{speed_profile_id}')
async def get_speed_profile(speed_profile_id: str,
                            session: AsyncSession = Depends(get_session)) -> SpeedProfileSchema | None:
    """ Получение профиля скорости по идентификатору """
    return await Dispatcher(session).get_speed_profile(speed_profile_id)

@traffic_flow_router.delete('/{speed_profile_id}')
async def delete_speed_profile(speed_profile_id: str,
                               session: AsyncSession = Depends(get_session)) -> SpeedProfileSchema | None:
    """ Удаление профиля скорости по идентификатору """
    return await Dispatcher(session).delete_speed_profile(speed_profile_id)


# Группа конечных точек API для блока обработки данных загруженности дорог
stops_clustering = APIRouter(tags=['StopsClustering'], prefix='/stops_clustering')

@stops_clustering.post('/data')
async def upload_clustering_data(clustering_data_file: UploadFile, name: str = Body(),
                                 session: AsyncSession = Depends(get_session)) -> ClusteringDataSchema | None:
    """ Загрузка исходных данных для кластеризации остановок """
    return await Dispatcher(session).upload_clustering_data(clustering_data_file, name)


@stops_clustering.get('/data/list')
async def get_clustering_data_list(session: AsyncSession = Depends(get_session)) -> List[ClusteringDataSchema]:
    """ Получение списка исходных данных для кластеризации остановок """
    return await Dispatcher(session).get_clustering_data_list()

@stops_clustering.delete('/data/{clustering_data_id}')
async def delete_clustering_data(clustering_data_id: str,
                                 session: AsyncSession = Depends(get_session)) -> ClusteringDataSchema:
    """ Удаление исходных данных для кластеризации остановок по идентификатору """
    return await Dispatcher(session).delete_clustering_data(clustering_data_id)

@stops_clustering.post('/generate')
async def generate_clustering_profiles(generate_clustering_profile_request: GenerateClusteringProfileRequest,
                                       session: AsyncSession = Depends(get_session)) -> List[TruncatedClusteringProfileSchema]:
    """ Генерация профилей кластеризации """
    return await Dispatcher(session).generate_clustering_profile(generate_clustering_profile_request.params)

@stops_clustering.post('/realize')
async def realize_clustering_profile(clustering_profile: TruncatedClusteringProfileSchema,
                                     session: AsyncSession = Depends(get_session)) -> ClusteringProfileSchema:
    """ Сохранение выбранного профиля кластеризации """
    return await Dispatcher(session).realize_clustering_profile(clustering_profile)

@stops_clustering.get('/list')
async def get_clustering_profiles_list(session: AsyncSession = Depends(get_session)) -> List[ClusteringProfileSchema]:
    """ Получение списка профилей кластеризации """
    return await Dispatcher(session).get_clustering_profiles_list()

@stops_clustering.post("/{clustering_profile_id}")
async def apply_clustering_profile(clustering_profile_id: str, stops_ids: List[str],
                                   session: AsyncSession = Depends(get_session)) -> ApplyClusteringResponse:
    """ Применение профиля кластеризации """
    return await Dispatcher(session).apply_clustering(clustering_profile_id, stops_ids)

@stops_clustering.delete("/{clustering_profile_id}")
async def delete_clustering_profile(clustering_profile_id: str,
                                    session: AsyncSession = Depends(get_session)) -> ClusteringProfileSchema | None:
    """ Удаление профиля кластеризации по идентификатору """
    return await Dispatcher(session).delete_clustering_profile(clustering_profile_id)

# Объединение отдельных групп конечных точек
router = APIRouter()
router.include_router(bus_data_router)
router.include_router(traffic_flow_router)
router.include_router(stops_clustering)