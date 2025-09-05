from abc import ABC, abstractmethod
from typing import List, Optional
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)


class PanelRepositoryPort(ABC):
    @abstractmethod
    async def get_all(self) -> List[PanelModel]:
        pass

    @abstractmethod
    async def get_by_id(self, model_id: str) -> Optional[PanelModel]:
        pass

    @abstractmethod
    async def create(self, panel: PanelModelCreate) -> PanelModel:
        pass

    @abstractmethod
    async def update(
        self, model_id: str, panel_update: PanelModelUpdate
    ) -> Optional[PanelModel]:
        pass

    @abstractmethod
    async def delete(self, model_id: str) -> bool:
        pass
