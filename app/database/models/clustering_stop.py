from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ClusteringStop(Base):
    """ Модель данных для связи таблиц профилей кластеризации и остановок отношением многие-ко-многим """

    __tablename__ = 'clustering_stops'

    __table_args__ = (
        CheckConstraint('cluster_index >= 0', name='cluster_index_constraint'),
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    clustering_profile_id: Mapped[UUID] = mapped_column(ForeignKey('clustering_profiles.id', ondelete='CASCADE'))
    stop_id: Mapped[UUID] = mapped_column(ForeignKey('stops.id', ondelete='CASCADE'))
    cluster_index: Mapped[int]
