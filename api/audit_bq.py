from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

TABLES = ['prices_aggregated', 'prices_cleaned', 'prices_raw', 'stg_prices', 'temp_images']
DATASET = 'price_intelligence_dbt'

print(f"Checking tables in {DATASET}...")

for t_id in TABLES:
    full_id = f"`{client.project}.{DATASET}.{t_id}`"
    print(f"\nTable: {t_id}")
    try:
        table = client.get_table(full_id.replace('`',''))
        print(f"Columns: {[f.name for f in table.schema]}")
        
        # Count rows
        count_q = f"SELECT COUNT(*) as count FROM {full_id}"
        count = list(client.query(count_q).result())[0].count
        print(f"Rows: {count}")
        
        if count > 0:
            # Check for image_url content
            if 'image_url' in [f.name for f in table.schema]:
                img_q = f"SELECT image_url FROM {full_id} WHERE image_url IS NOT NULL LIMIT 1"
                imgs = list(client.query(img_q).result())
                if imgs:
                    print(f"Sample Image: {imgs[0].image_url[:60]}...")
                else:
                    print("Sample Image: ALL NULL")
    except Exception as e:
        print(f"Error: {e}")
