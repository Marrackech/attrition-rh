import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@pytest.fixture
def valid_payload():
    return {
        "age": 35, "revenu_mensuel": 4500.0, "annees_dans_l_entreprise": 5,
        "heures_supplementaires": 10, "satisfaction_employee_nature_travail": 3.5,
        "niveau_hierarchique_poste": 2, "nombre_participation_pee": 1,
        "score_risque_depart": 0.4, "ratio_stagnation": 0.2, "ratio_experience_interne": 0.5
    }

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_predict_success(valid_payload):
    # On simule la réussite de la DB pour ne pas écrire dedans
    with patch("app.main.save_prediction"):
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200
        assert "probabilite_depart" in response.json()

def test_predict_invalid_data():
    # Test de validation (âge négatif)
    response = client.post("/predict", json={"age": -1})
    assert response.status_code == 422

def test_database_error_handling(valid_payload):
    """
    On force save_prediction à lever une erreur. 
    Grâce au try/except dans main.py, le test recevra bien une 500.
    """
    with patch("app.main.save_prediction", side_effect=Exception("Database Connection Error")):
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 500
        assert "Database Connection Error" in response.json()["detail"]

        ##pipeline ci/cd seulement pour deploiyer sur hugging face 
        ## commit vers github et le deploiement est automatique 
        ## assurer le fonctionnement via les tests unitaires et fonctionnels
        ## deployer sur huggingfce et lancer le pipeline 
        ##
        ##
        ##