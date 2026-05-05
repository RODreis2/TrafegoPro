from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RouteStopRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = None
    type: str | None = None


class OptimizeRouteRequest(BaseModel):
    start: RouteStopRequest
    destination: RouteStopRequest
    pickups: list[RouteStopRequest] = Field(default_factory=list)
    stops: list[RouteStopRequest] = Field(default_factory=list)
