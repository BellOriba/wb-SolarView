from pydantic import BaseModel, Field


class PVGISRequest(BaseModel):
    lat: float = Field(..., description="Latitude in decimal degrees")
    lon: float = Field(..., description="Longitude in decimal degrees")
    peakpower: float = Field(
        ..., gt=0, description="Peak power of the PV system in kWp"
    )
    loss: float = Field(..., ge=0, le=100, description="System loss in percentage")
