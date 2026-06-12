import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

print("=" * 55)
print("📊 VERIFICATION COMPLETE")
print("=" * 55)

# 1. Total brut BigQuery
r = list(client.query(f"SELECT COUNT(*) as t FROM {TABLE}").result())[0]
print(f"\n🗄️  Total brut BigQuery        : {r.t}")

# 2. Total après filtres (= ce que l'app affiche)
r = list(client.query(f"""
SELECT COUNT(*) as t FROM (
    SELECT name, source FROM {TABLE}
    WHERE price > 0 AND price < 500000
    AND name NOT LIKE '%Villa%'
    AND name NOT LIKE '%Appartement%'
    AND name NOT LIKE '%Vente%'
    AND name NOT LIKE '%VENDRE%'
    AND name NOT LIKE '%Location%'
    AND name NOT LIKE '%Terrain%'
    AND name NOT LIKE '%Maison%'
    AND name NOT LIKE '%Tuyau%'
    AND name NOT LIKE '%PVC%'
    AND name NOT LIKE '%papier%'
    AND name NOT LIKE '%feuilles%'
    AND name NOT LIKE '%Friteuse%'
    AND name NOT LIKE '%Voiture%'
    AND name NOT LIKE '%voiture%'
    AND name NOT LIKE '%Canapé%'
    AND name NOT LIKE '%Meuble%'
    AND name NOT LIKE '%meuble%'
    AND name NOT LIKE '%Matelas%'
    AND name NOT LIKE '%Chaise%'
    AND name NOT LIKE '%Moto%'
    AND name NOT LIKE '%Vélo%'
    AND name NOT LIKE '%m²%'
    GROUP BY name, source
)
""").result())[0]
print(f"📱 Total affiché dans l'app    : {r.t}")

# 3. Par source après filtres
rows = client.query(f"""
SELECT source, COUNT(DISTINCT name) as total
FROM {TABLE}
WHERE price > 0 AND price < 500000
AND name NOT LIKE '%Villa%'
AND name NOT LIKE '%Appartement%'
AND name NOT LIKE '%Vente%'
AND name NOT LIKE '%Voiture%'
AND name NOT LIKE '%Canapé%'
AND name NOT LIKE '%Meuble%'
AND name NOT LIKE '%Matelas%'
AND name NOT LIKE '%papier%'
AND name NOT LIKE '%Tuyau%'
GROUP BY source
ORDER BY total DESC
""").result()

print(f"\n📊 Par source (après filtres):")
print("-" * 35)
for r in rows:
    print(f"  {r.source}: {r.total}")

# 4. Produits exclus
r2 = list(client.query(f"SELECT COUNT(*) as t FROM {TABLE}").result())[0]
r3 = list(client.query(f"""
SELECT COUNT(*) as t FROM (
    SELECT name, source FROM {TABLE}
    WHERE price > 0 AND price < 500000
    AND name NOT LIKE '%Villa%'
    AND name NOT LIKE '%Appartement%'
    AND name NOT LIKE '%Voiture%'
    AND name NOT LIKE '%Canapé%'
    GROUP BY name, source
)
""").result())[0]
print(f"\n❌ Produits filtrés/exclus     : {r2.t - r3.t}")
print("=" * 55)