import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.application.services.geocoding_service import (
    GeocodedAddress,
    GeocodingService,
)


class NominatimGeocodingService(GeocodingService):
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "TrafegoPro/0.1 (development)"

    def geocode(self, address: str) -> GeocodedAddress | None:
        results = self.search(address, limit=1)

        if not results:
            return None

        return results[0]

    def search(self, query: str, limit: int = 5) -> list[GeocodedAddress]:
        limit = max(1, min(limit, 10))
        results = self._request(query=query, limit=limit)

        return [
            GeocodedAddress(
                address=query,
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
                provider="nominatim",
                display_name=result["display_name"],
            )
            for result in results
        ]

    def _request(self, query: str, limit: int) -> list[dict]:
        query = urlencode(
            {
                "q": query,
                "format": "json",
                "limit": limit,
                "addressdetails": 1,
            }
        )
        request = Request(
            url=f"{self.BASE_URL}?{query}",
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json",
            },
        )

        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
