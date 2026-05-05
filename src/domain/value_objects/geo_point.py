from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt


EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float

    def distance_to(self, other: "GeoPoint") -> float:
        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)
        lat2 = radians(other.latitude)
        lon2 = radians(other.longitude)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        haversine = (
            sin(delta_lat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        )
        central_angle = 2 * atan2(sqrt(haversine), sqrt(1 - haversine))

        return EARTH_RADIUS_KM * central_angle
