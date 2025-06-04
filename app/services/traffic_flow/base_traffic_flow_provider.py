from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List, Dict

import numpy as np
from sklearn.neighbors._kd_tree import KDTree

from app.common_types import BBox
from app.schemas.route import RouteSchema
from app.utils import utm_point_from_latlon, project_point_on_segment


@dataclass
class TrafficFlowSegment:
    """ Класс-контейнер для хранения информации о загруженности транспортных потоков на отдельном отрезке дороги """

    first_point: Tuple[float, float]
    second_point: Tuple[float, float]
    speed: float

    def json(self):
        """ Конвертация объекта в json-сериализуемый объект """
        return {
            'first_point': self.first_point,
            'second_point': self.second_point,
            'speed': self.speed
        }

    @staticmethod
    def from_json(json_dict):
        """ Построение объекта из json-сериализуемого объекта """
        return TrafficFlowSegment(
            first_point=json_dict.get('first_point'),
            second_point=json_dict.get('second_point'),
            speed=json_dict.get('speed')
        )

    def __post_init__(self):
        """ Инициализация """

        # Конвертация концов отрезка в систему координат UTM
        self.utm_first_point = utm_point_from_latlon(self.first_point[0], self.first_point[1])
        self.utm_second_point = utm_point_from_latlon(self.second_point[0], self.second_point[1])

        # Расчёт вектора ориентации отрезка дороги
        dx = self.utm_second_point[0] - self.utm_first_point[0]
        dy = self.utm_second_point[1] - self.utm_first_point[1]
        vector = np.array([dx, dy])
        norm = np.linalg.norm(vector)
        self.direction = vector / norm

    def get_point_snap_distance(self, target_point, extent=0.2):
        """ Определение кратчайшего расстояния от точки до отрезка дороги """

        # Используется функция для проекции точки на отрезок. Отступ при этом берётся отрицательным (отрезки дороги
        # немного удлиняются) для того, чтобы точке автобусного маршрута было проще сопоставить отрезок. Это снижает
        # количество "промахов" в случае дорог с сильной кривизной.
        padding = -extent
        _, snap_distance = project_point_on_segment(
            (self.first_point, self.second_point),
            target_point,
            padding
        )

        return snap_distance


class BaseTrafficFlowProvider(ABC):
    """ Базовый класс для получения данных о загруженности транспортных потоков """

    @staticmethod
    def match_routes_with_flows(routes: List[RouteSchema], flow_segments: List[TrafficFlowSegment]) -> Dict[str, List[float | None]]:
        """ Сопоставление геометрии маршрутов соответствующих узлов транспортных потоков """

        if len(flow_segments) == 0:
            return {}

        # Конвертация точек сегментов транспортных потоков в систему координат UTM (для корректного расчёта расстояний)
        flow_segments_as_points = []
        for segment in flow_segments:
            flow_segments_as_points += [segment.utm_first_point, segment.utm_second_point]

        # Организация точек сегментов в kd-дерево для обеспечения быстрого поиска ближайших соседей
        flow_node_tree = KDTree(flow_segments_as_points)

        routes_traffic_flow = {}

        # Последовательный обход маршрутов
        for route in routes:

            # Конвертация координат геометрии маршрута в СК UTM для корректного расчёта расстояний
            route_geometry_as_points = [utm_point_from_latlon(node.lat, node.lon) for node in route.geometry]

            # Определение индексов ближайших сегментов для каждой точки маршрута
            closest_segment_points_indices_matrix = flow_node_tree.query_radius(route_geometry_as_points, r=100)

            route_flow = []

            # Обход всех точек геометрии маршрута
            for i, utm_point in enumerate(route_geometry_as_points):

                # Определение ближайших сегментов для точки геометрии
                closest_segments_indices = set([j // 2 for j in closest_segment_points_indices_matrix[i]])
                closest_segments = [flow_segments[j] for j in closest_segments_indices]

                # Если рядом не обнаружено сегментов - переход к следующему узлу геометрии
                if len(closest_segments) == 0:
                    route_flow.append(None)
                    continue

                # Расчёт проекций точки на ближайшие сегменты
                latlon_point = (route.geometry[i].lat, route.geometry[i].lon)
                snap_distances = [segment.get_point_snap_distance(latlon_point) for segment in closest_segments]

                # Определение вектора направления движения транспорта в текущей точке геометрии.
                # Для всех точек, кроме последней, вектор определяется через точки: текущая -> следующая
                # Для последней точки: предыдущая -> текущая
                if i < len(route_geometry_as_points) - 1:
                    x1, y1 = utm_point
                    x2, y2 = route_geometry_as_points[i + 1]
                else:
                    x1, y1 = route_geometry_as_points[i - 1]
                    x2, y2 = utm_point

                translation_vector = np.array([x2 - x1, y2 - y1])
                translation_vector_magnitude = np.linalg.norm(translation_vector)

                # Проверка на то, что вектор имеет ненулевую длину
                if translation_vector_magnitude < 10e-2:
                    route_flow.append(None)
                    continue

                # Нормализация вектора направления
                direction_vector = translation_vector / translation_vector_magnitude

                # Расчёт скалярных произведений между направлением движения транспорта в точке текущей точке и
                # ориентациями ближайших сегментов транспортных потоков
                dot_products = [direction_vector.dot(segment.direction) for segment in closest_segments]

                packed_flow_segments = zip(closest_segments, snap_distances, dot_products)

                # Фильтрация узлов транспортных потоков по критерию со-направленности
                co_directional_flow_segments = [p for p in packed_flow_segments if p[2] > 0.8]

                # Проверка на то, что есть хотя бы один со-направленный сегмент
                if len(co_directional_flow_segments) == 0:
                    route_flow.append(None)
                    continue

                # Сортировка сегментов по удалённости от точки (через проекции)
                sorted_by_distance = sorted(co_directional_flow_segments, key=lambda p: p[1])

                # Сопоставление сегменту геометрии ближайшего со-направленного узла транспортного потока
                best_fitting_flow_segment = sorted_by_distance[0][0]
                route_flow.append(best_fitting_flow_segment.speed)

            # Сохранение результатов расчёта для маршрута
            routes_traffic_flow[str(route.id)] = route_flow

        return routes_traffic_flow
