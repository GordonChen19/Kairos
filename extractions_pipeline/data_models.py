from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class Modes(str, Enum):
    bus = "bus"
    mrt = "subway"

class Transport(BaseModel):
    source: str = Field(
        description='Where the transportation starts from'
    )

    destination: str = Field(
        description='Where the transportation ends at'
    )

    transportationMode: Modes = Field(
        description='The Mode of Transportation'
    )

class Transports(BaseModel):
    Transports: List[Transport] = Field(description='The list of transportation events in a journey',default=[])
    
