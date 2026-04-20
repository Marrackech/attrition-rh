# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
import app.database as db_module

@pytest.fixture(scope="function", autouse=True)
def override_db():
    """
    Avant chaque test :
    - Crée un moteur SQLite en mémoire
    - Crée toutes les tables (Employee, Prediction, PredictionLog)
    - Remplace SessionLocal dans app.database

    Après chaque test :
    - Détruit toutes les tables → base propre
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    # Injection dans le module database
    db_module.engine = engine
    db_module.SessionLocal = TestSession

    yield TestSession

    Base.metadata.drop_all(bind=engine)
    engine.dispose()