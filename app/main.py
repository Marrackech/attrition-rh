import time
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from app.schemas import EmployeeInput, PredictionOutput
from app.model import predict
from app.database import init_db, save_prediction
import os

# =========================
# API KEY AUTH
# =========================
# API_KEY = os.getenv("API_KEY", "dev-secret-key")
# Après
API_KEY = os.getenv("API_KEY", "dev-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou manquante. Ajoutez X-API-Key dans vos headers."
        )
    return api_key

# =========================
# APP
# =========================
app = FastAPI(
    title="Attrition RH API",
    description="API de prédiction de départ d'employés — Authentification par API Key (header X-API-Key)",
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

@app.post("/predict", response_model=PredictionOutput, dependencies=[Depends(verify_api_key)])
def predict_attrition(employee: EmployeeInput):
    start_time = time.time()
    try:
        result = predict(employee)
        inference_time_ms = (time.time() - start_time) * 1000

        log_data = {
            "inference_time_ms": inference_time_ms,
            "api_response_time_ms": inference_time_ms,
            "model_version": "v1.0",
            "status": "success"
        }

        save_prediction(
            employee.model_dump(),
            {
                "probabilite_depart": result.probabilite_depart,
                "prediction": result.prediction,
                "interpretation": result.interpretation,
            },
            log_data
        )
        return result

    except Exception as e:
        log_data = {
            "inference_time_ms": 0,
            "api_response_time_ms": 0,
            "model_version": "v1.0",
            "status": "error"
        }
        try:
            save_prediction(
                employee.model_dump(),
                {"probabilite_depart": 0, "prediction": 0, "interpretation": "error"},
                log_data
            )
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))