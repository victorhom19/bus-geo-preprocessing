from typing import List
from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class SpeedProfile(Base):
    """ Модель данных для сгенерированного скоростного профиля """

    __tablename__ = 'speed_profiles'

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    name: Mapped[str]
    speed_data_id: Mapped[UUID] = mapped_column(ForeignKey('speed_data.id', ondelete='CASCADE'))

    segments_speeds: Mapped[List['SegmentSpeed']] = relationship(lazy='selectin', order_by='SegmentSpeed.segment_order')