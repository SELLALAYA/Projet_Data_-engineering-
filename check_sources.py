import requests
sources = ['jumia.ma', 'avito.ma', 'amazon.com', 'connecto.ma']
for s in sources:
    try:
        r = requests.get(f'http://localhost:8000/prices?source={s}&limit=1')
        print(f"{s}: {r.status_code} total={r.json().get('total', 0)}")
    except Exception as e:
        print(f"{s}: Error {e}")
