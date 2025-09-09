import sys
from fastapi import APIRouter, HTTPException, Depends
from src.solar_api.domain.models import PVGISRequest
from src.solar_api.application.services.solar_service import SolarService
from src.solar_api.adapters.pvgis.pvgis_adapter import PVGISAdapter
from src.solar_api.application.services.auth_service import get_current_user
from src.solar_api.domain.user_models import UserInDB

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "python_version": sys.version, "message": "API is running!"}


@router.post("/calculate", tags=["Solar"])
async def calculate_solar_production(
    request: PVGISRequest,
    current_user: UserInDB = Depends(get_current_user),
):
    try:
        pvgis_adapter = PVGISAdapter()
        solar_service = SolarService(pvgis_service=pvgis_adapter)
        result = await solar_service.calculate_energy_production(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
