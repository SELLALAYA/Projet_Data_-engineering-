import time
import requests
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timezone

NIFI_URL = "http://price_nifi:8888/contentListener"

URLS = [
    ("https://www.electroplanet.ma/telephones-et-accessoires/smartphones", "Telephones & Smartphones"),
    ("https://www.electroplanet.ma/informatique/ordinateurs-portables", "Informatique"),
    ("https://www.electroplanet.ma/electromenager/refrigerateurs", "Electromenager"),
    ("https://www.electroplanet.ma/electromenager/lave-linge", "Electromenager"),
    ("https://www.electroplanet.ma/electromenager/climatiseurs", "Electromenager"),
]

class ElectroplanetMaSpider(scrapy.Spider):
    name = "electroplanet_ma"

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.electroplanet.ma/telephones-et-accessoires/smartphones",
            callback=self.parse,
            dont_filter=True,
            errback=self.handle_error,
        )

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure}")
        yield from self.run_selenium()

    def parse(self, response):
        yield from self.run_selenium()

    def get_driver(self):
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        opts.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=opts)

    def clean_price(self, price_text):
        try:
            cleaned = price_text.replace("DH", "").replace("\xa0", "").replace("\u202f", "").replace(" ", "").replace(",", ".").strip()
            return float(cleaned)
        except:
            return None

    def run_selenium(self):
        total = 0
        seen_names = set()
        driver = self.get_driver()

        for url, category in URLS:
            self.logger.info(f"Scraping: {url}")
            try:
                driver.get(url)
                time.sleep(8)
                for _ in range(5):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                items = driver.find_elements(By.CSS_SELECTOR, ".product-item")
                self.logger.info(f"Found {len(items)} items in {category}")

                for item in items:
                    try:
                        # Nom
                        try:
                            name = item.find_element(By.CSS_SELECTOR, ".product-item-link").text.strip()
                        except:
                            name = item.find_element(By.CSS_SELECTOR, "a").text.strip()

                        if not name or name in seen_names:
                            continue
                        seen_names.add(name)

                        # Prix special (prix actuel)
                        try:
                            price = self.clean_price(item.find_element(By.CSS_SELECTOR, ".special-price .price").text)
                        except:
                            try:
                                price = self.clean_price(item.find_element(By.CSS_SELECTOR, ".price-wrapper .price").text)
                            except:
                                price = None

                        # Ancien prix
                        try:
                            old_price = self.clean_price(item.find_element(By.CSS_SELECTOR, ".old-price .price").text)
                        except:
                            old_price = None

                        # Discount %
                        try:
                            discount_text = item.find_element(By.CSS_SELECTOR, ".price-discount-percent").text
                            discount = float(discount_text.replace("%", "").replace("-", "").strip())
                        except:
                            discount = None

                        # Image
                        try:
                            image_url = item.find_element(By.CSS_SELECTOR, "img.product-image-photo").get_attribute("src")
                        except:
                            image_url = None

                        # URL produit
                        try:
                            product_url = item.find_element(By.CSS_SELECTOR, "a.product-item-link").get_attribute("href")
                        except:
                            product_url = None

                        product = {
                            "product_name": name,
                            "price": price,
                            "old_price": old_price,
                            "discount_pct": discount,
                            "rating": None,
                            "currency": "MAD",
                            "category": category,
                            "image_url": image_url,
                            "url": product_url,
                            "source": "electroplanet.ma",
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

            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")

        driver.quit()
        self.logger.info(f"TOTAL sent to NiFi: {total}")