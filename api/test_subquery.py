from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

query = f"""
SELECT COUNT(*) as total FROM (
    SELECT name, source
    FROM {TABLE}
    WHERE price > 0
    GROUP BY name, source
)
"""
try:
    results = list(client.query(query).result())
    print(f"Total: {results[0].total}")
except Exception as e:
    print(f"Error: {e}")
