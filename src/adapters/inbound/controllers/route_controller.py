from fastapi import APIRouter, Depends

from src.adapters.inbound.dto.request.route_request import OptimizeRouteRequest
from src.adapters.inbound.dto.response.route_response import OptimizeRouteResponse
from src.adapters.inbound.mappers.route_mapper import RouteMapper
from src.application.use_cases.optimize_route import OptimizeRouteUseCase
from src.config.dependencies import get_optimize_route_use_case, get_route_mapper


router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(
    route_request: OptimizeRouteRequest,
    mapper: RouteMapper = Depends(get_route_mapper),
    use_case: OptimizeRouteUseCase = Depends(get_optimize_route_use_case),
) -> OptimizeRouteResponse:
    optimized_route = use_case.execute(
        start=mapper.to_start_entity(route_request.start),
        pickups=[
            mapper.to_pickup_entity(pickup)
            for pickup in [*route_request.pickups, *route_request.stops]
        ],
        destination=mapper.to_destination_entity(route_request.destination),
    )

    return mapper.to_response(optimized_route)
