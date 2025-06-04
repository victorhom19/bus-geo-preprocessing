from typing import Dict, List

from pydantic import BaseModel


SegmentSpeeds = List[float]
HourIntervalsToSpeeds = Dict[int, SegmentSpeeds]
WeekdayToHourIntervals = Dict[str, HourIntervalsToSpeeds]
RouteIdToWeekday = Dict[str, WeekdayToHourIntervals]

class SpeedDataSchema(BaseModel):
    id: str
    name: str

class SpeedProfileSchema(BaseModel):
    id: str
    name: str
    speed_data_id: str
    routes: RouteIdToWeekday
