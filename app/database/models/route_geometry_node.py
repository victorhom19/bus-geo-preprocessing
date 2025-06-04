from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class RouteGeometryNode(Base):
    """ Модель данных для узла геометрии маршрута """

    __tablename__ = 'route_geometry_nodes'
    __table_args__ = (
        CheckConstraint('node_order >= 0', name='node_order_constraint'),
        CheckConstraint('-90 <= lat and lat <= 90', name='lat_constraint'),
        CheckConstraint('-180 <= lon and lon <= 180', name='lon_constraint')
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    route_id: Mapped[UUID] = mapped_column(ForeignKey('routes.id', ondelete='CASCADE'))
    node_order: Mapped[int]
    lat: Mapped[float]
    lon: Mapped[float]
    type: Mapped[str]

    # Для организации иерархии используется polymorphic_identity:
    # RouteGeometryNode является базовым классом для RouteStopPositionNode и RouteObstacleNode
    __mapper_args__ = {
        'polymorphic_identity': 'geometry',
        'polymorphic_on': 'type',
        'with_polymorphic': '*'
    }
