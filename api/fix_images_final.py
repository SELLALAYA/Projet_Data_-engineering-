import json
import os
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

# Charger toutes les images par NOM
print("Chargement images...")
name_to_image = {}

# Jumia
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/jumia_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:500]] = p['image_url']
print(f"✅ Jumia: {len(name_to_image)} images")

# Amazon
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:500]] = p['image_url']
print(f"✅ Amazon ajouté")

# Avito
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:500]] = p['image_url']
print(f"✅ Avito ajouté")

print(f"Total: {len(name_to_image)} images chargées")

# Recréer table temporaire avec NAME comme clé
print("\nRecréation table temporaire...")
temp_table_id = 'project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.temp_images'
temp_schema = [
    bigquery.SchemaField('product_name', 'STRING'),
    bigquery.SchemaField('image_url', 'STRING'),
]
try:
    client.delete_table(temp_table_id)
    print("✅ Ancienne table supprimée")
except:
    pass

temp_table = bigquery.Table(temp_table_id, schema=temp_schema)
client.create_table(temp_table)
print("✅ Nouvelle table créée!")

# Insérer avec product_name comme clé
rows = [{'product_name': name[:500], 'image_url': url[:500]} 
        for name, url in name_to_image.items()]

batch_size = 500
total = 0
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    errors = client.insert_rows_json(temp_table_id, batch)
    if not errors:
        total += len(batch)
        print(f"✅ Batch {i}-{i+len(batch)} OK")
    else:
        print(f"❌ Erreur: {errors[0]}")

print(f"\n✅ {total} images insérées!")

# MERGE par nom
import time
print("\nAttente 10s pour propagation...")
time.sleep(10)

print("MERGE en cours...")
merge_query = """
MERGE `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned` T
USING `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.temp_images` S
ON T.name = S.product_name
WHEN MATCHED THEN
  UPDATE SET T.image_url = S.image_url
"""
job = client.query(merge_query)
job.result()
print("✅ MERGE terminé!")

# Vérification finale
rows_check = client.query("""
SELECT 
  source,
  COUNT(*) as total,
  COUNTIF(image_url IS NOT NULL AND image_url != '') as with_image
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
GROUP BY source
""").result()

print("\n📊 Résultat final:")
for r in rows_check:
    print(f"  {r.source}: {r.with_image}/{r.total} avec images")

print("\n🎉 DONE!")