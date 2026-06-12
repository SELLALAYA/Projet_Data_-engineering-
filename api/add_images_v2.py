import json
import os
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

# Charger toutes les images depuis les JSON par NOM
print("Chargement des images depuis JSON...")
name_to_image = {}

# Jumia
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/jumia_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:200]] = p['image_url']
print(f"✅ Jumia: {len([k for k in name_to_image])} images chargées")

# Amazon
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:200]] = p['image_url']
print(f"✅ Amazon ajouté")

# Avito
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json', encoding='utf-8'))
for p in data:
    if p.get('name') and p.get('image_url'):
        name_to_image[p['name'].strip()[:200]] = p['image_url']
print(f"✅ Avito ajouté")

print(f"\nTotal images disponibles: {len(name_to_image)}")

# Récupérer tous les produits de BigQuery
print("\nRécupération produits BigQuery...")
rows = client.query('''
    SELECT product_id, name 
    FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
''').result()

matched = 0
unmatched = 0
update_rows = []

for r in rows:
    name_clean = (r.name or '').strip()[:200]
    if name_clean in name_to_image:
        update_rows.append({
            'product_id_str': str(r.product_id) if r.product_id else '',
            'image_url': name_to_image[name_clean][:500]
        })
        matched += 1
    else:
        unmatched += 1

print(f"✅ Matched: {matched} produits avec images")
print(f"❌ Sans image: {unmatched} produits")

# Créer table temporaire
print("\nCréation table temporaire...")
temp_table_id = 'project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.temp_images'
temp_schema = [
    bigquery.SchemaField('product_id_str', 'STRING'),
    bigquery.SchemaField('image_url', 'STRING'),
]
try:
    client.delete_table(temp_table_id)
except:
    pass

temp_table = bigquery.Table(temp_table_id, schema=temp_schema)
client.create_table(temp_table)
print("✅ Table temporaire créée!")

# Insérer par batch
batch_size = 500
total = 0
for i in range(0, len(update_rows), batch_size):
    batch = update_rows[i:i+batch_size]
    errors = client.insert_rows_json(temp_table_id, batch)
    if not errors:
        total += len(batch)
        print(f"✅ Batch {i}-{i+len(batch)} OK")
    else:
        print(f"❌ Erreur: {errors[0]}")

print(f"\n🎉 DONE! {total} images prêtes!")
print("Lance maintenant: python update_bq_images.py")