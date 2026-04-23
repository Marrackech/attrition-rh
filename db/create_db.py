import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_DEV") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERREUR] DATABASE_URL non configurée")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "employees_full.csv")

def main():
    engine = create_engine(DATABASE_URL, echo=False)

    print("[1/2] Chargement du CSV...")
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.lower() for c in df.columns]
    print(f"      {len(df)} lignes chargées")

    print("[2/2] Insertion dans employees_dataset...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS employees_dataset CASCADE"))
        conn.commit()

    df.to_sql("employees_dataset", con=engine, if_exists="replace", index=False)

    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM employees_dataset")).scalar()
    print(f"[OK] {total} lignes insérées dans employees_dataset")

if __name__ == "__main__":
    main()