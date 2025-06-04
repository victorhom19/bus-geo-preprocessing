from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


from pydantic import BaseModel


class ClusteringStopsEntry(BaseModel):
    global_id: int
    stop_id: int
    stop_name: str
    station_name: str
    lon: float
    lat: float


class ClusteringStopsCorrespondenceEntry(BaseModel):
    timestamp: str
    route_id: int
    route_name: str
    stop_id_on: int
    stop_id_off: int
    count: float


class ClusteredStopEntry(ClusteringStopsEntry):
    cluster_id: int

class AnchorPoint(BaseModel):
    lat: float
    lon: float
    label: int

class CorrespondenceNode(BaseModel):
    id: str
    lon: float
    lat: float

class ClusteredCorrespondenceNode(CorrespondenceNode):
    is_anchor: bool
    cluster_index: int

class CorrespondenceEntry(BaseModel):
    timestamp: str
    node_from_id: str
    node_to_id: str
    transitions: float

class ClusteredCorrespondenceEntry(BaseModel):
    cluster_from_index: int
    cluster_to_index: int
    weekday: int
    hour_interval: int
    transitions: float


class StopsClusteringAlgorithm(Enum):

    def __repr__(self):
        return self.name

    HDBSCAN_KNN = 'hdbscan_knn'

class StopsClusteringParams(BaseModel):
    algorithm: StopsClusteringAlgorithm
    clustering_data_id: str
    algorithm_params: Optional[Any] = None
    min_score: Optional[float] = None
    max_clusters_count: Optional[int] = None


