from google.cloud import bigquery
import os
import pandas as pd
import numpy as np

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

VIRTUAL_CAT_SQL = """
CASE 
    WHEN (LOWER(name) LIKE '%tv%' OR LOWER(name) LIKE '%téléviseur%' OR LOWER(name) LIKE '%televiseur%') THEN 'TVs'
    WHEN (LOWER(name) LIKE '%tablet%' OR LOWER(name) LIKE '%ipad%' OR LOWER(name) LIKE '%tab %') THEN 'Tablets'
    WHEN LOWER(category) = 'telephones & smartphones' THEN 'Smartphones'
    WHEN LOWER(category) = 'informatique' THEN 'Informatique'
    WHEN LOWER(category) = 'electromenager' THEN 'Electromenager'
    ELSE 'Other'
END
"""

# Minimal EXCLUDE_WHERE to see what we get
EXCLUDE_WHERE = "price > 100 AND price < 150000"

query = f"""
WITH base_data AS (
    SELECT *, {VIRTUAL_CAT_SQL} as virtual_category
    FROM {TABLE}
    WHERE {EXCLUDE_WHERE}
)
SELECT price, discount_pct, rating, scraped_at FROM base_data WHERE virtual_category != 'Other'
"""

print("🚀 Running regression test query...")
df = client.query(query).to_dataframe()
print(f"📊 Total rows fetched: {len(df)}")
print(f"📋 Nulls in rating: {df['rating'].isna().sum()}")
print(f"📋 Nulls in discount_pct: {df['discount_pct'].isna().sum()}")

df_clean = df.dropna()
print(f"🧹 Rows after dropna(): {len(df_clean)}")

if len(df_clean) < 10:
    print("❌ NOT ENOUGH DATA FOR REGRESSION")
else:
    print("✅ ENOUGH DATA FOR REGRESSION")
