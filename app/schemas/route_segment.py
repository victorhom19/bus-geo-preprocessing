from pydantic import BaseModel


class RouteSegmentSchema(BaseModel):
    stop_from_id: str
    stop_to_id: str
    segment_order: int
    distance: float
    crossings: int
    traffic_signals: int
    speedbumps: int
    roundabouts: int
