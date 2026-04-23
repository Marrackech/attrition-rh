---
title: Attrition RH
emoji: 👥
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---



# Attrition RH — API de prédiction de départ des employés

API machine learning qui prédit si un employé risque de quitter l'entreprise.
Déployée en production sur Hugging Face Spaces : https://usermarrakech-attrition-rh-api.hf.space/docs

---

## Pourquoi ce projet

Le turnover en entreprise est coûteux et difficile à anticiper. Cette API permet aux équipes RH
d'identifier en amont les employés à risque de départ, afin d'agir avant qu'il ne soit trop tard.

Stack technique : FastAPI · Scikit-learn · PostgreSQL NEON · SQLAlchemy · Docker · GitHub Actions · Hugging Face

---

## Le modèle machine learning

| Élément | Détail |
|---|---|
| Algorithme | Logistic Regression (Scikit-learn) |
| Dataset | IBM HR Analytics — 1470 employés |
| Variables utilisées | 10 features sur 47 |
| Seuil de décision | 0.283 |
| F1-Score | 0.52 |
| Recall | 0.70 |

**Justification des choix techniques :**

- **Régression logistique** : choisie pour son interprétabilité dans un contexte RH. Un décideur doit pouvoir expliquer pourquoi un employé est signalé à risque.
- **Seuil 0.283** : volontairement bas pour maximiser le recall. Dans un contexte RH, il vaut mieux signaler un faux positif (employé qui ne part pas) que de rater un vrai départ.
- **10 features sur 47** : sélection par importance des coefficients. Les 37 variables restantes n'apportaient pas de signal significatif.
- **NEON PostgreSQL** : base serverless compatible avec Hugging Face Spaces, sans coût fixe pour un projet de démonstration.

---

## Authentification

L'API est protégée par une clé API (header `X-API-Key`).

Tous les appels à `/predict` nécessitent ce header :

```bash
curl -X POST "https://usermarrakech-attrition-rh-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre-cle-api" \
  -d '{"age": 28, "revenu_mensuel": 3500, "score_risque_depart": 1.2}'
```

Sans clé valide, l'API retourne `401 Unauthorized`.

En local, la clé par défaut est `dev-secret-key` (définie dans `.env`).
En production, la clé est injectée via les secrets GitHub Actions (`API_KEY`).

---

## Variables d'environnement

Créer un fichier `.env` à la racine avant de lancer l'API :

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
DATABASE_URL_DEV=postgresql://user:password@host:port/dbname_dev
API_KEY=votre-cle-api-secrete
ENV=development
```

| Variable | Description | Obligatoire |
|---|---|---|
| `DATABASE_URL` | URL PostgreSQL NEON (production) | Oui |
| `DATABASE_URL_DEV` | URL PostgreSQL pour le développement | Non |
| `API_KEY` | Clé d'authentification de l'API | Oui |
| `ENV` | Environnement (`development` ou `production`) | Non (défaut: development) |

**Bonnes pratiques de sécurité :**

- Le fichier `.env` est dans `.gitignore` et ne doit jamais être commité
- Ne jamais écrire de credentials en dur dans le code
- En production, toutes les variables sont injectées via les secrets GitHub Actions
- Un fichier `.env.example` est disponible à la racine comme modèle

---

## Base de données

La base PostgreSQL hébergée sur NEON contient 4 tables :

### Schéma et relations

```
employees_dataset (1470 lignes — dataset IBM HR Analytics)
    └── id (PK)
    └── 47 features (age, revenu_mensuel, score_risque_depart, ...)
    └── inserted_at

employees (données envoyées via POST /predict)
    └── id (PK)
    └── 47 features de l'employé
    └── created_at

predictions
    └── id (PK)
    └── employee_id (FK → employees.id)
    └── probabilite_depart (FLOAT, entre 0 et 1)
    └── prediction (INTEGER, 0 ou 1)
    └── interpretation (TEXT)
    └── created_at

prediction_logs
    └── id (PK)
    └── employee_id
    └── inference_time_ms
    └── api_response_time_ms
    └── model_version
    └── status (success / error)
    └── created_at
```

### Flux de données

1. L'utilisateur envoie les données via `POST /predict` avec le header `X-API-Key`
2. FastAPI valide les données via Pydantic
3. Le modèle ML calcule la probabilité de départ
4. Les données sont insérées dans `employees`
5. Le résultat est inséré dans `predictions` avec la clé étrangère `employee_id`
6. Le log de performance est inséré dans `prediction_logs`
7. L'API retourne le résultat en JSON

### Initialisation de la base

```bash
python create_db.py
```

Ce script crée les 4 tables et insère les 1470 lignes du dataset IBM HR Analytics dans `employees_dataset`.

---

## Besoins analytiques

Les données collectées à chaque prédiction permettent plusieurs analyses :

- **Monitoring du modèle** : suivi du temps d'inférence via `prediction_logs.inference_time_ms`
- **Distribution des prédictions** : ratio départs prédits / total via `predictions.prediction`
- **Profil des employés à risque** : croisement `employees` x `predictions` pour identifier les patterns
- **Tableau de bord RH** : les tables sont prêtes à être connectées à un outil BI (Metabase, Grafana, Power BI) via la connexion PostgreSQL NEON

---

## Installation locale

```bash
# Cloner le projet
git clone https://github.com/Marrackech/attrition-rh.git
cd attrition-rh

# Créer l'environnement Python
conda create -n attrition-api python=3.10
conda activate attrition-api

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Renseigner les valeurs dans .env

