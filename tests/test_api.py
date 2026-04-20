# tests/test_api.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.database import Employee, Prediction, PredictionLog
import app.database as db_module

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-secret-key"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_valid():
    with patch("app.main.save_prediction"):
        payload = {"age": 30, "revenu_mensuel": 3000, "annees_dans_l_entreprise": 2,
                   "heure_supplementaires": 3, "satisfaction_employee_nature_travail": 2.0,
                   "niveau_hierarchique_poste": 1, "nombre_participation_pee": 0,
                   "score_risque_depart": 1.5, "ratio_stagnation": 0.8, "ratio_experience_interne": 0.3}
        response = client.post("/predict", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert "probabilite_depart" in response.json()
        assert response.json()["prediction"] in [0, 1]
        assert 0 <= response.json()["probabilite_depart"] <= 1

def test_predict_sans_api_key():
    payload = {"age": 30}
    response = client.post("/predict", json=payload)
    assert response.status_code == 401

def test_predict_mauvaise_api_key():
    payload = {"age": 30}
    response = client.post("/predict", json=payload, headers={"X-API-Key": "mauvaise-cle"})
    assert response.status_code == 401

def test_database_employee_insertion():
    db = db_module.SessionLocal()
    employee = Employee(
        age=35, revenu_mensuel=5000,
        annees_dans_l_entreprise=3, heure_supplementaires=2,
        satisfaction_employee_nature_travail=3.0,
        niveau_hierarchique_poste=2, nombre_participation_pee=1,
        score_risque_depart=0.5, ratio_stagnation=0.3,
        ratio_experience_interne=0.6
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    assert employee.id is not None
    assert employee.age == 35
    db.delete(employee)
    db.commit()
    db.close()

def test_database_prediction_insertion():
    db = db_module.SessionLocal()
    employee = Employee(age=28, revenu_mensuel=3000, annees_dans_l_entreprise=1,
                        heure_supplementaires=5, satisfaction_employee_nature_travail=1.5,
                        niveau_hierarchique_poste=1, score_risque_depart=1.8)
    db.add(employee)
    db.flush()
    prediction = Prediction(employee_id=employee.id, probabilite_depart=0.85,
                            prediction=1, interpretation="Risque élevé de départ")
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    assert prediction.id is not None
    assert prediction.probabilite_depart == 0.85
    assert prediction.employee_id == employee.id
    db.delete(prediction)
    db.delete(employee)
    db.commit()
    db.close()

def test_database_log_insertion():
    db = db_module.SessionLocal()
    log = PredictionLog(employee_id=1, inference_time_ms=12.5,
                        api_response_time_ms=15.0, model_version="v1.0", status="success")
    db.add(log)
    db.commit()
    db.refresh(log)
    assert log.id is not None
    assert log.status == "success"
    db.delete(log)
    db.commit()
    db.close()

def test_save_prediction_real():
    from app.database import save_prediction
    employee_data = {k: 0.0 for k in [
        "age", "revenu_mensuel", "nombre_experiences_precedentes", "nombre_heures_travailless",
        "annees_dans_l_entreprise", "nombre_participation_pee", "nb_formations_suivies",
        "nombre_employee_sous_responsabilite", "distance_domicile_travail", "niveau_education",
        "frequence_deplacement", "annees_depuis_la_derniere_promotion",
        "satisfaction_employee_environnement", "note_evaluation_precedente",
        "niveau_hierarchique_poste", "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe", "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle", "heure_supplementaires", "augementation_salaire_precedente",
        "genre_M", "statut_marital_Divorce_e", "statut_marital_Marie_e",
        "departement_Consulting", "departement_Ressources_Humaines", "poste_Cadre_Commercial",
        "poste_Consultant", "poste_Directeur_Technique", "poste_Manager",
        "poste_Representant_Commercial", "poste_Ressources_Humaines", "poste_Senior_Manager",
        "poste_Tech_Lead", "domaine_etude_Entrepreunariat", "domaine_etude_Infra_Cloud",
        "domaine_etude_Marketing", "domaine_etude_Ressources_Humaines",
        "domaine_etude_Transformation_Digitale", "revenu_par_niveau", "score_satisfaction_global",
        "evolution_performance", "charge_travail", "ratio_stagnation", "ratio_experience_interne",
        "score_risque_depart", "engagement_formation"
    ]}
    result = {"probabilite_depart": 0.65, "prediction": 1, "interpretation": "Risque élevé de départ"}
    log_data = {"inference_time_ms": 10.0, "api_response_time_ms": 12.0,
                "model_version": "v1.0", "status": "success"}
    save_prediction(employee_data, result, log_data)
    db = db_module.SessionLocal()
    assert db.query(Employee).count() == 1
    assert db.query(Prediction).count() == 1
    assert db.query(PredictionLog).count() == 1
    db.close()

def test_predict_raises_500():
    with patch("app.main.predict") as mock_predict:
        with patch("app.main.save_prediction"):
            mock_predict.side_effect = Exception("Erreur modèle simulée")
            payload = {"age": 30, "score_risque_depart": 1.5}
            response = client.post("/predict", json=payload, headers=HEADERS)
            assert response.status_code == 500
            assert "Erreur modèle simulée" in response.json()["detail"]