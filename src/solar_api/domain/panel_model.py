from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PanelModelBase(BaseModel):
    name: str = Field(..., description="Name of the solar panel model")
    capacity: float = Field(..., gt=0, description="Panel capacity in kWp")
    efficiency: float = Field(
        ..., gt=0, le=100, description="Panel efficiency in percentage"
    )
    manufacturer: str = Field(..., description="Manufacturer name")
    type: str = Field(..., description="Type of the panel (e.g., Monocristalino)")


class PanelModelCreate(PanelModelBase):
    pass


class PanelModelUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the solar panel model")
    capacity: Optional[float] = Field(None, gt=0, description="Panel capacity in kWp")
    efficiency: Optional[float] = Field(
        None, gt=0, le=100, description="Panel efficiency in percentage"
    )
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    type: Optional[str] = Field(
        None, description="Type of the panel (e.g., Monocristalino)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Panel Name",
                "capacity": 0.5,
                "efficiency": 21.5,
                "manufacturer": "Updated Manufacturer",
                "type": "Updated Type",
            }
        }
    )


class PanelModelInDB(PanelModelBase):
    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the panel model"
    )
    user_id: int = Field(..., description="ID of the user who owns this panel model")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": 1,
                "name": "Canadian Solar 400W",
                "capacity": 0.4,
                "efficiency": 20.5,
                "manufacturer": "Canadian Solar",
                "type": "Monocristalino",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        },
    )


class PanelModel(PanelModelBase):
    id: UUID = Field(..., description="Unique identifier for the panel model")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Canadian Solar 400W",
                "capacity": 0.4,
                "efficiency": 20.5,
                "manufacturer": "Canadian Solar",
                "type": "Monocristalino",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        },
    )
