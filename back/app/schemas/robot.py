from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class RobotCreate(BaseModel):
    ipaddr: str = Field(..., max_length=16)
    token: str = Field(..., max_length=16)


class RobotResponse(BaseModel):
    id: int
    ipaddr: str
    token: Optional[str]
    is_connected: Optional[bool]
    first_connect: Optional[date]
    manual_manage: bool
    battery__battery_num: Optional[int] = None

    class Config:
        from_attributes = True


class RobotDataResponse(BaseModel):
    battery: str

