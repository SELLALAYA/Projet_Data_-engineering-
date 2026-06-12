from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

query = f"SELECT COUNT(*) as total FROM {TABLE} WHERE price > 0"
print(f"Running query: {query}")
try:
    results = client.query(query).result()
    for row in results:
        print(f"Total products: {row.total}")
except Exception as e:
    print(f"Error: {e}")

query_cat = f"SELECT category, COUNT(*) as count FROM {TABLE} GROUP BY category"
print(f"Running categories query: {query_cat}")
try:
    results = client.query(query_cat).result()
    for row in results:
        print(f"Category: {row.category}, Count: {row.count}")
except Exception as e:
    print(f"Error: {e}")
