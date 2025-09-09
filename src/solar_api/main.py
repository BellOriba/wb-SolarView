import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from src.solar_api.adapters.api import routes, panel_routes, user_routes, auth_routes
from src.solar_api.database import init_db, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    logger.info("Shutting down application...")
    await engine.dispose()


api_key_header = APIKeyHeader(
    name="X-API-Key", auto_error=False, scheme_name="APIKeyHeader"
)

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
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Authentication", "description": "Authentication related endpoints"},
        {"name": "Users", "description": "User management (admin only)"},
        {"name": "Panel Models", "description": "Solar panel models management"},
        {"name": "Solar", "description": "Calculate solar production"},
        {"name": "Health", "description": "Health check"},
    ],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = FastAPI.openapi(app)

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header"
        }
    }
    
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    
    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi

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


if __name__ == "__main__":
    uvicorn.run(
        "src.solar_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
    )
