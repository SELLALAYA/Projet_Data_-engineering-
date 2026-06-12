from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

TABLE_PRICES = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'
TABLE_IMAGES = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.temp_images`'

query = f"""
SELECT p.name, t.image_url 
FROM {TABLE_PRICES} p 
LEFT JOIN {TABLE_IMAGES} t ON p.name = t.product_name 
WHERE t.image_url IS NOT NULL 
LIMIT 5
"""

print(f"Running query...")
try:
    results = list(client.query(query).result())
    print(f"Matches found: {len(results)}")
    for r in results:
        print(f"Product: {r.name[:40]} | Image: {r.image_url[:50]}...")
except Exception as e:
    print(f"Error: {e}")

# Also check some data in temp_images directly
query2 = f"SELECT product_name, image_url FROM {TABLE_IMAGES} LIMIT 5"
print(f"\nChecking temp_images directly...")
try:
    results2 = list(client.query(query2).result())
    for r in results2:
        print(f"Name: {r.product_name[:40]} | Image: {r.image_url[:50]}...")
except Exception as e:
    print(f"Error: {e}")
