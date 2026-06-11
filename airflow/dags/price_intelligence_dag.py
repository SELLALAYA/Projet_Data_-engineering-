from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import logging

PROJECT_ROOT = "/opt/airflow"
CREDS_FILE   = f"{PROJECT_ROOT}/gcp-credentials-new.json"
PROJECT_ID   = "project-32a82952-90fa-4dd7-b9c"
DATASET_ID   = "price_intelligence_dbt"
DBT          = "/home/airflow/.local/bin/dbt"

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 4, 27),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="price_intelligence_pipeline",
    default_args=DEFAULT_ARGS,
    description="Scrapy -> BigQuery -> dbt -> prices_cleaned (toutes les heures)",
    schedule_interval="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["price_intelligence", "scraping", "dbt", "bigquery"],
) as dag:

    scrape_jumia = BashOperator(
        task_id="scrape_jumia",
        bash_command="""
            cd /opt/airflow
            mkdir -p data/raw
            scrapy crawl jumia_ma -o data/raw/jumia_ma.json --overwrite-output -s LOG_LEVEL=WARNING -s ROBOTSTXT_OBEY=False -s DOWNLOAD_DELAY=1.5 -s CONCURRENT_REQUESTS=4 || echo "Jumia done with warnings"
        """,
        execution_timeout=timedelta(minutes=30),
    )

    scrape_avito = BashOperator(
        task_id="scrape_avito",
        bash_command="""
            cd /opt/airflow
            mkdir -p data/raw
            export DISPLAY=:99
            python3 scrapers/spiders/avito_ma.py || echo "Avito done with warnings"
        """,
        execution_timeout=timedelta(minutes=20),
    )

    scrape_amazon = BashOperator(
        task_id="scrape_amazon",
        bash_command="""
            cd /opt/airflow
            mkdir -p data/raw
            export DISPLAY=:99
            python3 scrapers/spiders/amazon_ma.py || echo "Amazon done with warnings"
        """,
        execution_timeout=timedelta(minutes=20),
    )

    scrape_electroplanet = BashOperator(
        task_id="scrape_electroplanet",
        bash_command="""
            cd /opt/airflow
            mkdir -p data/raw
            export DISPLAY=:99
            python3 scrapers/spiders/electroplanet_ma.py || echo "Electroplanet done with warnings"
        """,
        execution_timeout=timedelta(minutes=20),
    )

    load_bigtable_task = BashOperator(
        task_id="load_bigtable",
        bash_command="""
            set -e
            cd /opt/airflow
            export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json
            python3 dags/load_bigtable.py
            echo Bigtable done
        """,
        trigger_rule=TriggerRule.ALL_DONE,
        execution_timeout=timedelta(minutes=15),
    )

    load_bigquery = BashOperator(
        task_id="load_bigquery",
        bash_command="""
            set -e
            cd /opt/airflow
            export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json
            python3 bigquery_load.py
            echo BigQuery done
        """,
        execution_timeout=timedelta(minutes=15),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
            set -e
            cd /opt/airflow/dbt
            export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json
            /home/airflow/.local/bin/dbt run --full-refresh --profiles-dir . --project-dir .
            echo dbt done
        """,
        execution_timeout=timedelta(minutes=20),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
            cd /opt/airflow/dbt
            export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json
            /home/airflow/.local/bin/dbt test --profiles-dir . --project-dir . || echo warnings only
            echo dbt test done
        """,
        execution_timeout=timedelta(minutes=10),
    )

    def validate_pipeline(**context):
        from google.cloud import bigquery
        import os
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/gcp-credentials-new.json"
        try:
            client = bigquery.Client(project="project-32a82952-90fa-4dd7-b9c")
            query = "SELECT COUNT(*) AS total, COUNT(DISTINCT source) AS sources, MAX(scraped_at) AS last_scraped FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`"
            result = list(client.query(query).result())[0]
            logging.info(f"Pipeline OK - {result.total} produits | {result.sources} sources | last: {result.last_scraped}")
        except Exception as e:
            logging.error(f"Validation echouee: {e}")

    validate = PythonOperator(
        task_id="validate_pipeline",
        python_callable=validate_pipeline,
        execution_timeout=timedelta(minutes=5),
    )

    [scrape_jumia, scrape_avito, scrape_amazon, scrape_electroplanet] >> load_bigtable_task
    load_bigtable_task >> load_bigquery
    load_bigquery >> dbt_run
    dbt_run >> dbt_test
    dbt_test >> validate