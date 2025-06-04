from typing import List
from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import CheckConstraint, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ClusteringProfile(Base):
    """ Модель данных для сгенерированного профиля кластеризации автобусных остановок """

    __tablename__ = 'clustering_profiles'
    __table_args__ = (
        CheckConstraint('clusters_count >= 0', name='clusters_count_constraint'),
        CheckConstraint('0 <= clustering_score and clustering_score <= 1', name='clustering_score_constraint'),
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    name: Mapped[str]
    clustering_data_id: Mapped[UUID] = mapped_column(ForeignKey('clustering_data.id', ondelete='CASCADE'))
    clustering_params: Mapped[JSON] = mapped_column(type_=JSON, nullable=False)
    clusters_count: Mapped[int]
    clustering_score: Mapped[float]

    clustering_anchors: Mapped[List['ClusteringAnchor']] = relationship(lazy='selectin')
    clustering_correspondence: Mapped[List['ClusteringCorrespondence']] = relationship(lazy='selectin')
