from sqlalchemy.orm import Session
from models.user import User
from models.meal import Meal
import datetime
import pandas as pd

class ProfileService:
    @staticmethod
    def get_user_profile(db: Session, user_id: int = 1):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def save_user_profile(db: Session, age: int, gender: str, weight_kg: float, 
                          height_cm: float, activity_level: str, fitness_goal: str, user_id: int = 1):
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            user.age = age
            user.gender = gender
            user.weight_kg = weight_kg
            user.height_cm = height_cm
            user.activity_level = activity_level
            user.fitness_goal = fitness_goal
        else:
            user = User(
                id=user_id,
                age=age,
                gender=gender,
                weight_kg=weight_kg,
                height_cm=height_cm,
                activity_level=activity_level,
                fitness_goal=fitness_goal
            )
            db.add(user)
            
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def calculate_metrics(user: User):
        if not user:
            return None
            
        # BMI = weight(kg) / height(m)^2
        height_m = user.height_cm / 100.0
        bmi = user.weight_kg / (height_m ** 2) if height_m > 0 else 0
        
        # BMI Category
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 25:
            bmi_category = "Normal"
        elif 25 <= bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

        # BMR (Mifflin-St Jeor)
        # Men: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) + 5
        # Women: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) - 161
        if user.gender == "Male":
            bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5
        else:
            bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161
            
        # Activity Multiplier
        activity_multipliers = {
            "Sedentary": 1.2,
            "Light": 1.375,
            "Moderate": 1.55,
            "Active": 1.725,
            "Very Active": 1.9
        }
        multiplier = activity_multipliers.get(user.activity_level, 1.2)
        tdee = bmr * multiplier
        
        # Target Calories based on Goal
        if user.fitness_goal == "Weight Loss":
            target_calories = tdee - 500
        elif user.fitness_goal == "Muscle Gain":
            target_calories = tdee + 500
        else:
            target_calories = tdee
            
        target_calories = max(1200, target_calories) # Safety floor
        
        # Macros
        # Standard: 30% Protein, 40% Carbs, 30% Fat
        # 1g Protein = 4 kcal, 1g Carb = 4 kcal, 1g Fat = 9 kcal
        
        if user.fitness_goal == "Weight Loss":
            p_ratio, c_ratio, f_ratio = 0.40, 0.30, 0.30
        elif user.fitness_goal == "Muscle Gain":
            p_ratio, c_ratio, f_ratio = 0.30, 0.45, 0.25
        else:
            p_ratio, c_ratio, f_ratio = 0.30, 0.40, 0.30
            
        target_protein = (target_calories * p_ratio) / 4.0
        target_carbs = (target_calories * c_ratio) / 4.0
        target_fats = (target_calories * f_ratio) / 9.0
        
        return {
            "bmi": round(bmi, 1),
            "bmi_category": bmi_category,
            "bmr": round(bmr),
            "tdee": round(tdee),
            "target_calories": round(target_calories),
            "target_protein": round(target_protein),
            "target_carbs": round(target_carbs),
            "target_fats": round(target_fats)
        }

    @staticmethod
    def generate_health_insights(user: User, metrics: dict, recent_meals_df: pd.DataFrame = None):
        if not user or not metrics:
            return []
            
        insights = []
        
        # BMI specific
        if metrics["bmi_category"] == "Underweight":
            insights.append("⚠️ **Underweight Warning**: Your BMI is below 18.5. Ensure you are meeting your daily caloric needs.")
        elif metrics["bmi_category"] in ["Overweight", "Obese"] and user.fitness_goal != "Weight Loss":
            insights.append("💡 **Health Tip**: Your BMI is elevated. Consider switching your goal to Weight Loss for better long-term health outcomes.")
            
        # Goal specific
        if user.fitness_goal == "Weight Loss":
            insights.append("📉 **Weight Loss**: Stick to your deficit of 500 kcal/day to safely lose ~0.5kg per week.")
        elif user.fitness_goal == "Muscle Gain":
            insights.append("💪 **Muscle Gain**: Ensure you hit your protein target daily, and maintain a progressive overload training routine.")
            
        # Meal History specific
        if recent_meals_df is not None and not recent_meals_df.empty:
            avg_cal = recent_meals_df["calories"].mean()
            if avg_cal > metrics["target_calories"] and user.fitness_goal == "Weight Loss":
                insights.append(f"⚠️ **Calorie Warning**: Your recent meals average {int(avg_cal)} kcal, exceeding your weight loss target of {metrics['target_calories']} kcal.")
            elif avg_cal < metrics["target_calories"] * 0.8 and user.fitness_goal == "Muscle Gain":
                insights.append(f"⚠️ **Calorie Deficit**: You are consistently eating below your target. It's difficult to gain muscle without sufficient calories.")
                
        return insights
