# TrafegoPro

The first microservice in the project, organized to study hexagonal
architecture.

```text
src/
  domain/
    entities/
      user.py

  application/
    ports/
      user_repository.py
    use_cases/
      create_user.py
      get_user.py

  adapters/
    inbound/
      controllers/
    outbound/
      repositories/
        postgres_user_repository.py
```

## Responsibilities

```text
domain      -> business rules and entities
application -> use cases and contracts required by the application
adapters    -> technical input and output: HTTP, database, queues, external APIs
```

## Expected Flow

```text
controller inbound
  -> use case
    -> port
      -> repository outbound
```

## Local Route Optimization

The first routing MVP does not depend on paid map APIs. It receives coordinates,
orders the pickup stops, and returns the estimated route using straight-line
distance.

```bash
uv run uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

The simple route planning UI is available at:

```text
http://127.0.0.1:8000
```

Endpoint:

```text
POST /routes/optimize
```

Example payload:

```json
{
  "start": {
    "label": "Inicio",
    "latitude": -23.55052,
    "longitude": -46.63331
  },
  "pickups": [
    {
      "label": "Coleta A",
      "latitude": -23.56168,
      "longitude": -46.65598
    },
    {
      "label": "Coleta B",
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

Current strategies:

```text
up to 8 pickups -> brute force, tests every possible order
9+ pickups      -> nearest neighbor, picks the closest next stop
```

This is good enough to validate the product flow. Later, the distance source can
be replaced with OSRM, Mapbox, Google, or GraphHopper to account for roads and
traffic.

## Geocoding

The API also exposes a geocoding endpoint backed by Nominatim/OpenStreetMap.
Use it to convert a typed address into coordinates before optimizing a route.

Endpoint:

```text
POST /geocode
```

Example payload:

```json
{
  "address": "Av. Paulista, 1000, Sao Paulo, SP"
}
```

Example response:

```json
{
  "address": "Av. Paulista, 1000, Sao Paulo, SP",
  "latitude": -23.564,
  "longitude": -46.652,
  "provider": "nominatim",
  "display_name": "..."
}
```

Nominatim public usage must be light: identify the app with a User-Agent,
respect the usage policy, and cache/save results before using this in production.
