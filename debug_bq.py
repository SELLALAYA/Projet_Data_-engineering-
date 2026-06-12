from google.cloud import bigquery
import os
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'api/credentials.json'
project_id = 'project-32a82952-90fa-4dd7-b9c'
client = bigquery.Client(project=project_id)

table_id = f"{project_id}.price_intelligence_dbt.prices_cleaned"

print(f"Checking table: {table_id}")

try:
    # 1. Row count
    query = f"SELECT COUNT(*) as total FROM `{table_id}`"
    total = list(client.query(query).result())[0].total
    print(f"TOTAL ROWS: {total}")

    # 2. Sample categories
    query_cats = f"SELECT category, COUNT(*) as count FROM `{table_id}` GROUP BY 1 ORDER BY 2 DESC"
    cats = list(client.query(query_cats).result())
    print("\nCATEGORIES IN TABLE:")
    for row in cats:
        print(f" - {row.category}: {row.count}")

    # 3. Check specific price range
    query_prices = f"SELECT MIN(price) as min_p, MAX(price) as max_p FROM `{table_id}`"
    prices = list(client.query(query_prices).result())[0]
    print(f"\nPRICE RANGE: {prices.min_p} to {prices.max_p}")

except Exception as e:
    print(f"ERROR: {e}")
