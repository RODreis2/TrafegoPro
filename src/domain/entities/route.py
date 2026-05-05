from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.domain.value_objects.geo_point import GeoPoint


class StopType(StrEnum):
    START = "start"
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    STOP = "stop"
    DESTINATION = "destination"


@dataclass(frozen=True)
class RouteStop:
    id: UUID
    label: str
    point: GeoPoint
    stop_type: StopType
    address: str | None = None


@dataclass(frozen=True)
class RouteLeg:
    origin: RouteStop
    destination: RouteStop
    distance_km: float


@dataclass(frozen=True)
class OptimizedRoute:
    stops: list[RouteStop]
    legs: list[RouteLeg]
    total_distance_km: float
    strategy: str
