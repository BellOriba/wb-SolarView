import sys
from fastapi import APIRouter, Depends, HTTPException
from src.solar_api.domain.models import PVGISRequest
from src.solar_api.application.services.solar_service import SolarService
from src.solar_api.adapters.pvgis.pvgis_adapter import PVGISAdapter
from src.solar_api.adapters.api.dependencies import verify_credentials

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "python_version": sys.version, "message": "API is running!"}


@router.post("/calculate", tags=["Solar"], dependencies=[Depends(verify_credentials)])
async def calculate_solar_production(request: PVGISRequest):
    try:
        pvgis_adapter = PVGISAdapter()
        solar_service = SolarService(pvgis_service=pvgis_adapter)
        result = await solar_service.calculate_energy_production(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
