import time
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.diet import DietPlanRequest, DietPlanResponse
from app.service.dietservice import DietPlannerService

router = APIRouter()
planner_service = DietPlannerService()

# ---------- Logging ----------
logger = logging.getLogger("diet_planner")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


@router.post("/generate", response_model=DietPlanResponse)
async def generate_diet_plan(request: DietPlanRequest):
    """
    Generate a 7-day personalized Indian diet plan (Monday–Sunday)
    using local data or fallback to Mistral LLM.
    """
    logger.info(f"API called for user: {request.name}, goal={request.goal}, region={request.region}")

    start_time = time.time()

    try:
        # ---- Step 1: Generate plan using async service ----
        plan = await planner_service.generate_diet_plan(request)

        if not plan or not plan.get("weekly_plan"):
            raise HTTPException(status_code=500, detail="Unable to generate diet plan. Please try again later.")

        # ---- Step 2: Calculate target calories ----
        target_calories = plan.get("target_calories")

        # ---- Step 3: Build summary ----
        summary = {
            "target_daily_calories": target_calories,
            "goal": request.goal,
            "bmr": plan.get("bmr"),
            "tips": [
                "Follow the diet plan consistently.",
                "Stay hydrated throughout the day.",
                "Exercise regularly to complement your goal."
            ],
        }

        duration = round(time.time() - start_time, 2)

        # ---- Step 4: Return final response ----
        return DietPlanResponse(
            success=True,
            message=plan.get("message"),
            user_profile=request.dict(),
            weekly_plan=plan.get("weekly_plan"),
            summary=summary,
            health_guidelines=[
                "Avoid sugary drinks.",
                "Include enough protein in every meal.",
                "Get at least 7 hours of sleep daily."
            ],
            generation_time_seconds=duration,
            generated_at=datetime.now().isoformat()
        )

    except HTTPException as http_err:
        logger.error(f"Error generating diet plan: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.exception(f"Unexpected error in /generate route: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error while generating the diet plan.")
