import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

print("Ajout colonne image_url...")
try:
    table_ref = client.get_table('project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned')
    new_schema = table_ref.schema + [
        bigquery.SchemaField('image_url', 'STRING', mode='NULLABLE')
    ]
    table_ref.schema = new_schema
    client.update_table(table_ref, ['schema'])
    print("✅ Colonne image_url ajoutée!")
except Exception as e:
    print(f"⚠️ {e}")

# Vérification schema
table = client.get_table('project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned')
print("\nSchema actuel:")
for field in table.schema:
    print(f"  {field.name} — {field.field_type}")