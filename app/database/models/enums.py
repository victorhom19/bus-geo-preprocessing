from typing import Literal, get_args

from sqlalchemy import Enum

ObstacleType = Literal["crossing", "traffic_signals", "speedbump", "roundabout"]
ObstacleTypeEnum = Enum(
    *get_args(ObstacleType),
    name="obstacle_type",
    create_constraint=True,
    validate_strings=True
)

BusDataSource = Literal["local", "osm"]
BusDataSourceEnum = Enum(
    *get_args(BusDataSource),
    name="bus_data_source",
    create_constraint=True,
    validate_strings=True
)
