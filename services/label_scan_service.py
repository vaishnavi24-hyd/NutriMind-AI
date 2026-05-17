from sqlalchemy.orm import Session
from models.food_label import FoodLabelScan
import json
import datetime

class LabelScanService:
    @staticmethod
    def add_scan(db: Session, image_path: str, extracted_text: str, analysis: dict):
        harmful_json = json.dumps(analysis.get("harmful_ingredients", []))
        
        db_scan = FoodLabelScan(
            image_path=image_path,
            extracted_text=extracted_text,
            ingredient_explanation=str(analysis.get("ingredient_explanation", "")),
            harmful_ingredients=harmful_json,
            is_ultra_processed=bool(analysis.get("is_ultra_processed", False)),
            health_score=int(analysis.get("health_score", 50)),
            healthier_alternatives=str(analysis.get("healthier_alternatives", "")),
            summary=str(analysis.get("summary", "")),
            upload_timestamp=datetime.datetime.utcnow()
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        return db_scan

    @staticmethod
    def get_all_scans(db: Session):
        return db.query(FoodLabelScan).order_by(FoodLabelScan.upload_timestamp.desc()).all()
