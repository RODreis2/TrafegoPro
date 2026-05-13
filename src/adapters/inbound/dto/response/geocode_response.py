from pydantic import BaseModel


class GeocodeResponse(BaseModel):
    address: str
    latitude: float
    longitude: float
    provider: str
    display_name: str
