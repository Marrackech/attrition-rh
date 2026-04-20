import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Charger le .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Charger le CSV
df = pd.read_csv("/Users/mac3/Desktop/AIengineer/projet5/attrition rh/data/employees_full.csv")

print(f"✅ CSV chargé : {df.shape[0]} lignes × {df.shape[1]} colonnes")

# Créer la connexion
engine = create_engine(DATABASE_URL)

# Importer dans Neon (crée la table automatiquement)
df.to_sql(
    name="employees_raw",
    con=engine,
    if_exists="replace",  # recrée la table si elle existe déjà
    index=False
)

print(f"✅ {df.shape[0]} lignes importées dans Neon → table employees_raw")

