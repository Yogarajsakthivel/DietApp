# service.py

from fastapi import FastAPI
from app.route import dietrouter, nutrition_routes

app = FastAPI(title="Diet Planner API", version="3.0.0")

# Include routers

app.include_router(nutrition_routes.router, prefix="/nutrition", tags=["nutrition"])
app.include_router(dietrouter.router, prefix="/diet-mistral", tags=["diet-mistral"])

@app.get("/")
async def root():
    return {
        "service": "diet-planner",
        "status": "ok",
        "available_routes": ["/diet", "/nutrition", "/diet-mistral"]
    }
