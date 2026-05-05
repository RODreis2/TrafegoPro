from src.application.services.geocoding_service import (
    GeocodedAddress,
    GeocodingService,
)


class GeocodeAddressUseCase:
    def __init__(self, geocoding_service: GeocodingService) -> None:
        self.geocoding_service = geocoding_service

    def execute(self, address: str) -> GeocodedAddress | None:
        return self.geocoding_service.geocode(address)
