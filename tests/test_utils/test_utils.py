import math

import pytest

from app.utils import Point, project_point_on_segment, utm_point_from_latlon


class TestUtils:

    EPS = 5

    def test_project_point_on_segment_1(self):
        """ Тест проекции точки на сегмент (стандартные условия) """

        segment = (60.00905395901133, 30.376232479388168), (60.00752998144263, 30.38548247862732)
        point = (60.008836489495735, 30.382471649857116)
        projected_point, distance = project_point_on_segment(segment, point, padding=0)

        gt_projected_point = (60.008099455093785, 30.382011738069018)
        gt_distance = 84.1

        assert abs(gt_distance - distance) < self.EPS
        assert self.points_are_equal(projected_point, gt_projected_point)

    def test_project_point_on_segment_2(self):
        """ Тест проекции точки на сегмент (проекция вне сегмента) """

        segment = (60.00905395901133, 30.376232479388168), (60.00752998144263, 30.38548247862732)
        point = (60.00682226857168, 30.38631040571538)
        projected_point, distance = project_point_on_segment(segment, point, padding=0)

        assert projected_point is None

    def test_project_point_on_segment_3(self):
        """ Тест проекции точки на сегмент (проекция попадает в сегмент благодаря доп. смещению) """

        segment = (60.00905395901133, 30.376232479388168), (60.00752998144263, 30.38548247862732)
        point = (60.00682226857168, 30.38631040571538)
        projected_point, distance = project_point_on_segment(segment, point, padding=-0.2)

        gt_projected_point = (60.007337345040895, 30.386619851766127)
        gt_distance = 59.1

        assert abs(gt_distance - distance) < self.EPS
        assert self.points_are_equal(projected_point, gt_projected_point)

    @classmethod
    def points_are_equal(cls, point1: Point, point2: Point) -> bool:
        utm_point1 = utm_point_from_latlon(point1[0], point1[1])
        utm_point2 = utm_point_from_latlon(point2[0], point2[1])
        dx = utm_point1[0] - utm_point2[0]
        dy = utm_point1[1] - utm_point2[1]
        return math.sqrt(dx**2 + dy**2) < cls.EPS
