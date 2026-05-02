from django.test import SimpleTestCase

from offers.scraper import _is_moroccan_offer, _normalize_text
from offers.scraper_ai import _parse_batch_json


class ScraperMoroccoFilterTests(SimpleTestCase):
    def test_is_moroccan_offer_positive(self):
        self.assertTrue(
            _is_moroccan_offer(
                {
                    "title": "Stage developpeur",
                    "description": "Poste base a Rabat",
                    "location": "Rabat",
                }
            )
        )

    def test_is_moroccan_offer_negative(self):
        self.assertFalse(
            _is_moroccan_offer(
                {
                    "title": "Software engineer",
                    "description": "Berlin startup",
                    "location": "Berlin",
                }
            )
        )

    def test_normalize_text(self):
        self.assertEqual(_normalize_text("  Python  Django  "), "python django")


class ScraperAIParseTests(SimpleTestCase):
    def test_parse_batch_json_array(self):
        raw = '[{"index": 0, "skills": ["Python"], "offer_type": "stage"}]'
        rows = _parse_batch_json(raw)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].get("index"), 0)
