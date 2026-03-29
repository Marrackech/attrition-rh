from pydantic import BaseModel, Field

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

class PredictionOutput(BaseModel):
    probabilite_depart: float
    prediction: int
    seuil_utilise: float
    interpretation: str