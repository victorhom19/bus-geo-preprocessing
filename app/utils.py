import math
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Tuple, List

import pygeos
import utm
from pygeos.lib import Geometry

Point = Tuple[float, float]
Segment = Tuple[Point, Point]


def project_point_on_segment(segment: Segment, point: Point, padding: float = 0) -> Tuple[Point | None, float]:
    """
    Проекция точки на отрезок

    В качестве результата возвращается кортеж из спроецированной точки (lat, lon) и расстояния от точки до отрезка.
    В случае, если проекция точки находится за границами отрезка - возвращается кортеж (None, math.inf)

    """

    # Конвертация координат точек в систему координат UTM
    # (аппроксимация декартовой системы координат)
    segment_start, segment_end = segment
    utm_segment_start = utm_point_from_latlon(segment_start[0], segment_start[1])
    utm_segment_end = utm_point_from_latlon(segment_end[0], segment_end[1])
    utm_point = utm_point_from_latlon(point[0], point[1])

    # Формулы и соотношения:
    # https://www.desmos.com/calculator/c84wacqfvt?lang=ru

    x1, y1 = utm_segment_start
    x2, y2 = utm_segment_end
    x3, y3 = utm_point

    alpha = math.atan2(y2 - y1, x2 - x1)
    beta = math.atan2(y3 - y1, x3 - x1)
    phi = beta - alpha

    d = math.sqrt((y3 - y1) ** 2 + (x3 - x1) ** 2)
    l = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    # Смещение относительно начала отрезка
    offset_from_first_point = d * math.cos(phi)

    # Проекционное расстояние
    snap_distance = abs(d * math.sin(phi))

    # Проверка вхождения спроецированной точки в границы отрезка (с учётом отступа)
    if offset_from_first_point < padding * l or offset_from_first_point > (1 - padding) * l:
        return None, math.inf

    # Определение координат спроецированной точки в UTM
    utm_projected_point = (
        x1 + offset_from_first_point * math.cos(alpha),
        y1 + offset_from_first_point * math.sin(alpha)
    )

    # Конвертация спроецированной точки из UTM в latlon
    zone_number, zone_letter = utm.from_latlon(float(point[0]), float(point[1]))[2:4]
    latlon_projected_point = utm.to_latlon(
        utm_projected_point[0], utm_projected_point[1],
        zone_number=zone_number,
        zone_letter=zone_letter
    )

    return latlon_projected_point, snap_distance

def frechet_distance(first_polyline: List[Point], second_polyline: List[Point]) -> float:
    """ Расчёт расстояния Фреше """

    # Преобразование точек первой ломанной latlon -> UTM -> Pygeos Geometry
    first_polyline_as_utm_points = [utm_point_from_latlon(p[0], p[1]) for p in first_polyline]
    first_route_geometry_string = ", ".join([f"{p[0]} {p[1]}" for p in first_polyline_as_utm_points])
    first_route_geometry = Geometry(f"LINESTRING ({first_route_geometry_string})")

    # Преобразование точек второй ломанной latlon -> UTM -> Pygeos Geometry
    second_polyline_as_utm_points = [utm_point_from_latlon(p[0], p[1]) for p in second_polyline]
    second_route_geometry_string = ", ".join([f"{p[0]} {p[1]}" for p in second_polyline_as_utm_points])
    second_route_geometry = Geometry(f"LINESTRING ({second_route_geometry_string})")

    # Расчёт расстояния Фреше с помощью библиотеки Pygeos
    res = pygeos.frechet_distance(first_route_geometry, second_route_geometry)

    return res

def utm_point_from_latlon(lat: float | Decimal, lon: float | Decimal) -> Point:
    """ Конвертация координат точки из latlon (EPSG 4326) в UTM """
    return utm.from_latlon(float(lat), float(lon))[:2]
