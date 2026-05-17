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
  "recommendation": "Consider replacing fries with a side salad and soda with sparkling water."
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
- "recommendation" MUST suggest a specific, healthier alternative or modification.'''
        
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
