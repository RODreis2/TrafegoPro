# TrafegoPro

TrafegoPro is a route-planning MVP built with FastAPI and a simple map UI. It
lets the user enter a starting point, intermediate pickups/deliveries/stops, and
a final destination, then returns an optimized stop order with estimated
distances.

The project is intentionally small and organized around hexagonal architecture
to keep business rules, application use cases, HTTP controllers, and external
services separated.

## Features

- Address search using Nominatim/OpenStreetMap.
- Route optimization using local distance calculations.
- Interactive map with OpenStreetMap tiles and OSRM road geometry for display.
- Stop types for pickup, delivery, and generic stops.
- API validation for coordinates, stop types, labels, and route size.
- Basic security headers and friendly errors for external provider failures.

## Architecture

```text
src/
  domain/       -> entities, value objects, and business concepts
  application/  -> use cases, DTOs, mappers, ports, and services
  adapters/     -> HTTP controllers and external providers
static/         -> browser UI
```

Main request flow:

```text
HTTP controller
  -> use case
    -> application service
      -> domain entities/value objects
```

## Running Locally

Requirements:

- Python 3.12+
- uv

Start the API and UI:

```bash
uv run uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## API Example

Endpoint:

```text
POST /routes/optimize
```

Payload:

```json
{
  "start": {
    "label": "Início",
    "latitude": -23.55052,
    "longitude": -46.63331
  },
  "stops": [
    {
      "label": "Coleta A",
      "type": "pickup",
      "latitude": -23.56168,
      "longitude": -46.65598
    },
    {
      "label": "Entrega B",
      "type": "dropoff",
      "latitude": -23.54894,
      "longitude": -46.63882
    }
  ],
  "destination": {
    "label": "Destino",
    "latitude": -23.58741,
    "longitude": -46.65763
  }
}
```

Current optimization strategies:

```text
up to 8 intermediate stops -> brute force, tests every possible order
9 intermediate stops       -> nearest neighbor, picks the closest next stop
```

The backend optimizes using straight-line distance between coordinates. The
frontend asks the public OSRM demo server for road geometry only to draw a more
realistic line on the map.

## Geocoding

Endpoint:

```text
POST /geocode
```

Payload:

```json
{
  "address": "Av. Paulista, 1000, São Paulo, SP"
}
```

Response:

```json
{
  "address": "Av. Paulista, 1000, São Paulo, SP",
  "latitude": -23.564,
  "longitude": -46.652,
  "provider": "nominatim",
  "display_name": "..."
}
```

Nominatim public usage must stay light. For a production version, add caching,
rate limiting, and a dedicated geocoding provider configuration.

## Security Notes

- No API keys or secrets are required for the current local demo.
- User input is validated with Pydantic before route optimization.
- Route size is capped to avoid expensive brute-force requests.
- Map popups are rendered with DOM nodes instead of interpolated HTML.
- External geocoding failures return controlled `503` responses.
- This project is demo-ready, not production-hardened. A public deployment
  should add rate limiting, observability, stronger provider configuration, and
  deployment-specific CORS policy.

## Tests

Install/sync dependencies and run:

```bash
uv run pytest
```

Quick syntax check:

```bash
uv run python -m compileall main.py src
```
