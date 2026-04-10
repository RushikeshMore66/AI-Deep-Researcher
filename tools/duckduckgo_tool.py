import json
from datetime import datetime, timezone
from duckduckgo_search import DDGS
from core.models import SearchResult
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Tools.DuckDuckGo")

class DuckDuckGoTool:
    def __init__(self, api_url: str = settings.DDG_API_URL):
        self.api_url = api_url

    def search(self, query: str, max_results: int = settings.DISCOVERY_MAX_RESULTS) -> list[SearchResult]:
        """Performs a search using duckduckgo_search DDGS text method."""
        try:
            logger.info(f"Searching for: {query}")
            retrieval_time = datetime.now(timezone.utc)
            rows: list[SearchResult] = []
            
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                
                # Check for None results (DDGS sometimes returns None if empty)
                if not results:
                    logger.info("Search returned no results from DDGS.")
                    return []
                    
                rank = 1
                for item in results:
                    rows.append(
                        SearchResult(
                            title=item.get("title", "")[:120],
                            url=item.get("href", ""),
                            snippet=item.get("body", ""),
                            rank=rank,
                            retrieval_time=retrieval_time,
                        )
                    )
                    rank += 1

            logger.info(f"Search found {len(rows)} results.")
            return rows
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []
