# GitHub Secrets — Liste complete du projet

==============================================
PARTIE 1 : SECRETS A CREER MAINTENANT
(ne dependent pas de GCP)
==============================================

[ ] AIRFLOW_DB_USER
    Valeur fixe : airflow
    
[ ] AIRFLOW_DB_PASSWORD
    Generer avec : openssl rand -base64 32
    
[ ] AIRFLOW_FERNET_KEY
    Generer avec : python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    
[ ] SLACK_WEBHOOK_URL
    Obtenir sur : api.slack.com/apps → Incoming Webhooks

==============================================
PARTIE 2 : SECRETS A CREER APRES TERRAFORM
(etape 3 — ne pas faire maintenant)
==============================================

[ ] GCP_PROJECT_ID
    Comment : Google Cloud Console → page accueil → Project ID

[ ] GCP_SA_KEY
    Comment : base64 -w 0 secrets/sa-key.json apres creation service account

[ ] GCP_REGION
    Valeur : europe-west1

[ ] COMPOSER_BUCKET
    Comment : terraform output composer_bucket

[ ] ARTIFACT_REGISTRY_URL
    Comment : terraform output artifact_registry_url

[ ] GKE_CLUSTER_NAME
    Comment : terraform output gke_cluster_name

[ ] BIGTABLE_INSTANCE_ID
    Comment : terraform output bigtable_instance_id

==============================================
STATUT DES TACHES SECTION A
==============================================

[X] Initialiser le depot GitHub        FAIT
[X] Strategie de branches              FAIT
[X] Branch Protection                  FAIT
[ ] Conventions de commits             A FAIRE
[ ] GitHub Secrets partie 1            A FAIRE
[ ] GitHub Secrets partie 2            APRES TERRAFORM
