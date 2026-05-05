from fastapi import APIRouter

from src.application.dto.request.route_request import OptimizeRouteRequest
from src.application.dto.response.route_response import OptimizeRouteResponse
from src.application.mapper.route_mapper import RouteMapper
from src.application.services.route_optimizer import RouteOptimizer
from src.application.use_cases.optimize_route import OptimizeRouteUseCase


router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(route_request: OptimizeRouteRequest) -> OptimizeRouteResponse:
    mapper = RouteMapper()
    use_case = OptimizeRouteUseCase(RouteOptimizer())

    optimized_route = use_case.execute(
        start=mapper.to_start_entity(route_request.start),
        pickups=[
            mapper.to_pickup_entity(pickup)
            for pickup in [*route_request.pickups, *route_request.stops]
        ],
        destination=mapper.to_destination_entity(route_request.destination),
    )

    return mapper.to_response(optimized_route)
