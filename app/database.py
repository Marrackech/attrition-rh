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
# 1. EMPLOYEES TABLE
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
# 2. PREDICTIONS TABLE
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
# 3. LOGS / MONITORING TABLE
# =========================
class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, nullable=True)

    request_timestamp = Column(DateTime, default=datetime.utcnow)

    inference_time_ms = Column(Float)

    api_response_time_ms = Column(Float)

    model_version = Column(String)

    status = Column(String)  # success / error

    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# INIT DB
# =========================
def init_db():
    Base.metadata.create_all(bind=engine)


# =========================
# SAVE PREDICTION
# =========================
def save_prediction(employee_data: dict, result: dict, log_data: dict = None):
    db = SessionLocal()
    try:
        # 1. Create employee
        employee = Employee(**employee_data)
        db.add(employee)
        db.flush()  # récupère employee.id sans commit

        # 2. Create prediction
        prediction = Prediction(
            employee_id=employee.id,
            probabilite_depart=result["probabilite_depart"],
            prediction=result["prediction"],
            interpretation=result["interpretation"]
        )
        db.add(prediction)

        # 3. Create log (optional)
        if log_data:
            log = PredictionLog(
                employee_id=employee.id,
                **log_data
            )
            db.add(log)

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la sauvegarde : {e}")
        raise e

    finally:
        db.close()