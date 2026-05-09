import os
import json
import datetime
import hashlib
from google.cloud import bigtable
from google.cloud.bigtable import row

def load_to_bigtable():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/gcp-credentials.json'

    client = bigtable.Client(project='project-32a82952-90fa-4dd7-b9c', admin=True)
    instance = client.instance('price-intelligence')
    table = instance.table('prices')

    sources = ['jumia_ma', 'avito_ma', 'amazon_ma', 'electroplanet_ma']
    total = 0
    batch = []
    BATCH_SIZE = 500

    def flush_batch(batch):
        if batch:
            table.mutate_rows(batch)
            print(f"  ✅ Batch de {len(batch)} produits envoyé!")
        return []

    for source in sources:
        path = f'/opt/airflow/data/raw/{source}.json'
        if not os.path.exists(path):
            print(f"⚠️ Fichier manquant: {path}")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        print(f"📦 Traitement {source}: {len(products)} produits...")

        for product in products:
            try:
                # ── product_id ──────────────────────────
                name = str(product.get('name', '')).strip()
                if not name:
                    continue
                product_id = hashlib.md5(name.encode()).hexdigest()[:12]

                # ── timestamp ───────────────────────────
                scraped_at_str = product.get('scraped_at', '')
                try:
                    scraped_at_dt = datetime.datetime.fromisoformat(
                        str(scraped_at_str).replace('+00:00', '')
                    )
                    ts = scraped_at_dt.strftime('%Y%m%d%H%M%S')
                except Exception:
                    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

                # ── Row key: product_id#timestamp ────────
                row_key = f"{product_id}#{ts}".encode()
                bt_row = table.direct_row(row_key)

                # ── Valeurs sécurisées ───────────────────
                try:
                    safe_price = float(product.get('price') or 0)
                except:
                    safe_price = 0.0

                try:
                    safe_old = float(product.get('old_price') or safe_price)
                except:
                    safe_old = safe_price

                discount_str = str(product.get('discount', '0%')).replace('%', '').strip()
                try:
                    discount_val = float(discount_str) if discount_str else 0.0
                except:
                    discount_val = 0.0

                price_change = round(safe_old - safe_price, 2)

                # ── price_cf ─────────────────────────────
                bt_row.set_cell('price_cf', b'current_price', str(safe_price).encode())
                bt_row.set_cell('price_cf', b'old_price',     str(safe_old).encode())
                bt_row.set_cell('price_cf', b'discount_pct',  str(round(discount_val, 2)).encode())
                bt_row.set_cell('price_cf', b'currency',      str(product.get('currency', 'MAD')).encode())

                # ── metadata_cf ──────────────────────────
                bt_row.set_cell('metadata_cf', b'name',       name.encode())
                bt_row.set_cell('metadata_cf', b'category',   str(product.get('category', '')).encode())
                bt_row.set_cell('metadata_cf', b'source',     str(product.get('source', '')).encode())
                bt_row.set_cell('metadata_cf', b'rating',     str(product.get('rating', '')).encode())
                bt_row.set_cell('metadata_cf', b'url',        str(product.get('url', '')).encode())
                bt_row.set_cell('metadata_cf', b'scraped_at', ts.encode())

                # ── agg_cf ───────────────────────────────
                bt_row.set_cell('agg_cf', b'price_change',  str(price_change).encode())
                bt_row.set_cell('agg_cf', b'is_discounted', b'1' if discount_val > 0 else b'0')
                bt_row.set_cell('agg_cf', b'last_updated',  ts.encode())

                batch.append(bt_row)
                total += 1

                # ── Flush tous les 500 ───────────────────
                if len(batch) >= BATCH_SIZE:
                    batch = flush_batch(batch)

            except Exception as e:
                print(f"⚠️ Produit ignoré: {e}")
                continue

    # ── Flush le reste ───────────────────────────
    flush_batch(batch)

    print(f"\n✅ TOTAL: {total} produits chargés dans Bigtable!")
    print(f"   Column families: price_cf ✅ metadata_cf ✅ agg_cf ✅")
    print(f"   Row key format: product_id#timestamp ✅")
    return total