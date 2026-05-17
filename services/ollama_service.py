import ollama
import streamlit as st

class OllamaService:
    """
    Service responsible for raw communication with the local Ollama instance.
    Includes built-in caching for performance.
    """

    @staticmethod
    @st.cache_data(show_spinner=False)
    def analyze_meal_image(image_bytes: bytes) -> str:
        """
        Sends the image to the local llama3.2-vision model.
        Uses st.cache_data to prevent redundant analysis of the exact same image bytes.
        
        Args:
            image_bytes: The raw bytes of the uploaded image.
            
        Returns:
            str: The raw JSON string response from the model.
            
        Raises:
            Exception: If Ollama is unreachable or the model errors.
        """
        system_prompt = '''You are an expert AI Nutritionist. Analyze the meal in the image.
You must accurately identify ALL visible food items separately (e.g., burger, fries, salad, drink).

Return ONLY valid JSON. Do not include explanations, markdown, or extra text.
You must use this exact JSON structure:
{
  "foods": [
    {
      "name": "Cheeseburger",
      "portion": "1 burger",
      "calories": 600,
      "protein": 30,
      "carbs": 40,
      "fat": 35,
      "confidence": 95
    }
  ],
  "total_calories": 600,
  "total_protein": 30,
  "total_carbs": 40,
  "total_fat": 35,
  "health_score": 45,
  "confidence_score": 90,
  "summary": "High calorie processed fast food meal. High in saturated fats and sodium.",
  "recommendations": [
    {"category": "Health Warning", "severity": "High", "message": "Ultra-processed food detected. High in sodium and saturated fat."},
    {"category": "Improvement Suggestion", "severity": "Medium", "message": "Consider baking instead of frying to reduce calories."},
    {"category": "Healthy Alternative", "severity": "Low", "message": "Try swapping the soda for sparkling water with lemon."}
  ]
}

IMPORTANT RULES:
- Identify EVERY distinct food item and add it to the "foods" array.
- "portion" should describe the amount (e.g., "1 cup", "150g", "2 slices").
- "calories", "protein", "carbs", "fat" (per food AND total) must be estimated integer values.
- Macro Consistency Rule: The sum of (fat * 9) + (carbs * 4) + (protein * 4) MUST roughly equal "calories".
- The "total_*" fields MUST be the sum of the respective fields from all items in the "foods" array.
- "health_score" must be an integer from 0 to 100 representing how healthy the overall meal is.
- "confidence_score" and "confidence" (per food) must be an integer from 0 to 100.
- Provide realistic numeric values. DO NOT return 0 for calories or macros unless genuinely zero-calorie.
- "summary" should be concise and strictly focused on nutritional impact.
- Generate 1-4 concise personalized recommendations in the "recommendations" array.
- Valid "category" values: "Health Warning", "Improvement Suggestion", "Fitness Tip", "Healthy Alternative".
- Valid "severity" values: "High", "Medium", "Low".
- Provide warnings for excessive sugar, ultra-processed foods, high saturated fat, low protein, or excessive calories.'''
        
        try:
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[{
                    'role': 'user',
                    'content': system_prompt,
                    'images': [image_bytes]
                }],
                format='json'
            )
            return response['message']['content']
        except Exception as e:
            # Re-raise to be handled by the orchestrator (NutritionService)
            raise Exception(f"Ollama inference failed: {str(e)}")

    @staticmethod
    def compare_meals(meal_a_data: dict, meal_b_data: dict) -> str:
        """
        Sends the analyzed JSON data of two meals to the local llama3.2 model
        to generate a comparative verdict.
        """
        import json
        system_prompt = '''You are an expert AI Nutritionist. Compare the two provided meals.
Return ONLY valid JSON. Do not include explanations or markdown.
You must use this exact JSON structure:
{
  "healthier_meal": "Meal A", 
  "better_for_weight_loss": "Meal A",
  "better_for_muscle_gain": "Meal B",
  "more_processed": "Meal B",
  "verdict": "Meal A is significantly healthier due to lower saturated fats, while Meal B is better for muscle gain but highly processed.",
  "recommendation": "Choose Meal A for daily consumption. Meal B should be eaten sparingly."
}

Ensure "healthier_meal", "better_for_weight_loss", "better_for_muscle_gain", and "more_processed" strictly return either "Meal A" or "Meal B" or "Tie".
'''
        
        user_content = f"Meal A Data:\n{json.dumps(meal_a_data)}\n\nMeal B Data:\n{json.dumps(meal_b_data)}"
        
        try:
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_content}
                ],
                format='json'
            )
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Ollama comparison failed: {str(e)}")
