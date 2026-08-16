#!/usr/bin/env python3
"""Collect Strategy Inc. filing metadata from the SEC submissions API."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

CIK = "0001050446"
URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"
FORMS = {"8-K", "10-Q", "10-K", "424B5", "S-3ASR"}


def download() -> bytes:
    req = Request(
        URL,
        headers={
            "User-Agent": "KAFKA2306 Strategy research https://github.com/KAFKA2306/mstr",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    with urlopen(req, timeout=60) as response:
        return response.read()


def normalize(raw: bytes) -> dict[str, object]:
    payload = json.loads(raw)
    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    rows = []
    for i, form in enumerate(forms):
        if form not in FORMS:
            continue
        accession = recent["accessionNumber"][i]
        primary = recent["primaryDocument"][i]
        accession_path = accession.replace("-", "")
        rows.append({
            "accession_number": accession,
            "form": form,
            "filing_date": recent["filingDate"][i],
            "report_date": recent["reportDate"][i],
            "acceptance_datetime": recent.get("acceptanceDateTime", [None] * len(forms))[i],
            "primary_document": primary,
            "source_url": f"https://www.sec.gov/Archives/edgar/data/1050446/{accession_path}/{primary}",
        })
    return {
        "schema_version": 1,
        "issuer": {"name": payload.get("name"), "cik": CIK, "tickers": payload.get("tickers", [])},
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_url": URL,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "filings": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/sec/strategy-filings.json"))
    args = parser.parse_args()
    result = normalize(download())
    if not result["filings"]:
        raise SystemExit("SEC submissions API returned no target filings")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(result['filings'])} filings -> {args.output}")


if __name__ == "__main__":
    main()
