CREATE TABLE IF NOT EXISTS employees_dataset (
    id SERIAL PRIMARY KEY,
    age FLOAT NOT NULL,
    revenu_mensuel FLOAT NOT NULL,
    nombre_experiences_precedentes FLOAT NOT NULL,
    nombre_heures_travailless FLOAT NOT NULL,
    annees_dans_l_entreprise FLOAT NOT NULL,
    nombre_participation_pee FLOAT NOT NULL,
    nb_formations_suivies FLOAT NOT NULL,
    nombre_employee_sous_responsabilite FLOAT NOT NULL,
    distance_domicile_travail FLOAT NOT NULL,
    niveau_education FLOAT NOT NULL,
    frequence_deplacement FLOAT NOT NULL,
    annees_depuis_la_derniere_promotion FLOAT NOT NULL,
    satisfaction_employee_environnement FLOAT NOT NULL,
    note_evaluation_precedente FLOAT NOT NULL,
    niveau_hierarchique_poste FLOAT NOT NULL,
    satisfaction_employee_nature_travail FLOAT NOT NULL,
    satisfaction_employee_equipe FLOAT NOT NULL,
    satisfaction_employee_equilibre_pro_perso FLOAT NOT NULL,
    note_evaluation_actuelle FLOAT NOT NULL,
    heure_supplementaires FLOAT NOT NULL,
    augementation_salaire_precedente FLOAT NOT NULL,
    genre_M FLOAT NOT NULL,
    statut_marital_Divorce_e FLOAT NOT NULL,
    statut_marital_Marie_e FLOAT NOT NULL,
    departement_Consulting FLOAT NOT NULL,
    departement_Ressources_Humaines FLOAT NOT NULL,
    poste_Cadre_Commercial FLOAT NOT NULL,
    poste_Consultant FLOAT NOT NULL,
    poste_Directeur_Technique FLOAT NOT NULL,
    poste_Manager FLOAT NOT NULL,
    poste_Representant_Commercial FLOAT NOT NULL,
    poste_Ressources_Humaines FLOAT NOT NULL,
    poste_Senior_Manager FLOAT NOT NULL,
    poste_Tech_Lead FLOAT NOT NULL,
    domaine_etude_Entrepreunariat FLOAT NOT NULL,
    domaine_etude_Infra_Cloud FLOAT NOT NULL,
    domaine_etude_Marketing FLOAT NOT NULL,
    domaine_etude_Ressources_Humaines FLOAT NOT NULL,
    domaine_etude_Transformation_Digitale FLOAT NOT NULL,
    revenu_par_niveau FLOAT NOT NULL,
    score_satisfaction_global FLOAT NOT NULL,
    evolution_performance FLOAT NOT NULL,
    charge_travail FLOAT NOT NULL,
    ratio_stagnation FLOAT NOT NULL,
    ratio_experience_interne FLOAT NOT NULL,
    score_risque_depart FLOAT NOT NULL,
    engagement_formation FLOAT NOT NULL,
    inserted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    age FLOAT, revenu_mensuel FLOAT, nombre_experiences_precedentes FLOAT,
    nombre_heures_travailless FLOAT, annees_dans_l_entreprise FLOAT,
    nombre_participation_pee FLOAT, nb_formations_suivies FLOAT,
    nombre_employee_sous_responsabilite FLOAT, distance_domicile_travail FLOAT,
    niveau_education FLOAT, frequence_deplacement FLOAT,
    annees_depuis_la_derniere_promotion FLOAT,
    satisfaction_employee_environnement FLOAT, note_evaluation_precedente FLOAT,
    niveau_hierarchique_poste FLOAT, satisfaction_employee_nature_travail FLOAT,
    satisfaction_employee_equipe FLOAT, satisfaction_employee_equilibre_pro_perso FLOAT,
    note_evaluation_actuelle FLOAT, heure_supplementaires FLOAT,
    augementation_salaire_precedente FLOAT, genre_M FLOAT,
    statut_marital_Divorce_e FLOAT, statut_marital_Marie_e FLOAT,
    departement_Consulting FLOAT, departement_Ressources_Humaines FLOAT,
    poste_Cadre_Commercial FLOAT, poste_Consultant FLOAT,
    poste_Directeur_Technique FLOAT, poste_Manager FLOAT,
    poste_Representant_Commercial FLOAT, poste_Ressources_Humaines FLOAT,
    poste_Senior_Manager FLOAT, poste_Tech_Lead FLOAT,
    domaine_etude_Entrepreunariat FLOAT, domaine_etude_Infra_Cloud FLOAT,
    domaine_etude_Marketing FLOAT, domaine_etude_Ressources_Humaines FLOAT,
    domaine_etude_Transformation_Digitale FLOAT, revenu_par_niveau FLOAT,
    score_satisfaction_global FLOAT, evolution_performance FLOAT,
    charge_travail FLOAT, ratio_stagnation FLOAT, ratio_experience_interne FLOAT,
    score_risque_depart FLOAT, engagement_formation FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    probabilite_depart FLOAT NOT NULL,
    prediction INTEGER NOT NULL,
    interpretation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prediction_logs (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    inference_time_ms FLOAT NOT NULL,
    api_response_time_ms FLOAT NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    status VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================
-- INDEX
-- Justification : ces colonnes sont les plus interrogées
-- pour le monitoring, le reporting RH et les analyses BI.
-- =============================================================

-- employees : filtrage par date de création (monitoring volumétrie)
CREATE INDEX IF NOT EXISTS idx_employees_created_at
    ON employees(created_at);

-- employees : filtrage par score de risque (profil employés à risque)
CREATE INDEX IF NOT EXISTS idx_employees_score_risque
    ON employees(score_risque_depart);

-- predictions : jointure avec employees (requête la plus fréquente)
CREATE INDEX IF NOT EXISTS idx_predictions_employee_id
    ON predictions(employee_id);

-- predictions : filtrage par résultat (ratio départs prédits / total)
CREATE INDEX IF NOT EXISTS idx_predictions_prediction
    ON predictions(prediction);

-- predictions : filtrage par date (suivi temporel des prédictions)
CREATE INDEX IF NOT EXISTS idx_predictions_created_at
    ON predictions(created_at);

-- prediction_logs : filtrage par statut success/error (monitoring erreurs)
CREATE INDEX IF NOT EXISTS idx_logs_status
    ON prediction_logs(status);

-- prediction_logs : filtrage par date (suivi temps d'inférence dans le temps)
CREATE INDEX IF NOT EXISTS idx_logs_created_at
    ON prediction_logs(created_at);

-- prediction_logs : jointure avec employees pour analyses croisées
CREATE INDEX IF NOT EXISTS idx_logs_employee_id
    ON prediction_logs(employee_id);

-- employees_dataset : filtrage par score de risque (analyses exploratoires)
CREATE INDEX IF NOT EXISTS idx_dataset_score_risque
    ON employees_dataset(score_risque_depart);