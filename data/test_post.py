import urllib.request
import json

data = {"product_name": "Test Realtime", "price": 99.99, "source": "test", "scraped_at": "now", "category": "test"}
url = "http://localhost:8888/contentListener"

req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req) as r:
        print(f"Status: {r.getcode()}")
except Exception as e:
    print(f"Error: {e}")
