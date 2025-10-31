from pydantic import BaseModel
from typing import List, Optional

class UserParams(BaseModel):
    name: str
    age: int
    goal: str  # "Weight Loss" / "Muscle Gain" / "Maintenance"
    height_cm: float
    current_weight_kg: float
    target_weight_kg: Optional[float] = None
    health_conditions: Optional[List[str]] = []
    region: Optional[str] = None
    cuisine_preference: Optional[str] = "Vegetarian"
    allergies: Optional[List[str]] = []

class FoodItem(BaseModel):
    item: str
    quantity: str

class NutritionRequest(BaseModel):
    foods: List[FoodItem]
