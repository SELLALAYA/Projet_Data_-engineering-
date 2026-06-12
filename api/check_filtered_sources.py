from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

EXCLUDE = [
    "price > 0",
    "price < 50000",
    "LOWER(name) NOT LIKE '%villa%'",
    "LOWER(name) NOT LIKE '%appartement%'",
    "LOWER(name) NOT LIKE '%terrain%'",
    "LOWER(name) NOT LIKE '%location%'",
    "LOWER(name) NOT LIKE '%vente%'",
    "LOWER(name) NOT LIKE '%m2%'",
    "LOWER(name) NOT LIKE '%tuyau%'",
    "LOWER(name) NOT LIKE '%raccord%'",
    "LOWER(name) NOT LIKE '%louer%'",
    "LOWER(name) NOT LIKE '%voiture%'",
    "LOWER(name) NOT LIKE '%auto%'",
    "LOWER(name) NOT LIKE '%moto%'",
    "LOWER(name) NOT LIKE '%camion%'",
    "LOWER(name) NOT LIKE '%meuble%'",
    "LOWER(name) NOT LIKE '%canapé%'",
    "LOWER(name) NOT LIKE '%coiffeuse%'"
]

WHERE = "WHERE " + " AND ".join(EXCLUDE)
query = f"SELECT source, COUNT(*) as count FROM {TABLE} {WHERE} GROUP BY source"

try:
    results = client.query(query).result()
    for row in results:
        print(f"{row.source}: {row.count}")
except Exception as e:
    print(f"Error: {e}")
