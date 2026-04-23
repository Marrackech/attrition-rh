CREATE TABLE IF NOT EXISTS employees_dataset (
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
    augementation_salaire_precedente FLOAT,
    genre_m FLOAT,
    statut_marital_divorce_e FLOAT, statut_marital_marie_e FLOAT,
    departement_consulting FLOAT, departement_ressources_humaines FLOAT,
    poste_cadre_commercial FLOAT, poste_consultant FLOAT,
    poste_directeur_technique FLOAT, poste_manager FLOAT,
    poste_representant_commercial FLOAT, poste_ressources_humaines FLOAT,
    poste_senior_manager FLOAT, poste_tech_lead FLOAT,
    domaine_etude_entrepreunariat FLOAT, domaine_etude_infra_cloud FLOAT,
    domaine_etude_marketing FLOAT, domaine_etude_ressources_humaines FLOAT,
    domaine_etude_transformation_digitale FLOAT,
    revenu_par_niveau FLOAT, score_satisfaction_global FLOAT,
    evolution_performance FLOAT, charge_travail FLOAT,
    ratio_stagnation FLOAT, ratio_experience_interne FLOAT,
    score_risque_depart FLOAT, engagement_formation FLOAT,
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
    augementation_salaire_precedente FLOAT, genre_m FLOAT,
    statut_marital_divorce_e FLOAT, statut_marital_marie_e FLOAT,
    departement_consulting FLOAT, departement_ressources_humaines FLOAT,
    poste_cadre_commercial FLOAT, poste_consultant FLOAT,
    poste_directeur_technique FLOAT, poste_manager FLOAT,
    poste_representant_commercial FLOAT, poste_ressources_humaines FLOAT,
    poste_senior_manager FLOAT, poste_tech_lead FLOAT,
    domaine_etude_entrepreunariat FLOAT, domaine_etude_infra_cloud FLOAT,
    domaine_etude_marketing FLOAT, domaine_etude_ressources_humaines FLOAT,
    domaine_etude_transformation_digitale FLOAT,
    revenu_par_niveau FLOAT, score_satisfaction_global FLOAT,
    evolution_performance FLOAT, charge_travail FLOAT,
    ratio_stagnation FLOAT, ratio_experience_interne FLOAT,
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