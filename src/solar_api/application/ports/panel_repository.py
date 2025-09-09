from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)


class PanelRepositoryPort(ABC):
    @abstractmethod
    async def get_all(self, user_id: int) -> List[PanelModel]:
        pass

    @abstractmethod
    async def get_by_id(self, model_id: UUID, user_id: int) -> Optional[PanelModel]:
        pass

    @abstractmethod
    async def create(self, panel: PanelModelCreate, user_id: int) -> PanelModel:
        pass

    @abstractmethod
    async def update(
        self, model_id: UUID, panel_update: PanelModelUpdate, user_id: int
    ) -> Optional[PanelModel]:
        pass

    @abstractmethod
    async def delete(self, model_id: UUID, user_id: int) -> bool:
        pass
