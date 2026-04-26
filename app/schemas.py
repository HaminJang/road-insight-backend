from pydantic import BaseModel
from typing import Optional

class DamageDetection(BaseModel):
    detected: bool
    confidence: float
    area_ratio: float
    damage_score: float
    bbox: Optional[list] = None

class AnalysisResponse(BaseModel):
    success: bool
    hash: str
    timestamp: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    detection: DamageDetection
    message: str
