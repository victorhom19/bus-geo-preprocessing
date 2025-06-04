from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class SegmentSpeed(Base):
    """ Модель данных для скорости сегмента маршрута (участка между двумя остановками) """

    __tablename__ = 'segments_speeds'
    __table_args__ = (
        CheckConstraint('speed >= 0', name='speed_constraint'),
        CheckConstraint('0 <= weekday and weekday <= 6', name='weekday_constraint'),
        CheckConstraint('0 <= hour_interval and hour_interval <= 23', name='hour_interval_constraint'),
        CheckConstraint('segment_order >= 0', name='segment_order_constraint')
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    weekday: Mapped[int]
    hour_interval: Mapped[int]
    speed_profile_id: Mapped[UUID] = mapped_column(ForeignKey('speed_profiles.id', ondelete='CASCADE'))
    route_segment_id: Mapped[UUID] = mapped_column(ForeignKey('route_segments.id', ondelete='CASCADE'))
    segment_order: Mapped[int]
    speed: Mapped[float]
