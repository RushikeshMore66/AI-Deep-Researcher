import re
from urllib.request import Request, urlopen
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Tools.Scraper")

def scrape_url(url: str, timeout_sec: int = settings.SCRAPER_TIMEOUT_SEC) -> str:
    """Fetches and cleans text from a URL."""
    try:
        logger.info(f"Scraping URL: {url}")
        req = Request(url, headers={"User-Agent": settings.SCRAPER_USER_AGENT})
        with urlopen(req, timeout=timeout_sec) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        
        # Strip script and style tags
        clean = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.IGNORECASE)
        clean = re.sub(r"<style[\s\S]*?</style>", " ", clean, flags=re.IGNORECASE)
        # Strip HTML tags
        clean = re.sub(r"<[^>]+>", " ", clean)
        # Collapse whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ""
