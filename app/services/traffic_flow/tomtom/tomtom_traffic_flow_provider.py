import asyncio
import json
import multiprocessing
import os
import time
from typing import List, Dict

from haversine import haversine, Unit
from sqlalchemy import select, asc

from app.common_types import BBox
from app.database.daos.speed_profile_dao import SpeedProfileDAO
from app.database.database import AsyncSessionFactory
from app.database.models import SegmentSpeed, RouteSegment
from app.logger import logger
from app.schemas.enums import Weekday
from app.schemas.route import RouteSchema
from app.schemas.route_geometry import RouteStopPositionSchema
from app.schemas.speed_profile_schema import SpeedProfileSchema, TruncatedSpeedProfileSchema, RouteIdToWeekday
from app.services.traffic_flow.base_traffic_flow_provider import BaseTrafficFlowProvider, TrafficFlowSegment
from config import SRC_PATH, app_config

HOURS = 24

class TomtomTrafficFlowProvider(BaseTrafficFlowProvider):
    """ Класс для получения данных о загруженности транспортных потоков посредством TomTom API """

    def __init__(self, session):
        self.session = session

    async def create_speed_profile(self, routes: List[RouteSchema], speed_data_id: str) -> RouteIdToWeekday:
        """ Получение данных о загруженности транспортных потоков"""

        logger.info(f"TRAFFIC FLOW > TOMTOM | FETCHING TRAFFIC FLOW")
        start = time.perf_counter()

        route_id_to_weekday = {}

        bbox = self.get_routes_bounds(routes)

        with multiprocessing.Pool(processes=min(len(Weekday), app_config.PROCESS_POOL_WORKERS_NUM)) as pool:
            items = [(weekday.value, bbox, routes, speed_data_id) for weekday in Weekday]
            for result in pool.starmap(self.routine, items):
                weekday, route_id_to_data = result
                for route_id, data in route_id_to_data.items():
                    if route_id not in route_id_to_weekday:
                        route_id_to_weekday[route_id] = {}
                    route_id_to_weekday[route_id][weekday] = data[weekday]
            pool.close()
            pool.join()

        end = time.perf_counter()

        log_message = "\n".join([
            f"GP > TRAFFIC FLOW > TOMTOM | Done:",
            f"GP > TRAFFIC FLOW > TOMTOM | * Affected routes: {len(routes)}",
            f"GP > TRAFFIC FLOW > TOMTOM | * Processing time: {end - start:3.2f} s"
        ])
        logger.info(log_message)

        return route_id_to_weekday

    @staticmethod
    def routine(weekday, bbox, routes, speed_data_id):
        traffic_flow = TomtomTrafficFlowProvider.get_traffic_flow_segments(speed_data_id, weekday, bbox)
        route_id_to_weekday = {}
        for hour in range(HOURS):
            traffic_flow_data = TomtomTrafficFlowProvider.match_routes_with_flows(routes, traffic_flow[hour])
            for route in routes:

                raw_speeds = traffic_flow_data[str(route.id)]

                segments_speeds = []

                segment_distance = 0
                segment_time = 0

                for node1, node2, speed in zip(route.geometry, route.geometry[1:], raw_speeds):
                    dist = haversine((node1.lat, node1.lon), (node2.lat, node2.lon),
                                     Unit.KILOMETERS)

                    if speed is None:
                        continue

                    if speed == 0:
                        speed = 40

                    segment_distance += dist
                    segment_time += dist / speed

                    if type(node2) is RouteStopPositionSchema:
                        segments_speeds.append(segment_distance / segment_time)
                        segment_distance = 0
                        segment_time = 0

                if str(route.id) not in route_id_to_weekday:
                    route_id_to_weekday[str(route.id)] = {}
                if weekday not in route_id_to_weekday[str(route.id)]:
                    route_id_to_weekday[str(route.id)][weekday] = {}
                if hour not in route_id_to_weekday[str(route.id)][weekday]:
                    route_id_to_weekday[str(route.id)][weekday][hour] = {}

                route_id_to_weekday[str(route.id)][weekday][hour] = segments_speeds

        return weekday, route_id_to_weekday

    @staticmethod
    def get_traffic_flow_segments(speed_data_id: str, day: str, bbox: BBox) -> Dict[int, List[TrafficFlowSegment]]:
        local_filename = speed_data_id + '_' + day + '.json'
        local_data_path = os.path.join(SRC_PATH, 'services/traffic_flow/files', local_filename)
        with open(local_data_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        segments = {_: [] for _ in range(HOURS)}
        for hour in range(HOURS):
            for entry in json_data[str(hour)]:
                segment = TrafficFlowSegment.from_json(entry)
                p1 = segment.first_point
                p2 = segment.second_point

                p1_inside_bbox = bbox[0] <= p1[1] <= bbox[2] and bbox[1] <= p1[0] <= bbox[3]
                p2_inside_bbox = bbox[0] <= p2[1] <= bbox[2] and bbox[1] <= p2[0] <= bbox[3]

                if p1_inside_bbox and p2_inside_bbox:
                    segments[hour].append(segment)

        return segments

    @staticmethod
    def get_routes_bounds(routes: List[RouteSchema]) -> BBox:
        min_lon = None
        min_lat = None
        max_lon = None
        max_lat = None

        for route in routes:
            for node in route.geometry:
                if min_lon is None or node.lon < min_lon:
                    min_lon = node.lon
                if min_lat is None or node.lat < min_lat:
                    min_lat = node.lat
                if max_lon is None or node.lon > max_lon:
                    max_lon = node.lon
                if max_lat is None or node.lat > max_lat:
                    max_lat = node.lat

        return min_lon, min_lat, max_lon, max_lat

