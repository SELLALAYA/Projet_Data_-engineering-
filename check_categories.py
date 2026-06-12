from google.cloud import bigquery
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'
query = f"SELECT DISTINCT category FROM {TABLE}"
results = client.query(query).result()
print("Categories in DB:")
for row in results:
    print(f"- {row.category}")
