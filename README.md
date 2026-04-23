# Price Intelligence Platform

Plateforme de veille tarifaire e-commerce en temps réel.

## Stack technique
- Scraping : Scrapy, Selenium
- Streaming : Apache NiFi
- Batch : Apache Airflow
- Stockage : Google Cloud Bigtable
- Transformation : dbt
- Analyse : Python, Pandas, SciPy
- Dashboard : Streamlit, Plotly
- Infra : Docker, Kubernetes, Terraform, GCP

## Lancer le projet en local
```bash
cp .env.example .env
# Remplir les vraies valeurs dans .env
docker-compose up
```

## Structure du projet
Voir docs/architecture/ pour les diagrammes.
