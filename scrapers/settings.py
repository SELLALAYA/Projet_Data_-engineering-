BOT_NAME = "price_intelligence"
SPIDER_MODULES = ["scrapers.spiders"]
NEWSPIDER_MODULE = "scrapers.spiders"

# Politesse
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Headers réalistes
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-MA,fr;q=0.9,en;q=0.8",
}
COOKIES_ENABLED = True

# Pipelines
ITEM_PIPELINES = {
    "scrapers.pipelines.AddMetadataPipeline": 100,
    "scrapers.pipelines.JsonExportPipeline":  200,
    "scrapers.pipelines.NifiStreamingPipeline": 300,
}

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

# Logs
LOG_LEVEL = "INFO"
LOG_FILE = None