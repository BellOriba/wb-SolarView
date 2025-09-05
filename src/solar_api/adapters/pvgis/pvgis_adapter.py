import httpx
from src.solar_api.application.ports.pvgis_service import PVGISServicePort
from src.solar_api.domain.models import PVGISRequest


class PVGISAdapter(PVGISServicePort):
    PVGIS_URL = "https://re.jrc.ec.europa.eu/api/pvcalc"

    async def get_pv_data(self, params: PVGISRequest) -> dict:
        api_params = {
            "lat": params.lat,
            "lon": params.lon,
            "peakpower": params.peakpower,
            "loss": params.loss,
            "outputformat": "json",
            "optimalinclination": 1,
            "optimalazimuth": 1,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.PVGIS_URL, params=api_params)
            response.raise_for_status()  # Lança exceção para respostas de erro (4xx ou 5xx)
            return response.json()
