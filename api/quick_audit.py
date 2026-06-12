from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

def audit(table_name):
    print(f"\n--- AUDIT FOR {table_name} ---")
    t = f"`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.{table_name}`"
    try:
        q1 = f"SELECT source, count(*) as n FROM {t} GROUP BY 1"
        for r in client.query(q1).result():
            print(f"{r.source}: {r.n} items")
    except Exception as e:
        print(f"Error: {e}")

audit("prices_cleaned")
audit("prices_raw")
audit("prices_aggregated")
