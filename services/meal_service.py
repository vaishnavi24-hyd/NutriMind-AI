from sqlalchemy.orm import Session
from models.meal import Meal
import datetime

class MealService:
    @staticmethod
    def add_meal(db: Session, image_path: str, food_name: str, calories: float, 
                 protein: float, carbs: float, fats: float, 
                 health_score: int, confidence_score: int, nutrition_summary: str,
                 upload_timestamp: datetime.datetime = None):
        if upload_timestamp is None:
            upload_timestamp = datetime.datetime.utcnow()
            
        db_meal = Meal(
            image_path=image_path,
            food_name=food_name,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
            health_score=health_score,
            confidence_score=confidence_score,
            nutrition_summary=nutrition_summary,
            upload_timestamp=upload_timestamp
        )
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        return db_meal

    @staticmethod
    def get_all_meals(db: Session, search_query: str = None, 
                      start_date: datetime.date = None, 
                      end_date: datetime.date = None,
                      min_calories: float = None,
                      max_calories: float = None,
                      sort_by: str = "newest"):
        query = db.query(Meal)
        
        if search_query:
            query = query.filter(Meal.food_name.ilike(f"%{search_query}%"))
            
        if start_date:
            # start_date is a datetime.date object. We can compare directly if upload_timestamp is datetime,
            # but usually it's better to convert date to datetime.
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            query = query.filter(Meal.upload_timestamp >= start_datetime)
            
        if end_date:
            # Add one day to include the end date fully
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
            query = query.filter(Meal.upload_timestamp <= end_datetime)
            
        if min_calories is not None:
            query = query.filter(Meal.calories >= min_calories)
            
        if max_calories is not None:
            query = query.filter(Meal.calories <= max_calories)
            
        if sort_by == "newest":
            query = query.order_by(Meal.upload_timestamp.desc())
        elif sort_by == "oldest":
            query = query.order_by(Meal.upload_timestamp.asc())
        elif sort_by == "highest_calories":
            query = query.order_by(Meal.calories.desc())
        elif sort_by == "lowest_calories":
            query = query.order_by(Meal.calories.asc())
            
        return query.all()
