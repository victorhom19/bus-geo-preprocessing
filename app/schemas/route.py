from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from app.schemas.enums import BusDataProvider
from app.schemas.route_geometry import RouteGeometryType
from app.schemas.route_segment import RouteSegmentSchema
from app.schemas.stop import StopSchema


class RouteSchema(BaseModel):
    id: str | UUID
    source: BusDataProvider
    name: str
    stops: List[StopSchema]
    final_stop_order: Optional[int] = None
    segments: List[RouteSegmentSchema]
    geometry: List[RouteGeometryType]
