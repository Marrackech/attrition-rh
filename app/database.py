import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ENV = os.getenv("ENV", "development")

if ENV == "production":
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    DATABASE_URL = os.getenv("DATABASE_URL_DEV")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Float)
    revenu_mensuel = Column(Float)
    score_risque_depart = Column(Float)
    ratio_stagnation = Column(Float)
    ratio_experience_interne = Column(Float)
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
    Base.metadata.create_all(bind=engine)

def save_prediction(employee_data: dict, result: dict, log_data: dict):
    db = SessionLocal()
    try:
        # On garde seulement les colonnes de la table employees
        employee_fields = {"age", "revenu_mensuel", "score_risque_depart", 
                          "ratio_stagnation", "ratio_experience_interne"}
        filtered_data = {k: v for k, v in employee_data.items() if k in employee_fields}
        
        employee = Employee(**filtered_data)
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