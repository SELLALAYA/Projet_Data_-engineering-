import os
import requests
from google.cloud import bigquery
from datetime import datetime

# Configuration
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Administrateur/Documents/fullstack/api/credentials.json'
project_id = 'project-32a82952-90fa-4dd7-b9c'
client = bigquery.Client(project=project_id)
TABLE = f'`{project_id}.price_intelligence_dbt.prices_cleaned`'

def check_for_price_alerts():
    """
    Scans BigQuery for products with significant price drops (>20%)
    and displays them in a summary report.
    """
    print("=" * 60)
    print(f"📊 PRICE INTELLIGENCE ALERT SYSTEM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    query = f"""
    SELECT name, source, price, old_price, discount_pct, url, category
    FROM {TABLE}
    WHERE price > 0 
      AND old_price > price 
      AND discount_pct >= 20
      AND price < 100000 -- Filter out outliers
    ORDER BY discount_pct DESC
    LIMIT 15
    """
    
    try:
        results = client.query(query).result()
        alerts = list(results)
        
        if not alerts:
            print("✨ No major price drops detected in the last scan.")
            return

        print(f"🔥 Found {len(alerts)} High-Impact Price Drops:")
        print("-" * 60)
        
        for i, row in enumerate(alerts, 1):
            name = row.name[:55] + "..." if len(row.name) > 55 else row.name
            print(f"{i}. [{row.source}] {name}")
            print(f"   Category: {row.category}")
            print(f"   Price: {row.price:,.0f} MAD (Was {row.old_price:,.0f} MAD)")
            print(f"   SAVINGS: {row.discount_pct:.0f}% OFF (Delta: {row.old_price - row.price:,.0f} MAD)")
            if row.url:
                print(f"   Link: {row.url}")
            print("-" * 60)
            
        print(f"🎉 Analysis Complete. {len(alerts)} alerts generated.")
        
    except Exception as e:
        print(f"❌ Error during alert generation: {e}")

if __name__ == "__main__":
    check_for_price_alerts()
