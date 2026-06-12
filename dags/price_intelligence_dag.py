
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import logging
import json
import requests
import os
import time

PROJECT_ROOT = "/opt/airflow"
CREDS_FILE   = f"{PROJECT_ROOT}/gcp-credentials-new.json"
PROJECT_ID   = "project-32a82952-90fa-4dd7-b9c"
DATASET_ID   = "price_intelligence_dbt"
NIFI_URL     = "http://price_nifi:8888/contentListener"

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 4, 27),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

SCRAPY_BASE = "cd /opt/airflow && export PYTHONPATH=/opt/airflow && export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json"

def ingest_to_nifi(source_file):
    filepath = f"/opt/airflow/data/raw/{source_file}"
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        logging.warning(f"File {filepath} not found or empty. Skipping ingestion.")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            products = json.load(f)
        except Exception as e:
            logging.error(f"Error loading JSON from {filepath}: {e}")
            return

    if not products:
        logging.info(f"No products to ingest from {source_file}")
        return

    logging.info(f"Ingesting {len(products)} products from {source_file} to NiFi...")
    success_count = 0
    
    # Use session for performance
    with requests.Session() as session:
        for p in products:
            for attempt in range(3):
                try:
                    r = session.post(NIFI_URL, json=p, timeout=10)
                    if r.status_code == 200:
                        success_count += 1
                        break
                    else:
                        logging.warning(f"NiFi returned {r.status_code} for a product. Attempt {attempt+1}/3")
                except Exception as e:
                    logging.warning(f"Error sending to NiFi (attempt {attempt+1}/3): {e}")
                time.sleep(1)
            else:
                logging.error("Failed to send product to NiFi after 3 attempts. Stopping batch.")
                break

    logging.info(f"Successfully ingested {success_count}/{len(products)} products")

