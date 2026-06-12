import scrapy
from datetime import datetime, timezone


class JumiaSpider(scrapy.Spider):
    """
    Spider Jumia Maroc — Price Intelligence Project
    Catégories : Téléphones & Smartphones | Informatique | Électroménager
    Champs : nom, prix, ancien prix, réduction, note, image, lien, catégorie
    """

    name = "jumia_ma"
    allowed_domains = ["jumia.ma"]

    CATEGORIES = {
        "Téléphones & Smartphones": [
            "https://www.jumia.ma/telephones-smartphones/",
            "https://www.jumia.ma/tablettes-tactiles/",
        ],
        "Informatique": [
            "https://www.jumia.ma/pc-portables/",
            "https://www.jumia.ma/ordinateurs-pc/",
            "https://www.jumia.ma/ecrans-d-ordinateurs/",
        ],
        "Électroménager": [
            "https://www.jumia.ma/gros-electromenager/",
            "https://www.jumia.ma/air-fryers/",
            "https://www.jumia.ma/micro-onde/",
        ],
    }

    def start_requests(self):
        for category, urls in self.CATEGORIES.items():
            for url in urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_listing,
                    meta={"category": category},
                )

    def parse_listing(self, response):
        category = response.meta["category"]
        products = response.css("article.prd")

        self.logger.info(f"[{category}] {len(products)} produits — {response.url}")

        for product in products:
            item = self._extract(product, category, response)
            if item:
                yield item

        next_page = response.css(
            "a[aria-label='Next Page']::attr(href), a[aria-label='Page suivante']::attr(href)"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_listing, meta={"category": category})

    def _extract(self, product, category, response):
        name = product.css("h3.name::text").get()
        if not name:
            return None

        price     = self._parse_price(product.css("div.prc::text").get() or product.css("span.prc::text").get())
        old_price = self._parse_price(product.css("div.old::text").get())
        discount  = (product.css("div.bdg._dsct::text").get() or "").strip() or None
        rating    = (product.css("div.stars._s::text").get() or "").strip() or None
        image     = (product.css("img.img-n-lazy::attr(data-src)").get()
                     or product.css("img::attr(data-src)").get()
                     or product.css("img::attr(src)").get())
        link      = product.css("a.core::attr(href)").get()
        url       = ("https://www.jumia.ma" + link if link and link.startswith("/") else response.urljoin(link) if link else None)

        return {
            "name":       name.strip(),
            "price":      price,
            "old_price":  old_price,
            "discount":   discount,
            "rating":     rating,
            "currency":   "MAD",
            "category":   category,
            "image_url":  image,
            "url":        url,
            "source":     "jumia.ma",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def _parse_price(self, raw):
        if not raw:
            return None
        try:
            return float(raw.replace("Dhs","").replace("MAD","").replace("\xa0","").replace(" ","").replace(",","").strip())
        except (ValueError, AttributeError):
            return None
