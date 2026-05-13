from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.inbound.dto.request.geocode_request import GeocodeRequest
from src.adapters.inbound.dto.response.geocode_response import GeocodeResponse
from src.application.ports.geocoding_port import GeocodingPortError
from src.application.use_cases.geocode_address import GeocodeAddressUseCase
from src.application.use_cases.search_geocode import SearchGeocodeUseCase
from src.config.dependencies import (
    get_geocode_address_use_case,
    get_search_geocode_use_case,
)


router = APIRouter(prefix="/geocode", tags=["geocoding"])


@router.post("", response_model=GeocodeResponse)
def geocode(
    geocode_request: GeocodeRequest,
    use_case: GeocodeAddressUseCase = Depends(get_geocode_address_use_case),
) -> GeocodeResponse:
    try:
        result = use_case.execute(geocode_request.address)
    except GeocodingPortError as error:
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
    use_case: SearchGeocodeUseCase = Depends(get_search_geocode_use_case),
) -> list[GeocodeResponse]:
    try:
        results = use_case.execute(q, limit=limit)
    except GeocodingPortError as error:
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
