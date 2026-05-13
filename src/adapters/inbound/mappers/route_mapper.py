from src.adapters.inbound.dto.request.route_request import RouteStopRequest
from src.adapters.inbound.dto.response.route_response import (
    OptimizeRouteResponse,
    RouteStopResponse,
)
from src.domain.entities.route import OptimizedRoute, RouteStop, StopType
from src.domain.value_objects.geo_point import GeoPoint


class RouteMapper:
    def to_start_entity(self, stop_request: RouteStopRequest) -> RouteStop:
        return self._to_entity(stop_request, StopType.START)

    def to_pickup_entity(self, stop_request: RouteStopRequest) -> RouteStop:
        return self._to_entity(stop_request, self._stop_type_from_request(stop_request))

    def to_destination_entity(self, stop_request: RouteStopRequest) -> RouteStop:
        return self._to_entity(stop_request, StopType.DESTINATION)

    def to_response(self, optimized_route: OptimizedRoute) -> OptimizeRouteResponse:
        leg_distances = [0.0, *(leg.distance_km for leg in optimized_route.legs)]
        cumulative_distance = 0.0
        stops: list[RouteStopResponse] = []

        for index, stop in enumerate(optimized_route.stops):
            leg_distance = leg_distances[index]
            cumulative_distance += leg_distance
            stops.append(
                RouteStopResponse(
                    id=stop.id,
                    sequence=index,
                    label=stop.label,
                    type=stop.stop_type.value,
                    latitude=stop.point.latitude,
                    longitude=stop.point.longitude,
                    address=stop.address,
                    leg_distance_km=round(leg_distance, 2),
                    cumulative_distance_km=round(cumulative_distance, 2),
                )
            )

        return OptimizeRouteResponse(
            strategy=optimized_route.strategy,
            total_distance_km=round(optimized_route.total_distance_km, 2),
            stops=stops,
        )

    def _to_entity(
        self,
        stop_request: RouteStopRequest,
        stop_type: StopType,
    ) -> RouteStop:
        return RouteStop(
            id=stop_request.id,
            label=stop_request.label,
            point=GeoPoint(
                latitude=stop_request.latitude,
                longitude=stop_request.longitude,
            ),
            stop_type=stop_type,
            address=stop_request.address,
        )

    def _stop_type_from_request(self, stop_request: RouteStopRequest) -> StopType:
        if stop_request.type is None:
            return StopType.PICKUP

        try:
            return StopType(stop_request.type)
        except ValueError:
            return StopType.STOP
