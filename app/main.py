import time
from fastapi import FastAPI, HTTPException
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
    # Initialise les tables au lancement
    init_db()

@app.get("/")
def root():
    return {"message": "API Attrition RH — opérationnelle"}

@app.post("/predict", response_model=PredictionOutput)
def predict_attrition(employee: EmployeeInput):
    start_time = time.time()
    try:
        # 1. Prédiction via le modèle ML
        result = predict(employee)
        inference_time_ms = (time.time() - start_time) * 1000

        # 2. Préparation des logs techniques
        log_data = {
            "inference_time_ms": inference_time_ms,
            "api_response_time_ms": inference_time_ms,
            "model_version": "v1.0",
            "status": "success"
        }

        # 3. Sauvegarde en base de données
        # On sépare bien les dictionnaires pour éviter l'erreur de colonnes
        save_prediction(
            employee_data=employee.model_dump(), 
            result=result.model_dump(), 
            log_data=log_data
        )

        return result

    except Exception as e:
        # En cas d'erreur, on renvoie une erreur 500 détaillée
        print(f"Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))