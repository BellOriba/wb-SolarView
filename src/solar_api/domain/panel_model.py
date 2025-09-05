from pydantic import BaseModel, Field, model_validator
from typing import Optional
from typing_extensions import Annotated


class PanelModelBase(BaseModel):
    name: Annotated[
        Optional[str], Field(None, description="Name of the solar panel model")
    ]
    capacity: Annotated[
        Optional[float], Field(None, gt=0, description="Panel capacity in kWp")
    ]
    efficiency: Annotated[
        Optional[float],
        Field(None, gt=0, le=100, description="Panel efficiency in percentage"),
    ]
    manufacturer: Annotated[Optional[str], Field(None, description="Manufacturer name")]
    type: Annotated[
        Optional[str],
        Field(None, description="Type of the panel (e.g., Monocristalino)"),
    ]

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_field(cls, data):
        if not any(
            field in data
            for field in ["name", "capacity", "efficiency", "manufacturer", "type"]
        ):
            raise ValueError("At least one field must be provided for update")
        return data


class PanelModelCreate(PanelModelBase):
    name: str = Field(..., description="Name of the solar panel model")
    capacity: float = Field(..., gt=0, description="Panel capacity in kWp")
    efficiency: float = Field(
        ..., gt=0, le=100, description="Panel efficiency in percentage"
    )
    manufacturer: str = Field(..., description="Manufacturer name")
    type: str = Field(..., description="Type of the panel (e.g., Monocristalino)")


class PanelModelUpdate(PanelModelBase):
    name: Annotated[
        Optional[str], Field(None, description="Name of the solar panel model")
    ] = None
    capacity: Annotated[
        Optional[float], Field(None, gt=0, description="Panel capacity in kWp")
    ] = None
    efficiency: Annotated[
        Optional[float],
        Field(None, gt=0, le=100, description="Panel efficiency in percentage"),
    ] = None
    manufacturer: Annotated[
        Optional[str], Field(None, description="Manufacturer name")
    ] = None
    type: Annotated[
        Optional[str],
        Field(None, description="Type of the panel (e.g., Monocristalino)"),
    ] = None


class PanelModel(PanelModelBase):
    id: str = Field(..., description="Unique identifier for the panel model")
    name: str = Field(..., description="Name of the solar panel model")
    capacity: float = Field(..., gt=0, description="Panel capacity in kWp")
    efficiency: float = Field(
        ..., gt=0, le=100, description="Panel efficiency in percentage"
    )
    manufacturer: str = Field(..., description="Manufacturer name")
    type: str = Field(..., description="Type of the panel (e.g., Monocristalino)")

    class Config:
        from_attributes = True
