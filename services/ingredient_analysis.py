import ollama
import json
import re

class IngredientAnalysisService:
    """
    Analyzes extracted text from food labels using local Ollama model.
    """

    @staticmethod
    def analyze_label_text(ocr_text: str) -> dict:
        system_prompt = '''You are an expert toxicologist and nutritionist. Analyze the following OCR-extracted text from a food label.
Return ONLY valid JSON. Do not include explanations, markdown, or extra text.
You must use this exact JSON structure:
{
  "ingredient_explanation": "A short summary of the main ingredients found.",
  "harmful_ingredients": ["High Fructose Corn Syrup", "Red 40", "Sodium Benzoate"],
  "is_ultra_processed": true,
  "health_score": 35,
  "healthier_alternatives": "Consider whole grain alternatives with no added sugars.",
  "summary": "This product contains multiple artificial additives and high sugar."
}

IMPORTANT RULES:
- Identify any high sugar content, trans fats, preservatives, or artificial additives and place them in the "harmful_ingredients" list.
- "is_ultra_processed" should be boolean true/false.
- "health_score" must be an integer from 0 to 100.
- Return ONLY valid JSON format.'''

        try:
            response = ollama.chat(
                model='llama3.2',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': f"Food label OCR text:\n\n{ocr_text}"}
                ],
                format='json'
            )
            raw_response = response['message']['content']
            
            # Simple cleanup fallback
            cleaned = raw_response
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
                
            try:
                analysis = json.loads(cleaned)
            except json.JSONDecodeError:
                # Regex fallback
                match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if match:
                    analysis = json.loads(match.group(0))
                else:
                    raise Exception("Failed to parse JSON")
                    
            return analysis
        except Exception as e:
            # Provide safe fallback on error
            return {
                "ingredient_explanation": "Error analyzing OCR text.",
                "harmful_ingredients": [],
                "is_ultra_processed": False,
                "health_score": 50,
                "healthier_alternatives": "Unable to provide alternatives due to an analysis error.",
                "summary": f"Failed to analyze: {str(e)}"
            }
