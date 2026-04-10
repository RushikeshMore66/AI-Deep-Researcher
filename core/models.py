from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any

class QueryKind(str, Enum):
    TICKER = "ticker"
    GENERAL = "general_query"

@dataclass
class QueryIntent:
    raw_input: str
    kind: QueryKind
    normalized_query: str
    confidence: float
    ticker: str | None = None
    company_name: str | None = None
    industry: str | None = None
    core_business: str | None = None
    context_tags: list[str] = field(default_factory=list)

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    rank: int
    retrieval_time: datetime
    source_type: str = "web"

@dataclass
class ResearchAngle:
    angle_id: str
    title: str
    keywords: list[str]
    rationale: str
    query: str = ""

@dataclass
class SourceRecord:
    source_id: str
    angle_id: str
    title: str
    url: str
    snippet: str
    content: str | None = None
    fetched_ok: bool = False
    error: str | None = None
    published_at: datetime | None = None

@dataclass
class Claim:
    claim_id: str
    angle_id: str
    text: str
    numbers: list[str] = field(default_factory=list)
    supporting_source_ids: list[str] = field(default_factory=list)
    confidence: float = 0.5

@dataclass
class EvidenceBullet:
    claim_id: str
    claim: str
    source_id: str
    source_title: str
    url: str
    snippet: str
    rationale: str = ""

@dataclass
class SectionFinding:
    angle_id: str
    angle_title: str
    findings: list[str] = field(default_factory=list)

@dataclass
class ConflictItem:
    topic: str
    description: str
    source_ids: list[str] = field(default_factory=list)

@dataclass
class QualityChecks:
    passed: bool
    citation_coverage: float
    source_diversity: int
    freshness_warnings: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)

@dataclass
class ResearchReport:
    executive_summary: str
    sections: list[SectionFinding]
    evidence_bullets: list[EvidenceBullet]
    risks_uncertainties: list[str]
    conflicts: list[ConflictItem]
    what_to_watch_next: list[str]
    quality_checks: QualityChecks
    charts: list[dict[str, Any]] = field(default_factory=list)
    networks: list[dict[str, Any]] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    json_output: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class ResearchState:
    input_query: str
    intent: QueryIntent | None = None
    resolved_entity: str | None = None
    discovery_results: list[SearchResult] = field(default_factory=list)
    angles: list[ResearchAngle] = field(default_factory=list)
    sources_by_angle: dict[str, list[SourceRecord]] = field(default_factory=dict)
    all_claims: list[Claim] = field(default_factory=list)
    evidence: list[EvidenceBullet] = field(default_factory=list)
    sections: list[SectionFinding] = field(default_factory=list)
    conflicts: list[ConflictItem] = field(default_factory=list)
    report: ResearchReport | None = None
    errors: list[str] = field(default_factory=list)
