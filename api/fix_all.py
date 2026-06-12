import os, json, time
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = 'project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned'

# ETAPE 1 - Importer Amazon
print("=== ETAPE 1 - Import Amazon ===")
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
print(f"✅ {total} produits Amazon importés!")

# ETAPE 2 - Remettre les images pour Jumia et Avito
print("\n=== ETAPE 2 - Remise des images Jumia + Avito ===")
name_to_image = {}

data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/jumia_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:300]] = p['image_url'][:500]
print(f"✅ Jumia: {len(name_to_image)} images")

data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:300]] = p['image_url'][:500]
print(f"✅ Avito ajouté — Total: {len(name_to_image)} images")

# Récupérer les noms depuis BigQuery
print("Récupération noms BigQuery...")
rows_bq = client.query(f"""
    SELECT DISTINCT name FROM `{TABLE}`
    WHERE name IS NOT NULL
    AND source IN ('jumia.ma', 'avito.ma')
""").result()

matched = []
for r in rows_bq:
    name = (r.name or '').strip()[:300]
    if name in name_to_image:
        matched.append((name, name_to_image[name]))

print(f"✅ {len(matched)} noms matchés pour images!")

# UPDATE par batch
batch_size = 100
total_updated = 0
for i in range(0, len(matched), batch_size):
    batch = matched[i:i+batch_size]
    cases = []
    for name, url in batch:
        n = name.replace("\\", "\\\\").replace("'", "\\'")
        u = url.replace("\\", "\\\\").replace("'", "\\'")
        cases.append(f"WHEN name = '{n}' THEN '{u}'")
    names_list = ", ".join([f"'{n.replace(chr(39), chr(92)+chr(39))}'" for n, u in batch])
    update_sql = f"""
    UPDATE `{TABLE}`
    SET image_url = CASE {chr(10).join(cases)} ELSE image_url END
    WHERE name IN ({names_list})
    """
    try:
        job = client.query(update_sql)
        job.result()
        total_updated += len(batch)
        print(f"✅ Images batch {i}-{i+len(batch)} OK")
    except Exception as e:
        print(f"❌ Erreur: {str(e)[:80]}")
    time.sleep(1)

print(f"\n✅ {total_updated} produits mis à jour avec images!")

# Vérification finale
print("\n=== VERIFICATION FINALE ===")
rows_check = client.query(f"""
SELECT source,
    COUNT(*) as total,
    COUNTIF(image_url IS NOT NULL AND image_url != '') as avec_image
FROM `{TABLE}`
GROUP BY source
ORDER BY total DESC
""").result()

for r in rows_check:
    print(f"  {r.source}: {r.total} produits, {r.avec_image} avec images")

print("\n🎉 DONE!")