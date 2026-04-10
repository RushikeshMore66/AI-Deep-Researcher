import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from core.models import SearchResult, SourceRecord
from core.orchestrator import ResearchOrchestrator


def _fake_search(*args, **kwargs) -> list[SearchResult]:
    now = datetime.now(timezone.utc)
    return [
        SearchResult("Company earnings", "https://s1.com", "Quarterly results rose 15% year over year.", 1, now),
        SearchResult("Market positioning", "https://s2.com", "Competition and market share shifts are ongoing.", 2, now),
        SearchResult("12-month stock view", "https://s3.com", "Returns in the last 12 months were volatile.", 3, now),
    ]


def _fake_research(angles):
    output = {}
    for idx, angle in enumerate(angles, start=1):
        output[angle.angle_id] = [
            SourceRecord(
                source_id=f"{angle.angle_id}-src-{idx}",
                angle_id=angle.angle_id,
                title=f"Source {idx}",
                url=f"https://example{idx}.com",
                snippet="Revenue grew 12% and margins expanded by 2 points.",
                content="Revenue grew 12% and margins expanded by 2 points. Management guided for FY growth of 8%.",
                fetched_ok=True,
            )
        ]
    return output


class PipelineIntegrationTests(unittest.TestCase):
    @patch("tools.duckduckgo_tool.DuckDuckGoTool.search", side_effect=_fake_search)
    @patch("modules.researcher.perform_parallel_research", side_effect=_fake_research)
    def test_pipeline_for_ticker(self, *_mocks) -> None:
        orchestrator = ResearchOrchestrator("NVDA")
        report = orchestrator.run()
        self.assertTrue(report.executive_summary)
        self.assertGreaterEqual(len(report.sections), 1)
        self.assertGreaterEqual(len(report.evidence_bullets), 1)
        self.assertIsNotNone(report.quality_checks)

    @patch("tools.duckduckgo_tool.DuckDuckGoTool.search", side_effect=_fake_search)
    @patch("modules.researcher.perform_parallel_research", side_effect=_fake_research)
    def test_pipeline_for_general_query(self, *_mocks) -> None:
        orchestrator = ResearchOrchestrator("future of edge AI inference")
        report = orchestrator.run()
        self.assertGreaterEqual(len(report.sections), 1)
        self.assertGreaterEqual(len(report.what_to_watch_next), 1)


if __name__ == "__main__":
    unittest.main()
