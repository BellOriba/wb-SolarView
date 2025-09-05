from abc import ABC, abstractmethod
from src.solar_api.domain.models import PVGISRequest


class PVGISServicePort(ABC):
    @abstractmethod
    async def get_pv_data(self, params: PVGISRequest) -> dict:
        raise NotImplementedError
