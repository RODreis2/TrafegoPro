from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    address: str = Field(min_length=3)
