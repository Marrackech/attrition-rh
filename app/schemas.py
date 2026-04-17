from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =========================
# INPUT (EMPLOYEE)
# =========================
class EmployeeInput(BaseModel):
    age: int = Field(..., ge=18, le=70)
    revenu_mensuel: float = Field(..., gt=0)
    annees_dans_l_entreprise: int = Field(..., ge=0)
    heures_supplementaires: int = Field(..., ge=0)
    satisfaction_employee_nature_travail: float = Field(..., ge=1, le=4)
    niveau_hierarchique_poste: int = Field(..., ge=1, le=5)
    nombre_participation_pee: int = Field(..., ge=0)
    score_risque_depart: float = Field(..., ge=0)
    ratio_stagnation: float = Field(..., ge=0)
    ratio_experience_interne: float = Field(..., ge=0)


# =========================
# OUTPUT API (PREDICTION)
# =========================
class PredictionOutput(BaseModel):
    employee_id: Optional[int] = None
    probabilite_depart: float
    prediction: int
    interpretation: str
    model_version: Optional[str] = "v1.0"
    created_at: Optional[datetime] = None


# =========================
# LOG (OPTIONNEL DEBUG)
# =========================
class PredictionLogSchema(BaseModel):
    employee_id: Optional[int] = None
    inference_time_ms: float
    api_response_time_ms: float
    model_version: str
    status: str
    request_timestamp: Optional[datetime] = None