from typing import Optional, List
from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import CheckConstraint, asc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.enums import BusDataSource, BusDataSourceEnum


class Route(Base):
    """ Модель данных для автобусного маршрута """

    __tablename__ = 'routes'
    __table_args__ = (
        CheckConstraint('final_stop_order >= 0', name='final_stop_order_constraint'),
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    source: Mapped[BusDataSource] = mapped_column(BusDataSourceEnum)
    external_source_id: Mapped[Optional[str]]
    name: Mapped[str]
    final_stop_order: Mapped[int]

    stops: Mapped[List['RouteStop']] = relationship(lazy='selectin', order_by='asc(RouteStop.stop_order)')
    segments: Mapped[List['RouteSegment']] = relationship(lazy='selectin', order_by='asc(RouteSegment.segment_order)')
    geometry: Mapped[List['RouteGeometryNode']] = relationship(lazy='selectin', order_by='asc(RouteGeometryNode.node_order)')
