from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

query = f"""
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN discount_pct > 0 THEN 1 END) as with_discount,
    MAX(discount_pct) as max_discount,
    COUNT(CASE WHEN old_price IS NOT NULL AND old_price > price THEN 1 END) as with_old_price
FROM {TABLE}
"""
print(f"Running query: {query}")
try:
    results = client.query(query).result()
    for row in results:
        print(f"Total: {row.total}, With Discount: {row.with_discount}, Max Discount: {row.max_discount}, With Old Price: {row.with_old_price}")
except Exception as e:
    print(f"Error: {e}")
