from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.current_btc_state import latest_verified_state, load_verified_btc_disclosures

ALLOWED_EVENT_TYPES = {"acquisition", "sale", "no_change"}
ALLOWED_SOURCE_TYPES = {"sec_8k", "strategy_official"}
ALLOWED_HOSTS = {"www.sec.gov", "www.strategy.com"}
OPTIONAL_NONNEGATIVE_FIELDS = {
    "aggregate_purchase_price_usd",
    "average_purchase_price_usd",
    "btc_sale_price_usd",
    "average_sale_price_usd",
    "usd_reserve_usd",
}


def parse_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise AssertionError(f"invalid {field}: {value}") from exc


def main() -> None:
    data = load_verified_btc_disclosures()
    assert data["schema_version"] == "strategy-btc-disclosures.v1"
    assert data["entity"] == "Strategy Inc"
    assert data["ticker"] == "MSTR"

    records = data["records"]
    assert records, "records must not be empty"
    ids: set[str] = set()
    order_keys: list[tuple[date, date, str]] = []

    for record in records:
        record_id = record["record_id"]
        assert record_id not in ids, f"duplicate record_id: {record_id}"
        ids.add(record_id)

        reported = parse_iso_date(record["reported_date"], "reported_date")
        as_of_raw = record.get("as_of_date")
        as_of = reported
        if as_of_raw:
            as_of = parse_iso_date(as_of_raw, "as_of_date")
            assert as_of <= reported, f"as_of_date after reported_date: {record_id}"
        order_keys.append((reported, as_of, record_id))

        event_type = record["event_type"]
        btc_delta = record["btc_delta"]
        assert event_type in ALLOWED_EVENT_TYPES, f"invalid event_type: {record_id}"
        assert isinstance(btc_delta, int), f"btc_delta must be int: {record_id}"
        if event_type == "acquisition":
            assert btc_delta > 0, f"acquisition must have positive btc_delta: {record_id}"
        elif event_type == "sale":
            assert btc_delta < 0, f"sale must have negative btc_delta: {record_id}"
        else:
            assert btc_delta == 0, f"no_change must have zero btc_delta: {record_id}"

        assert isinstance(record["total_btc"], int) and record["total_btc"] > 0
        for field in OPTIONAL_NONNEGATIVE_FIELDS:
            if field in record:
                value = record[field]
                assert isinstance(value, (int, float)) and value >= 0, (
                    f"{field} must be non-negative numeric: {record_id}"
                )

        assert record["source_type"] in ALLOWED_SOURCE_TYPES
        assert record["verification_status"] == "primary_source_verified"
        parsed = urlparse(record["source_url"])
        assert parsed.scheme == "https", f"non-HTTPS source: {record_id}"
        assert parsed.netloc in ALLOWED_HOSTS, f"non-primary host: {record_id}"

    assert order_keys == sorted(order_keys), (
        "records must be ordered by report date and disclosed as-of state"
    )

    latest = latest_verified_state(data)
    declared = data["latest_verified"]
    for key in ("as_of_date", "reported_date", "total_btc", "source_url"):
        assert latest[key] == declared[key], f"latest_verified mismatch for {key}"

    for key in ("aggregate_purchase_price_usd", "average_purchase_price_usd"):
        if key in latest or key in declared:
            assert latest.get(key) == declared.get(key), (
                f"latest_verified mismatch for {key}"
            )

    assert data["reconciliation_policy"].startswith(
        "Reported aggregate BTC holdings are authoritative"
    )

    print(
        f"validated {len(records)} primary-source BTC disclosures; "
        f"latest={latest['total_btc']} as_of={latest['as_of_date']}"
    )


if __name__ == "__main__":
    main()
