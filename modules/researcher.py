from concurrent.futures import ThreadPoolExecutor, as_completed
from core.models import ResearchAngle, SourceRecord
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.scraper import scrape_url
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Modules.Researcher")

def _research_single_angle(angle: ResearchAngle) -> list[SourceRecord]:
    """Internal helper to research a single angle with retry and simplification logic."""
    client = DuckDuckGoTool()
    
    # We will try up to 3 times with simplified queries
    queries_to_try = [
        angle.query,
        f"{angle.query.split(' ')[0]} {angle.title}",  # Simpler fallback
        angle.title # Broadest fallback
    ]
    
    for attempt, query in enumerate(queries_to_try):
        logger.info(f"Researching angle '{angle.title}', attempt {attempt+1} with query: {query}")
        results = client.search(query, max_results=settings.RESEARCH_MAX_RESULTS_PER_ANGLE)
        
        records = []
        for idx, item in enumerate(results):
            record = SourceRecord(
                source_id=f"{angle.angle_id}-src-{idx + 1}-{attempt}",
                angle_id=angle.angle_id,
                title=item.title,
                url=item.url,
                snippet=item.snippet,
            )
            
            # Scrape content
            content = scrape_url(record.url)
            if content:
                record.content = content
                record.fetched_ok = True
                records.append(record)
            else:
                record.fetched_ok = False
                
        # Phase 4 Validation: Ensure at least 3 valid sources
        if len(records) >= 3:
            logger.info(f"Angle '{angle.title}' achieved {len(records)} valid sources.")
            return records
        else:
            logger.warning(f"Angle '{angle.title}' only found {len(records)} sources on attempt {attempt+1}. Retrying...")
            
    logger.warning(f"Angle '{angle.title}' failed to find enough sources after all retries.")
    return records

def perform_parallel_research(angles: list[ResearchAngle]) -> dict[str, list[SourceRecord]]:
    """Runs research for each angle in parallel."""
    logger.info(f"Starting parallel research for {len(angles)} angles")
    outputs: dict[str, list[SourceRecord]] = {}
    
    with ThreadPoolExecutor(max_workers=settings.RESEARCH_MAX_WORKERS) as pool:
        future_to_angle = {pool.submit(_research_single_angle, angle): angle for angle in angles}
        
        for future in as_completed(future_to_angle):
            angle = future_to_angle[future]
            try:
                sources = future.result()
                outputs[angle.angle_id] = sources
                logger.info(f"Completed research for angle: {angle.title}")
            except Exception as e:
                logger.error(f"Angle research failed for '{angle.title}': {e}")
                outputs[angle.angle_id] = []
                
    return outputs
