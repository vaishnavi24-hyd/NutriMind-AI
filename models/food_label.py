from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from database.database import Base
import datetime

class FoodLabelScan(Base):
    __tablename__ = "food_label_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String, index=True)
    extracted_text = Column(String)
    ingredient_explanation = Column(String)
    harmful_ingredients = Column(String)  # Stored as JSON string
    is_ultra_processed = Column(Boolean, default=False)
    health_score = Column(Integer)
    healthier_alternatives = Column(String)
    summary = Column(String)
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
