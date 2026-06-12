import json
import os
import time
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

# Charger images
print("Chargement images...")
name_to_image = {}

data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/jumia_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:300]] = p['image_url'][:500]

data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:300]] = p['image_url'][:500]

data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:300]] = p['image_url'][:500]

print(f"✅ {len(name_to_image)} images chargées")

# Récupérer les noms depuis BigQuery
print("Récupération noms BigQuery...")
rows = client.query('''
    SELECT DISTINCT name
    FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
    WHERE name IS NOT NULL
''').result()

matched_names = []
for r in rows:
    name = (r.name or '').strip()[:300]
    if name in name_to_image:
        matched_names.append((name, name_to_image[name]))

print(f"✅ {len(matched_names)} noms matchés!")

# UPDATE par batch de 100 avec UPDATE SQL direct
print("UPDATE en cours par batch...")
batch_size = 100
total_updated = 0

for i in range(0, len(matched_names), batch_size):
    batch = matched_names[i:i+batch_size]
    
    # Construire CASE WHEN
    cases = []
    for name, url in batch:
        n = name.replace("\\", "\\\\").replace("'", "\\'")
        u = url.replace("\\", "\\\\").replace("'", "\\'")
        cases.append(f"WHEN name = '{n}' THEN '{u}'")
    
    names_list = ", ".join([f"'{n.replace(chr(39), chr(92)+chr(39))}'" for n, u in batch])
    
    update_sql = f"""
    UPDATE `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
    SET image_url = CASE
        {chr(10).join(cases)}
        ELSE image_url
    END
    WHERE name IN ({names_list})
    """
    
    try:
        job = client.query(update_sql)
        job.result()
        total_updated += len(batch)
        print(f"✅ Batch {i}-{i+len(batch)} OK — {total_updated} mis à jour")
    except Exception as e:
        print(f"❌ Erreur batch {i}: {str(e)[:100]}")
    
    time.sleep(2)

# Vérification finale
print("\nVérification finale...")
rows_check = client.query("""
SELECT source,
    COUNT(*) as total,
    COUNTIF(image_url IS NOT NULL AND image_url != '') as with_image
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
GROUP BY source
""").result()

print("\n📊 Résultat:")
for r in rows_check:
    print(f"  {r.source}: {r.with_image}/{r.total} avec images ✅")

print(f"\n🎉 DONE! {total_updated} produits mis à jour avec images!")