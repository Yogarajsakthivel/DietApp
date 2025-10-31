from fastapi import APIRouter, HTTPException
from app.models.schemas import NutritionRequest
from app.service.nutrition_service import compute_meal_nutrition

router = APIRouter()

@router.post("/analyze")
async def analyze(req: NutritionRequest):
    try:
        out = await compute_meal_nutrition(req.dict())
        return {"success": True, "meal_nutrition": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
