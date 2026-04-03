from fastapi import FastAPI
from app.schemas import EmployeeInput, PredictionOutput
from app.model import predict
from app.database import init_db, save_prediction

app = FastAPI(
    title="Attrition RH API",
    description="API de prédiction de départ d'employés",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "API Attrition RH — opérationnelle"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionOutput)
def predict_attrition(employee: EmployeeInput):
    result = predict(employee)
    save_prediction(employee.dict(), result.dict())
    return result
    #(le modèle Pydantic) fait automatiquement :

# validation des types (int, float)
# validation des contraintes (ge=0, le=70, etc.)
# gestion des erreurs → retourne 422 automatiquement