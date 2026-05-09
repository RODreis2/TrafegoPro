from fastapi.testclient import TestClient

from main import app
from src.application.dto.request.route_request import MAX_ROUTE_STOPS


client = TestClient(app)


def route_stop(label: str, latitude: float, longitude: float, stop_type: str = "pickup"):
    return {
        "label": label,
        "latitude": latitude,
        "longitude": longitude,
        "type": stop_type,
        "address": f"{label} address",
    }


def valid_payload():
    return {
        "start": route_stop("Start", -23.55052, -46.63331),
        "stops": [
            route_stop("Stop A", -23.56168, -46.65598),
            route_stop("Stop B", -23.54894, -46.63882, "dropoff"),
        ],
        "destination": route_stop("Destination", -23.58741, -46.65763),
    }


def test_optimize_route_returns_ordered_stops_and_distances():
    response = client.post("/routes/optimize", json=valid_payload())

    assert response.status_code == 200
    body = response.json()

    assert body["strategy"] == "brute_force"
    assert body["total_distance_km"] > 0
    assert [stop["sequence"] for stop in body["stops"]] == [0, 1, 2, 3]
    assert body["stops"][0]["leg_distance_km"] == 0
    assert body["stops"][-1]["cumulative_distance_km"] == body["total_distance_km"]


def test_optimize_route_rejects_invalid_coordinates():
    payload = valid_payload()
    payload["start"]["latitude"] = -120

    response = client.post("/routes/optimize", json=payload)

    assert response.status_code == 422


def test_optimize_route_rejects_invalid_stop_type():
    payload = valid_payload()
    payload["stops"][0]["type"] = "warehouse"

    response = client.post("/routes/optimize", json=payload)

    assert response.status_code == 422


def test_optimize_route_rejects_too_many_stops():
    payload = valid_payload()
    payload["stops"] = [
        route_stop(f"Stop {index}", -23.55 + index * 0.001, -46.63)
        for index in range(MAX_ROUTE_STOPS + 1)
    ]

    response = client.post("/routes/optimize", json=payload)

    assert response.status_code == 422
