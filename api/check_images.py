from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

rows = client.query("""
SELECT image_url, source, name
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
WHERE image_url IS NOT NULL 
AND image_url != ''
LIMIT 5
""").result()

count = 0
for r in rows:
    print(f"source: {r.source}")
    print(f"name: {r.name[:50]}")
    print(f"image_url: {r.image_url[:80]}")
    print("---")
    count += 1

if count == 0:
    print("❌ Aucune image trouvée dans BigQuery !")
else:
    print(f"✅ {count} produits avec images trouvés !")