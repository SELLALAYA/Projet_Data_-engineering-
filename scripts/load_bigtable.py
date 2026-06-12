import json
import os
import glob
from datetime import datetime, timezone
from google.cloud import bigtable

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/gcp-credentials-new.json"

PROJECT_ID = "project-32a82952-90fa-4dd7-b9c"
INSTANCE_ID = "price-intelligence"
TABLE_ID = "prices"

client = bigtable.Client(project=PROJECT_ID, admin=False)
table = client.instance(INSTANCE_ID).table(TABLE_ID)

def safe_bytes(value):
    return str(value).encode('utf-8') if value is not None else b''

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def load_to_bigtable():
    from google.cloud.bigtable.row_set import RowSet
    files = glob.glob("/opt/airflow/data/raw/*.json")
    print(f"Found {len(files)} files")
    
    total_written = 0
    total_alerts = 0

    for filepath in files:
        if os.path.getsize(filepath) == 0:
            print(f"[SKIP] {filepath} is empty")
            continue
            
        source = os.path.basename(filepath).replace(".json", "").replace("_", ".")
        try:
            with open(filepath, encoding='utf-8') as f:
                products = json.load(f)
        except Exception as e:
            print(f"[ERROR] {filepath}: {e}")
            continue

        alerts = []
        
        for product_chunk in chunk_list(products, 500):
            row_set = RowSet()
            valid_products = []
            
            for p in product_chunk:
                name = p.get("product_name", "").strip()
                price = p.get("price")
                src = p.get("source", source)
                
                if not name or not price:
                    continue
                    
                product_key = f"{src}#{name}"[:100]
                row_set.add_row_key(product_key.encode('utf-8'))
                valid_products.append((p, product_key))
                
            if not valid_products:
                continue
                
            prev_prices = {}
            try:
                for row in table.read_rows(row_set=row_set):
                    if row and "price_cf" in row.cells:
                        cells = row.cells["price_cf"]
                        if b"price" in cells:
                            prev_prices[row.row_key.decode('utf-8')] = float(cells[b"price"][0].value.decode('utf-8'))
            except Exception as e:
                print(f"Error reading batch previous prices: {e}")

            mutations = []
            for p, product_key in valid_products:
                name = p.get("product_name", "").strip()
                price = p.get("price")
                src = p.get("source", source)
                ts = datetime.now(timezone.utc).isoformat()
                
                prev_price = prev_prices.get(product_key)
                price_changed = prev_price is not None and abs(float(price) - prev_price) > 0.01

                if price_changed:
                    change_pct = ((float(price) - prev_price) / prev_price) * 100
                    alerts.append({
                        "product": name,
                        "source": src,
                        "old_price": prev_price,
                        "new_price": float(price),
                        "change_pct": round(change_pct, 2)
                    })

                row = table.direct_row(product_key.encode('utf-8'))
                row.set_cell("price_cf", "price", safe_bytes(price))
                row.set_cell("price_cf", "source", safe_bytes(src))
                row.set_cell("price_cf", "category", safe_bytes(p.get("category", "")))
                row.set_cell("price_cf", "currency", safe_bytes(p.get("currency", "MAD")))
                row.set_cell("metadata_cf", "product_name", safe_bytes(name))
                row.set_cell("metadata_cf", "scraped_at", safe_bytes(ts))
                row.set_cell("metadata_cf", "url", safe_bytes(p.get("url", "")))

                if prev_price:
                    row.set_cell("agg_cf", "prev_price", safe_bytes(prev_price))
                    row.set_cell("agg_cf", "price_changed", b"true" if price_changed else b"false")

                if p.get("old_price"):
                    row.set_cell("agg_cf", "old_price", safe_bytes(p["old_price"]))
                    row.set_cell("agg_cf", "is_discounted", b"true")

                mutations.append(row)

            if mutations:
                table.mutate_rows(mutations)
                total_written += len(mutations)

        print(f"[OK] {source}: {len(products)} produits, {len(alerts)} price changes detected")
        total_alerts += len(alerts)

        for alert in alerts[:5]:
            direction = "UP" if alert["change_pct"] > 0 else "DOWN"
            print(f"  [{direction}] {alert['product'][:50]} | {alert['old_price']} -> {alert['new_price']} MAD ({alert['change_pct']:+.1f}%)")

    print(f"\nTOTAL: {total_written} rows written to Bigtable")
    print(f"TOTAL ALERTS: {total_alerts} price changes detected")

if __name__ == "__main__":
    load_to_bigtable()