from collections import defaultdict
from datetime import datetime, timedelta, timezone
from core.models import Claim, ConflictItem, ResearchAngle, SectionFinding, QualityChecks, EvidenceBullet, SourceRecord
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Modules.Synthesizer")

def build_report_sections(angles: list[ResearchAngle], claims: list[Claim]) -> list[SectionFinding]:
    """Groups claims by angle and creates report sections."""
    logger.info("Synthesizing report sections")
    grouped: dict[str, list[Claim]] = defaultdict(list)
    for claim in claims:
        grouped[claim.angle_id].append(claim)
    
    by_id = {a.angle_id: a for a in angles}
    sections: list[SectionFinding] = []
    
    for angle in angles:
        # Take up to 6 findings per angle
        findings = [c.text for c in grouped.get(angle.angle_id, [])[:6]]
        sections.append(
            SectionFinding(
                angle_id=angle.angle_id,
                angle_title=by_id[angle.angle_id].title,
                findings=findings,
            )
        )
    return sections

def detect_data_conflicts(claims: list[Claim]) -> list[ConflictItem]:
    """Detects numeric inconsistencies across extracted claims."""
    logger.info("Detecting data conflicts")
    conflicts: list[ConflictItem] = []
    for claim in claims:
        nums = claim.numbers
        if len(set(nums)) > 1 and len(nums) > 1:
            conflicts.append(
                ConflictItem(
                    topic=f"Numeric inconsistency in {claim.angle_id}",
                    description=f"Claim contains multiple numeric signals: {', '.join(nums[:4])}",
                    source_ids=claim.supporting_source_ids,
                )
            )
    return conflicts

def perform_quality_audit(
    sources: list[SourceRecord], 
    evidence: list[EvidenceBullet], 
    sections: list[SectionFinding]
) -> QualityChecks:
    """Evaluates the overall quality and reliability of the research."""
    logger.info("Performing quality audit")
    
    unique_sources = {s.url for s in sources}
    findings_count = sum(len(s.findings) for s in sections)
    
    citation_coverage = 0.0 if findings_count == 0 else min(len(evidence) / findings_count, 1.0)
    
    stale_warnings: list[str] = []
    stale_cutoff = datetime.now(timezone.utc) - timedelta(days=settings.STALE_SOURCE_DAYS)
    
    for source in sources:
        if source.published_at and source.published_at < stale_cutoff:
            stale_warnings.append(f"Potentially stale source: {source.title}")

    failed: list[str] = []
    if citation_coverage < settings.MIN_CITATION_COVERAGE:
        failed.append("Citation coverage below threshold.")
    if len(unique_sources) < settings.MIN_SOURCE_DIVIERSTY if hasattr(settings, 'MIN_SOURCE_DIVIERSTY') else settings.MIN_SOURCE_DIVERSITY:
        # Small typo check on settings if needed, but I used MIN_SOURCE_DIVERSITY in settings.py
        failed.append("Source diversity below threshold.")
        
    return QualityChecks(
        passed=not failed,
        citation_coverage=citation_coverage,
        source_diversity=len(unique_sources),
        freshness_warnings=stale_warnings,
        failed_checks=failed,
    )

def generate_executive_summary(sections: list[SectionFinding]) -> str:
    """Generates a high-level summary based on compiled sections."""
    covered = [s.angle_title for s in sections if s.findings]
    if not covered:
        return "Limited evidence was gathered. Results are directional and require additional sources."
    return f"Research covers {len(covered)} major angles: " + ", ".join(covered[:4]) + "."

def generate_dashboard_json(claims: list[Claim], intent) -> dict:
    """Generates structured JSON data for visualizations (Charts, Networks, Timelines)."""
    logger.info("Generating Machine JSON for dashboard")
    
    time_series = []
    networks = []
    timeline = []
    
    # Base node for network
    networks.append({"source": intent.company_name or intent.ticker or "Target", "target": intent.industry or "Market", "type": "Industry"})
    
    current_year = datetime.now().year
    
    for claim in claims:
        # Build timeline from dates
        for date in claim.numbers:
            if str(current_year) in date or str(current_year-1) in date:
                if {"year": date, "event": claim.text[:50] + "..."} not in timeline:
                    timeline.append({"year": date, "event": claim.text[:50] + "..."})
                    
        # Extract potential relationships for network
        if claim.angle_id == "competition_positioning":
            networks.append({"source": intent.company_name or intent.ticker or "Target", "target": f"Competitor Signal ({claim.claim_id})", "type": "Competes with", "evidence": claim.text[:40]})
            
        # Time series / Comparisons
        if claim.angle_id == "performance_12m" and claim.numbers:
            time_series.append({"metric": f"KPI {claim.claim_id}", "value": claim.numbers[0], "context": claim.text[:30]})
            
    return {
        "charts": time_series,
        "networks": networks,
        "timeline": timeline
    }
