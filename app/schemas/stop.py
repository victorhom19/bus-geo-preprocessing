from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Extra

from app.schemas.enums import BusDataProvider


class StopSchema(BaseModel, extra=Extra.allow):
    id: str
    source: BusDataProvider
    external_source_id: Optional[str] = None
    name: str
    lon: float
    lat: float
