from typing import Any

from pydantic import BaseModel

from app.schemas.stop import StopSchema
from app.schemas.stops_clustering import StopsClusteringParams


class ClusteringDataSchema(BaseModel):
    id: str
    name: str

class TruncatedClusteringProfileSchema(BaseModel):
    name: str
    clustering_params: StopsClusteringParams
    clusters_count: int
    clustering_score: float

class ClusteringProfileSchema(BaseModel):
    id: str
    name: str
    clustering_params: StopsClusteringParams
    clusters_count: int
    clustering_score: float


class ClusteredStopSchema(StopSchema):
    cluster_index: int
