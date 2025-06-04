from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.enums import BusDataSource, BusDataSourceEnum


class Stop(Base):
    """ Модель данных для автобусной остановки """

    # Название таблицы
    __tablename__ = "stops"

    # Определение ограничений
    __table_args__ = (
        CheckConstraint('-90 <= lat and lat <= 90', name='lat_constraint'),
        CheckConstraint('-180 <= lon and lon <= 180', name='lon_constraint')
    )

    # Поля таблицы
    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    source: Mapped[BusDataSource] = mapped_column(BusDataSourceEnum)
    external_source_id: Mapped[Optional[str]]
    name: Mapped[str]
    lat: Mapped[float]
    lon: Mapped[float]
