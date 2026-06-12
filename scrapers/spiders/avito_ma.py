import json
import time
import requests
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from parsel import Selector
from datetime import datetime, timezone

NIFI_URL = "http://price_nifi:8888/contentListener"

KEYWORDS_PHONES = [
    'iphone', 'samsung', 'xiaomi', 'huawei', 'oppo', 'realme', 'oneplus',
    'redmi', 'galaxy', 'smartphone', 'telephone', 'mobile', 'vivo', 'nokia',
    'motorola', 'infinix', 'tecno', 'ipad', 'tablette', 'tablet'
]

KEYWORDS_INFO = [
    'laptop', 'ordinateur', 'pc ', 'macbook', 'dell', 'hp ', 'lenovo',
    'asus', 'acer', 'portable', 'bureau', 'ecran', 'moniteur', 'clavier',
    'imprimante', 'disque', 'ssd', 'ram', 'processeur'
]

KEYWORDS_ELECTRO = [
    'refriger', 'frigo', 'congel', 'lave-linge', 'machine a laver',
    'climatiseur', 'clim', 'four', 'micro-onde', 'aspirateur', 'cafetiere',
    'television', 'tv ', ' tv', 'smart tv', 'ecran plat', 'hisense',
    'samsung tv', 'lg ', 'brandt', 'beko', 'tefal', 'rowenta', 'dyson'
]

CATEGORIES = [
    ("https://www.avito.ma/fr/maroc/telephones-_iphones_et_smartphones-a_vendre", "Telephones & Smartphones", KEYWORDS_PHONES),
    ("https://www.avito.ma/fr/maroc/ordinateurs_portables-a_vendre", "Informatique", KEYWORDS_INFO),
    ("https://www.avito.ma/fr/maroc/television-a_vendre", "Electromenager", KEYWORDS_ELECTRO),
    ("https://www.avito.ma/fr/maroc/refrigerateurs_et_congelateurs-a_vendre", "Electromenager", KEYWORDS_ELECTRO),
]

def is_relevant(name, keywords):
    name_lower = name.lower()
    return any(k in name_lower for k in keywords)

class AvitoMaSpider(scrapy.Spider):
    name = "avito_ma"
    start_urls = ["https://www.avito.ma"]

    def get_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)

    def parse(self, response):
        driver = self.get_driver()
        total = 0
        skipped = 0

        for url, category, keywords in CATEGORIES:
            self.logger.info(f"Scraping: {category} — {url}")
            for page in range(1, 4):
                page_url = url if page == 1 else f"{url}?o={page}"
                try:
                    driver.get(page_url)
                    time.sleep(5)
                except Exception as e:
                    self.logger.error(f"Driver error: {e}")
                    break

                sel = Selector(text=driver.page_source)
                scripts = sel.css("script[id^='search-ad-schema']::text").getall()

                if not scripts:
                    self.logger.info(f"No items on page {page}, stopping")
                    break

                for script in scripts:
                    try:
                        data = json.loads(script)
                        name = data.get("name", "").strip()
                        offers = data.get("offers", {})
                        price_raw = offers.get("price", None)
                        product_url = offers.get("url", "")
                        images = data.get("image", [])

                        if not name:
                            continue

                        # Filtrer uniquement les produits pertinents
                        if not is_relevant(name, keywords):
                            skipped += 1
                            continue

                        try:
                            price = float(str(price_raw).replace(" ", "").replace(",", ".")) if price_raw else None
                        except:
                            price = None

                        product = {
                            "product_name": name,
                            "price": price,
                            "old_price": None,
                            "discount_pct": None,
                            "rating": None,
                            "currency": "MAD",
                            "category": category,
                            "image_url": images[0] if isinstance(images, list) and images else None,
                            "url": product_url,
                            "source": "avito.ma",
                            "scraped_at": datetime.now(timezone.utc).isoformat(),
                        }

                        try:
                            requests.post(NIFI_URL, json=product, timeout=5)
                            total += 1
                            self.logger.info(f"Sent to NiFi: {name} — {price} MAD")
                        except Exception as e:
                            self.logger.error(f"NiFi error: {e}")

                        yield product

                    except Exception:
                        continue

        driver.quit()
        self.logger.info(f"TOTAL sent: {total} | Skipped (irrelevant): {skipped}")