# models/diet.py

from typing import List, Dict, Optional
from pydantic import BaseModel, validator


# ---------------------- Request Model ---------------------- #

class DietPlanRequest(BaseModel):
    name: str
    age: int
    goal: str
    height_cm: float
    current_weight_kg: float
    target_weight_kg: float
    health_conditions: Optional[List[str]] = []
    region: str
    cuisine_preference: str
    allergies: Optional[List[str]] = []

    @validator("region", pre=True)
    def normalize_region(cls, v):
        return v.strip().lower() if v else v


# ---------------------- Response Models ---------------------- #

class MealDetails(BaseModel):
    items: List[str]
    calories: int
    cooking_method: Optional[str] = None


class DailyMealsStructure(BaseModel):
    early_morning: Optional[MealDetails] = None
    breakfast: MealDetails
    mid_morning_snack: Optional[MealDetails] = None
    lunch: MealDetails
    evening_snack: MealDetails
    dinner: MealDetails
    bedtime_snack: Optional[MealDetails] = None


class NutritionInfo(BaseModel):
    protein_g: int
    carbs_g: int
    fats_g: int
    fiber_g: int
    sodium_mg: int
    sugar_g: int


class DayMealPlan(BaseModel):
    day_number: int
    day_name: str
    total_calories: int
    meals: DailyMealsStructure
    nutritional_breakdown: NutritionInfo
    hydration_reminder: str
    exercise_suggestion: str
    health_tips: List[str]


class DietPlanResponse(BaseModel):
    """Final response format"""
    success: bool
    message: str
    user_profile: Dict
    weekly_plan: List[DayMealPlan]
    summary: Dict
    health_guidelines: List[str]
    generation_time_seconds: float
    generated_at: str
