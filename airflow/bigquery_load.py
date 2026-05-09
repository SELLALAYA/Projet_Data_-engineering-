import os, json
from datetime import datetime
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/gcp-credentials-new.json'

PROJECT_ID = "project-32a82952-90fa-4dd7-b9c"
DATASET_ID = "price_intelligence_dbt"
TABLE_ID = "prices_raw"

FILES = [
    '/opt/airflow/data/raw/jumia_ma.json',
    '/opt/airflow/data/raw/avito_ma.json',
    '/opt/airflow/data/raw/amazon_ma.json',
    '/opt/airflow/data/raw/electroplanet_ma.json',
]

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("price", "FLOAT"),
    bigquery.SchemaField("old_price", "FLOAT"),
    bigquery.SchemaField("discount_pct", "FLOAT"),
    bigquery.SchemaField("rating", "FLOAT"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("image_url", "STRING"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("scraped_at", "TIMESTAMP"),
]

# Supprimer la table pour forcer la recreation avec le bon schema
client.delete_table(table_ref, not_found_ok=True)

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_TRUNCATE",
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
)

all_rows = []
for file_path in FILES:
    source = file_path.split("/")[-1].replace("_ma.json", "")
    if not os.path.exists(file_path):
        print(f"Manquant: {file_path}")
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            for item in data:
                d = item.get("discount", None)
                dpct = None
                if d:
                    try: dpct = float(str(d).replace("%","").strip())
                    except: pass
                r = item.get("rating", None)
                rating = None
                if r:
                    try: rating = float(str(r).split()[0])
                    except: pass
                all_rows.append({
                    "product_name": item.get("name") or item.get("title") or item.get("product_name", ""),
                    "price": float(item.get("price", 0) or 0),
                    "old_price": float(item.get("old_price", 0) or 0) or None,
                    "discount_pct": dpct,
                    "rating": rating,
                    "currency": item.get("currency", "MAD"),
                    "category": item.get("category", ""),
                    "image_url": item.get("image_url", None),
                    "source": source,
                    "url": item.get("url", ""),
                    "scraped_at": datetime.utcnow().isoformat(),
                })
        except Exception as e:
            print(f"Erreur {file_path}: {e}")

print(f"Total rows: {len(all_rows)}")
print(f"Sample image_url: {all_rows[0].get('image_url')}")

import tempfile, pathlib
tmp = pathlib.Path('/tmp') / 'prices_raw.ndjson'
with open(tmp, "w", encoding="utf-8") as f:
    for row in all_rows:
        f.write(json.dumps(row) + "\n")

with open(tmp, "rb") as f:
    job = client.load_table_from_file(f, table_ref, job_config=job_config)
    job.result()

print(f"OK {len(all_rows)} lignes chargees dans {table_ref}")