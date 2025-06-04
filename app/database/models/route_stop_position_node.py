from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.route_geometry_node import RouteGeometryNode


class RouteStopPositionNode(RouteGeometryNode):
    """ Модель данных для узла геометрии маршрута (место остановки автобуса) """

    # __tablename__ = "route_stop_position_nodes"
    #
    # id: Mapped[UUID] = mapped_column(ForeignKey("route_geometry_nodes.id", ondelete='CASCADE'), primary_key=True)
    corresponding_stop_id: Mapped[UUID] = mapped_column(ForeignKey("stops.id", ondelete='CASCADE'), nullable=True)

    # Для связи с родительским классом RouteGeometryNode используется polymorphic_identity
    __mapper_args__ = {
        "polymorphic_identity": "stop_position",
    }
