import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "development")
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    if ENV == "production"
    else (os.getenv("DATABASE_URL_DEV") or os.getenv("DATABASE_URL"))
)

if not DATABASE_URL:
    print(f"[ERREUR] DATABASE_URL non configurée pour ENV={ENV}")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "employees_full.csv")
SQL_PATH = os.path.join(BASE_DIR, "schema.sql")

COLUMN_MAPPING = {
    "statut_marital_Divorcé(e)": "statut_marital_Divorce_e",
    "statut_marital_Marié(e)": "statut_marital_Marie_e",
    "departement_Ressources Humaines": "departement_Ressources_Humaines",
    "poste_Cadre Commercial": "poste_Cadre_Commercial",
    "poste_Directeur Technique": "poste_Directeur_Technique",
    "poste_Représentant Commercial": "poste_Representant_Commercial",
    "poste_Ressources Humaines": "poste_Ressources_Humaines",
    "poste_Senior Manager": "poste_Senior_Manager",
    "poste_Tech Lead": "poste_Tech_Lead",
    "domaine_etude_Infra & Cloud": "domaine_etude_Infra_Cloud",
    "domaine_etude_Ressources Humaines": "domaine_etude_Ressources_Humaines",
    "domaine_etude_Transformation Digitale": "domaine_etude_Transformation_Digitale",
}

def main():
    print(f"=== Initialisation BDD — ENV={ENV} ===")
    engine = create_engine(DATABASE_URL, echo=False, future=True)

    print("[1/2] Création des tables...")
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                conn.execute(text(stmt))
        conn.commit()
    print("[1/2] Tables créées.")

    print("[2/2] Insertion du dataset...")
    df = pd.read_csv(CSV_PATH)
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    with engine.connect() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM employees_dataset")).scalar()
        if existing > 0:
            print(f"       {existing} lignes existantes, nettoyage...")
            conn.execute(text("DELETE FROM employees_dataset"))
            conn.commit()
    df.to_sql("employees_dataset", con=engine, if_exists="append", index=False, chunksize=200)
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM employees_dataset")).scalar()
    print(f"[2/2] {total} lignes insérées.")
    print("[OK] Base initialisée avec succès.")

if __name__ == "__main__":
    main()