import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timezone
from parsel import Selector
import time

CATEGORIES = [
    ("https://www.avito.ma/fr/maroc/telephones_et_tablettes-a_vendre", "Téléphones & Smartphones"),
    ("https://www.avito.ma/fr/maroc/informatique_et_multimedia-a_vendre", "Informatique"),
    ("https://www.avito.ma/fr/maroc/electromenager-a_vendre", "Électroménager"),
]

def scrape_avito():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_products = []

    for url, category in CATEGORIES:
        print(f"\n[Avito] Scraping : {category}")

        for page in range(1, 16):  # 15 pages par catégorie
            page_url = url if page == 1 else f"{url}?o={page}"
            print(f"  Page {page}...", end=" ", flush=True)

            driver.get(page_url)
            time.sleep(5)

            sel = Selector(text=driver.page_source)
            scripts = sel.css("script[id^='search-ad-schema']::text").getall()

            if not scripts:
                print("fin de pagination")
                break

            count = 0
            for script in scripts:
                try:
                    data = json.loads(script)
                    name = data.get("name", "")
                    offers = data.get("offers", {})
                    price_raw = offers.get("price", None)
                    product_url = offers.get("url", "")
                    images = data.get("image", [])

                    if not name:
                        continue

                    try:
                        price = float(str(price_raw).replace(" ", "").replace(",", ".")) if price_raw else None
                    except:
                        price = None

                    product = {
                        "name": name,
                        "price": price,
                        "old_price": None,
                        "discount": None,
                        "rating": None,
                        "currency": "MAD",
                        "category": category,
                        "image_url": images[0] if images else None,
                        "url": product_url,
                        "source": "avito.ma",
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                    all_products.append(product)
                    count += 1
                except Exception:
                    continue

            print(f"✅ {count} produits")

    driver.quit()

    import os
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/avito_ma.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 TOTAL : {len(all_products)} produits → data/raw/avito_ma.json")

if __name__ == "__main__":
    scrape_avito()