import json
import os
import base64
from google.cloud import bigquery
from datetime import datetime

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'

# Configuration
RAW_FILE = 'C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json'
TABLE_ID = 'project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

def get_category_from_url(url):
    url = url.lower()
    if any(k in url for k in ['ordinateurs_portables', 'informatique', 'tablettes', 'imprimantes']):
        return 'Informatique'
    if any(k in url for k in ['telephones', 'smartphones', 'smartphone']):
        return 'Telephones & Smartphones'
    if any(k in url for k in ['electromenager', 'image_et_son', 'accessoires_informatique']):
        return 'Electromenager'
    return None

def is_junk(name, url):
    name = name.lower()
    url = url.lower()
    
    # Real estate and cars keywords
    real_estate = ['villa', 'appartement', 'maison', 'terrain', 'étage', 'chambre', 'salon', 'm²', 'immobilier', 'résidence']
    vehicles = ['voiture', 'auto', 'moto', 'vélo', 'camion', 'bateau']
    professional = ['bureau', 'local', 'commerce', 'fonds de commerce', 'usine', 'entrepôt']
    
    # If URL contains these, it's definitely junk for us
    if any(k in url for k in ['immobilier', 'voitures_d_occasion', 'motos', 'emplois', 'services']):
        return True
        
    # If name contains these, it's likely junk
    if any(k in name for k in real_estate + vehicles + professional):
        return True
        
    return False

# 1. Supprimer les anciens Avito
print("Suppression des anciens produits Avito...")
client.query(f"DELETE FROM `{TABLE_ID}` WHERE source = 'avito.ma'").result()
print("Anciens produits supprimés")

# 2. Charger et filtrer les données
print(f"Chargement de {RAW_FILE}...")
with open(RAW_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []
skipped_junk = 0
skipped_no_cat = 0
skipped_no_price = 0

for i, p in enumerate(data):
    name = p.get('product_name') or p.get('name') or 'Unknown'
    url = p.get('url', '')
    price = p.get('price')
    
    # Filter junk
    if is_junk(name, url):
        skipped_junk += 1
        continue
        
    # Get correct category
    cat = get_category_from_url(url)
    if not cat:
        skipped_no_cat += 1
        continue
        
    # Check price
    try:
        if price is None:
            skipped_no_price += 1
            continue
        price_val = float(str(price).replace(' ', '').replace('DH', ''))
        if price_val <= 0 or price_val > 50000:
            skipped_no_price += 1
            continue
    except:
        skipped_no_price += 1
        continue

    # Prepare row
    product_id_bytes = base64.b64encode(f'avito_{i:04d}'.encode('utf-8')).decode('utf-8')
    
    rows.append({
        'product_id': product_id_bytes,
        'name': name[:500],
        'price': price_val,
        'old_price': price_val,
        'discount_pct': 0.0,
        'rating': 4.0,
        'currency': 'MAD',
        'category': cat,
        'source': 'avito.ma',
        'image_url': p.get('image_url', ''),
        'url': url,
        'scraped_at': datetime.fromtimestamp(p.get('scraped_at', 1779559284)).strftime('%Y-%m-%dT%H:%M:%SZ')
    })

print(f"Stats: Junk={skipped_junk}, NoCat={skipped_no_cat}, NoPrice={skipped_no_price}, Ready={len(rows)}")

# 3. Import par batch
batch_size = 200
total_inserted = 0
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    errors = client.insert_rows_json(TABLE_ID, batch)
    if errors:
        print(f'Erreur batch {i}: {errors[0]}')
    else:
        total_inserted += len(batch)
        print(f'Batch {i}-{i+len(batch)} importé')

print(f'DONE! {total_inserted} produits Avito importés!')
