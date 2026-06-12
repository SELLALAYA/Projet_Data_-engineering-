import os
import json
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = 'project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned'

# Charger les données Amazon
print("Chargement Amazon JSON...")
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))

rows = []
for p in data:
    try:
        price = float(p.get('price', 0) or 0)
        if price <= 0:
            continue
        rows.append({
            'name': str(p.get('name', ''))[:500],
            'price': price,
            'old_price': float(p.get('old_price', price) or price),
            'discount_pct': float(p.get('discount_pct', 0) or 0),
            'rating': float(p.get('rating', 4.0) or 4.0),
            'currency': 'MAD',
            'category': str(p.get('category', 'Informatique')),
            'source': 'amazon.com',
            'image_url': str(p.get('image_url', '') or ''),
        })
    except:
        continue

print(f"✅ {len(rows)} produits Amazon prêts")

# Insérer par batch
batch_size = 200
total = 0
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    errors = client.insert_rows_json(TABLE, batch)
    if not errors:
        total += len(batch)
        print(f"✅ Batch {i}-{i+len(batch)} OK")
    else:
        print(f"❌ Erreur: {errors[0]}")

print(f"\n🎉 {total} produits Amazon réimportés!")

# Vérification
rows_check = client.query(f"""
SELECT source, COUNT(*) as total
FROM `{TABLE}`
GROUP BY source
ORDER BY total DESC
""").result()

print("\n📊 BigQuery maintenant:")
for r in rows_check:
    print(f"  {r.source}: {r.total}")