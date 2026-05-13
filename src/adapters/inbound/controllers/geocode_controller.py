from fastapi import APIRouter, HTTPException, Query, status

from src.adapters.outbound.services.nominatim_geocoding_service import (
    GeocodingProviderError,
    NominatimGeocodingService,
)
from src.adapters.inbound.dto.request.geocode_request import GeocodeRequest
from src.adapters.inbound.dto.response.geocode_response import GeocodeResponse
from src.application.use_cases.geocode_address import GeocodeAddressUseCase


router = APIRouter(prefix="/geocode", tags=["geocoding"])


@router.post("", response_model=GeocodeResponse)
def geocode(geocode_request: GeocodeRequest) -> GeocodeResponse:
    use_case = GeocodeAddressUseCase(NominatimGeocodingService())
    try:
        result = use_case.execute(geocode_request.address)
    except GeocodingProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Geocoding provider is temporarily unavailable",
        ) from error

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return GeocodeResponse(
        address=result.address,
        latitude=result.latitude,
        longitude=result.longitude,
        provider=result.provider,
        display_name=result.display_name,
    )


@router.get("/search", response_model=list[GeocodeResponse])
def search_geocode(
    q: str = Query(min_length=3),
    limit: int = Query(default=5, ge=1, le=10),
) -> list[GeocodeResponse]:
    try:
        results = NominatimGeocodingService().search(q, limit=limit)
    except GeocodingProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Geocoding provider is temporarily unavailable",
        ) from error

    return [
        GeocodeResponse(
            address=result.address,
            latitude=result.latitude,
            longitude=result.longitude,
            provider=result.provider,
            display_name=result.display_name,
        )
        for result in results
    ]
