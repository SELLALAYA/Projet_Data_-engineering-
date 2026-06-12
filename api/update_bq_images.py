import os
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

print("Ajout colonne image_url dans prices_cleaned...")
try:
    table_ref = client.get_table('project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned')
    new_schema = table_ref.schema + [
        bigquery.SchemaField('image_url', 'STRING', mode='NULLABLE')
    ]
    table_ref.schema = new_schema
    client.update_table(table_ref, ['schema'])
    print("✅ Colonne image_url ajoutée!")
except Exception as e:
    print(f"⚠️ Colonne existe déjà ou erreur: {e}")

print("\nMise à jour images via MERGE...")
merge_query = """
MERGE `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned` T
USING `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.temp_images` S
ON CAST(T.product_id AS STRING) = S.product_id_str
WHEN MATCHED THEN
  UPDATE SET T.image_url = S.image_url
"""

job = client.query(merge_query)
job.result()
print("✅ MERGE terminé!")

# Vérification
print("\nVérification...")
rows = client.query("""
SELECT 
  COUNT(*) as total,
  COUNTIF(image_url IS NOT NULL AND image_url != '') as with_image
FROM `project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`
""").result()

for r in rows:
    print(f"✅ Total produits    : {r.total}")
    print(f"✅ Avec image_url   : {r.with_image}")
    print(f"❌ Sans image       : {r.total - r.with_image}")

print("\n🎉 DONE! Les images sont dans BigQuery!")
print("Maintenant redémarre FastAPI et rafraîchis Angular!")