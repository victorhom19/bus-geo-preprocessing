from uuid import UUID

from pydantic import BaseModel

from app.schemas.enums import BusDataProvider


class StopSchema(BaseModel):
    id: str
    source: BusDataProvider
    name: str
    lon: float
    lat: float
