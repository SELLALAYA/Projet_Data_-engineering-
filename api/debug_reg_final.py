from google.cloud import bigquery
import os
import pandas as pd
import numpy as np

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

project_id = 'project-32a82952-90fa-4dd7-b9c'
TABLE = f'`{project_id}.price_intelligence_dbt.prices_cleaned`'

ALLOWED_BQ_CATS = ['Informatique', 'Telephones & Smartphones', 'Electromenager']
START_JUNK = ['pochette', 'coque', 'etui', 'étui', 'protecteur', 'verre trempé', 'incassable', 'film', 'cable', 'câble', 'adaptateur', 'chargeur', 'batterie externe', 'power bank', 'station de charge', 'tapis de souris', 'sac à dos', 'sacoche', 'housse', 'cartouche', 'toner', 'encre', 'papier photo', 'porte-clés', 'mousqueton', 'support mural', 'support pc', 'support rotatif']
START_JUNK_REGEX = r'(?i)^(' + '|'.join(START_JUNK) + r')\b'

# Simplified regex for testing
CONTAINS_JUNK_REGEX = r'(?i)(\b(moto|auto)\b)'

EXCLUDE_FILTERS = [
    "price > 100",
    "price < 150000",
    f"(category IN ({', '.join([f"'{c}'" for c in ALLOWED_BQ_CATS])}) OR (LOWER(name) LIKE '%tv%' OR LOWER(name) LIKE '%tablet%' OR LOWER(name) LIKE '%ipad%'))",
    f"NOT REGEXP_CONTAINS(LOWER(name), r'{START_JUNK_REGEX}')",
    "LENGTH(name) < 300",
    "(source != 'avito.ma' OR (price BETWEEN 250 AND 50000))"
]
EXCLUDE_WHERE = " AND ".join(EXCLUDE_FILTERS)

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

query = f"""
WITH base_data AS (
    SELECT *, {VIRTUAL_CAT_SQL} as virtual_category
    FROM {TABLE}
    WHERE {EXCLUDE_WHERE}
)
SELECT price, discount_pct, rating, scraped_at, virtual_category FROM base_data
"""

print("🚀 Testing FULL backend filtering logic...")
df = client.query(query).to_dataframe()
print(f"📊 Rows after EXCLUDE_WHERE: {len(df)}")
print(f"📋 Virtual Category Counts:\n{df['virtual_category'].value_counts()}")

df_reg = df[df['virtual_category'] != 'Other'].copy()
print(f"📊 Rows after removing 'Other': {len(df_reg)}")

df_reg['rating'] = df_reg['rating'].fillna(0)
df_reg['discount_pct'] = df_reg['discount_pct'].fillna(0)
df_clean = df_reg.dropna()

print(f"🧹 Rows after final dropna(): {len(df_clean)}")
if not df_clean.empty:
    print(f"✅ Samples:\n{df_clean.head()}")
