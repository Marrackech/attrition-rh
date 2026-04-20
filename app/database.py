import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ENV = os.getenv("ENV", "development")
Base = declarative_base()
engine = None
SessionLocal = None


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Float)
    revenu_mensuel = Column(Float)
    nombre_experiences_precedentes = Column(Float)
    nombre_heures_travailless = Column(Float)
    annees_dans_l_entreprise = Column(Float)
    nombre_participation_pee = Column(Float)
    nb_formations_suivies = Column(Float)
    nombre_employee_sous_responsabilite = Column(Float)
    distance_domicile_travail = Column(Float)
    niveau_education = Column(Float)
    frequence_deplacement = Column(Float)
    annees_depuis_la_derniere_promotion = Column(Float)
    satisfaction_employee_environnement = Column(Float)
    note_evaluation_precedente = Column(Float)
    niveau_hierarchique_poste = Column(Float)
    satisfaction_employee_nature_travail = Column(Float)
    satisfaction_employee_equipe = Column(Float)
    satisfaction_employee_equilibre_pro_perso = Column(Float)
    note_evaluation_actuelle = Column(Float)
    heure_supplementaires = Column(Float)
    augementation_salaire_precedente = Column(Float)
    genre_M = Column(Float)
    statut_marital_Divorce_e = Column(Float)
    statut_marital_Marie_e = Column(Float)
    departement_Consulting = Column(Float)
    departement_Ressources_Humaines = Column(Float)
    poste_Cadre_Commercial = Column(Float)
    poste_Consultant = Column(Float)
    poste_Directeur_Technique = Column(Float)
    poste_Manager = Column(Float)
    poste_Representant_Commercial = Column(Float)
    poste_Ressources_Humaines = Column(Float)
    poste_Senior_Manager = Column(Float)
    poste_Tech_Lead = Column(Float)
    domaine_etude_Entrepreunariat = Column(Float)
    domaine_etude_Infra_Cloud = Column(Float)
    domaine_etude_Marketing = Column(Float)
    domaine_etude_Ressources_Humaines = Column(Float)
    domaine_etude_Transformation_Digitale = Column(Float)
    revenu_par_niveau = Column(Float)
    score_satisfaction_global = Column(Float)
    evolution_performance = Column(Float)
    charge_travail = Column(Float)
    ratio_stagnation = Column(Float)
    ratio_experience_interne = Column(Float)
    score_risque_depart = Column(Float)
    engagement_formation = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    probabilite_depart = Column(Float)
    prediction = Column(Integer)
    interpretation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    inference_time_ms = Column(Float)
    api_response_time_ms = Column(Float)
    model_version = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    global engine, SessionLocal
    if ENV == "production":
        DATABASE_URL = os.getenv("DATABASE_URL")
    else:
        DATABASE_URL = os.getenv("DATABASE_URL_DEV") or os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError(f"DATABASE_URL non configurée pour ENV={ENV}")
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)


def save_prediction(employee_data: dict, result: dict, log_data: dict):
    db = SessionLocal()
    try:
        employee = Employee(**employee_data)
        db.add(employee)
        db.flush()
        prediction = Prediction(
            employee_id=employee.id,
            probabilite_depart=result["probabilite_depart"],
            prediction=result["prediction"],
            interpretation=result["interpretation"]
        )
        db.add(prediction)
        log = PredictionLog(
            employee_id=employee.id,
            inference_time_ms=log_data["inference_time_ms"],
            api_response_time_ms=log_data["api_response_time_ms"],
            model_version=log_data["model_version"],
            status=log_data["status"]
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()