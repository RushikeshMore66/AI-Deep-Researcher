from pydantic_settings import BaseSettings
from typing import Any

class Settings(BaseSettings):
    # Search & Discovery
    DDG_API_URL: str = "https://api.duckduckgo.com/"
    DISCOVERY_MAX_RESULTS: int = 8
    
    # Angle Generation
    MAX_ANGLES: int = 4
    ANGLE_TEMPLATES: list[tuple[str, str, list[str]]] = [
        ("swot_analysis", "SWOT Analysis", ["strengths", "weaknesses", "opportunities", "threats"]),
        ("performance_12m", "Last 12 Months Performance", ["12 months", "performance", "returns", "trend"]),
        ("competition_positioning", "Competition and Market Positioning", ["competitors", "market share", "positioning", "moat"]),
        ("latest_results_guidance", "Latest Results and Forward Guidance", ["quarterly", "results", "guidance", "forecast"]),
    ]
    
    # Researching & Scraping
    RESEARCH_MAX_RESULTS_PER_ANGLE: int = 5
    RESEARCH_MAX_WORKERS: int = 4
    SCRAPER_TIMEOUT_SEC: int = 12
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (compatible; DeepResearchBot/1.0)"
    
    # Extraction
    MAX_CLAIMS_PER_SOURCE: int = 3
    MIN_CLAIM_SENTENCE_LENGTH: int = 40
    
    # Synthesis & Quality
    MIN_CITATION_COVERAGE: float = 0.8
    MIN_SOURCE_DIVERSITY: int = 4
    STALE_SOURCE_DAYS: int = 365
    
    # Intent Classification Database
    # Format: Ticker: (Company Name, Industry, Core Business, Tags)
    TICKER_DB: dict[str, tuple[str, str, str, list[str]]] = {
        "NVDA": ("NVIDIA Corporation", "Semiconductors", "GPUs, AI hardware, Datacenter", ["semiconductors", "GPUs", "AI", "datacenter"]),
        "AAPL": ("Apple Inc.", "Consumer Electronics", "Smartphones, Computers, Wearables, Services", ["consumer electronics", "services", "hardware"]),
        "MSFT": ("Microsoft Corp.", "Technology", "Cloud, Enterprise Software, OS, AI", ["cloud", "enterprise software", "AI"]),
        "GOOGL": ("Alphabet Inc.", "Technology", "Search, Ads, Cloud, AI", ["internet", "ads", "cloud", "AI"]),
        "AMZN": ("Amazon.com Inc.", "E-commerce & Cloud", "Retail, Cloud computing, Logistics", ["ecommerce", "cloud", "logistics"]),
    }

    class Config:
        case_sensitive = True

settings = Settings()
