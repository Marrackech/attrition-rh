---
title: Attrition RH API
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🏢 Prédiction d'Attrition RH

API Machine Learning permettant de prédire si un employé risque de quitter l'entreprise.

---

## 🚀 Démo

🔗 https://usermarrakech-attrition-rh-api.hf.space/docs

---

## 🎯 Objectif

- Prédire le risque de départ des employés
- Aider les RH à anticiper le turnover
- Déployer un pipeline MLOps complet (ML + API + BDD + CI/CD)

---

## 🧠 Modèle Machine Learning

| Élément | Valeur |
|---|---|
| Algorithme | Logistic Regression |
| Features | 10 variables sélectionnées |
| F1-Score | 0.52 |
| Recall | 0.70 |

---

## 📊 Architecture globale


Utilisateur → FastAPI → Modèle ML → PostgreSQL (NEON) → Réponse JSON


---

## 🗄️ Base de données

### Table `predictions`

| Champ | Type |
|---|---|
| id | Integer (PK) |
| age | Integer |
| revenu_mensuel | Float |
| probabilite_depart | Float |
| prediction | Integer |
| created_at | Timestamp |

### Flux de données

1. Requête utilisateur via API
2. Prétraitement des données
3. Prédiction du modèle ML
4. Stockage dans PostgreSQL (NEON)
5. Retour JSON

---

## ⚙️ Installation locale

```bash
git clone https://github.com/Marrackech/attrition-rh.git
cd attrition-rh

conda create -n attrition-api python=3.10
conda activate attrition-api

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8001


🐳 Docker
Build image
docker build -t attrition-api .
Run container
docker run -p 8001:8001 attrition-api


🧪 Tests
pytest tests/ -v --cov=app



🔐 Variables d'environnement

Créer un fichier .env à la racine :

DATABASE_URL=postgresql://user:password@host:port/db
HF_TOKEN=your_huggingface_token
Variable	Description
DATABASE_URL	Connexion PostgreSQL (NEON)
HF_TOKEN	Token Hugging Face


🚀 Déploiement
GitHub Actions (CI/CD)
Build Docker automatique
Déploiement sur Hugging Face Spaces


🔒 Sécurité
Variables sensibles dans .env
.env ignoré via .gitignore
Aucun secret dans le code source


🛠️ Stack technique
FastAPI
Scikit-learn
PostgreSQL (NEON)
Docker
GitHub Actions
Hugging Face Spaces

📈 Améliorations futures
Authentification JWT
Dashboard RH (Power BI / Streamlit)
Amélioration modèle ML (XGBoost)
Monitoring des prédictions


👤 Auteur

Haroun Tanane