# Initialiser la base de données (crée les tables + insère 1470 lignes)
python create_db.py

# Lancer l'API
uvicorn app.main:app --reload --port 8000
```

L'API est accessible sur http://127.0.0.1:8000/docs (Swagger UI).

---

## Docker

```bash
# Construire l'image
docker build -t attrition-api .

# Lancer le conteneur
docker run -p 8000:8000 --env-file .env attrition-api
```

---

## Tests

```bash
# Lancer tous les tests avec rapport de couverture
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Résultats actuels

```
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py       0      0   100%
app/database.py     102      1    99%   94
app/main.py          42      1    98%   34
app/model.py         23      0   100%
app/schemas.py       55      0   100%
-----------------------------------------------
TOTAL               222      2    99%

37 passed in 5.80s
```

### Couverture de code — 99%

La suite de tests atteint **99% de couverture** sur l'ensemble du code applicatif (222 instructions, 2 manquantes). Seules 2 lignes ne sont pas couvertes : une dans `database.py` (ligne 94, branche de reconnexion rare) et une dans `main.py` (ligne 34, branche de démarrage en environnement de test).

Ce niveau de couverture a été obtenu progressivement en ciblant chaque branche de code non testée, notamment :

- **Le fallback d'erreur dans `/predict`** : le bloc `except` de l'endpoint appelle `save_prediction` pour logger l'échec même quand le modèle plante. Un test dédié (`test_predict_erreur_save_prediction_fallback`) vérifie que cet appel a bien lieu et que l'exception interne est silencieusement absorbée — permettant à l'API de retourner un `500` propre sans lever une seconde erreur.
- **Le rollback de base de données** : `test_save_prediction_rollback_sur_erreur` vérifie que la session SQLAlchemy effectue bien un rollback si une insertion échoue à mi-chemin, garantissant l'intégrité des données.
- **L'initialisation de la base selon l'environnement** : `test_init_db_production` et `test_init_db_sans_database_url` couvrent les deux branches de `init_db()` — avec et sans `DATABASE_URL` définie.

### Ce que les tests couvrent

Les 37 tests se répartissent en deux fichiers :

**`tests/test_api.py` — 23 tests**

- Endpoints GET (`/`, `/health`, `/debug-env`)
- Authentification : appel valide, sans clé, avec mauvaise clé → `401`
- Prédiction : succès, erreur modèle → `500`, fallback de sauvegarde en cas d'erreur
- Insertions réelles en base SQLite en mémoire (`Employee`, `Prediction`, `PredictionLog`)
- Persistance des données après insertion
- Suppression en cascade (employee → prediction)
- Rollback sur erreur de base de données
- Initialisation de la base (`init_db`) en mode production et sans URL

**`tests/test_model.py` — 14 tests**

- Type de retour (`PredictionOutput`)
- Contraintes sur les valeurs : probabilité entre 0 et 1, prédiction vaut 0 ou 1
- Cohérence seuil / prédiction : si `probabilite >= 0.283` alors `prediction == 1`
- Cohérence interprétation : risque élevé vs risque faible
- Robustesse : tous les champs à zéro, valeurs extrêmes positives et négatives
- Répétabilité : même entrée → même sortie

### Philosophie de test

- **Base isolée** : tous les tests utilisent une base SQLite en mémoire (via `conftest.py`), sans jamais toucher la base de production.
- **Mocks ciblés** : les tests qui simulent des erreurs utilisent `unittest.mock.patch` pour intercepter uniquement les fonctions concernées, sans modifier le code applicatif.
- **Pas de faux positifs** : chaque assertion teste un comportement précis (code HTTP, valeur retournée, nombre d'appels à une fonction) plutôt qu'une simple absence d'exception.

---

## Déploiement CI/CD

Le pipeline GitHub Actions se déclenche à chaque push sur `main` :

1. Installation des dépendances Python
2. Exécution des 37 tests pytest
3. Build de l'image Docker
4. Déploiement automatique sur Hugging Face Spaces via `HF_TOKEN`

Secrets configurés dans GitHub (Settings > Secrets and variables > Actions) :

| Secret | Description |
|---|---|
| `DATABASE_URL` | URL PostgreSQL NEON production |
| `HF_TOKEN` | Token Hugging Face pour le déploiement |
| `API_KEY` | Clé d'authentification de l'API |

---

## Gestion des environnements

| Environnement | Variable ENV | Base de données utilisée |
|---|---|---|
| Développement | `development` | `DATABASE_URL_DEV` |
| Production | `production` | `DATABASE_URL` |

---

## Structure du projet

```
attrition-rh/
├── app/
│   ├── __init__.py
│   ├── main.py        # Endpoints FastAPI + authentification API Key
│   ├── model.py       # Chargement et prédiction ML
│   ├── schemas.py     # Validation Pydantic
│   └── database.py    # Modèles SQLAlchemy et sauvegarde
├── models/
│   ├── best_lr.pkl
│   ├── scaler.pkl
│   └── colonnes.json
├── data/
│   └── employees_full.csv
├── tests/
│   ├── conftest.py    # Fixture SQLite en mémoire
│   ├── test_api.py    # Tests endpoints et base de données (23 tests)
│   └── test_model.py  # Tests modèle ML (14 tests)
├── .github/
│   └── workflows/
│       └── ci.yml
├── create_db.py       # Script init BDD + insertion dataset
├── schema.sql         # Schéma SQL complet avec contraintes
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Auteur

Haroun Tanane
