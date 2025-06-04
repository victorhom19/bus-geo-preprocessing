from enum import Enum


class BusDataProvider(Enum):
    LOCAL = 'local'
    OSM = 'osm'

class RouteGeometryNodeType(Enum):
    GEOMETRY = 'geometry'
    OBSTACLE = 'obstacle'
    STOP_POSITION = 'stop_position'

class RouteObstacleType(Enum):
    CROSSING = 'crossing'
    TRAFFIC_SIGNALS = 'traffic_signals'
    SPEEDBUMP = 'speedbump'
    ROUNDABOUT = 'roundabout'

class Weekday(Enum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'
