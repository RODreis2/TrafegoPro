from src.application.ports.geocoding_port import (
    GeocodedAddress,
    GeocodingPort,
)


class GeocodeAddressUseCase:
    def __init__(self, geocoding_port: GeocodingPort) -> None:
        self.geocoding_port = geocoding_port

    def execute(self, address: str) -> GeocodedAddress | None:
        return self.geocoding_port.geocode(address)
