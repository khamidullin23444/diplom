from pydantic import BaseModel
from typing import List, Dict


class SensorDataPoint(BaseModel):
    x: int
    y: int


SensorData = List[Dict[str, int]]

