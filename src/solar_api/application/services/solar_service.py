from src.solar_api.application.ports.pvgis_service import PVGISServicePort
from src.solar_api.domain.models import PVGISRequest


class SolarService:
    def __init__(self, pvgis_service: PVGISServicePort):
        self.pvgis_service = pvgis_service

    async def calculate_energy_production(self, params: PVGISRequest) -> dict:
        return await self.pvgis_service.get_pv_data(params)
