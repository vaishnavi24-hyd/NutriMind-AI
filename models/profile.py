from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database.database import Base
import datetime

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer)
    gender = Column(String)  # "Male", "Female"
    weight_kg = Column(Float)
    height_cm = Column(Float)
    activity_level = Column(String) # "Sedentary", "Light", "Moderate", "Active", "Very Active"
    fitness_goal = Column(String) # "Weight Loss", "Maintenance", "Muscle Gain"
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
