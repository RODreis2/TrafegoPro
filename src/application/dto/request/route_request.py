from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


MAX_ROUTE_STOPS = 9
StopRequestType = Literal["pickup", "dropoff", "stop"]


class RouteStopRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str = Field(min_length=1, max_length=80)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = Field(default=None, max_length=300)
    type: StopRequestType | None = None


class OptimizeRouteRequest(BaseModel):
    start: RouteStopRequest
    destination: RouteStopRequest
    pickups: list[RouteStopRequest] = Field(default_factory=list)
    stops: list[RouteStopRequest] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_route_size(self) -> "OptimizeRouteRequest":
        if len(self.pickups) + len(self.stops) > MAX_ROUTE_STOPS:
            raise ValueError(f"A route can have at most {MAX_ROUTE_STOPS} stops.")

        return self
