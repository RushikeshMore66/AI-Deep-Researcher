import unittest

from src.research.models import QueryKind
from src.research.query_understanding import classify_and_enrich_query


class QueryUnderstandingTests(unittest.TestCase):
    def test_known_ticker_enrichment(self) -> None:
        result = classify_and_enrich_query("NVDA")
        self.assertEqual(result.kind, QueryKind.TICKER)
        self.assertEqual(result.company_name, "NVIDIA")
        self.assertIn("AI", result.context_tags)

    def test_general_query_classification(self) -> None:
        result = classify_and_enrich_query("impact of AI chips on cloud capex")
        self.assertEqual(result.kind, QueryKind.GENERAL)
        self.assertEqual(result.normalized_query, "impact of AI chips on cloud capex")


if __name__ == "__main__":
    unittest.main()
