# tests/test_model.py
import pytest
from app.schemas import EmployeeInput, PredictionOutput
from app.model import predict, SEUIL


# ── Fixture : employé par défaut (tous les champs à 0) ──────────────────────

@pytest.fixture
def employee_defaut():
    return EmployeeInput()


@pytest.fixture
def employee_risque_eleve():
    return EmployeeInput(
        score_risque_depart=2.5,
        ratio_stagnation=1.8,
        heure_supplementaires=2.0,
        satisfaction_employee_nature_travail=0.5,
        annees_dans_l_entreprise=0.2,
    )


@pytest.fixture
def employee_risque_faible():
    return EmployeeInput(
        score_risque_depart=-1.5,
        ratio_stagnation=-1.0,
        heure_supplementaires=-0.5,
        satisfaction_employee_nature_travail=2.0,
        annees_dans_l_entreprise=1.5,
        revenu_mensuel=1.2,
    )


# ── Tests du type de retour ──────────────────────────────────────────────────

def test_predict_retourne_prediction_output(employee_defaut):
    result = predict(employee_defaut)
    assert isinstance(result, PredictionOutput)


def test_predict_probabilite_est_float(employee_defaut):
    result = predict(employee_defaut)
    assert isinstance(result.probabilite_depart, float)


def test_predict_prediction_est_entier(employee_defaut):
    result = predict(employee_defaut)
    assert isinstance(result.prediction, int)


# ── Tests des contraintes sur les valeurs ───────────────────────────────────

def test_probabilite_entre_0_et_1(employee_defaut):
    result = predict(employee_defaut)
    assert 0.0 <= result.probabilite_depart <= 1.0


def test_prediction_vaut_0_ou_1(employee_defaut):
    result = predict(employee_defaut)
    assert result.prediction in [0, 1]


def test_seuil_utilise_est_correct(employee_defaut):
    result = predict(employee_defaut)
    assert result.seuil_utilise == SEUIL


def test_interpretation_non_vide(employee_defaut):
    result = predict(employee_defaut)
    assert isinstance(result.interpretation, str)
    assert len(result.interpretation) > 0


# ── Tests de cohérence prediction / probabilité ─────────────────────────────

def test_coherence_prediction_1_si_proba_superieure_seuil(employee_defaut):
    result = predict(employee_defaut)
    if result.probabilite_depart >= SEUIL:
        assert result.prediction == 1
    else:
        assert result.prediction == 0


def test_coherence_interpretation_risque_eleve(employee_risque_eleve):
    result = predict(employee_risque_eleve)
    if result.prediction == 1:
        assert result.interpretation == "Risque élevé de départ"


def test_coherence_interpretation_risque_faible(employee_risque_faible):
    result = predict(employee_risque_faible)
    if result.prediction == 0:
        assert result.interpretation == "Risque faible de départ"


# ── Tests de robustesse ──────────────────────────────────────────────────────

def test_predict_avec_tous_champs_a_zero():
    employee = EmployeeInput()
    result = predict(employee)
    assert result is not None
    assert 0.0 <= result.probabilite_depart <= 1.0


def test_predict_avec_valeurs_extremes_positives():
    employee = EmployeeInput(
        age=3.0,
        revenu_mensuel=3.0,
        score_risque_depart=3.0,
        ratio_stagnation=3.0,
    )
    result = predict(employee)
    assert 0.0 <= result.probabilite_depart <= 1.0


def test_predict_avec_valeurs_extremes_negatives():
    employee = EmployeeInput(
        age=-3.0,
        revenu_mensuel=-3.0,
        score_risque_depart=-3.0,
        ratio_stagnation=-3.0,
    )
    result = predict(employee)
    assert 0.0 <= result.probabilite_depart <= 1.0


def test_predict_repetable():
    """Le même input doit toujours donner le même output."""
    employee = EmployeeInput(score_risque_depart=1.0, ratio_stagnation=0.5)
    result1 = predict(employee)
    result2 = predict(employee)
    assert result1.probabilite_depart == result2.probabilite_depart
    assert result1.prediction == result2.prediction