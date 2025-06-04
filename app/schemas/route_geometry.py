from pydantic import BaseModel

from app.schemas.enums import RouteGeometryNodeType, RouteObstacleType


class RouteGeometryNodeSchema(BaseModel):
    type: RouteGeometryNodeType
    lat: float
    lon: float

class RouteObstacleSchema(RouteGeometryNodeSchema):
    obstacle_type: RouteObstacleType

class RouteStopPositionSchema(RouteGeometryNodeSchema):
    corresponding_stop_id: str


RouteGeometryType = RouteGeometryNodeSchema | RouteStopPositionSchema | RouteObstacleSchema
