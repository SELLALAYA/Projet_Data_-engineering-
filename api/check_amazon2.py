import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

# Voir toutes les sources
rows = client.query(f"""
SELECT source, COUNT(*) as total
FROM {TABLE}
GROUP BY source
ORDER BY total DESC
""").result()

print("Sources dans BigQuery:")
for r in rows:
    print(f"  {r.source}: {r.total}")