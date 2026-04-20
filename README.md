---
title: Attrition RH API
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Attrition RH — API de prédiction de départ des employés

Ce projet est une API machine learning qui prédit si un employé risque de quitter l'entreprise.
L'idée est simple : on envoie les informations d'un employé, et le modèle répond avec une probabilité de départ et une interprétation claire.

Le projet est déployé en production sur Hugging Face Spaces et accessible publiquement ici :
https://usermarrakech-attrition-rh-api.hf.space/docs

---

## Pourquoi ce projet

Le turnover en entreprise est coûteux et difficile à anticiper. Ce projet aide les équipes RH à identifier
en amont les employés qui présentent un risque de départ, afin de pouvoir agir avant qu'il ne soit trop tard.

Côté technique, c'est un projet MLOps complet qui couvre toute la chaîne : entraînement du modèle,
exposition via une API REST, stockage des données en base PostgreSQL, tests automatisés, Docker,
et déploiement continu via GitHub Actions.

---

## Comment ça marche

On envoie une requête à l'API avec les données d'un employé (âge, salaire, ancienneté, satisfaction, etc.),
et l'API retourne une probabilité de départ entre 0 et 1, ainsi qu'une interprétation en français.

Exemple de requête :

```bash
curl -X POST "https://usermarrakech-attrition-rh-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "revenu_mensuel": 3500,
    "annees_dans_l_entreprise": 2,
    "heures_supplementaires": 5,
    "satisfaction_employee_nature_travail": 2.0,
    "niveau_hierarchique_poste": 1,
    "nombre_participation_pee": 0,
    "score_risque_depart": 1.2,
    "ratio_stagnation": 0.8,
    "ratio_experience_interne": 0.3
  }'
```

Réponse :

```json
{
  "probabilite_depart": 0.87,
  "prediction": 1,
  "interpretation": "Risque élevé de départ",
  "seuil_utilise": 0.283,
  "model_version": "v1.0"
}
```

---

## Le modèle machine learning

Le modèle est une régression logistique entraînée sur le dataset IBM HR Analytics qui contient
1470 employés réels. Sur les 47 variables disponibles, on en a retenu 10 après sélection de features.

| Élément            | Détail                                      |
|--------------------|---------------------------------------------|
| Algorithme         | Logistic Regression (Scikit-learn)          |
| Dataset            | IBM HR Analytics — 1470 employés            |
| Variables utilisées | 10 features sur 47                         |
| Seuil de décision  | 0.283                                       |
| F1-Score           | 0.52                                        |
| Recall             | 0.70                                        |

Le seuil de 0.283 a été choisi volontairement bas pour maximiser le recall. Dans un contexte RH,
il vaut mieux avoir quelques faux positifs (signaler un employé qui ne part pas) que de rater
un vrai départ. C'est un choix métier, pas une erreur.

Les 10 variables retenues sont : l'âge, le revenu mensuel, l'ancienneté dans l'entreprise,
les heures supplémentaires, la satisfaction au travail, le niveau hiérarchique du poste,
la participation au PEE, le score de risque de départ, le ratio de stagnation et le ratio
d'expérience interne.

---

## Base de données

Chaque prédiction est enregistrée dans une base PostgreSQL hébergée sur NEON.
La base contient 3 tables reliées entre elles.

### employees

Stocke les données brutes de l'employé envoyées dans la requête.

| Colonne                              | Type      |
|--------------------------------------|-----------|
| id                                   | Integer (PK) |
| age                                  | Integer   |
| revenu_mensuel                       | Float     |
| annees_dans_l_entreprise             | Integer   |
| heures_supplementaires               | Integer   |
| satisfaction_employee_nature_travail | Float     |
| niveau_hierarchique_poste            | Integer   |
| nombre_participation_pee             | Integer   |
| score_risque_depart                  | Float     |
| ratio_stagnation                     | Float     |
| ratio_experience_interne             | Float     |
| created_at                           | Timestamp |

### predictions

Stocke le résultat de la prédiction, lié à l'employé via employee_id.

| Colonne             | Type         |
|---------------------|--------------|
| id                  | Integer (PK) |
| employee_id         | Integer (FK → employees.id) |
| probabilite_depart  | Float        |
| prediction          | Integer (0 ou 1) |
| interpretation      | String       |
| created_at          | Timestamp    |

### prediction_logs

Stocke les informations de monitoring : temps de réponse, version du modèle, statut.

| Colonne               | Type         |
|-----------------------|--------------|
| id                    | Integer (PK) |
| employee_id           | Integer      |
| inference_time_ms     | Float        |
| api_response_time_ms  | Float        |
| model_version         | String       |
| status                | String (success / error) |
| created_at            | Timestamp    |

