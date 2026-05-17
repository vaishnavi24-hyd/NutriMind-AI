import pandas as pd
from sqlalchemy.orm import Session
from models.meal import Meal
import datetime

class AnalyticsService:
    @staticmethod
    def get_analytics_dataframe(db: Session, start_date: datetime.date = None, end_date: datetime.date = None):
        """Fetches meals from the database and returns a pandas DataFrame."""
        query = db.query(Meal)
        
        if start_date:
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            query = query.filter(Meal.upload_timestamp >= start_datetime)
            
        if end_date:
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
            query = query.filter(Meal.upload_timestamp <= end_datetime)
            
        meals = query.all()
        
        if not meals:
            return pd.DataFrame()
            
        data = []
        for meal in meals:
            data.append({
                "id": meal.id,
                "food_name": meal.food_name,
                "calories": meal.calories,
                "protein": meal.protein,
                "carbs": meal.carbs,
                "fats": meal.fats,
                "health_score": meal.health_score,
                "upload_timestamp": meal.upload_timestamp,
                "date": meal.upload_timestamp.date(),
                "week": meal.upload_timestamp.isocalendar()[1]
            })
            
        df = pd.DataFrame(data)
        return df

    @staticmethod
    def generate_ai_insights(df: pd.DataFrame):
        """Generates simple heuristic-based insights from the analytics dataframe."""
        if df.empty:
            return [{"type": "info", "message": "No data available to generate insights.", "icon": "ℹ️"}]
            
        insights = []
        
        avg_calories = df["calories"].mean()
        avg_protein = df["protein"].mean()
        avg_carbs = df["carbs"].mean()
        avg_fats = df["fats"].mean()
        avg_health = df["health_score"].mean()
        total_meals = len(df)
        
        # 1. Calorie insights
        if avg_calories > 1000: # Per meal
            insights.append({
                "type": "warning", 
                "icon": "📈", 
                "message": "**Calorie Surplus Detected:** Your average meal calorie intake is exceptionally high. Consider portion control if weight loss is your goal."
            })
        elif avg_calories < 300:
            insights.append({
                "type": "warning", 
                "icon": "⚠️", 
                "message": "**Low Calorie Warning:** Your logged meals average very low calories. Make sure you are meeting your basal metabolic needs."
            })
        else:
            insights.append({
                "type": "success", 
                "icon": "✅", 
                "message": "**Balanced Calories:** Your calorie intake per meal looks balanced and consistent with general healthy guidelines."
            })
            
        # 2. Macro Imbalance Detection
        total_macros = avg_protein + avg_carbs + avg_fats
        if total_macros > 0:
            protein_pct = (avg_protein / total_macros) * 100
            carbs_pct = (avg_carbs / total_macros) * 100
            fats_pct = (avg_fats / total_macros) * 100
            
            if protein_pct < 15:
                insights.append({
                    "type": "warning", 
                    "icon": "🍗", 
                    "message": "**Macro Imbalance:** Your protein intake is low relative to other macros. Adding lean meats, tofu, or legumes can help preserve muscle mass."
                })
            elif protein_pct > 35:
                insights.append({
                    "type": "success", 
                    "icon": "💪", 
                    "message": "**High Protein Profile:** You are consuming an excellent proportion of protein per meal, great for muscle recovery!"
                })
                
            if carbs_pct > 60:
                insights.append({
                    "type": "info", 
                    "icon": "🍞", 
                    "message": "**Carb-Heavy Diet:** A significant portion of your macros comes from carbs. Ensure they are complex carbs like whole grains."
                })
            
            if fats_pct > 40:
                insights.append({
                    "type": "warning", 
                    "icon": "🥑", 
                    "message": "**High Fat Consumption:** Your fat intake is high. Focus on healthy fats (avocados, nuts) and limit saturated/trans fats."
                })
            
        # 3. Health Score insights
        if avg_health >= 80:
            insights.append({
                "type": "success", 
                "icon": "🌟", 
                "message": "**Excellent Diet Quality:** Your meals have very high health scores! You have established great healthy habits."
            })
        elif avg_health < 60:
            insights.append({
                "type": "warning", 
                "icon": "🥗", 
                "message": "**Room for Improvement:** Try incorporating more whole foods, greens, and complex carbs to boost your overall health score."
            })
            
        # 4. Meal Frequency
        if total_meals >= 10:
             insights.append({
                "type": "info", 
                "icon": "📊", 
                "message": f"**Data Richness:** You've logged {total_meals} meals in this period. Great job keeping your food journal consistent!"
            })
            
        return insights
