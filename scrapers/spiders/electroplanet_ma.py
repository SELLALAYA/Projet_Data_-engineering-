import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timezone

URLS = [
    ("https://www.electroplanet.ma/telephones-et-accessoires/smartphones", "Téléphones & Smartphones"),
    ("https://www.electroplanet.ma/telephones-et-accessoires/tablettes", "Informatique"),
    ("https://www.electroplanet.ma/informatique/ordinateurs-portables", "Informatique"),
    ("https://www.electroplanet.ma/informatique/ordinateurs-de-bureau", "Informatique"),
    ("https://www.electroplanet.ma/electromenager/refrigerateurs", "Électroménager"),
    ("https://www.electroplanet.ma/electromenager/lave-linge", "Électroménager"),
    ("https://www.electroplanet.ma/electromenager/climatiseurs", "Électroménager"),
    ("https://www.electroplanet.ma/petit-electromenager/cafetières", "Électroménager"),
]

def detect_category(name):
    name_lower = name.lower()
    if any(k in name_lower for k in [
        'iphone', 'samsung', 'xiaomi', 'oppo', 'huawei', 'smartphone',
        'telephone', 'mobile', 'realme', 'oneplus', 'redmi', 'galaxy',
        'infinix', 'tecno', 'itel', 'vivo', 'nokia', 'motorola']):
        return "Téléphones & Smartphones"
    if any(k in name_lower for k in [
        'tablette', 'tablet', 'ipad', 'laptop', 'ordinateur', ' pc ',
        'bureau', 'portable', 'ecran', 'clavier', 'souris', 'imprimante',
        'disque', 'memoire', 'ram', 'processeur', 'carte graphique']):
        return "Informatique"
    if any(k in name_lower for k in [
        'refriger', 'frigo', 'congel', 'lave-linge', 'lavsech', 'mal ',
        'machine a laver', 'climatiseur', 'clim', 'four', 'micro-onde',
        'aspirateur', 'aspira', 'cafetiere', 'electromenager', 'lave vais',
        'seche', 'hotte', 'fer a repasser', 'fer vapeur', 'defroisseur',
        'friteuse', 'purificateur', 'antimoustique', 'mixeur', 'blender',
        'grille-pain', 'bouilloire', 'robot', 'cuiseur', 'plaque',
        'beko', 'arthur martin', 'aeg', 'hisense', 'rowenta', 'tefal',
        'taurus', 'severin', 'kenwood', 'laurastar', 'dyson', 'solac']):
        return "Électroménager"
    return "Électroménager"

def clean_price(price_text):
    try:
        cleaned = price_text.replace('DH', '').replace('\xa0', '').replace(' ', '').replace(',', '.').strip()
        return float(cleaned)
    except:
        return None

def get_driver():
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def scrape_electroplanet():
    all_products = []
    seen_names = set()

    for url, forced_category in URLS:
        cat_name = url.split('/')[-1]
        print(f"\n[Electroplanet] Scraping : {cat_name}")

        driver = get_driver()
        try:
            driver.get(url)
            time.sleep(6)

            # Scroll pour charger tous les produits
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            items = driver.find_elements(By.CSS_SELECTOR, '.product-item')
            print(f"  {len(items)} produits détectés...", end=" ", flush=True)

            count = 0
            for item in items:
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '.product-item-link').text.strip()
                    except:
                        name = item.find_element(By.CSS_SELECTOR, 'a').text.strip()

                    if not name or name in seen_names:
                        continue
                    seen_names.add(name)

                    # Utiliser la catégorie forcée par l'URL ou détecter automatiquement
                    category = detect_category(name) if detect_category(name) != "Électroménager" else forced_category

                    try:
                        price_text = item.find_element(By.CSS_SELECTOR, '.price').text
                        price = clean_price(price_text)
                    except:
                        price = None

                    try:
                        old_price_text = item.find_element(By.CSS_SELECTOR, '.old-price .price').text
                        old_price = clean_price(old_price_text)
                    except:
                        old_price = None

                    try:
                        image_url = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                    except:
                        image_url = None

                    try:
                        product_url = item.find_element(By.CSS_SELECTOR, 'a.product-item-link').get_attribute('href')
                    except:
                        try:
                            product_url = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                        except:
                            product_url = None

                    all_products.append({
                        "name": name,
                        "price": price,
                        "old_price": old_price,
                        "discount": None,
                        "rating": None,
                        "currency": "MAD",
                        "category": category,
                        "image_url": image_url,
                        "url": product_url,
                        "source": "electroplanet.ma",
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                    count += 1
                except:
                    continue

            print(f"✅ {count} produits uniques")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        finally:
            driver.quit()

    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/electroplanet_ma.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    from collections import Counter
    cats = Counter(p['category'] for p in all_products)
    print(f"\n📊 Répartition par catégorie:")
    for cat, nb in cats.items():
        print(f"  {cat}: {nb} produits")

    print(f"\n🎉 TOTAL : {len(all_products)} produits → data/raw/electroplanet_ma.json")

if __name__ == "__main__":
    scrape_electroplanet()