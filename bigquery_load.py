import os, json
from datetime import datetime, timezone
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/gcp-credentials-new.json"

PROJECT_ID = "project-32a82952-90fa-4dd7-b9c"
DATASET_ID = "price_intelligence_dbt"
TABLE_ID   = "prices_raw"
TABLE_REF  = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

EXCHANGE_RATES = {"MAD": 1.0, "USD": 10.2, "EUR": 11.0}

FILES = [
    ("/opt/airflow/data/raw/jumia_ma.json",    "jumia.ma",    "MAD"),
    ("/opt/airflow/data/raw/avito_ma.json",    "avito.ma",    "MAD"),
    ("/opt/airflow/data/raw/amazon_ma.json",   "amazon.com",  "USD"),
    ("/opt/airflow/data/raw/connecto_ma.json", "connecto.ma", "MAD"),
]

SCHEMA = [
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("price",        "FLOAT"),
    bigquery.SchemaField("old_price",    "FLOAT"),
    bigquery.SchemaField("discount_pct", "FLOAT"),
    bigquery.SchemaField("rating",       "FLOAT"),
    bigquery.SchemaField("currency",     "STRING"),
    bigquery.SchemaField("category",     "STRING"),
    bigquery.SchemaField("image_url",    "STRING"),
    bigquery.SchemaField("source",       "STRING"),
    bigquery.SchemaField("url",          "STRING"),
    bigquery.SchemaField("scraped_at",   "TIMESTAMP"),
]

client = bigquery.Client(project=PROJECT_ID)

def parse_float(val):
    if val is None: return None
    try: return float(str(val).replace(",",".").replace(" ",""))
    except: return None

def parse_ts(val):
    if val is None: return datetime.now(timezone.utc).isoformat()
    try: return datetime.fromtimestamp(int(val), tz=timezone.utc).isoformat()
    except: return str(val)

def to_mad(price, currency):
    if price is None: return None
    return round(price * EXCHANGE_RATES.get(str(currency).upper(), 1.0), 2)

all_rows = []

for file_path, default_source, default_currency in FILES:
    if not os.path.exists(file_path):
        print(f"[SKIP] {file_path}")
        continue
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            if not isinstance(item, dict): continue
            name = (item.get("product_name") or item.get("name") or "").strip()
            if not name: continue
            currency = item.get("currency", default_currency).upper()
            price    = parse_float(item.get("price"))
            price_mad = to_mad(price, currency)
            row = {
                "product_name": name,
                "price":        price_mad,
                "old_price":    parse_float(item.get("old_price")),
                "discount_pct": parse_float(item.get("discount_pct")),
                "rating":       parse_float(item.get("rating")),
                "currency":     "MAD",
                "category":     item.get("category", ""),
                "image_url":    item.get("image_url"),
                "source":       item.get("source", default_source),
                "url":          item.get("url", ""),
                "scraped_at":   parse_ts(item.get("scraped_at")),
            }
            all_rows.append(row)
            count += 1
        print(f"[OK] {default_source}: {count} rows")
    except Exception as e:
        print(f"[ERR] {file_path}: {e}")

print(f"\nTOTAL: {len(all_rows)} rows")

if not all_rows:
    print("Aucune donnee")
    exit(0)

import pathlib
tmp = pathlib.Path("/tmp/prices_raw.ndjson")
with open(tmp, "w", encoding="utf-8") as f:
    for row in all_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

job_config = bigquery.LoadJobConfig(
    schema=SCHEMA,
    write_disposition="WRITE_TRUNCATE",
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    ignore_unknown_values=True,
)

client.delete_table(TABLE_REF, not_found_ok=True)
with open(tmp, "rb") as f:
    job = client.load_table_from_file(f, TABLE_REF, job_config=job_config)
    job.result()

print(f"\n✅ {len(all_rows)} lignes chargees dans BigQuery")

result = list(client.query(
    f"""SELECT source, COUNT(*) as cnt, ROUND(AVG(price),0) as avg_price
        FROM `{TABLE_REF}`
        GROUP BY source ORDER BY cnt DESC""",
    location="US"
).result())

print("\n=== BigQuery par source ===")
for r in result:
    print(f"  {r.source}: {r.cnt} produits | moy: {r.avg_price} MAD")
print(f"  TOTAL: {sum(r.cnt for r in result)}")
