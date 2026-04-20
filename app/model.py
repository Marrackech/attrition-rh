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

# Mapping noms Pydantic -> noms réels colonnes
MAPPING = {
    "statut_marital_Divorce_e": "statut_marital_Divorcé(e)",
    "statut_marital_Marie_e": "statut_marital_Marié(e)",
    "departement_Ressources_Humaines": "departement_Ressources Humaines",
    "poste_Cadre_Commercial": "poste_Cadre Commercial",
    "poste_Directeur_Technique": "poste_Directeur Technique",
    "poste_Representant_Commercial": "poste_Représentant Commercial",
    "poste_Ressources_Humaines": "poste_Ressources Humaines",
    "poste_Senior_Manager": "poste_Senior Manager",
    "poste_Tech_Lead": "poste_Tech Lead",
    "domaine_etude_Infra_Cloud": "domaine_etude_Infra & Cloud",
    "domaine_etude_Ressources_Humaines": "domaine_etude_Ressources Humaines",
    "domaine_etude_Transformation_Digitale": "domaine_etude_Transformation Digitale",
}

def predict(employee: EmployeeInput) -> PredictionOutput:
    input_dict = employee.model_dump()

    # Créer DataFrame avec les 47 colonnes initialisées à 0
    data = pd.DataFrame(0, index=[0], columns=COLONNES)

    # Remplir avec les valeurs reçues en appliquant le mapping
    for col, val in input_dict.items():
        real_col = MAPPING.get(col, col)
        if real_col in data.columns:
            data.at[0, real_col] = val

    # Prédiction (données déjà scalées car X_scaled exporté)
    proba = model.predict_proba(data[COLONNES])[0][1]

    prediction = int(proba >= SEUIL)
    interpretation = "Risque élevé de départ" if prediction == 1 else "Risque faible de départ"

    return PredictionOutput(
        probabilite_depart=round(float(proba), 4),
        prediction=prediction,
        seuil_utilise=SEUIL,
        interpretation=interpretation
    )