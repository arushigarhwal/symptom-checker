from typing import List, Optional
from pydantic import BaseModel, Field, constr

class Condition(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    likelihood_note: constr(strip_whitespace=True, min_length=1)
    evidence: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    conditions: List[Condition] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    disclaimer: str
    raw_model_output: Optional[str] = None  # for debugging / audits

class AnalysisRequest(BaseModel):
    symptoms: constr(strip_whitespace=True, min_length=5, max_length=4000)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    duration_days: Optional[int] = Field(default=None, ge=0, le=365)

class SafeError(BaseModel):
    error: str
    details: Optional[str] = None
