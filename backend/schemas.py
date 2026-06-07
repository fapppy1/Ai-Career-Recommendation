"""
API Request/Response Schemas using Pydantic
Proposal Alignment: Objective 3 - Robust API design
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# ===== Authentication Schemas =====

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    industry: Optional[str] = "Technology"
    skills: Optional[List[str]] = []
    experience_level: Optional[str] = "Intermediate"
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v):
            raise ValueError('Password must contain upper and lowercase letters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ===== Recommendation Schemas =====

class RecommendationRequest(BaseModel):
    skills: List[str] = Field(..., min_items=1, max_items=20)
    industry: Optional[str] = "Technology"
    experience_level: Optional[str] = "Intermediate"
    
    @validator('skills', each_item=True)
    def validate_skill(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Skill cannot be empty')
        if len(v) > 50:
            raise ValueError('Each skill must be under 50 characters')
        return v.strip().title()

class RecommendationResponse(BaseModel):
    success: bool
    recommendations: Optional[List[Dict[str, Any]]] = None
    skill_analysis: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ===== Cybersecurity Schemas =====

class URLCheckRequest(BaseModel):
    url: str = Field(..., min_length=10, max_length=2048)
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class URLCheckResponse(BaseModel):
    success: bool
    url: str
    result: Dict[str, Any]
    error: Optional[str] = None

class JobAnalysisRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: str = Field(..., min_length=20, max_length=10000)
    salary: Optional[str] = None
    contact_email: Optional[EmailStr] = None

class JobAnalysisResponse(BaseModel):
    success: bool
    analysis: Dict[str, Any]
    error: Optional[str] = None

# ===== Evaluation Schemas =====

class EvaluationMetrics(BaseModel):
    user_id: int
    period_days: int
    total_feedback: int
    average_rating: float
    precision: float
    high_ratings_pct: float
    response_time_avg_ms: Optional[float] = None
    proposal_alignment: str

# ===== Utility Functions =====

def validate_request(model_class: BaseModel, data: Dict) -> tuple[bool, Any, Optional[str]]:
    """
    Validate request data against Pydantic schema
    Returns: (is_valid, validated_data_or_errors, error_message)
    """
    try:
        validated = model_class(**data)
        return True, validated.dict(), None
    except Exception as e:
        return False, None, str(e)