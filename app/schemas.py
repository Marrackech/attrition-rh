from pydantic import BaseModel
from typing import Optional

class EmployeeInput(BaseModel):
    age: Optional[float] = 0
    revenu_mensuel: Optional[float] = 0
    nombre_experiences_precedentes: Optional[float] = 0
    nombre_heures_travailless: Optional[float] = 0
    annees_dans_l_entreprise: Optional[float] = 0
    nombre_participation_pee: Optional[float] = 0
    nb_formations_suivies: Optional[float] = 0
    nombre_employee_sous_responsabilite: Optional[float] = 0
    distance_domicile_travail: Optional[float] = 0
    niveau_education: Optional[float] = 0
    frequence_deplacement: Optional[float] = 0
    annees_depuis_la_derniere_promotion: Optional[float] = 0
    satisfaction_employee_environnement: Optional[float] = 0
    note_evaluation_precedente: Optional[float] = 0
    niveau_hierarchique_poste: Optional[float] = 0
    satisfaction_employee_nature_travail: Optional[float] = 0
    satisfaction_employee_equipe: Optional[float] = 0
    satisfaction_employee_equilibre_pro_perso: Optional[float] = 0
    note_evaluation_actuelle: Optional[float] = 0
    heure_supplementaires: Optional[float] = 0
    augementation_salaire_precedente: Optional[float] = 0
    genre_M: Optional[float] = 0
    statut_marital_Divorce_e: Optional[float] = 0
    statut_marital_Marie_e: Optional[float] = 0
    departement_Consulting: Optional[float] = 0
    departement_Ressources_Humaines: Optional[float] = 0
    poste_Cadre_Commercial: Optional[float] = 0
    poste_Consultant: Optional[float] = 0
    poste_Directeur_Technique: Optional[float] = 0
    poste_Manager: Optional[float] = 0
    poste_Representant_Commercial: Optional[float] = 0
    poste_Ressources_Humaines: Optional[float] = 0
    poste_Senior_Manager: Optional[float] = 0
    poste_Tech_Lead: Optional[float] = 0
    domaine_etude_Entrepreunariat: Optional[float] = 0
    domaine_etude_Infra_Cloud: Optional[float] = 0
    domaine_etude_Marketing: Optional[float] = 0
    domaine_etude_Ressources_Humaines: Optional[float] = 0
    domaine_etude_Transformation_Digitale: Optional[float] = 0
    revenu_par_niveau: Optional[float] = 0
    score_satisfaction_global: Optional[float] = 0
    evolution_performance: Optional[float] = 0
    charge_travail: Optional[float] = 0
    ratio_stagnation: Optional[float] = 0
    ratio_experience_interne: Optional[float] = 0
    score_risque_depart: Optional[float] = 0
    engagement_formation: Optional[float] = 0

class PredictionOutput(BaseModel):
    probabilite_depart: float
    prediction: int
    seuil_utilise: float
    interpretation: str