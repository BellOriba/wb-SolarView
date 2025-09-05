from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)
from src.solar_api.application.services.panel_service import PanelService
from src.solar_api.adapters.repositories.json_panel_repository import (
    JSONPanelRepository,
)
from src.solar_api.adapters.api.dependencies import verify_credentials
import os

router = APIRouter(prefix="/api/panel-models", tags=["Panel Models"])

PANEL_MODELS_FILE = os.getenv("PANEL_MODELS_FILE", "storage/models.json")
panel_repository = JSONPanelRepository(PANEL_MODELS_FILE)
panel_service = PanelService(panel_repository)


@router.get(
    "/", response_model=List[PanelModel], dependencies=[Depends(verify_credentials)]
)
async def list_panel_models():
    return await panel_service.get_all_models()


@router.get(
    "/{model_id}", response_model=PanelModel, dependencies=[Depends(verify_credentials)]
)
async def get_panel_model(model_id: str):
    model = await panel_service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel model with ID {model_id} not found",
        )
    return model


@router.post(
    "/",
    response_model=PanelModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_credentials)],
)
async def create_panel_model(panel: PanelModelCreate):
    try:
        return await panel_service.create_model(panel)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{model_id}", response_model=PanelModel, dependencies=[Depends(verify_credentials)]
)
async def update_panel_model(model_id: str, panel_update: PanelModelUpdate):
    updated_panel = await panel_service.update_model(model_id, panel_update)
    if not updated_panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel model with ID {model_id} not found",
        )
    return updated_panel


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_credentials)],
)
async def delete_panel_model(model_id: str):
    success = await panel_service.delete_model(model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel model with ID {model_id} not found",
        )
    return None
