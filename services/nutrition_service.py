import json
import re
import datetime
from typing import Tuple
from sqlalchemy.orm import Session
from services.ollama_service import OllamaService
from services.meal_service import MealService
from models.meal import Meal

class NutritionService:
    """
    Orchestrates the AI image analysis workflow.
    Handles JSON parsing, data validation, fallbacks, and database persistence.
    """

    @staticmethod
    def process_and_save_meal(db: Session, image_bytes: bytes, file_path: str, timestamp_str: str) -> Tuple[Meal, dict]:
        """
        Coordinates the Ollama inference, parses the result safely, and saves it to the database.
        
        Args:
            db: SQLAlchemy session.
            image_bytes: Raw bytes of the image for the Ollama call.
            file_path: Local path where the image is saved.
            timestamp_str: Timestamp string indicating when the upload occurred.
            
        Returns:
            Tuple[Meal, dict]: The saved Meal database model and a dictionary of debug logs.
            
        Raises:
            Exception: Propagates any fatal errors during inference or DB saving.
        """
        debug_logs = {
            "raw_response": "",
            "errors": [],
            "cleaned_json": {}
        }
        
        # 1. Get raw AI response
        raw_text = OllamaService.analyze_meal_image(image_bytes)
        debug_logs["raw_response"] = raw_text
        
        # 2. Clean and parse JSON
        cleaned_text = raw_text
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
            
        analysis = None
        try:
            analysis = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            debug_logs["errors"].append(f"Standard JSON parse failed: {str(e)}. Attempting regex extraction.")
            # Fallback regex extraction
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                try:
                    analysis = json.loads(match.group(0))
                    debug_logs["errors"].append("Regex JSON extraction succeeded.")
                except json.JSONDecodeError as e2:
                    debug_logs["errors"].append(f"Regex JSON parse failed: {str(e2)}. Attempting aggressive regex value extraction.")
            
        # Aggressive fallback extraction using regex if JSON parsing partially fails
        if not analysis:
            debug_logs["errors"].append("Attempting aggressive regex key-value extraction.")
            analysis = {}
            
            for key in ["total_calories", "total_protein", "total_carbs", "total_fat", "health_score", "confidence_score", "calories"]:
                val_match = re.search(f'"{key}"\s*:\s*"?(\d+\.?\d*)"?', raw_text, re.IGNORECASE)
                if val_match:
                    analysis[key] = float(val_match.group(1))
                    
            summary_match = re.search(r'"summary"\s*:\s*"(.*?)"', raw_text, re.IGNORECASE)
            if summary_match:
                analysis["summary"] = summary_match.group(1)
                
            rec_match = re.search(r'"recommendation"\s*:\s*"(.*?)"', raw_text, re.IGNORECASE)
            if rec_match:
                analysis["recommendation"] = rec_match.group(1)
                
            # Attempt to extract foods array or default it
            foods_match = re.search(r'"foods"\s*:\s*(\[.*?\])', raw_text, re.DOTALL)
            if foods_match:
                try:
                    analysis["foods"] = json.loads(foods_match.group(1))
                except json.JSONDecodeError:
                    analysis["foods"] = []
                    
            if not analysis.get("total_calories") and not analysis.get("calories"):
                analysis = None
                
        if not analysis:
            debug_logs["errors"].append("Total parsing failure. Using intelligent defaults.")
            # Intelligent fallback if the model completely hallucinated
            analysis = {
                "foods": [{"name": "Unrecognized Meal", "portion": "1 serving", "calories": 500, "protein": 20, "carbs": 50, "fat": 15, "confidence": 0}],
                "total_calories": 500.0,
                "total_protein": 20.0,
                "total_carbs": 50.0,
                "total_fat": 15.0,
                "health_score": 50,
                "confidence_score": 0,
                "summary": "The AI provided an invalid response format. Using estimated default values.",
                "recommendation": "Please try taking another picture with better lighting."
            }
            
        debug_logs["cleaned_json"] = analysis
            
        # 3. Validate and extract with safe type-casting
        foods = analysis.get("foods", [])
        food_items = [f.get("name", "Unknown Food") for f in foods if isinstance(f, dict)]
        if not food_items:
            # Fallback for old schema
            old_items = analysis.get("food_items", [])
            food_items = old_items if isinstance(old_items, list) else [analysis.get("food_name", "Unknown Meal")]
            
        if len(food_items) > 0:
            food_name = ", ".join([str(item) for item in food_items])
        else:
            food_name = "Unknown Meal"
            
        def extract_number(val, default_val):
            if val is None or val == "":
                return default_val
            if isinstance(val, (int, float)):
                return float(val) if float(val) != 0.0 else default_val
            match = re.search(r'(\d+\.?\d*)', str(val))
            if match:
                parsed = float(match.group(1))
                return parsed if parsed != 0.0 else default_val
            return default_val

        calories = extract_number(analysis.get("total_calories", analysis.get("calories")), 500.0)
        protein = extract_number(analysis.get("total_protein", analysis.get("protein")), 20.0)
        carbs = extract_number(analysis.get("total_carbs", analysis.get("carbs")), 50.0)
        fats = extract_number(analysis.get("total_fat", analysis.get("fat", analysis.get("fats"))), 15.0)
        health_score = int(extract_number(analysis.get("health_score"), 50.0))
        confidence_score = int(extract_number(analysis.get("confidence_score"), 50.0))
        
        # Enforce realistic bounds
        calories = min(max(calories, 0.0), 5000.0)
        protein = min(max(protein, 0.0), 300.0)
        carbs = min(max(carbs, 0.0), 500.0)
        fats = min(max(fats, 0.0), 300.0)
        health_score = min(max(health_score, 0), 100)
        confidence_score = min(max(confidence_score, 0), 100)
        
        debug_logs["parsed_numeric_values"] = {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fats,
            "health_score": health_score,
            "confidence_score": confidence_score
        }
            
        # We will save the entire structured analysis as JSON in nutrition_summary
        # so the UI can parse it out and render individual food cards.
        full_summary = json.dumps(analysis)
        
        upload_time = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        
        # 4. Save to Database
        db_meal = MealService.add_meal(
            db=db,
            image_path=file_path,
            food_name=food_name,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
            health_score=health_score,
            confidence_score=confidence_score,
            nutrition_summary=full_summary,
            upload_timestamp=upload_time
        )
        
        return db_meal, debug_logs
