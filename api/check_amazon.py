import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

rows = client.query(f"""
SELECT COUNT(DISTINCT name) as total
FROM {TABLE}
WHERE source = 'amazon.com'
AND price > 0 AND price < 500000
""").result()
print(f"Amazon total: {list(rows)[0].total}")