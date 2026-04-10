from core.models import ResearchReport
from utils.logger import get_logger

logger = get_logger("Modules.ReportGenerator")

def render_markdown(report: ResearchReport) -> str:
    """Converts a ResearchReport object into a structured Markdown string."""
    logger.info("Generating Markdown report")
    lines: list[str] = []
    
    lines.append("# Executive Summary")
    lines.append(report.executive_summary)
    lines.append("")
    
    lines.append("# Key Findings by Angle")
    for section in report.sections:
        lines.append(f"## {section.angle_title}")
        if not section.findings:
            lines.append("- Limited findings for this angle.")
        for finding in section.findings:
            lines.append(f"- {finding}")
    lines.append("")
    
    lines.append("# Evidence Bullets")
    for bullet in report.evidence_bullets:
        lines.append(f"- {bullet.claim} ([{bullet.source_title}]({bullet.url}))")
    lines.append("")
    
    lines.append("# Risks and Uncertainties")
    for risk in report.risks_uncertainties:
        lines.append(f"- {risk}")
        
    if report.conflicts:
        lines.append("")
        lines.append("# Conflicting Information")
        for conflict in report.conflicts:
            lines.append(f"- {conflict.topic}: {conflict.description}")
            
    lines.append("")
    lines.append("# What to Watch Next")
    for watch in report.what_to_watch_next:
        lines.append(f"- {watch}")
        
    lines.append("")
    lines.append("# Quality Checks")
    lines.append(f"- Passed: {report.quality_checks.passed}")
    lines.append(f"- Citation coverage: {report.quality_checks.citation_coverage:.2f}")
    lines.append(f"- Source diversity: {report.quality_checks.source_diversity}")
    for failure in report.quality_checks.failed_checks:
        lines.append(f"- Gap: {failure}")
        
    lines.append("")
    lines.append("# Machine Data (Strict JSON)")
    lines.append("```json")
    
    import json
    machine_output = {
        "summary": [report.executive_summary],
        "angles": [{"title": s.angle_title, "findings": s.findings} for s in report.sections],
        "charts": report.charts,
        "networks": report.networks,
        "timeline": report.timeline,
        "sources": [{"claim": b.claim, "url": b.url} for b in report.evidence_bullets],
        "risks": report.risks_uncertainties,
        "watchlist": report.what_to_watch_next
    }
    
    lines.append(json.dumps(machine_output, indent=2))
    lines.append("```")
        
    return "\n".join(lines)
