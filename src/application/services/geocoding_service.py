from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GeocodedAddress:
    address: str
    latitude: float
    longitude: float
    provider: str
    display_name: str


class GeocodingService(ABC):
    @abstractmethod
    def geocode(self, address: str) -> GeocodedAddress | None:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[GeocodedAddress]:
        pass
