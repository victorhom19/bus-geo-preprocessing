from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ClusteringAnchor(Base):
    """ Модель данных для опорной точки кластеризации """

    __tablename__ = 'clustering_anchors'
    __table_args__ = (
        CheckConstraint('-90 <= lat and lat <= 90', name='lat_constraint'),
        CheckConstraint('-180 <= lon and lon <= 180', name='lon_constraint'),
        CheckConstraint('cluster_index >= 0', name='cluster_index_constraint')
    )

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    clustering_profile_id: Mapped[UUID] = mapped_column(ForeignKey('clustering_profiles.id', ondelete='CASCADE'))
    lat: Mapped[float]
    lon: Mapped[float]
    cluster_index: Mapped[int]
