from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

query = """
SELECT category, COUNT(*) as total
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
WHERE (
    LOWER(name) LIKE '%tv%' 
    OR LOWER(name) LIKE '%téléviseur%' 
    OR LOWER(name) LIKE '%televiseur%'
    OR LOWER(name) LIKE '%tablet%' 
    OR LOWER(name) LIKE '%ipad%' 
    OR LOWER(name) LIKE '%tab %'
)
GROUP BY category
ORDER BY total DESC
"""

print("🔍 Potential TVs/Tablets by category:")
rows = client.query(query).result()
for r in rows:
    print(f"  {r.category}: {r.total}")

print("\n🔍 All Categories:")
rows = client.query("SELECT category, COUNT(*) as total FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned` GROUP BY category").result()
for r in rows:
    print(f"  {r.category}: {r.total}")
