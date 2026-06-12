from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'api/credentials.json'
project_id = 'project-32a82952-90fa-4dd7-b9c'
client = bigquery.Client(project=project_id)

table_id = f"{project_id}.price_intelligence_dbt.prices_cleaned"

junk_words = ['voiture', 'livre', 'roman', 'appartement', 'villa', 'terrain', 'moteur', 'pneu', 'vêtement', 'habit', 'chaussure']

print(f"Searching for misclassified junk in {table_id}...")

for word in junk_words:
    query = f"SELECT name, category, source FROM `{table_id}` WHERE LOWER(name) LIKE '%{word}%' LIMIT 5"
    results = list(client.query(query).result())
    if results:
        print(f"\nFound items containing '{word}':")
        for row in results:
            print(f" - [{row.category}] {row.name} ({row.source})")
    else:
        print(f"No items found for '{word}'")
