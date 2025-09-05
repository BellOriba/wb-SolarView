import uvicorn
from fastapi import FastAPI
from src.solar_api.adapters.api import routes
from src.solar_api.adapters.api import panel_routes

app = FastAPI(
    title="SolarView API",
    description="API to estimate solar panel energy production using PVGIS and manage panel models.",
    version="1.0.0",
)

app.include_router(routes.router)
app.include_router(panel_routes.router)


@app.get("/", include_in_schema=False)
def root():
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
