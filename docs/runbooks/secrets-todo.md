# GitHub Secrets — Quoi creer et QUAND

================================================
CE FICHIER EST UNE LISTE DE RAPPEL UNIQUEMENT
Rien a creer maintenant
================================================

## SECRETS A CREER A L'ETAPE 2 (Docker Compose)

[ ] AIRFLOW_DB_USER
    Pourquoi : docker-compose en a besoin pour demarrer PostgreSQL
    Valeur : airflow (valeur standard fixe)

[ ] AIRFLOW_DB_PASSWORD
    Pourquoi : docker-compose en a besoin pour securiser PostgreSQL
    Comment generer : openssl rand -base64 32

[ ] AIRFLOW_FERNET_KEY
    Pourquoi : Airflow en a besoin pour chiffrer ses connexions
    Comment generer : python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

## SECRETS A CREER A L'ETAPE 3 (Terraform)

[ ] GCP_PROJECT_ID
    Pourquoi : GitHub Actions doit savoir dans quel projet GCP travailler
    Comment : Google Cloud Console → page accueil → Project ID

[ ] GCP_SA_KEY
    Pourquoi : GitHub Actions doit s authentifier sur GCP
    Comment : base64 -w 0 secrets/sa-key.json apres creation service account

[ ] GCP_REGION
    Pourquoi : Terraform doit savoir ou creer les ressources
    Valeur : europe-west1

[ ] COMPOSER_BUCKET
    Pourquoi : CI/CD copie les DAGs Airflow dans ce bucket automatiquement
    Comment : terraform output composer_bucket

[ ] ARTIFACT_REGISTRY_URL
    Pourquoi : Docker images stockees ici, Kubernetes les recupere ici
    Comment : terraform output artifact_registry_url

[ ] GKE_CLUSTER_NAME
    Pourquoi : kubectl a besoin du nom du cluster pour deployer
    Comment : terraform output gke_cluster_name

[ ] BIGTABLE_INSTANCE_ID
    Pourquoi : scrapers et DAGs doivent savoir ou stocker les prix
    Comment : terraform output bigtable_instance_id

## SECRETS A CREER A L'ETAPE 6 (Monitoring)

[ ] SLACK_WEBHOOK_URL
    Pourquoi : Prometheus envoie des alertes Slack en cas de panne
    Comment : api.slack.com/apps → Incoming Webhooks

================================================
STATUT ACTUEL DU PROJET
================================================

[X] Etape 1A — Structure GitHub         FAIT
[X] Etape 1B — Ce fichier todo          FAIT
[X] Etape 1C — Strategie de branches    FAIT
[X] Etape 1D — Branch Protection        FAIT
[ ] Etape 1E — Conventions de commits   A FAIRE
[ ] Etape 2  — Docker Compose           A FAIRE
[ ] Etape 3  — Terraform GCP            A FAIRE
[ ] Etape 4  — CI/CD GitHub Actions     A FAIRE
[ ] Etape 5  — Kubernetes               A FAIRE
[ ] Etape 6  — Monitoring               A FAIRE
[ ] Etape 7  — Great Expectations       A FAIRE
[ ] Etape 8  — Tests et Demo            A FAIRE
