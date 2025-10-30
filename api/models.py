from pydantic import BaseModel
from typing import Dict, Optional


class MoodAnalysisResponse(BaseModel):
    mood: str
    energy: float
    tempo: float
    key: str
    explanation: str
    duration: Optional[float] = None
    similar_moods: Optional[Dict[str, float]] = None


class MoodAnalysisRequest(BaseModel):
    detailed: bool = False
    similarity_search: bool = False