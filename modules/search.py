from core.models import QueryIntent, SearchResult
from tools.duckduckgo_tool import DuckDuckGoTool
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Modules.Search")

def run_discovery_search(intent: QueryIntent) -> list[SearchResult]:
    """Runs the initial discovery search based on classified intent."""
    logger.info("Initializing discovery search")
    tool = DuckDuckGoTool()
    
    queries = [
        intent.normalized_query,
        f"{intent.company_name or intent.ticker or intent.raw_input} company overview business model",
        intent.company_name or intent.ticker or intent.raw_input
    ]
    
    for attempt, query in enumerate(queries):
        logger.info(f"Discovery search attempt {attempt+1} with query: {query}")
        results = tool.search(query, max_results=settings.DISCOVERY_MAX_RESULTS)
        if results:
            logger.info(f"Discovery search succeeded with {len(results)} results.")
            return results
            
    logger.warning("Discovery search failed to find results after retries.")
    return []
