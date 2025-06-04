from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ClusteringCorrespondence(Base):
    """ Модель данных для матрицы корреспонденций, полученной в результате кластеризации """

    __tablename__ = 'clustering_correspondences'
    __table_args__ = (
        CheckConstraint('cluster_from_index >= 0 and cluster_to_index >= 0', name='cluster_index_constraint'),
        CheckConstraint('0 <= weekday and weekday <= 6', name='weekday_constraint'),
        CheckConstraint('0 <= hour_interval and hour_interval <= 23', name='hour_interval_constraint'),
        CheckConstraint('transitions >= 0', name='transitions_count_constraint'),
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    clustering_profile_id: Mapped[UUID] = mapped_column(ForeignKey('clustering_profiles.id', ondelete='CASCADE'))
    cluster_from_index: Mapped[int]
    cluster_to_index: Mapped[int]
    weekday: Mapped[int]
    hour_interval: Mapped[int]
    transitions: Mapped[float]
