from typing import List, Optional

from pydantic import BaseModel

from app.common_types import BBox
from app.schemas.clustering_profile_schema import ClusteredStopSchema
from app.schemas.enums import BusDataProvider
from app.schemas.route import RouteSchema
from app.schemas.stop import StopSchema
from app.schemas.stops_clustering import StopsClusteringParams, ClusteredCorrespondenceEntry


# Схемы для описания тела запросов и ответов API

class GetBusDataRequest(BaseModel):
    source: BusDataProvider
    bbox: Optional[BBox] = None

class GetBusDataResponse(BaseModel):
    routes: List[RouteSchema]
    stops: List[StopSchema]

class GenerateSpeedProfileRequest(BaseModel):
    name: str
    routes_ids: List[str]
    speed_data_id: str

class TruncatedSpeedProfile(BaseModel):
    id: str
    name: str

class GetSpeedProfilesResponse(BaseModel):
    speed_profiles: List[TruncatedSpeedProfile]

class GenerateClusteringProfileRequest(BaseModel):
    name: str
    params: StopsClusteringParams

class ApplyClusteringResponse(BaseModel):
    clustered_stops: List[ClusteredStopSchema]
    clustered_correspondence: List[ClusteredCorrespondenceEntry]
