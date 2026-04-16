import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# =========================
# TABLE EMPLOYEES
# =========================
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    revenu_mensuel = Column(Float)
    annees_dans_l_entreprise = Column(Integer)
    heures_supplementaires = Column(Integer)
    satisfaction_employee_nature_travail = Column(Float)
    niveau_hierarchique_poste = Column(Integer)
    nombre_participation_pee = Column(Integer)
    score_risque_depart = Column(Float)
    ratio_stagnation = Column(Float)
    ratio_experience_interne = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    predictions = relationship("Prediction", back_populates="employee")

# =========================
# TABLE PREDICTIONS
# =========================
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    probabilite_depart = Column(Float)
    prediction = Column(Integer)
    interpretation = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", back_populates="predictions")

# =========================
# TABLE LOGS
# =========================
class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=True)
    inference_time_ms = Column(Float)
    api_response_time_ms = Column(Float)
    model_version = Column(String)
    status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# INITIALISATION DB
# =========================
def init_db():
    # ATTENTION : Décommentez drop_all pour le premier push sur Hugging Face
    # afin de supprimer l'ancienne table qui cause l'erreur 500.
    # Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)

# =========================
# FONCTION DE SAUVEGARDE
# =========================
def save_prediction(employee_data: dict, result: dict, log_data: dict = None):
    db = SessionLocal()
    try:
        # 1. On crée l'employé
        employee = Employee(
            age=employee_data.get("age"),
            revenu_mensuel=employee_data.get("revenu_mensuel"),
            annees_dans_l_entreprise=employee_data.get("annees_dans_l_entreprise"),
            heures_supplementaires=employee_data.get("heures_supplementaires"),
            satisfaction_employee_nature_travail=employee_data.get("satisfaction_employee_nature_travail"),
            niveau_hierarchique_poste=employee_data.get("niveau_hierarchique_poste"),
            nombre_participation_pee=employee_data.get("nombre_participation_pee"),
            score_risque_depart=employee_data.get("score_risque_depart"),
            ratio_stagnation=employee_data.get("ratio_stagnation"),
            ratio_experience_interne=employee_data.get("ratio_experience_interne"),
        )
        db.add(employee)
        db.flush() 

        # 2. On crée la prédiction (STRICTEMENT SANS AGE NI REVENU)
        prediction = Prediction(
            employee_id=employee.id,
            probabilite_depart=result.get("probabilite_depart"),
            prediction=result.get("prediction"),
            interpretation=result.get("interpretation")
        )
        db.add(prediction)

        # 3. On crée le log technique
        if log_data:
            log = PredictionLog(
                employee_id=employee.id,
                inference_time_ms=log_data.get("inference_time_ms"),
                api_response_time_ms=log_data.get("api_response_time_ms"),
                model_version=log_data.get("model_version"),
                status=log_data.get("status"),
            )
            db.add(log)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erreur DB : {e}")
        raise e
    finally:
        db.close()