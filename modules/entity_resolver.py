from core.models import QueryIntent
from utils.logger import get_logger

logger = get_logger("Modules.EntityResolver")

def resolve_entities(intent: QueryIntent) -> str | None:
    """Resolves a canonical entity name, industry, and core business from the classified intent."""
    if intent.company_name:
        entity = intent.company_name
    elif intent.ticker:
        entity = intent.ticker
    else:
        entity = None
    
    if entity:
        if not intent.industry:
            # Heuristic default for unknown companies
            intent.industry = "General Industry"
        if not intent.core_business:
            intent.core_business = "Products and Services"
            
        logger.info(f"Resolved entity: {entity} | Industry: {intent.industry} | Core: {intent.core_business}")
    else:
        logger.info("No specific entity resolved from query.")
    
    return entity
