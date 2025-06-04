from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class RouteSegment(Base):
    """ Модель данных для сегмента маршрута (участок между двумя остановками) """

    __tablename__ = 'route_segments'
    __table_args__ = (
        CheckConstraint('stop_from_id != stop_to_id', name='stops_constraint'),
        CheckConstraint('segment_order >= 0', name='segment_order_constraint'),
        CheckConstraint('distance >= 0', name='distance_constraint'),
        CheckConstraint('crossings >= 0', name='crossings_constraint'),
        CheckConstraint('traffic_signals >= 0', name='traffic_signals_constraint'),
        CheckConstraint('speedbumps >= 0', name='speedbumps_constraint'),
        CheckConstraint('roundabouts >= 0', name='roundabouts_constraint'),
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    route_id: Mapped[UUID] = mapped_column(ForeignKey('routes.id', ondelete='CASCADE'))
    stop_from_id: Mapped[UUID] = mapped_column(ForeignKey('stops.id', ondelete='CASCADE'))
    stop_to_id: Mapped[UUID] = mapped_column(ForeignKey('stops.id', ondelete='CASCADE'))
    segment_order: Mapped[int]
    distance: Mapped[float]
    crossings: Mapped[int]
    traffic_signals: Mapped[int]
    speedbumps: Mapped[int]
    roundabouts: Mapped[int]
