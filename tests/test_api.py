from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.database import SessionLocal, Employee, Prediction, PredictionLog, init_db

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_valid():
    with patch("app.main.save_prediction"):
        payload = {
            "age": 30, "revenu_mensuel": 3000,
            "annees_dans_l_entreprise": 2, "heures_supplementaires": 3,
            "satisfaction_employee_nature_travail": 2.0,
            "niveau_hierarchique_poste": 1, "nombre_participation_pee": 0,
            "score_risque_depart": 1.5, "ratio_stagnation": 0.8,
            "ratio_experience_interne": 0.3
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        assert "probabilite_depart" in response.json()
        assert response.json()["prediction"] in [0, 1]
        assert 0 <= response.json()["probabilite_depart"] <= 1

def test_predict_invalid_age():
    with patch("app.main.save_prediction"):
        payload = {
            "age": -5, "revenu_mensuel": 3000,
            "annees_dans_l_entreprise": 2, "heures_supplementaires": 3,
            "satisfaction_employee_nature_travail": 2.0,
            "niveau_hierarchique_poste": 1, "nombre_participation_pee": 0,
            "score_risque_depart": 1.5, "ratio_stagnation": 0.8,
            "ratio_experience_interne": 0.3
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

def test_predict_missing_field():
    with patch("app.main.save_prediction"):
        response = client.post("/predict", json={"age": 30})
        assert response.status_code == 422

# ── Tests base de données réels ──────────────────────────
def test_database_employee_insertion():
    db = SessionLocal()
    employee = Employee(
        age=35, revenu_mensuel=5000,
        annees_dans_l_entreprise=3, heures_supplementaires=2,
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
    db = SessionLocal()
    employee = Employee(
        age=28, revenu_mensuel=3000,
        annees_dans_l_entreprise=1, heures_supplementaires=5,
        satisfaction_employee_nature_travail=1.5,
        niveau_hierarchique_poste=1, nombre_participation_pee=0,
        score_risque_depart=1.8, ratio_stagnation=0.9,
        ratio_experience_interne=0.2
    )
    db.add(employee)
    db.flush()

    prediction = Prediction(
        employee_id=employee.id,
        probabilite_depart=0.85,
        prediction=1,
        interpretation="Risque élevé de départ"
    )
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
    db = SessionLocal()
    log = PredictionLog(
        employee_id=1,
        inference_time_ms=12.5,
        api_response_time_ms=15.0,
        model_version="v1.0",
        status="success"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    assert log.id is not None
    assert log.status == "success"

    db.delete(log)
    db.commit()
    db.close()