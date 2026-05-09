import json
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timezone

KEYWORDS = [
    # Téléphones & Smartphones
    ("iphone", "Téléphones & Smartphones"),
    ("samsung galaxy", "Téléphones & Smartphones"),
    ("xiaomi smartphone", "Téléphones & Smartphones"),
    ("oppo smartphone", "Téléphones & Smartphones"),
    ("huawei smartphone", "Téléphones & Smartphones"),
    ("realme smartphone", "Téléphones & Smartphones"),
    ("oneplus smartphone", "Téléphones & Smartphones"),
    # Informatique
    ("laptop computer", "Informatique"),
    ("pc portable", "Informatique"),
    ("tablette tactile", "Informatique"),
    ("ecran ordinateur", "Informatique"),
    ("clavier souris", "Informatique"),
    ("disque dur externe", "Informatique"),
    # Électroménager
    ("refrigerateur", "Électroménager"),
    ("washing machine", "Électroménager"),
    ("climatiseur", "Électroménager"),
    ("microwave oven", "Électroménager"),
    ("aspirateur", "Électroménager"),
    ("machine cafe", "Électroménager"),
]

def get_driver():
    opts = Options()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--disable-extensions')
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_amazon():
    driver = get_driver()
    all_products = []

    driver.get('https://www.amazon.com')
    time.sleep(random.uniform(3, 5))

    for keyword, category in KEYWORDS:
        print(f"\n[Amazon] {category} — '{keyword}'")

        for page in range(1, 6):  # 5 pages par keyword
            url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}&page={page}"
            print(f"  Page {page}...", end=" ", flush=True)
            driver.get(url)
            time.sleep(random.uniform(4, 7))

            if "Toutes nos excuses" in driver.title or "Sorry" in driver.title:
                print(f"⚠️ Bloqué — on attend 20s...")
                time.sleep(20)
                driver.get(url)
                time.sleep(random.uniform(5, 8))
                if "Toutes nos excuses" in driver.title:
                    print("⛔ Toujours bloqué — on passe")
                    break

            items = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')

            if not items:
                print("fin de pagination")
                break

            count = 0
            for item in items:
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, 'h2 span').text.strip()
                    except:
                        continue
                    if not name:
                        continue

                    try:
                        price_raw = item.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen').get_attribute('innerHTML')
                        price_raw = price_raw.replace('MAD', '').replace('\xa0', '').replace(',', '.').strip()
                        price = float(price_raw)
                    except:
                        price = None

                    try:
                        rating_text = item.find_element(By.CSS_SELECTOR, '.a-icon-star-small .a-icon-alt').get_attribute('innerHTML')
                        rating = float(rating_text.split(' ')[0].replace(',', '.'))
                    except:
                        rating = None

                    try:
                        image_url = item.find_element(By.CSS_SELECTOR, 'img.s-image').get_attribute('src')
                    except:
                        image_url = None

                    try:
                        product_url = item.find_element(By.CSS_SELECTOR, 'a.a-link-normal.s-no-outline').get_attribute('href')
                    except:
                        product_url = None

                    all_products.append({
                        "name": name,
                        "price": price,
                        "old_price": None,
                        "discount": None,
                        "rating": rating,
                        "currency": "MAD",
                        "category": category,
                        "image_url": image_url,
                        "url": product_url,
                        "source": "amazon.com",
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                    count += 1
                except:
                    continue

            print(f"✅ {count} produits")
            time.sleep(random.uniform(2, 4))

    driver.quit()

    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/amazon_ma.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 TOTAL : {len(all_products)} produits → data/raw/amazon_ma.json")

if __name__ == "__main__":
    scrape_amazon()