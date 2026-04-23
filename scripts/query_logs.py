"""
query_logs.py — Consultation et export des données loggées en base
Usage :
    python scripts/query_logs.py                  # résumé général
    python scripts/query_logs.py --table logs     # logs de performance
    python scripts/query_logs.py --table predictions  # prédictions
    python scripts/query_logs.py --table risque   # employés à risque
    python scripts/query_logs.py --export         # export CSV dans exports/
"""

import os
import sys
import argparse
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_DEV") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERREUR] DATABASE_URL non configurée dans .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL, echo=False)

# =============================================================
# REQUÊTES
# =============================================================

QUERIES = {

    "summary": """
        SELECT
            (SELECT COUNT(*) FROM employees)        AS total_employes,
            (SELECT COUNT(*) FROM predictions)      AS total_predictions,
            (SELECT COUNT(*) FROM predictions WHERE prediction = 1) AS departs_predits,
            (SELECT COUNT(*) FROM prediction_logs)  AS total_logs,
            (SELECT COUNT(*) FROM prediction_logs WHERE status = 'error') AS total_erreurs,
            (SELECT ROUND(AVG(inference_time_ms)::numeric, 2) FROM prediction_logs WHERE status = 'success') AS inference_moy_ms
    """,

    "predictions": """
        SELECT
            p.id,
            p.employee_id,
            ROUND(p.probabilite_depart::numeric, 4) AS probabilite_depart,
            p.prediction,
            p.interpretation,
            p.created_at
        FROM predictions p
        ORDER BY p.created_at DESC
        LIMIT 100
    """,

    "logs": """
        SELECT
            l.id,
            l.employee_id,
            ROUND(l.inference_time_ms::numeric, 2)     AS inference_ms,
            ROUND(l.api_response_time_ms::numeric, 2)  AS reponse_ms,
            l.model_version,
            l.status,
            l.created_at
        FROM prediction_logs l
        ORDER BY l.created_at DESC
        LIMIT 100
    """,

    "risque": """
        SELECT
            e.id,
            e.age,
            e.revenu_mensuel,
            e.score_risque_depart,
            ROUND(p.probabilite_depart::numeric, 4) AS probabilite_depart,
            p.interpretation,
            p.created_at
        FROM employees e
        JOIN predictions p ON p.employee_id = e.id
        WHERE p.prediction = 1
        ORDER BY p.probabilite_depart DESC
        LIMIT 50
    """,

    "erreurs": """
        SELECT
            l.id,
            l.employee_id,
            l.status,
            l.model_version,
            l.created_at
        FROM prediction_logs l
        WHERE l.status = 'error'
        ORDER BY l.created_at DESC
    """,
}

# =============================================================
# FONCTIONS
# =============================================================

def afficher_summary():
    with engine.connect() as conn:
        row = conn.execute(text(QUERIES["summary"])).fetchone()
    print("\n========== RÉSUMÉ GÉNÉRAL ==========")
    print(f"  Employés enregistrés     : {row.total_employes}")
    print(f"  Prédictions totales      : {row.total_predictions}")
    print(f"  Départs prédits (pred=1) : {row.departs_predits}")
    print(f"  Logs totaux              : {row.total_logs}")
    print(f"  Erreurs loggées          : {row.total_erreurs}")
    print(f"  Temps inférence moyen    : {row.inference_moy_ms} ms")
    print("=====================================\n")


def afficher_table(nom):
    if nom not in QUERIES:
        print(f"[ERREUR] Table inconnue : {nom}")
        print(f"         Choix disponibles : {', '.join(QUERIES.keys())}")
        sys.exit(1)
    with engine.connect() as conn:
        df = pd.read_sql(text(QUERIES[nom]), conn)
    if df.empty:
        print(f"[INFO] Aucune donnée dans '{nom}'")
        return df
    print(f"\n========== {nom.upper()} ({len(df)} lignes) ==========")
    print(df.to_string(index=False))
    print()
    return df


def exporter(nom, df):
    os.makedirs("exports", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"exports/{nom}_{ts}.csv"
    df.to_csv(path, index=False)
    print(f"[EXPORT] {path}")


# =============================================================
# MAIN
# =============================================================

def main():
    parser = argparse.ArgumentParser(description="Consultation des logs Attrition RH")
    parser.add_argument(
        "--table",
        choices=list(QUERIES.keys()),
        help="Table à afficher : summary, predictions, logs, risque, erreurs"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Exporter le résultat en CSV dans exports/"
    )
    args = parser.parse_args()

    if not args.table:
        afficher_summary()
        return

    df = afficher_table(args.table)
    if args.export and not df.empty:
        exporter(args.table, df)


if __name__ == "__main__":
    main()