from fastapi import FastAPI
from src.solar_api.adapters.api import routes

app = FastAPI(
    title="SolarView API",
    description="API to estimate solar panel energy production using PVGIS.",
    version="1.0.0",
)

app.include_router(routes.router)


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to SolarView API. See /docs for documentation."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
