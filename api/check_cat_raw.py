import json

print("=== JUMIA ===")
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/jumia_ma.json', encoding='utf-8'))
cats = {}
for p in data:
    cat = p.get('category', 'None')
    cats[cat] = cats.get(cat, 0) + 1
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

print("\n=== AVITO ===")
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/avito_ma.json', encoding='utf-8'))
cats = {}
for p in data:
    cat = p.get('category', 'None')
    cats[cat] = cats.get(cat, 0) + 1
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

print("\n=== AMAZON ===")
data = json.load(open('C:/Users/Administrateur/Downloads/price_intelligence_jumia (1)/price_intelligence/data/raw/amazon_ma.json', encoding='utf-8'))
cats = {}
for p in data:
    cat = p.get('category', 'None')
    cats[cat] = cats.get(cat, 0) + 1
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")