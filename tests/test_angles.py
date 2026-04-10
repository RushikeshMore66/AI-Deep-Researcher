import unittest
from datetime import datetime, timezone

from src.research.angles import generate_angles
from src.research.models import SearchResult


class AngleTests(unittest.TestCase):
    def test_generate_non_overlapping_angles(self) -> None:
        now = datetime.now(timezone.utc)
        results = [
            SearchResult("NVIDIA earnings", "https://a.com", "quarterly growth and guidance updates", 1, now),
            SearchResult("GPU market share", "https://b.com", "competition and market positioning trends", 2, now),
            SearchResult("Stock performance", "https://c.com", "12 month returns and valuation changes", 3, now),
        ]
        angles = generate_angles(results, max_angles=4)
        self.assertGreaterEqual(len(angles), 3)
        self.assertLessEqual(len(angles), 4)
        titles = {a.title for a in angles}
        self.assertIn("SWOT Analysis", titles)


if __name__ == "__main__":
    unittest.main()
