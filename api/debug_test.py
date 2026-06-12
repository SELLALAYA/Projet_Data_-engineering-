import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
from google.cloud import bigquery

client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

try:
    rows = client.query(f"""
        SELECT name, MIN(price) as price, ANY_VALUE(source) as source, ANY_VALUE(image_url) as image_url 
        FROM {TABLE} 
        WHERE price > 0 AND price < 500000 
        GROUP BY name, source 
        LIMIT 3
    """).result()
    for r in rows:
        print(r.name[:40], r.price, r.source)
    print('OK! Query works!')
except Exception as e:
    print(f'ERROR: {e}')