import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from src.solar_api.adapters.api import routes, panel_routes, user_routes, auth_routes
from src.solar_api.database import init_db, get_db
from src.solar_api.application.services.auth_service import AuthService

app = FastAPI(
    title="SolarView API",
    description="""
    API to estimate solar panel energy production using PVGIS and manage panel models.
    
    ## Authentication
    
    This API uses API Key for authentication. To get started:
    1. Login at `/auth/login` with your email and password
    2. Use the returned API key in the `X-API-Key` header for all requests
    
    ## Security
    - All API endpoints require authentication by default
    - Admin endpoints are protected and require admin privileges
    - API keys should be kept secure and not shared
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(panel_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Bem-vindo à API do WB SolarView. Acesse /docs para ver a documentação da API."
    }

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("Database initialized")

if __name__ == "__main__":
    uvicorn.run(
        "src.solar_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
    )
