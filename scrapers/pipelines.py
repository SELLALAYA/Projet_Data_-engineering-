import json
import os
import requests
from datetime import datetime, timezone

class AddMetadataPipeline:
    """Ajoute scraped_at et source si absents."""
    def process_item(self, item, spider):
        if not item.get("scraped_at"):
            item["scraped_at"] = datetime.now(timezone.utc).isoformat()
        if not item.get("source"):
            item["source"] = spider.name
        return item

class JsonExportPipeline:
    """Sauvegarde dans data/raw/jumia_ma.json — format JSON array."""
    def open_spider(self, spider):
        os.makedirs("data/raw", exist_ok=True)
        self.filename = f"data/raw/{spider.name}.json"
        self.file = open(self.filename, "w", encoding="utf-8")
        self.file.write("[\n")
        self.first = True
        spider.logger.info(f"Export → {self.filename}")

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()
        spider.logger.info(f"Terminé → {self.filename}")

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False, indent=2)
        if not self.first:
            self.file.write(",\n")
        self.file.write(line)
        self.first = False
        return item

class NifiStreamingPipeline:
    """Envoie chaque item vers NiFi en temps reel."""

    def process_item(self, item, spider):
        try:
            requests.post(
                "http://price_nifi:8888/contentListener",
                json=dict(item),
                timeout=2
            )
            spider.logger.info(f"Sent to NiFi: {item.get('name','?')}")
        except Exception as e:
            spider.logger.warning(f"NiFi send failed: {e}")
        return item