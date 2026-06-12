from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

rows = client.query("""
SELECT category, COUNT(*) as total
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
GROUP BY category
ORDER BY total DESC
""").result()

print("📊 Catégories dans BigQuery:")
print("-" * 40)
for r in rows:
    print(f"  {r.category}: {r.total} produits")