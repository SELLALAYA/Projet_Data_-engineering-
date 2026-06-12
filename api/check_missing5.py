import os, json
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

# Noms dans BigQuery
existing = set()
rows = client.query(f"""
    SELECT DISTINCT name FROM {TABLE}
    WHERE source = 'amazon.com'
""").result()
for r in rows:
    existing.add(r.name)

print(f"Amazon dans BigQuery: {len(existing)}")

# Noms dans JSON
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))

missing = []
for p in data:
    price = float(p.get('price', 0) or 0)
    if price <= 0:
        continue
    name = str(p.get('name', ''))[:500]
    if name not in existing:
        missing.append(name)

print(f"\n❌ Produits manquants ({len(missing)}):")
for name in missing:
    print(f"  - {name[:80]}")