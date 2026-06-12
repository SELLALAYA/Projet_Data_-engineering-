from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

query = f"SELECT COUNT(*) as count FROM {TABLE} WHERE discount_pct IS NOT NULL AND rating IS NOT NULL AND price > 0"
try:
    results = client.query(query).result()
    for row in results:
        print(f"Products with discount and rating: {row.count}")
except Exception as e:
    print(f"Error: {e}")
