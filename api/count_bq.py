import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

rows = client.query(f"""
SELECT source, COUNT(*) as total
FROM {TABLE}
GROUP BY source
ORDER BY total DESC
""").result()

total = 0
print("📊 BigQuery - prices_cleaned:")
print("-" * 35)
for r in rows:
    print(f"  {r.source}: {r.total}")
    total += r.total
print("-" * 35)
print(f"  TOTAL: {total}")