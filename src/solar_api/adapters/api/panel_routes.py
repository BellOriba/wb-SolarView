from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.solar_api.database import get_db
from src.solar_api.adapters.repositories.postgres_panel_repository import (
    PostgresPanelRepository,
)
from src.solar_api.application.services.panel_service import PanelService
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)
from src.solar_api.adapters.api.dependencies import (
    get_current_active_user,
    get_admin_user,
)
from src.solar_api.domain.user_models import UserInDB

router = APIRouter(prefix="/api/panel-models", tags=["Panel Models"])


def get_panel_service(db: AsyncSession = Depends(get_db)) -> PanelService:
    panel_repository = PostgresPanelRepository(db)
    return PanelService(panel_repository)


@router.get(
    "/",
    response_model=List[PanelModel],
    summary="List all panel models for the current user",
)
async def list_panel_models(
    current_user: UserInDB = Depends(get_current_active_user),
    panel_service: PanelService = Depends(get_panel_service),
    manufacturer: Optional[str] = None,
    min_power: Optional[float] = None,
    max_price: Optional[float] = None,
    min_efficiency: Optional[float] = None,
):
    panels = await panel_service.get_all_models(user_id=current_user.id)

    if manufacturer is not None:
        panels = [p for p in panels if p.manufacturer == manufacturer]
    if min_power is not None:
        panels = [p for p in panels if p.capacity >= min_power]
    if min_efficiency is not None:
        panels = [p for p in panels if p.efficiency >= min_efficiency]

    return panels


@router.get(
    "/{model_id}", response_model=PanelModel, summary="Get a specific panel model by ID"
)
async def get_panel_model(
    model_id: UUID,
    current_user: UserInDB = Depends(get_current_active_user),
    panel_service: PanelService = Depends(get_panel_service),
):
    return await panel_service.get_model_by_id(
        model_id=model_id, user_id=current_user.id
    )


@router.post(
    "/",
    response_model=PanelModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new panel model",
)
async def create_panel_model(
    panel: PanelModelCreate,
    admin_user: UserInDB = Depends(get_admin_user),
    panel_service: PanelService = Depends(get_panel_service),
):
    return await panel_service.create_model(panel=panel, user_id=admin_user.id)


@router.put(
    "/{model_id}", response_model=PanelModel, summary="Update an existing panel model"
)
async def update_panel_model(
    model_id: UUID,
    panel_update: PanelModelUpdate,
    admin_user: UserInDB = Depends(get_admin_user),
    panel_service: PanelService = Depends(get_panel_service),
):
    return await panel_service.update_model(
        model_id=model_id, panel_update=panel_update, user_id=admin_user.id
    )


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a panel model",
)
async def delete_panel_model(
    model_id: UUID,
    admin_user: UserInDB = Depends(get_admin_user),
    panel_service: PanelService = Depends(get_panel_service),
):
    await panel_service.delete_model(model_id=model_id, user_id=admin_user.id)
    return None
