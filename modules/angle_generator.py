import re
from collections import Counter
from core.models import ResearchAngle, SearchResult
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Modules.AngleGenerator")

_STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "are", "was", "have", "about", "into", "over"}

def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return [w for w in words if w not in _STOPWORDS]

def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

from core.models import QueryIntent, ResearchAngle, SearchResult

def generate_research_angles(intent: QueryIntent, discovery_results: list[SearchResult]) -> list[ResearchAngle]:
    """Generates 3-4 non-overlapping research angles with smart context-aware queries."""
    logger.info("Generating research angles")
    
    corpus = " ".join(f"{x.title}. {x.snippet}" for x in discovery_results)
    freq = Counter(_tokenize(corpus))
    top_terms = [w for w, _ in freq.most_common(24)]

    generated: list[ResearchAngle] = []
    seen_keyword_sets: list[set[str]] = []
    
    # Base context string
    context_str = intent.company_name or intent.ticker or intent.raw_input
    
    import datetime
    current_year = datetime.datetime.now().year
    
    for angle_id, title, seeds in settings.ANGLE_TEMPLATES:
        kws = list(dict.fromkeys(seeds + top_terms[:6]))[:8]
        kw_set = set(_tokenize(" ".join(kws)))
        
        # Check for overlap
        if any(_jaccard(kw_set, s) > 0.6 for s in seen_keyword_sets):
            logger.debug(f"Skipping overlapping angle: {title}")
            continue
            
        seen_keyword_sets.append(kw_set)
        
        # Construct Smart Query Context
        smart_query = f"{context_str} "
        if angle_id == "latest_results_guidance":
            smart_query += f"latest earnings results {current_year} guidance forecast"
        elif angle_id == "performance_12m":
            smart_query += f"financial performance revenue growth {current_year}"
        elif angle_id == "competition_positioning":
            smart_query += f"competitors market share {intent.industry if intent.industry else 'industry'}"
        elif angle_id == "swot_analysis":
            smart_query += f"SWOT analysis strengths weaknesses opportunities"
        else:
            smart_query += f"{title} {' '.join(kws[:3])}"

        generated.append(
            ResearchAngle(
                angle_id=angle_id,
                title=title,
                keywords=kws,
                rationale=f"Built from discovery results and focused on {title.lower()}.",
                query=smart_query
            )
        )
        
        if len(generated) >= settings.MAX_ANGLES:
            break

    logger.info(f"Successfully generated {len(generated)} research angles.")
    return generated
