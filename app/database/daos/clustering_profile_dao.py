import json
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.daos.base_dao import BaseDAO
from app.database.daos.route_dao import RouteDAO
from app.database.models import SpeedProfile, SegmentSpeed, ClusteringProfile, ClusteringAnchor, \
    ClusteringCorrespondence
from app.schemas.clustering_profile_schema import ClusteringProfileSchema, TruncatedClusteringProfileSchema
from app.schemas.speed_profile_schema import RouteIdToWeekday
from app.schemas.stops_clustering import ClusteredCorrespondenceNode, CorrespondenceEntry, ClusteredCorrespondenceEntry, \
    StopsClusteringParams


class ClusteringProfileDAO(BaseDAO):
    """ DAO-класс для работы с объектами профилей кластеризации """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ClusteringProfile)

    async def create(self, clustering_profile: TruncatedClusteringProfileSchema,
                     nodes: List[ClusteredCorrespondenceNode],
                     correspondence: List[ClusteredCorrespondenceEntry]) -> ClusteringProfile:
        """ Создание записи о профиле кластеризации """

        # Подготовка JSON-значения для параметров алгоритма кластеризации
        params = clustering_profile.clustering_params.dict()
        params['algorithm'] = params['algorithm'].value

        # Создание записи о профиле кластеризации
        _clustering_profile = ClusteringProfile(
            name=clustering_profile.name,
            clustering_data_id=UUID(clustering_profile.clustering_params.clustering_data_id),
            clustering_params=f"{params}",
            clusters_count=clustering_profile.clusters_count,
            clustering_score=clustering_profile.clustering_score
        )
        self.session.add(_clustering_profile)
        await self.session.flush()
        await self.session.refresh(_clustering_profile)

        # Создание записей об опорных точках кластеризации
        for node in nodes:
            if not node.is_anchor:
                continue
            _anchor = ClusteringAnchor(
                clustering_profile_id=_clustering_profile.id,
                lat=node.lat,
                lon=node.lon,
                cluster_index=node.cluster_index
            )
            self.session.add(_anchor)

        # Создание записей обновлённой матрицы корреспонденций
        for corr_entry in correspondence:
            _clustering_correspondence = ClusteringCorrespondence(
                clustering_profile_id=_clustering_profile.id,
                cluster_from_index=corr_entry.cluster_from_index,
                cluster_to_index=corr_entry.cluster_to_index,
                weekday=corr_entry.weekday,
                hour_interval=corr_entry.hour_interval,
                transitions=corr_entry.transitions
            )
            self.session.add(_clustering_correspondence)

        await self.session.commit()
        await self.session.refresh(_clustering_profile)

        return _clustering_profile
