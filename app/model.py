import joblib
import os
import json
import pandas as pd
from app.schemas import EmployeeInput, PredictionOutput

SEUIL = 0.283
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chargement des artefacts
model = joblib.load(os.path.join(BASE_DIR, "models", "best_lr.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "models", "scaler.pkl"))
with open(os.path.join(BASE_DIR, "models", "colonnes.json"), "r") as f:
    COLONNES = json.load(f)
def predict(employee: EmployeeInput) -> PredictionOutput:
    # 1. Conversion Pydantic -> Dict
    input_dict = employee.model_dump()
    
    # 2. Création du DataFrame avec colonnes fixes (ordre respecté)
    data = pd.DataFrame(0, index=[0], columns=COLONNES)
    
    # 3. Remplissage des données reçues
    for col, val in input_dict.items():
        if col in data.columns:
            data.at[0, col] = val
            
    # 4. Prétraitement et Prédiction
    data_scaled = scaler.transform(data[COLONNES])
    proba = model.predict_proba(data_scaled)[0][1]
    
    prediction = int(proba >= SEUIL)
    interpretation = "Risque élevé de départ" if prediction == 1 else "Risque faible de départ"

    return PredictionOutput(
        probabilite_depart=round(float(proba), 4),
        prediction=prediction,
        seuil_utilise=SEUIL,
        interpretation=interpretation
    )