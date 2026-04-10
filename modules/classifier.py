from core.models import QueryIntent, QueryKind
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Modules.Classifier")

def classify_intent(user_input: str) -> QueryIntent:
    """Classifies user input into TICKER or GENERAL research kinds."""
    raw = user_input.strip()
    upper = raw.upper()
    
    # Check if input matches a known ticker in our DB
    # Note: ticker_db in settings has (company_name, tags)
    if upper in settings.TICKER_DB:
        company, industry, core_business, tags = settings.TICKER_DB[upper]
        logger.info(f"Identified known ticker: {upper} ({company})")
        return QueryIntent(
            raw_input=raw,
            kind=QueryKind.TICKER,
            normalized_query=f"{company} ({upper}) business, financials, outlook",
            confidence=0.95,
            ticker=upper,
            company_name=company,
            industry=industry,
            core_business=core_business,
            context_tags=tags,
        )

    # Check for common company name indicators
    company_indicators = [" INC", " CORP", " LTD", " PLC", " GROUP", " HOLDINGS", " TECH"]
    if any(indicator in upper for indicator in company_indicators):
        logger.info(f"Identified company name via indicator: {raw}")
        return QueryIntent(
            raw_input=raw,
            kind=QueryKind.TICKER,
            normalized_query=f"{raw} business model financials and strategic outlook",
            confidence=0.85,
            company_name=raw,
            context_tags=["corporate research", "financial analysis"],
        )

    # Basic ticker-like match (1-5 letters)
    import re
    if re.fullmatch(r"[A-Z]{1,5}", upper):
        logger.info(f"Identified potential ticker: {upper}")
        return QueryIntent(
            raw_input=raw,
            kind=QueryKind.TICKER,
            normalized_query=f"{upper} company business financial performance",
            confidence=0.7,
            ticker=upper,
            company_name=None,
            context_tags=["public company", "financial analysis"],
        )

    # Single word queries are often companies
    if " " not in raw and len(raw) > 2:
        logger.info(f"Defaulting single-word query to company research: {raw}")
        return QueryIntent(
            raw_input=raw,
            kind=QueryKind.TICKER,
            normalized_query=f"{raw} company business and market performance",
            confidence=0.6,
            company_name=raw,
            context_tags=["company research"],
        )

    logger.info("Classified as general query")
    return QueryIntent(
        raw_input=raw,
        kind=QueryKind.GENERAL,
        normalized_query=raw,
        confidence=0.9,
        context_tags=["general research"],
    )