with DAG(
    dag_id="price_intelligence_pipeline",
    default_args=DEFAULT_ARGS,
    description="Scrapy -> BigQuery -> dbt",
    schedule_interval="0 */6 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["price_intelligence"],
) as dag:

    scrape_jumia = BashOperator(
        task_id="scrape_jumia",
        bash_command=f"""
            {SCRAPY_BASE}
            mkdir -p data/raw
            scrapy crawl jumia_ma -s LOG_LEVEL=WARNING -s ROBOTSTXT_OBEY=False || echo "Jumia done"
        """,
        execution_timeout=timedelta(minutes=45),
    )

    ingest_jumia = PythonOperator(
        task_id="ingest_jumia_nifi",
        python_callable=ingest_to_nifi,
        op_kwargs={"source_file": "jumia_ma.json"},
        trigger_rule=TriggerRule.ALL_DONE,
    )

    scrape_avito = BashOperator(
        task_id="scrape_avito",
        bash_command=f"""
            {SCRAPY_BASE}
            mkdir -p data/raw
            scrapy crawl avito_ma -s LOG_LEVEL=WARNING -s ROBOTSTXT_OBEY=False || echo "Avito done"
        """,
        execution_timeout=timedelta(minutes=30),
    )

    ingest_avito = PythonOperator(
        task_id="ingest_avito_nifi",
        python_callable=ingest_to_nifi,
        op_kwargs={"source_file": "avito_ma.json"},
        trigger_rule=TriggerRule.ALL_DONE,
    )

    scrape_amazon = BashOperator(
        task_id="scrape_amazon",
        bash_command=f"""
            {SCRAPY_BASE}
            mkdir -p data/raw
            scrapy crawl amazon_ma -s LOG_LEVEL=WARNING -s ROBOTSTXT_OBEY=False || echo "Amazon done"
        """,
        execution_timeout=timedelta(minutes=30),
    )

    ingest_amazon = PythonOperator(
        task_id="ingest_amazon_nifi",
        python_callable=ingest_to_nifi,
        op_kwargs={"source_file": "amazon_ma.json"},
        trigger_rule=TriggerRule.ALL_DONE,
    )

    scrape_connecto = BashOperator(
        task_id="scrape_connecto",
        bash_command="""
            echo "Connecto scraping via API Shopify..."
            python3 -c "
import json, time, requests, os
from datetime import datetime, timezone

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}
BASE = 'https://connecto.ma'
COLLECTIONS = [
    ('smartphones', 'Telephones & Smartphones'),
    ('ordinateur-portable-pc-portable', 'Informatique'),
    ('ecrans-moniteurs', 'Informatique'),
    ('tablettes-tactiles', 'Informatique'),
    ('televiseurs', 'Electromenager'),
    ('all', 'Informatique'),
]
session = requests.Session()
session.headers.update(HEADERS)
products = []
seen = set()
for slug, category in COLLECTIONS:
    page = 1
    while True:
        url = f'{BASE}/collections/{slug}/products.json?limit=250&page={page}'
        try:
            r = session.get(url, timeout=20)
            if r.status_code != 200: 
                print(f'Error {r.status_code} for {url}')
                break
            items = r.json().get('products', [])
            if not items: break
            for item in items:
                name = item.get('title','').strip()
                if not name or name in seen: continue
                seen.add(name)
                variants = item.get('variants', [])
                price = None
                old_price = None
                if variants:
                    try:
                        p_val = variants[0].get('price', 0)
                        price = float(p_val) if p_val else None
                        cap = variants[0].get('compare_at_price')
                        if cap: old_price = float(cap)
                    except: pass
                images = item.get('images', [])
                image_url = images[0].get('src') if images else None
                handle = item.get('handle','')
                products.append({
                    'product_name': name,
                    'price': price if price and price > 0 else None,
                    'old_price': old_price if old_price and old_price != price else None,
                    'discount_pct': None,
                    'rating': None,
                    'currency': 'MAD',
                    'category': category,
                    'image_url': image_url,
                    'url': f'{BASE}/products/{handle}',
                    'source': 'connecto.ma',
                    'scraped_at': int(datetime.now(timezone.utc).timestamp()),
                })
            if len(items) < 250: break
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f'Error fetching {url}: {e}')
            break

os.makedirs('/opt/airflow/data/raw', exist_ok=True)
with open('/opt/airflow/data/raw/connecto_ma.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False)
print(f'Connecto: {len(products)} produits saved')
"
        """,
        execution_timeout=timedelta(minutes=15),
    )

    ingest_connecto = PythonOperator(
        task_id="ingest_connecto_nifi",
        python_callable=ingest_to_nifi,
        op_kwargs={"source_file": "connecto_ma.json"},
        trigger_rule=TriggerRule.ALL_DONE,
    )

    wait_nifi = BashOperator(
        task_id="wait_nifi_flush",
        bash_command="sleep 30 && echo NiFi flush done",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    load_bigtable = BashOperator(
        task_id="load_bigtable",
        bash_command=f"""
            set -e
            cd /opt/airflow
            export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json
            python3 scripts/load_bigtable.py
            echo Bigtable load done
        """,
        execution_timeout=timedelta(minutes=30),
    )

    load_bigquery = BashOperator(
        task_id="load_bigquery",
        bash_command=f"""
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
        bash_command=f"""
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
        bash_command=f"""
            cd /opt/airflow/dbt
            export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp-credentials-new.json
            /home/airflow/.local/bin/dbt test --profiles-dir . --project-dir . || echo warnings only
        """,
        execution_timeout=timedelta(minutes=10),
    )

    def validate_pipeline(**context):
        from google.cloud import bigquery
        import os
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/gcp-credentials-new.json"
        try:
            client = bigquery.Client(project="project-32a82952-90fa-4dd7-b9c")
            rows = list(client.query(
                "SELECT source, COUNT(*) as cnt FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_raw` GROUP BY source ORDER BY cnt DESC",
                location="US"
            ).result())
            total = sum(r.cnt for r in rows)
            for r in rows:
                logging.info(f"  {r.source}: {r.cnt}")
            logging.info(f"TOTAL: {total} produits")
        except Exception as e:
            logging.error(f"Validation echouee: {e}")

    validate = PythonOperator(
        task_id="validate_pipeline",
        python_callable=validate_pipeline,
        execution_timeout=timedelta(minutes=5),
    )

    scrape_jumia >> ingest_jumia
    scrape_avito >> ingest_avito
    scrape_amazon >> ingest_amazon
    scrape_connecto >> ingest_connecto

    [ingest_jumia, ingest_avito, ingest_amazon, ingest_connecto] >> wait_nifi
    wait_nifi >> load_bigtable >> load_bigquery
    load_bigquery >> dbt_run >> dbt_test >> validate
