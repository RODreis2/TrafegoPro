from src.adapters.outbound.services.nominatim_geocoding_service import (
    NominatimGeocodingService,
)
from src.adapters.inbound.mappers.route_mapper import RouteMapper
from src.application.services.route_optimizer import RouteOptimizer
from src.application.use_cases.geocode_address import GeocodeAddressUseCase
from src.application.use_cases.optimize_route import OptimizeRouteUseCase
from src.application.use_cases.search_geocode import SearchGeocodeUseCase


def get_geocode_address_use_case() -> GeocodeAddressUseCase:
    return GeocodeAddressUseCase(NominatimGeocodingService())


def get_search_geocode_use_case() -> SearchGeocodeUseCase:
    return SearchGeocodeUseCase(NominatimGeocodingService())


def get_optimize_route_use_case() -> OptimizeRouteUseCase:
    return OptimizeRouteUseCase(RouteOptimizer())


def get_route_mapper() -> RouteMapper:
    return RouteMapper()
