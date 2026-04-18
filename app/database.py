import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

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
    probabilite_depart = Column(Float)
    prediction = Column(Integer)
    interpretation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_prediction(employee_data: dict, result: dict):
    db = SessionLocal()
    try:
        prediction = Prediction(
            **employee_data,
            probabilite_depart=result["probabilite_depart"],
            prediction=result["prediction"],
            interpretation=result["interpretation"]
        )
        db.add(prediction)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la sauvegarde : {e}")
        raise e
    finally:
        db.close()