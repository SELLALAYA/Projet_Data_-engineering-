import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

rows = client.query(f"""
SELECT source,
    COUNT(*) as total,
    COUNTIF(image_url IS NOT NULL AND image_url != '') as avec_image,
    COUNTIF(image_url IS NULL OR image_url = '') as sans_image
FROM {TABLE}
GROUP BY source
ORDER BY total DESC
""").result()

print("📊 Images dans BigQuery:")
print("-" * 55)
total_all = 0
total_img = 0
for r in rows:
    pct = round(r.avec_image / r.total * 100) if r.total > 0 else 0
    print(f"  {r.source}:")
    print(f"    Total     : {r.total}")
    print(f"    Avec image: {r.avec_image} ({pct}%)")
    print(f"    Sans image: {r.sans_image}")
    total_all += r.total
    total_img += r.avec_image
print("-" * 55)
print(f"  TOTAL     : {total_all}")
print(f"  Avec image: {total_img} ({round(total_img/total_all*100)}%)")
print(f"  Sans image: {total_all - total_img}")