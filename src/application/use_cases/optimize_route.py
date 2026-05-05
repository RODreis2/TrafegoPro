from src.application.services.route_optimizer import RouteOptimizer
from src.domain.entities.route import OptimizedRoute, RouteStop


class OptimizeRouteUseCase:
    def __init__(self, route_optimizer: RouteOptimizer) -> None:
        self.route_optimizer = route_optimizer

    def execute(
        self,
        start: RouteStop,
        pickups: list[RouteStop],
        destination: RouteStop,
    ) -> OptimizedRoute:
        return self.route_optimizer.optimize(start, pickups, destination)
