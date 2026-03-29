from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Attrition RH — opérationnelle"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_valid():
    payload = {
        "age": 30,
        "revenu_mensuel": 3000,
        "annees_dans_l_entreprise": 2,
        "heures_supplementaires": 3,
        "satisfaction_employee_nature_travail": 2.0,
        "niveau_hierarchique_poste": 1,
        "nombre_participation_pee": 0,
        "score_risque_depart": 1.5,
        "ratio_stagnation": 0.8,
        "ratio_experience_interne": 0.3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "probabilite_depart" in response.json()
    assert response.json()["prediction"] in [0, 1]
    assert response.json()["probabilite_depart"] >= 0
    assert response.json()["probabilite_depart"] <= 1

def test_predict_invalid_age():
    payload = {
        "age": -5,
        "revenu_mensuel": 3000,
        "annees_dans_l_entreprise": 2,
        "heures_supplementaires": 3,
        "satisfaction_employee_nature_travail": 2.0,
        "niveau_hierarchique_poste": 1,
        "nombre_participation_pee": 0,
        "score_risque_depart": 1.5,
        "ratio_stagnation": 0.8,
        "ratio_experience_interne": 0.3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_missing_field():
    payload = {"age": 30}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422