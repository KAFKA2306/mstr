from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "verified_btc_disclosures_2026.json"


def load_verified_btc_disclosures(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def latest_verified_state(data: dict[str, Any]) -> dict[str, Any]:
    records = [record for record in data["records"] if record.get("as_of_date")]
    if not records:
        raise ValueError("no disclosure has an as_of_date")
    return max(records, key=lambda record: (record["as_of_date"], record["reported_date"], record["record_id"]))


def main() -> None:
    data = load_verified_btc_disclosures()
    latest = latest_verified_state(data)
    print(
        json.dumps(
            {
                "entity": data["entity"],
                "ticker": data["ticker"],
                "as_of_date": latest["as_of_date"],
                "reported_date": latest["reported_date"],
                "total_btc": latest["total_btc"],
                "source_url": latest["source_url"],
                "verification_status": latest["verification_status"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
