import re
from core.models import Claim, EvidenceBullet, SourceRecord
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Modules.Extractor")

def extract_insights(angle_id: str, sources: list[SourceRecord]) -> list[Claim]:
    """Extracts structured claims from a list of sources for a specific angle."""
    logger.info(f"Extracting insights for angle: {angle_id}")
    claims: list[Claim] = []
    claim_num = 1
    
    for source in sources:
        text = (source.content or source.snippet or "").strip()
        if not text:
            continue
            
        sentences = re.split(r"(?<=[.!?])\s+", text)
        picked = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < settings.MIN_CLAIM_SENTENCE_LENGTH:
                continue
                
            # Extract numbers/percentages and dates (like 2024, 2025)
            numbers = re.findall(r"\b\d+(?:\.\d+)?(?:%|[a-zA-Z]+)?\b", sentence)
            dates = re.findall(r"\b(?:20\d\d|19\d\d)\b", sentence)
            
            # Mandate facts: Ensure the claim has numeric or date data
            if not numbers and not dates:
                continue
                
            claims.append(
                Claim(
                    claim_id=f"{angle_id}-claim-{claim_num}",
                    angle_id=angle_id,
                    text=sentence[:300],
                    numbers=numbers + dates,
                    supporting_source_ids=[source.source_id],
                    confidence=0.85 if (numbers and dates) else 0.70,
                )
            )
            claim_num += 1
            picked += 1
            if picked >= settings.MAX_CLAIMS_PER_SOURCE:
                break
                
    logger.info(f"Extracted {len(claims)} insights for angle {angle_id}.")
    return claims

def map_evidence(claims: list[Claim], sources: list[SourceRecord]) -> list[EvidenceBullet]:
    """Maps extracted claims back to their original sources for verification."""
    logger.info("Mapping claims to evidence")
    source_index = {s.source_id: s for s in sources}
    bullets: list[EvidenceBullet] = []
    
    for claim in claims:
        for source_id in claim.supporting_source_ids:
            source = source_index.get(source_id)
            if not source:
                continue
                
            snippet = source.snippet if source.snippet else (source.content or "")[:220]
            bullets.append(
                EvidenceBullet(
                    claim_id=claim.claim_id,
                    claim=claim.text,
                    source_id=source_id,
                    source_title=source.title,
                    url=source.url,
                    snippet=snippet[:260],
                    rationale="Source text supports the extracted claim.",
                )
            )
    return bullets
