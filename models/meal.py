from sqlalchemy import Column, Integer, String, Float, DateTime
from database.database import Base
import datetime

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, index=True)
    food_name = Column(String, index=True)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fats = Column(Float)
    health_score = Column(Integer)
    confidence_score = Column(Integer, default=0)
    nutrition_summary = Column(String)
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
