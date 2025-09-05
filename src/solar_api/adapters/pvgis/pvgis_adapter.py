import httpx
from typing import Dict, Any
from src.solar_api.application.ports.pvgis_service import PVGISServicePort
from src.solar_api.domain.models import PVGISRequest


class PVGISAdapter(PVGISServicePort):
    PVGIS_URL = "https://re.jrc.ec.europa.eu/api/pvcalc"

    async def get_pv_data(self, params: PVGISRequest) -> Dict[str, Any]:
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
            response.raise_for_status()
            return self._format_response(response.json())

    def _format_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "latitude": raw_response["inputs"]["location"]["latitude"],
            "longitude": raw_response["inputs"]["location"]["longitude"],
            "elevation": raw_response["inputs"]["location"]["elevation"],
            "meteo_data": {
                "year_min": raw_response["inputs"]["meteo_data"]["year_min"],
                "year_max": raw_response["inputs"]["meteo_data"]["year_max"],
            },
            "mounting_system": raw_response["inputs"]["mounting_system"],
            "pv_module": {
                "technology": raw_response["inputs"]["pv_module"]["technology"],
                "peak_power": raw_response["inputs"]["pv_module"]["peak_power"],
                "system_loss": raw_response["inputs"]["pv_module"]["system_loss"],
            },
            "economic_data": raw_response["inputs"]["economic_data"],
            "outputs": {
                "monthly": raw_response["outputs"]["monthly"],
                "totals": raw_response["outputs"]["totals"],
            },
        }
