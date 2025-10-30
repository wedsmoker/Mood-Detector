from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional


class MoodAnalysisResponse(BaseModel):
    mood: str
    tempo: float  # Swapped order to match README
    energy: float
    key: str
    explanation: str

    # Optional fields (excluded from response if None)
    model_config = ConfigDict(exclude_none=True)


class MoodAnalysisRequest(BaseModel):
    detailed: bool = False
    similarity_search: bool = False