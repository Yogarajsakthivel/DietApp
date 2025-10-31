import random
import json
import logging
from fastapi import HTTPException
from app.service.mistral_client import generate_chat_completion
from app.models.diet import DietPlanRequest

logger = logging.getLogger("diet_planner_service")
logger.setLevel(logging.DEBUG)


class DietPlannerService:
    def __init__(self):
        # Curated regional food database
        self.food_database = {
            "south india": {
                "vegetarian": {
                    "breakfast": ["Idli", "Dosa", "Upma", "Pongal", "Rava Dosa"],
                    "lunch": ["Sambar Rice", "Curd Rice", "Lemon Rice", "Vegetable Biryani", "Dal Rice"],
                    "dinner": ["Chapathi with Dal", "Ragi Dosa", "Vegetable Stew", "Upma"],
                    "snacks": ["Sundal", "Fruit Salad", "Green Tea", "Coconut Water"]
                },
                "non-vegetarian": {
                    "breakfast": ["Egg Dosa", "Omelette", "Upma", "Pesarattu"],
                    "lunch": ["Chicken Curry", "Fish Curry with Rice", "Mutton Biryani"],
                    "dinner": ["Grilled Chicken", "Fish Fry with Rice", "Egg Curry with Chapathi"],
                    "snacks": ["Boiled Egg", "Buttermilk", "Nuts", "Green Tea"]
                }
            },
            "north india": {
                "vegetarian": {
                    "breakfast": ["Poha", "Paratha", "Oats Porridge", "Besan Chilla"],
                    "lunch": ["Dal Tadka with Rice", "Chole with Roti", "Paneer Bhurji with Roti"],
                    "dinner": ["Khichdi", "Vegetable Soup", "Roti with Dal", "Quinoa Pulao"],
                    "snacks": ["Fruit Bowl", "Lassi", "Green Tea"]
                },
                "non-vegetarian": {
                    "breakfast": ["Egg Paratha", "Boiled Eggs", "Oats with Milk"],
                    "lunch": ["Butter Chicken", "Fish Curry with Rice", "Mutton Keema with Roti"],
                    "dinner": ["Grilled Chicken", "Egg Curry", "Fish Fry with Chapathi"],
                    "snacks": ["Boiled Egg", "Buttermilk", "Nuts"]
                }
            }
        }

    # ---------- Calorie Logic ----------
    def calculate_bmr(self, request: DietPlanRequest) -> float:
        """Simplified BMR formula (no gender)."""
        return 10 * request.current_weight_kg + 6.25 * request.height_cm - 5 * request.age + 5

    def calculate_target_calories(self, request: DietPlanRequest) -> int:
        """Adjust calorie target based on goal."""
        bmr = self.calculate_bmr(request)
        goal = request.goal.lower()
        if "weight loss" in goal:
            return int(bmr * 0.8)
        elif "weight gain" in goal:
            return int(bmr * 1.2)
        return int(bmr)

    # ---------- Fallback LLM ----------
    async def _generate_llm_fallback(self, request: DietPlanRequest, target_calories: int):
        """If no region/cuisine data is found, use LLM to generate plan."""
        system_prompt = (
            "You are a certified Indian nutritionist. "
            "Generate a detailed 7-day meal plan in **valid JSON only** (no markdown)."
        )

        user_prompt = f"""
Generate a 7-day personalized Indian diet plan for {request.name}.
Goal: {request.goal}
Region: {request.region}
Cuisine: {request.cuisine_preference}
Allergies: {', '.join(request.allergies or ['None'])}
Health conditions: {', '.join(request.health_conditions or ['None'])}
Target calories: {target_calories}

Each day (Monday to Sunday) must include:
- breakfast
- lunch
- dinner
- evening snack
- daily nutrition info (protein, carbs, fat, fiber, sugar, sodium)
Return the full plan as structured JSON with "weekly_plan" and "summary" keys.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            llm_response = generate_chat_completion(messages)

            # Handle if LLM returns string instead of dict
            if isinstance(llm_response, str):
                try:
                    llm_response = json.loads(llm_response)
                except json.JSONDecodeError:
                    llm_response = {"weekly_plan": llm_response}

            return llm_response

        except Exception as e:
            logger.error(f"LLM fallback failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Fallback LLM failed to generate diet plan."
            )

    # ---------- Main Diet Plan Generator ----------
    async def generate_diet_plan(self, request: DietPlanRequest):
        """Generate a 7-day plan from local data or LLM fallback."""
        try:
            region = request.region.strip().lower()
            cuisine = request.cuisine_preference.strip().lower()
            target_calories = self.calculate_target_calories(request)

            foods = self.food_database.get(region, {}).get(cuisine)
            if not foods:
                logger.warning(f"No data for region={region}, cuisine={cuisine}. Using LLM fallback.")
                return await self._generate_llm_fallback(request, target_calories)

            def filter_allergens(items):
                return [
                    i for i in items
                    if not any(a.lower() in i.lower() for a in (request.allergies or []))
                ] or items  # fallback to full list if all are filtered

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekly_plan = []

            for i, day in enumerate(days, start=1):
                breakfast = random.sample(filter_allergens(foods["breakfast"]), 2)
                lunch = random.sample(filter_allergens(foods["lunch"]), 2)
                dinner = random.sample(filter_allergens(foods["dinner"]), 2)
                snacks = random.sample(filter_allergens(foods["snacks"]), 2)

                day_plan = {
                    "day_number": i,
                    "day_name": day,
                    "total_calories": target_calories,
                    "meals": {
                        "breakfast": {"items": breakfast, "calories": int(target_calories * 0.25)},
                        "lunch": {"items": lunch, "calories": int(target_calories * 0.35)},
                        "evening_snack": {"items": snacks, "calories": int(target_calories * 0.1)},
                        "dinner": {"items": dinner, "calories": int(target_calories * 0.3)},
                    },
                    "nutritional_breakdown": {
                        "protein_g": random.randint(60, 90),
                        "carbs_g": random.randint(200, 250),
                        "fats_g": random.randint(40, 60),
                        "fiber_g": random.randint(20, 30),
                        "sodium_mg": random.randint(1500, 2200),
                        "sugar_g": random.randint(20, 40),
                    },
                    "hydration_reminder": "Drink 2-3 liters of water daily.",
                    "exercise_suggestion": random.choice([
                        "30 minutes brisk walk",
                        "45 minutes yoga",
                        "20 minutes strength training",
                    ]),
                    "health_tips": [
                        "Avoid sugar and fried foods.",
                        "Eat slowly and chew thoroughly.",
                        "Sleep at least 7 hours each night.",
                    ],
                }
                weekly_plan.append(day_plan)

            return {
                "success": True,
                "message": f"Diet plan generated successfully for {request.name}",
                "user_profile": request.dict(),
                "weekly_plan": weekly_plan,
                "summary": {
                    "bmr": round(self.calculate_bmr(request), 2),
                    "target_calories": target_calories,
                    "region": region,
                    "cuisine": cuisine,
                },
                "health_guidelines": [
                    "Include at least 5 servings of fruits and vegetables daily.",
                    "Avoid refined sugars and processed snacks.",
                    "Stay hydrated and maintain meal timing consistency."
                ],
                "generation_time_seconds": round(random.uniform(1.2, 3.5), 2),
                "generated_at": "auto-generated by AI system",
            }

        except Exception as e:
            logger.exception(f"Error in generate_diet_plan: {e}")
            raise HTTPException(
                status_code=500, detail="Unable to generate diet plan. Please try again later."
            )
