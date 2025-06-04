from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.enums import ObstacleType, ObstacleTypeEnum
from app.database.models.route_geometry_node import RouteGeometryNode


class RouteObstacleNode(RouteGeometryNode):
    """ Модель данных для узла геометрии маршрута (дорожное препятствие) """

    obstacle_type: Mapped[ObstacleType] = mapped_column(ObstacleTypeEnum, nullable=True)

    # Для связи с родительским классом RouteGeometryNode используется polymorphic_identity
    __mapper_args__ = {
        "polymorphic_identity": "obstacle",
    }
