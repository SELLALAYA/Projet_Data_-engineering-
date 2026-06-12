import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

rows = client.query(f"""
SELECT COUNT(*) as total FROM (
    SELECT name, source FROM {TABLE}
    WHERE price > 0 AND price < 500000
    AND name NOT LIKE '%Villa%'
    AND name NOT LIKE '%Appt%'
    AND name NOT LIKE '%Appartement%'
    AND name NOT LIKE '%Vente%'
    AND name NOT LIKE '%VENDRE%'
    AND name NOT LIKE '%vendre%'
    AND name NOT LIKE '%Location%'
    AND name NOT LIKE '%Terrain%'
    AND name NOT LIKE '%Maison%'
    AND name NOT LIKE '%Tuyau%'
    AND name NOT LIKE '%PVC%'
    AND name NOT LIKE '%Canapé%'
    AND name NOT LIKE '%Meuble%'
    AND name NOT LIKE '%meuble%'
    AND name NOT LIKE '%Matelas%'
    AND name NOT LIKE '%papier%'
    AND name NOT LIKE '%feuilles%'
    AND name NOT LIKE '%Friteuse%'
    AND name NOT LIKE '%friteuse%'
    AND name NOT LIKE '%Voiture%'
    AND name NOT LIKE '%voiture%'
    GROUP BY name, source
)
""").result()
total = list(rows)[0].total
print(f"Total produits affiches dans app : {total}")

rows2 = client.query(f"""
SELECT source, COUNT(DISTINCT name) as total
FROM {TABLE}
WHERE price > 0 AND price < 500000
AND name NOT LIKE '%Villa%'
AND name NOT LIKE '%Appartement%'
AND name NOT LIKE '%Vente%'
AND name NOT LIKE '%papier%'
AND name NOT LIKE '%feuilles%'
AND name NOT LIKE '%Voiture%'
GROUP BY source
ORDER BY total DESC
""").result()

print("\nPar source:")
for r in rows2:
    print(f"  {r.source}: {r.total}")