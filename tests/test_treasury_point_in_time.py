import json
import tempfile
import unittest
from pathlib import Path

from scripts.update_treasury import build_views, point_in_time_snapshots, validate_ledger


class TreasuryPointInTimeTest(unittest.TestCase):
    def sample_ledger(self):
        base = "https://www.sec.gov/Archives/edgar/data/1050446"
        return {
            "schema_version": 1,
            "entity": {"name": "Strategy Inc", "cik": "0001050446"},
            "events": [
                {
                    "id": "old",
                    "event_type": "snapshot",
                    "effective_at": "2024-01-01",
                    "filed_at": "2024-01-02",
                    "observed_at": "2024-01-02T12:00:00Z",
                    "source_url": f"{base}/000119312524000001/old.htm",
                    "facts": [
                        {"name": "bitcoin_holdings", "value": 100, "unit": "BTC", "fact_class": "state"},
                        {"name": "basic_shares_outstanding", "value": 10, "unit": "shares", "fact_class": "state"},
                    ],
                },
                {
                    "id": "future-share-disclosure",
                    "event_type": "snapshot",
                    "effective_at": "2024-01-03",
                    "filed_at": "2024-01-05",
                    "observed_at": "2024-01-05T09:00:00Z",
                    "source_url": f"{base}/000119312524000002/new.htm",
                    "facts": [
                        {"name": "basic_shares_outstanding", "value": 20, "unit": "shares", "fact_class": "state"}
                    ],
                },
            ],
        }

    def refs(self):
        return {
            "old": {
                "accession_number": "0001193125-24-000001",
                "document": "old.htm",
                "source_url": "https://www.sec.gov/old.htm",
                "filed_at": "2024-01-02",
            },
            "future-share-disclosure": {
                "accession_number": "0001193125-24-000002",
                "document": "new.htm",
                "source_url": "https://www.sec.gov/new.htm",
                "filed_at": "2024-01-05",
            },
        }

    def archive(self):
        return {
            "source_url": "https://www.strategy.com/financial-documents",
            "retrieved_at": "2026-08-18T00:00:00+00:00",
            "sha256": "a" * 64,
            "evidence": "data/treasury/evidence/strategy-financial-documents-a.html",
            "verified_markers": [
                "SEC Filings and Documents",
                "Form 8-K",
                "Jul 6, 2026",
            ],
        }

    def test_future_share_count_is_not_backfilled(self):
        ledger = self.sample_ledger()
        validate_ledger(ledger)
        events = []
        for event, ref in zip(ledger["events"], self.refs().values()):
            events.append({**event, "accession_number": ref["accession_number"]})
        snapshots = point_in_time_snapshots(events)
        self.assertEqual(
            snapshots[0]["state"]["basic_shares_outstanding"]["value"], 10
        )
        self.assertEqual(
            snapshots[1]["state"]["basic_shares_outstanding"]["value"], 20
        )
        self.assertEqual(snapshots[0]["state"]["bitcoin_holdings"]["value"], 100)

    def test_filing_before_effective_date_is_rejected(self):
        ledger = self.sample_ledger()
        ledger["events"][0]["filed_at"] = "2023-12-31"
        with self.assertRaisesRegex(ValueError, "filed_at precedes effective_at"):
            validate_ledger(ledger)

    def test_non_sec_source_is_rejected(self):
        ledger = self.sample_ledger()
        ledger["events"][0]["source_url"] = "https://example.com/old.htm"
        with self.assertRaisesRegex(
            ValueError, "canonical source must be SEC Archives"
        ):
            validate_ledger(ledger)

    def test_build_views_preserves_accession_and_known_at(self):
        ledger = self.sample_ledger()
        with tempfile.TemporaryDirectory() as tmp:
            api = Path(tmp)
            index = build_views(ledger, self.refs(), self.archive(), api)
            latest = json.loads((api / "latest.json").read_text())
            events = json.loads((api / "events.json").read_text())
        self.assertEqual(index["coverage"]["event_count"], 2)
        self.assertEqual(
            latest["state"]["basic_shares_outstanding"]["value"], 20
        )
        self.assertEqual(
            latest["state"]["basic_shares_outstanding"]["known_at"],
            "2024-01-05T09:00:00Z",
        )
        self.assertEqual(
            events["events"][0]["accession_number"], "0001193125-24-000001"
        )
        self.assertEqual(index["issuer_archive_monitor"]["sha256"], "a" * 64)


if __name__ == "__main__":
    unittest.main()