### Ce qui se passe à chaque requête

1. L'utilisateur envoie les données via POST /predict
2. FastAPI valide les données (Pydantic vérifie les types et les contraintes)
3. Le modèle ML calcule la probabilité de départ
4. Les données employé sont insérées dans la table employees
5. Le résultat est inséré dans predictions avec la clé étrangère employee_id
6. Le log de performance est inséré dans prediction_logs
7. L'API retourne le résultat en JSON

---

## Variables d'environnement

Créer un fichier `.env` à la racine du projet avant de lancer l'API :

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
HF_TOKEN=your_huggingface_token
```

| Variable     | Description                                        |
|--------------|----------------------------------------------------|
| DATABASE_URL | URL de connexion à la base PostgreSQL NEON         |
| HF_TOKEN     | Token Hugging Face utilisé pour le déploiement CI/CD |

Ces variables ne doivent jamais être committées dans Git. Le fichier `.env` est listé dans `.gitignore`.
En production, elles sont injectées via les secrets GitHub Actions (Settings > Secrets and variables).

Un fichier `.env.example` est disponible à la racine comme modèle.

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

# Copier le fichier d'environnement et renseigner vos valeurs
cp .env.example .env

# Lancer l'API en local
uvicorn app.main:app --reload --port 8000
```

L'API est ensuite accessible sur http://127.0.0.1:8000/docs (Swagger UI).

---

## Docker

```bash
# Construire l'image
docker build -t attrition-api .

# Lancer le conteneur avec les variables d'environnement
docker run -p 8000:8000 --env-file .env attrition-api
```

---

## Tests

Les tests couvrent les endpoints API, le modèle ML et la base de données.
Pour les tests de base de données, on utilise SQLite en mémoire afin d'éviter
de toucher à la base de production pendant les tests.

```bash
# Lancer tous les tests avec le rapport de couverture
pytest tests/ -v --cov=app --cov-report=term-missing

# Générer un rapport HTML consultable dans le navigateur
pytest tests/ -v --cov=app --cov-report=html
# Puis ouvrir htmlcov/index.html
```

Résultats actuels :

```
Name              Stmts   Miss  Cover
-------------------------------------
app/__init__.py       0      0   100%
app/database.py      58      1    98%
app/main.py          31      1    97%
app/model.py         22      0   100%
app/schemas.py       17      0   100%
-------------------------------------
TOTAL               128      2    98%

10 passed in 5.08s
```

---

## Déploiement CI/CD

Le pipeline se déclenche automatiquement à chaque push sur la branche main.

Les étapes sont les suivantes :
1. Installation des dépendances Python
2. Exécution de tous les tests pytest
3. Build de l'image Docker
4. Déploiement automatique sur Hugging Face Spaces via HF_TOKEN

Les secrets DATABASE_URL et HF_TOKEN sont configurés dans GitHub (Settings > Secrets and variables > Actions)
et jamais écrits dans le code source.

---

## Sécurité

Les variables sensibles (URL de base de données, tokens) sont stockées dans `.env` en local
et dans les secrets GitHub Actions en production. Le fichier `.env` est dans `.gitignore`
et n'apparaît jamais dans l'historique Git.

Aucune credential n'est écrite en dur dans le code source.

---

## Structure du projet

```
attrition-rh/
├── app/
│   ├── __init__.py
│   ├── main.py          # Endpoints FastAPI
│   ├── model.py         # Chargement et prédiction ML
│   ├── schemas.py       # Validation des données (Pydantic)
│   └── database.py      # Modèles SQLAlchemy et sauvegarde
├── models/
│   ├── best_lr.pkl      # Modèle entraîné sérialisé
│   ├── scaler.pkl       # Scaler pour la normalisation
│   └── colonnes.json    # Ordre des features attendu
├── tests/
│   ├── conftest.py      # Fixture SQLite en mémoire
│   ├── test_api.py      # Tests endpoints et base de données
│   └── test_model.py    # Tests modèle ML
├── .github/
│   └── workflows/
│       └── ci.yml       # Pipeline CI/CD GitHub Actions
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Stack technique

| Composant       | Technologie                        |
|-----------------|------------------------------------|
| API             | FastAPI + Uvicorn                  |
| Modèle ML       | Scikit-learn (Logistic Regression) |
| Base de données | PostgreSQL sur NEON                |
| ORM             | SQLAlchemy                         |
| Validation      | Pydantic v2                        |
| Tests           | Pytest + pytest-cov                |
| Docker          | Image Python 3.10 slim             |
| CI/CD           | GitHub Actions                     |
| Hébergement     | Hugging Face Spaces                |

---

## Auteur

Haroun Tanane
