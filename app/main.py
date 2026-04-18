# from fastapi import FastAPI, HTTPException
# from app.schemas import EmployeeInput, PredictionOutput
# from app.model import predict
# from app.database import init_db, save_prediction

# app = FastAPI(
#     title="Attrition RH API",
#     description="API de prédiction de départ d'employés",
#     version="1.0.0"
# )

# @app.on_event("startup")
# def startup():
#     init_db()

# @app.get("/")
# def root():
#     return {"message": "API Attrition RH — opérationnelle"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/predict", response_model=PredictionOutput)
# def predict_attrition(employee: EmployeeInput):
#     try:
#         # 1. Calcul de la prédiction via le modèle
#         result = predict(employee)
        
#         # 2. Sauvegarde dans la base de données
#         # On convertit les objets Pydantic en dictionnaires
#         save_prediction(employee.model_dump(), result.model_dump())
        
#         return result
#     except Exception as e:
#         # Permet de renvoyer une erreur 500 propre au lieu d'un crash serveur
#         raise HTTPException(status_code=500, detail=str(e))
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
    init_db()

@app.get("/")
def root():
    return {"message": "API Attrition RH — opérationnelle"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionOutput)
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

        save_prediction(employee.model_dump(), result.model_dump(), log_data)
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