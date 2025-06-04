from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import ForeignKey, CheckConstraint, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class RouteStop(Base):
    """ Модель данных для связи таблиц маршрутов и остановок отношением многие-ко-многим """

    __tablename__ = 'routes_stops'
    __table_args__ = (
        CheckConstraint('stop_order >= 0', name='stop_order_constraint'),
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    route_id: Mapped[UUID] = mapped_column(ForeignKey('routes.id', ondelete='CASCADE'))
    stop_id: Mapped[UUID] = mapped_column(ForeignKey('stops.id', ondelete='CASCADE'))
    stop_order: Mapped[int]

    stop: Mapped["Stop"] = relationship(lazy='selectin')
