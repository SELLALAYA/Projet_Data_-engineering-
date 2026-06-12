import json
import os
import base64
from google.cloud import bigquery
from datetime import datetime

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'

# Charger les donnees
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))

products_with_price = [p for p in data if p['price'] is not None and p['price'] > 0]
print(f'Produits avec prix: {len(products_with_price)}')

rows = []
for i, p in enumerate(products_with_price):
    price = float(p['price'])
    old_price = float(p['old_price']) if p.get('old_price') and p['old_price'] else price

    discount_pct = 0.0
    if old_price and old_price > price:
        discount_pct = round((old_price - price) / old_price * 100, 1)

    # product_id doit etre BYTES encode en base64
    product_id_bytes = base64.b64encode(f'amazon_{i:04d}'.encode('utf-8')).decode('utf-8')

    # scraped_at doit etre TIMESTAMP format correct
    try:
        scraped_at = p.get('scraped_at', '2026-04-27T00:00:00+00:00')
        # Nettoyer le format
        scraped_at = scraped_at.replace('+00:00', 'Z') if '+00:00' in scraped_at else scraped_at
    except:
        scraped_at = '2026-04-27T00:00:00Z'

    rows.append({
        'product_id': product_id_bytes,
        'name': (p.get('name') or 'Unknown')[:500],
        'price': price,
        'old_price': old_price,
        'discount_pct': discount_pct,
        'rating': float(p['rating']) if p.get('rating') else 4.0,
        'currency': 'MAD',
        'category': p.get('category', 'Informatique'),
        'source': 'amazon.com',
        'scraped_at': scraped_at
    })

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
table_id = 'project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned'

batch_size = 200
total_inserted = 0
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    errors = client.insert_rows_json(table_id, batch)
    if errors:
        print(f'Erreur batch {i}: {errors[0]}')
    else:
        total_inserted += len(batch)
        print(f'✅ Batch {i}-{i+len(batch)} importé OK')

print(f'\n🎉 DONE! {total_inserted} produits amazon importés dans BigQuery!')

# Verification finale
print('\nVerification dans BigQuery...')
check_client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
rows_check = check_client.query('SELECT source, COUNT(*) as total FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned` GROUP BY source ORDER BY total DESC').result()
for r in rows_check:
    print(f'  {r.source}: {r.total} produits')