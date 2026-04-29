# GitHub Secrets — Quoi creer et QUAND

================================================
CE FICHIER EST UNE LISTE DE RAPPEL UNIQUEMENT
NE RIEN CREER MAINTENANT
Chaque secret sera cree au bon moment
================================================

## SECRETS A CREER A L ETAPE 2 (Docker Compose)
Ces secrets seront necessaires quand tu ecriras
le fichier docker-compose.yml

[ ] AIRFLOW_DB_USER
    Pourquoi : PostgreSQL a besoin d un nom utilisateur
                pour creer la base de donnees Airflow
    Valeur fixe : airflow
    Action : creer sur GitHub quand tu fais docker-compose.yml

[ ] AIRFLOW_DB_PASSWORD
    Pourquoi : PostgreSQL a besoin d un mot de passe
                pour securiser la base Airflow
    Comment generer : openssl rand -base64 32
    Action : creer sur GitHub quand tu fais docker-compose.yml

[ ] AIRFLOW_FERNET_KEY
    Pourquoi : Airflow chiffre ses connexions avec cette cle
                sans elle Airflow refuse de demarrer
    Comment generer : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    Action : creer sur GitHub quand tu fais docker-compose.yml

## SECRETS A CREER A L ETAPE 3 (Terraform + GCP)
Ces secrets seront disponibles seulement apres
avoir execute terraform apply

[ ] GCP_PROJECT_ID
    Pourquoi : toutes les commandes gcloud ont besoin
                de savoir dans quel projet GCP travailler
    Comment : Google Cloud Console → page accueil → Project ID
    Action : creer apres avoir cree le projet sur GCP

[ ] GCP_SA_KEY
    Pourquoi : GitHub Actions s authentifie sur GCP
                avec cette cle pour deployer
    Comment : base64 -w 0 secrets/sa-key.json
    Action : creer apres avoir cree le service account GCP

[ ] GCP_REGION
    Pourquoi : Terraform sait ou creer les ressources GCP
    Valeur : europe-west1
    Action : creer quand tu commences Terraform

[ ] COMPOSER_BUCKET
    Pourquoi : CI/CD copie les DAGs Airflow dans ce bucket
    Comment : terraform output composer_bucket
    Action : creer apres terraform apply

[ ] ARTIFACT_REGISTRY_URL
    Pourquoi : Docker images stockees ici
                Kubernetes les recupere ici pour deployer
    Comment : terraform output artifact_registry_url
    Action : creer apres terraform apply

[ ] GKE_CLUSTER_NAME
    Pourquoi : kubectl se connecte au cluster avec ce nom
    Comment : terraform output gke_cluster_name
    Action : creer apres terraform apply

[ ] BIGTABLE_INSTANCE_ID
    Pourquoi : scrapers et DAGs savent ou stocker les prix
    Comment : terraform output bigtable_instance_id
    Action : creer apres terraform apply

## SECRETS A CREER A L ETAPE 6 (Monitoring)
Ces secrets seront necessaires quand tu configureras
Prometheus et Grafana

[ ] SLACK_WEBHOOK_URL
    Pourquoi : Prometheus envoie des alertes sur Slack
                quand un pipeline tombe en panne
    Comment : api.slack.com/apps → Incoming Webhooks
    Action : creer quand tu configures le monitoring

================================================
STATUT ACTUEL DU PROJET
================================================

[X] Etape 1A — Structure GitHub              FAIT
[X] Etape 1B — Ce fichier todo               FAIT
[X] Etape 1C — Strategie de branches         FAIT
[X] Etape 1D — Branch Protection             FAIT
[X] Etape 1E — Conventions de commits        FAIT
[ ] Etape 2  — Docker Compose                A FAIRE
[ ] Etape 3  — Terraform GCP                 A FAIRE
[ ] Etape 3B — GitHub Secrets partie GCP     A FAIRE
[ ] Etape 4  — CI/CD GitHub Actions          A FAIRE
[ ] Etape 5  — Kubernetes                    A FAIRE
[ ] Etape 6  — Monitoring                    A FAIRE
[ ] Etape 7  — Great Expectations            A FAIRE
[ ] Etape 8  — Tests et Demo                 A FAIRE
