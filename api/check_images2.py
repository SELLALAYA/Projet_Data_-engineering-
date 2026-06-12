import json

# Vérifier jumia
try:
    data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/jumia_ma.json', encoding='utf-8'))
    with_img = [p for p in data if p.get('image_url') or p.get('image') or p.get('img')]
    print(f"Jumia: {len(data)} produits, {len(with_img)} avec images")
    if with_img:
        first = with_img[0]
        key = 'image_url' if 'image_url' in first else 'image' if 'image' in first else 'img'
        print(f"  Clé image: '{key}'")
        print(f"  Exemple: {first[key][:80]}")
except Exception as e:
    print(f"Jumia erreur: {e}")

# Vérifier amazon
try:
    data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))
    with_img = [p for p in data if p.get('image_url') or p.get('image') or p.get('img')]
    print(f"\nAmazon: {len(data)} produits, {len(with_img)} avec images")
    if with_img:
        first = with_img[0]
        key = 'image_url' if 'image_url' in first else 'image' if 'image' in first else 'img'
        print(f"  Clé image: '{key}'")
        print(f"  Exemple: {first[key][:80]}")
except Exception as e:
    print(f"Amazon erreur: {e}")

# Vérifier avito
try:
    data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json', encoding='utf-8'))
    with_img = [p for p in data if p.get('image_url') or p.get('image') or p.get('img')]
    print(f"\nAvito: {len(data)} produits, {len(with_img)} avec images")
    if with_img:
        first = with_img[0]
        key = 'image_url' if 'image_url' in first else 'image' if 'image' in first else 'img'
        print(f"  Clé image: '{key}'")
        print(f"  Exemple: {first[key][:80]}")
except Exception as e:
    print(f"Avito erreur: {e}")