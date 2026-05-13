from uuid import UUID

from pydantic import BaseModel


class RouteStopResponse(BaseModel):
    id: UUID
    sequence: int
    label: str
    type: str
    latitude: float
    longitude: float
    address: str | None
    leg_distance_km: float
    cumulative_distance_km: float


class OptimizeRouteResponse(BaseModel):
    strategy: str
    total_distance_km: float
    stops: list[RouteStopResponse]
