from itertools import permutations

from src.domain.entities.route import OptimizedRoute, RouteLeg, RouteStop


MAX_BRUTE_FORCE_STOPS = 8


class RouteOptimizer:
    def optimize(
        self,
        start: RouteStop,
        pickups: list[RouteStop],
        destination: RouteStop,
    ) -> OptimizedRoute:
        ordered_pickups, strategy = self._order_pickups(start, pickups, destination)
        ordered_stops = [start, *ordered_pickups, destination]
        legs = self._build_legs(ordered_stops)

        return OptimizedRoute(
            stops=ordered_stops,
            legs=legs,
            total_distance_km=sum(leg.distance_km for leg in legs),
            strategy=strategy,
        )

    def _order_pickups(
        self,
        start: RouteStop,
        pickups: list[RouteStop],
        destination: RouteStop,
    ) -> tuple[list[RouteStop], str]:
        if len(pickups) <= MAX_BRUTE_FORCE_STOPS:
            return self._order_by_brute_force(start, pickups, destination), "brute_force"

        return self._order_by_nearest_neighbor(start, pickups), "nearest_neighbor"

    def _order_by_brute_force(
        self,
        start: RouteStop,
        pickups: list[RouteStop],
        destination: RouteStop,
    ) -> list[RouteStop]:
        best_order: tuple[RouteStop, ...] = tuple(pickups)
        best_distance = float("inf")

        for candidate in permutations(pickups):
            distance = self._route_distance([start, *candidate, destination])
            if distance < best_distance:
                best_distance = distance
                best_order = candidate

        return list(best_order)

    def _order_by_nearest_neighbor(
        self,
        start: RouteStop,
        pickups: list[RouteStop],
    ) -> list[RouteStop]:
        remaining = pickups.copy()
        ordered: list[RouteStop] = []
        current = start

        while remaining:
            next_stop = min(
                remaining,
                key=lambda stop: current.point.distance_to(stop.point),
            )
            ordered.append(next_stop)
            remaining.remove(next_stop)
            current = next_stop

        return ordered

    def _build_legs(self, stops: list[RouteStop]) -> list[RouteLeg]:
        return [
            RouteLeg(
                origin=stops[index],
                destination=stops[index + 1],
                distance_km=stops[index].point.distance_to(stops[index + 1].point),
            )
            for index in range(len(stops) - 1)
        ]

    def _route_distance(self, stops: list[RouteStop]) -> float:
        return sum(
            stops[index].point.distance_to(stops[index + 1].point)
            for index in range(len(stops) - 1)
        )
