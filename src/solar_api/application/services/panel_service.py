from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from src.solar_api.application.ports.panel_repository import PanelRepositoryPort
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)


class PanelService:
    def __init__(self, panel_repository: PanelRepositoryPort):
        self.panel_repository = panel_repository

    async def get_all_models(self, user_id: int) -> List[PanelModel]:
        try:
            return await self.panel_repository.get_all(user_id=user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve panel models: {str(e)}",
            )

    async def get_model_by_id(self, model_id: UUID, user_id: int) -> PanelModel:
        panel = await self.panel_repository.get_by_id(
            model_id=model_id, user_id=user_id
        )
        if not panel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Panel model with ID {model_id} not found",
            )
        return panel

    async def create_model(self, panel: PanelModelCreate, user_id: int) -> PanelModel:
        try:
            return await self.panel_repository.create(panel=panel, user_id=user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create panel model: {str(e)}",
            )

    async def update_model(
        self, model_id: UUID, panel_update: PanelModelUpdate, user_id: int
    ) -> PanelModel:
        await self.get_model_by_id(model_id=model_id, user_id=user_id)

        try:
            updated_panel = await self.panel_repository.update(
                model_id=model_id, panel_update=panel_update, user_id=user_id
            )
            if not updated_panel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Panel model with ID {model_id} not found",
                )
            return updated_panel
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update panel model: {str(e)}",
            )

    async def delete_model(self, model_id: UUID, user_id: int) -> bool:
        await self.get_model_by_id(model_id=model_id, user_id=user_id)

        try:
            success = await self.panel_repository.delete(
                model_id=model_id, user_id=user_id
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Panel model with ID {model_id} not found",
                )
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete panel model: {str(e)}",
            )
