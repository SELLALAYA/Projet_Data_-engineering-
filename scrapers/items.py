import scrapy


class ProductItem(scrapy.Item):
    """
    Modèle de données unifié pour tous les sites.
    Chaque spider remplit ces champs.
    """
    # Champs principaux
    name        = scrapy.Field()   # Nom du produit
    price       = scrapy.Field()   # Prix (float, en MAD ou devise locale)
    currency    = scrapy.Field()   # Devise (ex: "MAD", "USD")
    category    = scrapy.Field()   # Catégorie principale
    url         = scrapy.Field()   # Lien direct vers le produit

    # Metadata pipeline
    source      = scrapy.Field()   # Nom du site (ex: "jumia_ma")
    scraped_at  = scrapy.Field()   # Timestamp ISO 8601
