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

    def verified(self):
        common = {
            "form": "8-K",
            "report_date": "2024-01-01",
            "acceptance_datetime": "2024-01-02T12:00:00.000Z",
            "primary_document": "primary.htm",
            "submissions_source_url": "https://data.sec.gov/submissions/CIK0001050446.json",
            "submissions_sha256": "a" * 64,
            "submissions_evidence": "data/treasury/evidence/sec-submissions.json",
        }
        return {
            "old": {**common, "accession_number": "0001193125-24-000001", "document": "old.htm", "filing_date": "2024-01-02"},
            "future-share-disclosure": {**common, "accession_number": "0001193125-24-000002", "document": "new.htm", "filing_date": "2024-01-05"},
        }

    def test_future_share_count_is_not_backfilled(self):
        ledger = self.sample_ledger()
        validate_ledger(ledger)
        events = []
        for event, accession in zip(ledger["events"], self.verified().values()):
            events.append({**event, "accession_number": accession["accession_number"], "sec_submissions_sha256": "a" * 64})
        snapshots = point_in_time_snapshots(events)
        self.assertEqual(snapshots[0]["state"]["basic_shares_outstanding"]["value"], 10)
        self.assertEqual(snapshots[1]["state"]["basic_shares_outstanding"]["value"], 20)
        self.assertEqual(snapshots[0]["state"]["bitcoin_holdings"]["value"], 100)

    def test_filing_before_effective_date_is_rejected(self):
        ledger = self.sample_ledger()
        ledger["events"][0]["filed_at"] = "2023-12-31"
        with self.assertRaisesRegex(ValueError, "filed_at precedes effective_at"):
            validate_ledger(ledger)

    def test_non_sec_source_is_rejected(self):
        ledger = self.sample_ledger()
        ledger["events"][0]["source_url"] = "https://example.com/old.htm"
        with self.assertRaisesRegex(ValueError, "canonical source must be SEC Archives"):
            validate_ledger(ledger)

    def test_build_views_preserves_accession_and_known_at(self):
        ledger = self.sample_ledger()
        with tempfile.TemporaryDirectory() as tmp:
            api = Path(tmp)
            index = build_views(ledger, self.verified(), api)
            latest = json.loads((api / "latest.json").read_text())
            events = json.loads((api / "events.json").read_text())
        self.assertEqual(index["coverage"]["event_count"], 2)
        self.assertEqual(latest["state"]["basic_shares_outstanding"]["value"], 20)
        self.assertEqual(latest["state"]["basic_shares_outstanding"]["known_at"], "2024-01-05T09:00:00Z")
        self.assertEqual(events["events"][0]["accession_number"], "0001193125-24-000001")
        self.assertEqual(events["events"][0]["sec_submissions_sha256"], "a" * 64)


if __name__ == "__main__":
    unittest.main()
