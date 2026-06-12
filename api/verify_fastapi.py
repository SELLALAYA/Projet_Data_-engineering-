import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

EXCLUDE = [
    "price > 0", "price < 500000",
    "name NOT LIKE '%Villa%'", "name NOT LIKE '%Appt%'",
    "name NOT LIKE '%Appartement%'", "name NOT LIKE '%Vente%'",
    "name NOT LIKE '%VENDRE%'", "name NOT LIKE '%vendre%'",
    "name NOT LIKE '%Location%'", "name NOT LIKE '%Terrain%'",
    "name NOT LIKE '%Maison%'", "name NOT LIKE '%m²%'",
    "name NOT LIKE '%Tuyau%'", "name NOT LIKE '%PVC%'",
    "name NOT LIKE '%Raccord%'", "name NOT LIKE '%Compte%'",
    "name NOT LIKE '%compte%'", "name NOT LIKE '%Casablanca%'",
    "name NOT LIKE '%Rabat%'", "name NOT LIKE '%Marrakech%'",
    "name NOT LIKE '%Tanger%'", "name NOT LIKE '%Agadir%'",
    "name NOT LIKE '%LITS%'", "name NOT LIKE '%Canapé%'",
    "name NOT LIKE '%canapé%'", "name NOT LIKE '%Meuble%'",
    "name NOT LIKE '%meuble%'", "name NOT LIKE '%Matelas%'",
    "name NOT LIKE '%matelas%'", "name NOT LIKE '%Literie%'",
    "name NOT LIKE '%literie%'", "name NOT LIKE '%Coiffeuse%'",
    "name NOT LIKE '%coiffeuse%'", "name NOT LIKE '%papier%'",
    "name NOT LIKE '%Papier%'", "name NOT LIKE '%doublure%'",
    "name NOT LIKE '%feuilles%'", "name NOT LIKE '%Friteuse%'",
    "name NOT LIKE '%friteuse%'", "name NOT LIKE '%Chaise%'",
    "name NOT LIKE '%chaise%'", "name NOT LIKE '%Voiture%'",
    "name NOT LIKE '%voiture%'", "name NOT LIKE '%Moto%'",
    "name NOT LIKE '%moto%'", "name NOT LIKE '%Vélo%'",
    "name NOT LIKE '%vélo%'",
]

WHERE = "WHERE " + " AND ".join(EXCLUDE)

print("=" * 55)
print("📊 VERIFICATION EXACTE - MEMES FILTRES QUE FASTAPI")
print("=" * 55)

# Total exact comme FastAPI
r = list(client.query(f"""
SELECT COUNT(*) as t FROM (
    SELECT name, source FROM {TABLE}
    {WHERE}
    GROUP BY name, source
)
""").result())[0]
print(f"\n📱 Total exact app (FastAPI)   : {r.t}")

# Par source
rows = client.query(f"""
SELECT source, COUNT(DISTINCT name) as total
FROM {TABLE}
{WHERE}
GROUP BY source
ORDER BY total DESC
""").result()

print(f"\n📊 Par source:")
print("-" * 40)
total = 0
for r in rows:
    print(f"  {r.source}: {r.total}")
    total += r.total

# Par categorie
rows2 = client.query(f"""
SELECT category, COUNT(DISTINCT name) as total
FROM {TABLE}
{WHERE}
GROUP BY category
ORDER BY total DESC
""").result()

print(f"\n📊 Par categorie:")
print("-" * 40)
for r in rows2:
    print(f"  {r.category}: {r.total}")

# Avec images
r2 = list(client.query(f"""
SELECT COUNT(*) as t FROM (
    SELECT name, source FROM {TABLE}
    {WHERE}
    AND image_url IS NOT NULL AND image_url != ''
    GROUP BY name, source
)
""").result())[0]
print(f"\n🖼️  Avec images                : {r2.t}")
print(f"❌ Sans images                : {r.t - r2.t}")
print(f"\n🗄️  Total brut BigQuery        : 6931")
print("=" * 55)