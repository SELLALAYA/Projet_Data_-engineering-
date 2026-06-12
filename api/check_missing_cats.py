from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

query = """
SELECT category, COUNT(*) as total
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
WHERE category NOT IN ('Informatique', 'Telephones & Smartphones', 'Electromenager')
GROUP BY category
"""

print("🔍 Categories NOT in whitelist:")
rows = client.query(query).result()
for r in rows:
    print(f"  {r.category}: {r.total}")
