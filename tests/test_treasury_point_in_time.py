import json
import tempfile
import unittest
from pathlib import Path

from scripts.update_treasury import build_views, point_in_time_snapshots, validate_ledger


class TreasuryPointInTimeTest(unittest.TestCase):
    def sample_ledger(self):
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
                    "source_url": "https://www.sec.gov/old.htm",
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
                    "source_url": "https://www.sec.gov/new.htm",
                    "facts": [
                        {"name": "basic_shares_outstanding", "value": 20, "unit": "shares", "fact_class": "state"}
                    ],
                },
            ],
        }

    def test_future_share_count_is_not_backfilled(self):
        ledger = self.sample_ledger()
        validate_ledger(ledger)
        events = []
        for event in ledger["events"]:
            events.append({**event, "source_sha256": event["id"] * 16})
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
        with self.assertRaisesRegex(ValueError, "non-SEC source"):
            validate_ledger(ledger)

    def test_build_views_preserves_source_hash_and_known_at(self):
        ledger = self.sample_ledger()
        verified = {
            "old": {"sha256": "a" * 64, "path": "a.htm", "source_url": "https://www.sec.gov/old.htm"},
            "future-share-disclosure": {"sha256": "b" * 64, "path": "b.htm", "source_url": "https://www.sec.gov/new.htm"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            api = Path(tmp)
            index = build_views(ledger, verified, api)
            latest = json.loads((api / "latest.json").read_text())
            events = json.loads((api / "events.json").read_text())
        self.assertEqual(index["coverage"]["event_count"], 2)
        self.assertEqual(latest["state"]["basic_shares_outstanding"]["value"], 20)
        self.assertEqual(latest["state"]["basic_shares_outstanding"]["known_at"], "2024-01-05T09:00:00Z")
        self.assertEqual(events["events"][0]["source_sha256"], "a" * 64)


if __name__ == "__main__":
    unittest.main()
