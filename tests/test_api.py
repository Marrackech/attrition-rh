# tests/test_api.py
import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.main import app
from app.database import Employee, Prediction, PredictionLog
import app.database as db_module

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-secret-key"}


# ─── Activation globale des FK SQLite ────────────────────────────────────────

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ─── Helper nettoyage FK ──────────────────────────────────────────────────────

def _cleanup_prediction_employee(db, prediction, employee):
    """Deux commits séparés pour respecter la contrainte FK sans relationship()."""
    db.delete(prediction)
    db.commit()
    db.delete(employee)
    db.commit()


# ─── Tests API ────────────────────────────────────────────────────────────────

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
            "annees_dans_l_entreprise": 2, "heure_supplementaires": 3,
            "satisfaction_employee_nature_travail": 2.0,
            "niveau_hierarchique_poste": 1, "nombre_participation_pee": 0,
            "score_risque_depart": 1.5, "ratio_stagnation": 0.8,
            "ratio_experience_interne": 0.3
        }
        response = client.post("/predict", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert "probabilite_depart" in response.json()
        assert response.json()["prediction"] in [0, 1]
        assert 0 <= response.json()["probabilite_depart"] <= 1

def test_predict_sans_api_key():
    response = client.post("/predict", json={"age": 30})
    assert response.status_code == 401

def test_predict_mauvaise_api_key():
    response = client.post("/predict", json={"age": 30}, headers={"X-API-Key": "mauvaise-cle"})
    assert response.status_code == 401

def test_predict_raises_500():
    with patch("app.main.predict") as mock_predict:
        with patch("app.main.save_prediction"):
            mock_predict.side_effect = Exception("Erreur modèle simulée")
            payload = {"age": 30, "score_risque_depart": 1.5}
            response = client.post("/predict", json=payload, headers=HEADERS)
            assert response.status_code == 500
            assert "Erreur modèle simulée" in response.json()["detail"]


# ─── Tests intégrité Employee ─────────────────────────────────────────────────

def test_database_employee_insertion():
    db = db_module.SessionLocal()
    employee = Employee(
        age=35, revenu_mensuel=5000, annees_dans_l_entreprise=3,
        heure_supplementaires=2, satisfaction_employee_nature_travail=3.0,
        niveau_hierarchique_poste=2, nombre_participation_pee=1,
        score_risque_depart=0.5, ratio_stagnation=0.3, ratio_experience_interne=0.6
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    assert employee.id is not None
    assert isinstance(employee.id, int)
    assert isinstance(employee.age, float)
    assert isinstance(employee.revenu_mensuel, float)
    assert isinstance(employee.annees_dans_l_entreprise, float)
    assert isinstance(employee.satisfaction_employee_nature_travail, float)
    assert isinstance(employee.score_risque_depart, float)
    assert isinstance(employee.ratio_stagnation, float)
    assert isinstance(employee.ratio_experience_interne, float)
    assert employee.age == 35.0
    assert employee.revenu_mensuel == 5000.0
    assert employee.satisfaction_employee_nature_travail == 3.0
    assert employee.score_risque_depart == 0.5

    db.delete(employee)
    db.commit()
    db.close()


def test_employee_champ_obligatoire_absent():
    """
    Aucun champ n'est nullable=False dans le schéma Employee actuel.
    Ce test documente que l'insertion d'un Employee vide est acceptée en base.
    Si des contraintes NOT NULL sont ajoutées dans database.py, ce test devra être revu.
    """
    db = db_module.SessionLocal()
    employee = Employee()
    db.add(employee)
    db.commit()
    db.refresh(employee)

    assert employee.id is not None
    assert employee.age is None
    assert employee.revenu_mensuel is None
    assert employee.score_risque_depart is None
    assert employee.satisfaction_employee_nature_travail is None

    db.delete(employee)
    db.commit()
    db.close()


def test_employee_champs_optionnels_sont_none():
    """Les champs non renseignés doivent valoir None, pas une valeur par défaut inattendue."""
    db = db_module.SessionLocal()
    employee = Employee(age=25, revenu_mensuel=2000, score_risque_depart=0.1)
    db.add(employee)
    db.commit()
    db.refresh(employee)

    assert employee.nombre_participation_pee is None
    assert employee.ratio_stagnation is None
    assert employee.ratio_experience_interne is None

    db.delete(employee)
    db.commit()
    db.close()


# ─── Tests intégrité Prediction ──────────────────────────────────────────────

def test_database_prediction_insertion():
    db = db_module.SessionLocal()
    employee = Employee(
        age=28, revenu_mensuel=3000, annees_dans_l_entreprise=1,
        heure_supplementaires=5, satisfaction_employee_nature_travail=1.5,
        niveau_hierarchique_poste=1, score_risque_depart=1.8
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
    assert isinstance(prediction.id, int)
    assert isinstance(prediction.employee_id, int)
    assert isinstance(prediction.probabilite_depart, float)
    assert isinstance(prediction.prediction, int)
    assert isinstance(prediction.interpretation, str)
    assert prediction.probabilite_depart == 0.85
    assert prediction.prediction == 1
    assert prediction.employee_id == employee.id
    assert prediction.interpretation == "Risque élevé de départ"

    _cleanup_prediction_employee(db, prediction, employee)
    db.close()


def test_prediction_sans_employee_leve_erreur():
    """
    Avec PRAGMA foreign_keys=ON activé globalement,
    une Prediction avec employee_id inexistant doit lever une IntegrityError.
    """
    db = db_module.SessionLocal()
    prediction = Prediction(
        employee_id=999999,
        probabilite_depart=0.5,
        prediction=0,
        interpretation="test"
    )
    db.add(prediction)
    with pytest.raises(Exception):
        db.commit()
    db.rollback()
    db.close()


def test_probabilite_depart_dans_intervalle():
    """probabilite_depart doit être un float compris entre 0 et 1."""
    db = db_module.SessionLocal()
    employee = Employee(age=30, revenu_mensuel=3000, score_risque_depart=0.5)
    db.add(employee)
    db.flush()

    prediction = Prediction(
        employee_id=employee.id,
        probabilite_depart=0.72,
        prediction=1,
        interpretation="Risque modéré"
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    assert isinstance(prediction.probabilite_depart, float)
    assert 0.0 <= prediction.probabilite_depart <= 1.0

    _cleanup_prediction_employee(db, prediction, employee)
    db.close()


# ─── Tests intégrité PredictionLog ───────────────────────────────────────────

def test_database_log_insertion():
    db = db_module.SessionLocal()
    log = PredictionLog(
        employee_id=1, inference_time_ms=12.5,
        api_response_time_ms=15.0, model_version="v1.0", status="success"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    assert log.id is not None
    assert isinstance(log.id, int)
    assert isinstance(log.inference_time_ms, float)
    assert isinstance(log.api_response_time_ms, float)
    assert isinstance(log.model_version, str)
    assert isinstance(log.status, str)
    assert log.status == "success"
    assert log.model_version == "v1.0"
    assert log.inference_time_ms == 12.5
    assert log.api_response_time_ms == 15.0

    db.delete(log)
    db.commit()
    db.close()


# ─── Test save_prediction (intégrité end-to-end) ─────────────────────────────

def test_save_prediction_real():
    from app.database import save_prediction

    employee_data = {k: 0.0 for k in [
        "age", "revenu_mensuel", "nombre_experiences_precedentes",
        "nombre_heures_travailless", "annees_dans_l_entreprise",
        "nombre_participation_pee", "nb_formations_suivies",
        "nombre_employee_sous_responsabilite", "distance_domicile_travail",
        "niveau_education", "frequence_deplacement",
        "annees_depuis_la_derniere_promotion",
        "satisfaction_employee_environnement", "note_evaluation_precedente",
        "niveau_hierarchique_poste", "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle", "heure_supplementaires",
        "augementation_salaire_precedente", "genre_M",
        "statut_marital_Divorce_e", "statut_marital_Marie_e",
        "departement_Consulting", "departement_Ressources_Humaines",
        "poste_Cadre_Commercial", "poste_Consultant",
        "poste_Directeur_Technique", "poste_Manager",
        "poste_Representant_Commercial", "poste_Ressources_Humaines",
        "poste_Senior_Manager", "poste_Tech_Lead",
        "domaine_etude_Entrepreunariat", "domaine_etude_Infra_Cloud",
        "domaine_etude_Marketing", "domaine_etude_Ressources_Humaines",
        "domaine_etude_Transformation_Digitale", "revenu_par_niveau",
        "score_satisfaction_global", "evolution_performance",
        "charge_travail", "ratio_stagnation", "ratio_experience_interne",
        "score_risque_depart", "engagement_formation"
    ]}
    result = {
        "probabilite_depart": 0.65,
        "prediction": 1,
        "interpretation": "Risque élevé de départ"
    }
    log_data = {
        "inference_time_ms": 10.0,
        "api_response_time_ms": 12.0,
        "model_version": "v1.0",
        "status": "success"
    }
    save_prediction(employee_data, result, log_data)

    db = db_module.SessionLocal()

    assert db.query(Employee).count() == 1
    assert db.query(Prediction).count() == 1
    assert db.query(PredictionLog).count() == 1

    emp = db.query(Employee).first()
    pred = db.query(Prediction).first()
    log = db.query(PredictionLog).first()

    assert isinstance(emp.id, int)
    assert isinstance(pred.probabilite_depart, float)
    assert isinstance(pred.prediction, int)
    assert isinstance(log.inference_time_ms, float)
    assert isinstance(log.status, str)
    assert pred.probabilite_depart == 0.65
    assert pred.prediction == 1
    assert pred.interpretation == "Risque élevé de départ"
    assert log.model_version == "v1.0"
    assert log.status == "success"
    assert log.inference_time_ms == 10.0
    assert pred.employee_id == emp.id

    db.close()


# ─── Tests fonctionnalité des requêtes ───────────────────────────────────────

def test_suppression_employee():
    """Vérifie qu'un employee supprimé n'existe plus en base."""
    db = db_module.SessionLocal()
    employee = Employee(age=40, revenu_mensuel=4000, score_risque_depart=0.3)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    employee_id = employee.id

    assert db.query(Employee).filter(Employee.id == employee_id).first() is not None

    db.delete(employee)
    db.commit()

    assert db.query(Employee).filter(Employee.id == employee_id).first() is None
    db.close()


def test_suppression_prediction():
    """Vérifie qu'une prediction supprimée n'existe plus en base."""
    db = db_module.SessionLocal()
    employee = Employee(age=30, revenu_mensuel=3000, score_risque_depart=0.5)
    db.add(employee)
    db.flush()

    prediction = Prediction(
        employee_id=employee.id,
        probabilite_depart=0.60,
        prediction=1,
        interpretation="Risque élevé de départ"
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    prediction_id = prediction.id

    db.delete(prediction)
    db.commit()

    assert db.query(Prediction).filter(Prediction.id == prediction_id).first() is None

    db.delete(employee)
    db.commit()
    db.close()


def test_insertion_employee_persistee():
    """Vérifie que l'employee inséré est retrouvable dans une nouvelle session."""
    db = db_module.SessionLocal()
    employee = Employee(age=45, revenu_mensuel=6000, score_risque_depart=0.9)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    employee_id = employee.id
    db.close()

    db2 = db_module.SessionLocal()
    retrieved = db2.query(Employee).filter(Employee.id == employee_id).first()
    assert retrieved is not None
    assert retrieved.age == 45.0
    assert retrieved.revenu_mensuel == 6000.0
    assert retrieved.score_risque_depart == 0.9

    db2.delete(retrieved)
    db2.commit()
    db2.close()


def test_insertion_prediction_persistee():
    """Vérifie que la prediction insérée est retrouvable dans une nouvelle session."""
    db = db_module.SessionLocal()
    employee = Employee(age=33, revenu_mensuel=3500, score_risque_depart=1.2)
    db.add(employee)
    db.flush()

    prediction = Prediction(
        employee_id=employee.id,
        probabilite_depart=0.78,
        prediction=1,
        interpretation="Risque élevé de départ"
    )
    db.add(prediction)
    db.commit()

    prediction_id = prediction.id
    employee_id = employee.id
    db.close()

    db2 = db_module.SessionLocal()
    retrieved = db2.query(Prediction).filter(Prediction.id == prediction_id).first()
    assert retrieved is not None
    assert retrieved.probabilite_depart == 0.78
    assert retrieved.prediction == 1
    assert retrieved.interpretation == "Risque élevé de départ"

    db2.delete(retrieved)
    db2.commit()

    emp_to_delete = db2.query(Employee).filter(Employee.id == employee_id).first()
    db2.delete(emp_to_delete)
    db2.commit()
    db2.close()


# ─── Tests couverture database.py ────────────────────────────────────────────

def test_init_db_production(monkeypatch):
    """Couvre la branche ENV=production dans init_db()."""
    original_env = db_module.ENV
    db_module.ENV = "production"
    monkeypatch.setenv("DATABASE_URL", os.getenv("DATABASE_URL_DEV", "sqlite:///./test.db"))
    try:
        db_module.init_db()
        assert db_module.SessionLocal is not None
        assert db_module.engine is not None
    finally:
        db_module.ENV = original_env


def test_init_db_sans_database_url(monkeypatch):
    """Couvre le raise ValueError quand DATABASE_URL est absente."""
    original_env = db_module.ENV
    db_module.ENV = "production"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_DEV", raising=False)
    try:
        with pytest.raises(ValueError, match="DATABASE_URL non configurée"):
            db_module.init_db()
    finally:
        db_module.ENV = original_env


def test_save_prediction_rollback_sur_erreur():
    """Couvre le bloc except (rollback + raise) dans save_prediction."""
    from app.database import save_prediction

    employee_data = {k: 0.0 for k in [
        "age", "revenu_mensuel", "nombre_experiences_precedentes",
        "nombre_heures_travailless", "annees_dans_l_entreprise",
        "nombre_participation_pee", "nb_formations_suivies",
        "nombre_employee_sous_responsabilite", "distance_domicile_travail",
        "niveau_education", "frequence_deplacement",
        "annees_depuis_la_derniere_promotion",
        "satisfaction_employee_environnement", "note_evaluation_precedente",
        "niveau_hierarchique_poste", "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle", "heure_supplementaires",
        "augementation_salaire_precedente", "genre_M",
        "statut_marital_Divorce_e", "statut_marital_Marie_e",
        "departement_Consulting", "departement_Ressources_Humaines",
        "poste_Cadre_Commercial", "poste_Consultant",
        "poste_Directeur_Technique", "poste_Manager",
        "poste_Representant_Commercial", "poste_Ressources_Humaines",
        "poste_Senior_Manager", "poste_Tech_Lead",
        "domaine_etude_Entrepreunariat", "domaine_etude_Infra_Cloud",
        "domaine_etude_Marketing", "domaine_etude_Ressources_Humaines",
        "domaine_etude_Transformation_Digitale", "revenu_par_niveau",
        "score_satisfaction_global", "evolution_performance",
        "charge_travail", "ratio_stagnation", "ratio_experience_interne",
        "score_risque_depart", "engagement_formation"
    ]}

    # result avec clé manquante → KeyError → rollback + raise
    result_invalide = {"probabilite_depart": 0.5}

    log_data = {
        "inference_time_ms": 5.0,
        "api_response_time_ms": 6.0,
        "model_version": "v1.0",
        "status": "success"
    }

    with pytest.raises(KeyError):
        save_prediction(employee_data, result_invalide, log_data)

    # Vérifier que le rollback a bien eu lieu : aucun employee orphelin en base
    db = db_module.SessionLocal()
    assert db.query(Employee).count() == 0
    db.close()


# ─── Tests couverture main.py ─────────────────────────────────────────────────

def test_debug_env():
    """Couvre le endpoint GET /debug-env."""
    response = client.get("/debug-env")
    assert response.status_code == 200
    data = response.json()
    assert "API_KEY_set" in data
    assert "API_set" in data
    assert "ENV" in data
    assert isinstance(data["API_KEY_set"], bool)
    assert isinstance(data["API_set"], bool)


def test_predict_erreur_save_prediction_fallback():
    """
    Couvre les lignes 87-88 : le save_prediction du bloc except dans /predict.
    Simule une erreur modèle ET un save_prediction fallback qui échoue silencieusement.
    """
    with patch("app.main.predict") as mock_predict:
        with patch("app.main.save_prediction") as mock_save:
            mock_predict.side_effect = Exception("Erreur modèle")
            mock_save.side_effect = Exception("Erreur save fallback")
            payload = {"age": 30, "score_risque_depart": 1.5}
            response = client.post("/predict", json=payload, headers=HEADERS)
            assert response.status_code == 500
            assert "Erreur modèle" in response.json()["detail"]
            assert mock_save.call_count == 1