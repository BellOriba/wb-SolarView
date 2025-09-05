from typing import List, Optional
from src.solar_api.application.ports.panel_repository import PanelRepositoryPort
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)


class PanelService:
    def __init__(self, panel_repository: PanelRepositoryPort):
        self.panel_repository = panel_repository

    async def get_all_models(self) -> List[PanelModel]:
        return await self.panel_repository.get_all()

    async def get_model_by_id(self, model_id: str) -> Optional[PanelModel]:
        return await self.panel_repository.get_by_id(model_id)

    async def create_model(self, panel: PanelModelCreate) -> PanelModel:
        return await self.panel_repository.create(panel)

    async def update_model(
        self, model_id: str, panel_update: PanelModelUpdate
    ) -> Optional[PanelModel]:
        if not await self.panel_repository.get_by_id(model_id):
            return None
        return await self.panel_repository.update(model_id, panel_update)

    async def delete_model(self, model_id: str) -> bool:
        return await self.panel_repository.delete(model_id)
