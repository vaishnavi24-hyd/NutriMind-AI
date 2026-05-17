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
You must accurately identify complex meals such as burgers, pizza, diverse Indian meals (e.g., curries, naan, biryani, dosa), rice dishes, salads, and beverages.

Return ONLY valid JSON. Do not include explanations, markdown, or extra text.
You must use this exact JSON structure:
{
"food_items": ["burger", "fries", "coke"],
"calories": 850,
"protein": 32,
"carbs": 65,
"fat": 48,
"health_score": 45,
"confidence_score": 90,
"summary": "High calorie processed fast food meal. High in saturated fats and sodium.",
"recommendation": "Consider replacing fries with a side salad and soda with sparkling water."
}

IMPORTANT RULES:
- "calories", "protein", "carbs", "fat" must be estimated integer values.
- Macro Consistency Rule: The sum of (fat * 9) + (carbs * 4) + (protein * 4) MUST roughly equal the "calories". Do NOT provide mathematically impossible macros.
- "health_score" must be an integer from 0 to 100 representing how healthy the meal is.
- "confidence_score" must be an integer from 0 to 100 representing your confidence in identifying the food and estimating its macros.
- Provide realistic numeric values. DO NOT return 0 for calories or macros unless the item is genuinely zero-calorie (like water).
- "summary" should be concise and strictly focused on nutritional impact.
- "recommendation" MUST suggest a specific, healthier alternative or modification for the exact meal shown.'''
        
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
