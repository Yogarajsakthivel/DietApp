# service/nutrition_service.py
from app.service.mistral_client import generate_chat_completion
import json, traceback
import re

async def compute_meal_nutrition(payload: dict):
    try:
        foods = "\n".join([f"- {f['item']} ({f['quantity']})" for f in payload.get("foods", [])])
        prompt = f"""
You are a certified dietitian AI. Estimate the total calories and macronutrients for this meal:

{foods}

Return ONLY a valid JSON object with this exact structure:
{{
  "breakdown": [
    {{"item": "food name", "quantity": "amount", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}}
  ],
  "total_calories": 0,
  "macros": {{"protein": 0, "carbs": 0, "fat": 0}}
}}
"""
        print("⚙️ Sending prompt to Mistral API...")
        messages = [{"role": "user", "content": prompt}]
        result = generate_chat_completion(messages)
        print("✅ Mistral response:", result[:500])

        # Remove Markdown backticks or code fences
        cleaned = re.sub(r"^```json|```$", "", result.strip(), flags=re.MULTILINE)

        return json.loads(cleaned)
    except Exception as e:
        print("❌ Error in compute_meal_nutrition:", e)
        traceback.print_exc()
        return {"error": str(e)}
