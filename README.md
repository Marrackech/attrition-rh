---
title: Attrition RH API
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🏢 Prédiction d'Attrition RH

API Machine Learning pour prédire si un employé va quitter l'entreprise.

## 🚀 API en production

🔗 [https://usermarrakech-attrition-rh-api.hf.space/docs](https://usermarrakech-attrition-rh-api.hf.space/docs)

## 🎯 Résultats du modèle

| Métrique | Score |
|---|---|
| Modèle | Logistic Regression |
| Recall | 70% |
| F1-Score | 0.52 |
| Couverture tests | 98% |

## ⚙️ Installation locale

```bash
git clone https://github.com/Marrackech/attrition-rh.git
cd attrition-rh
conda create -n attrition-api python=3.10
conda activate attrition-api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## 🧪 Tests

```bash
pytest tests/ -v --cov=app
```

## 🛠️ Stack

FastAPI · scikit-learn · PostgreSQL NEON · Docker · GitHub Actions · Hugging Face

## 👤 Auteur

Haroun Tanane 