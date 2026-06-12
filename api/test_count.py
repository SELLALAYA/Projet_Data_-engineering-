from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

EXCLUDE = [
    "price > 0",
    "price < 500000",
    "name NOT LIKE '%Villa%'",
    "name NOT LIKE '%Appt%'",
    "name NOT LIKE '%Appartement%'",
    "name NOT LIKE '%Vente%'",
    "name NOT LIKE '%VENDRE%'",
    "name NOT LIKE '%vendre%'",
    "name NOT LIKE '%Location%'",
    "name NOT LIKE '%Terrain%'",
    "name NOT LIKE '%Maison%'",
    "name NOT LIKE '%m²%'",
    "name NOT LIKE '%Tuyau%'",
    "name NOT LIKE '%PVC%'",
    "name NOT LIKE '%Raccord%'",
    "name NOT LIKE '%Compte%'",
    "name NOT LIKE '%compte%'",
    "name NOT LIKE '%Casablanca%'",
    "name NOT LIKE '%Rabat%'",
    "name NOT LIKE '%Marrakech%'",
    "name NOT LIKE '%Tanger%'",
    "name NOT LIKE '%Agadir%'",
    "name NOT LIKE '%LITS%'",
    "name NOT LIKE '%Canapé%'",
    "name NOT LIKE '%canapé%'",
    "name NOT LIKE '%Meuble%'",
    "name NOT LIKE '%meuble%'",
    "name NOT LIKE '%Matelas%'",
    "name NOT LIKE '%matelas%'",
    "name NOT LIKE '%Literie%'",
    "name NOT LIKE '%literie%'",
    "name NOT LIKE '%Coiffeuse%'",
    "name NOT LIKE '%coiffeuse%'",
    "name NOT LIKE '%papier%'",
    "name NOT LIKE '%Papier%'",
    "name NOT LIKE '%doublure%'",
    "name NOT LIKE '%feuilles%'",
    "name NOT LIKE '%Friteuse%'",
    "name NOT LIKE '%friteuse%'",
    "name NOT LIKE '%Chaise%'",
    "name NOT LIKE '%chaise%'",
    "name NOT LIKE '%Voiture%'",
    "name NOT LIKE '%voiture%'",
    "name NOT LIKE '%Moto%'",
    "name NOT LIKE '%moto%'",
    "name NOT LIKE '%Vélo%'",
    "name NOT LIKE '%vélo%'",
]

EXCLUDE_WHERE = " AND ".join(EXCLUDE)

query = f"SELECT COUNT(*) as count FROM {TABLE} WHERE {EXCLUDE_WHERE}"
results = list(client.query(query).result())
print(f"Filtered Count: {results[0].count}")
