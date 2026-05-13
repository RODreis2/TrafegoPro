from src.application.ports.geocoding_port import GeocodedAddress, GeocodingPort


class SearchGeocodeUseCase:
    def __init__(self, geocoding_port: GeocodingPort) -> None:
        self.geocoding_port = geocoding_port

    def execute(self, query: str, limit: int = 5) -> list[GeocodedAddress]:
        return self.geocoding_port.search(query, limit=limit)
