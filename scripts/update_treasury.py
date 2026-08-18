#!/usr/bin/env python3
"""Verify Strategy treasury events against SEC submissions metadata and publish PIT views."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CIK = "0001050446"
SUBMISSIONS_URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"
DEFAULT_LEDGER = ROOT / "data" / "treasury" / "major-events.json"
DEFAULT_EVIDENCE = ROOT / "data" / "treasury" / "evidence"
DEFAULT_API = ROOT / "api" / "v1" / "bitcoin-treasury"
USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "KAFKA2306 Strategy research https://github.com/KAFKA2306/mstr",
)
ACCESSION_RE = re.compile(r"/(\d{18})/([^/?#]+)$")


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def parse_time(value: str) -> datetime:
    if len(value) == 10:
        return datetime.fromisoformat(value).replace(tzinfo=UTC)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def source_identity(url: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "www.sec.gov":
        raise ValueError(f"canonical source must be SEC Archives: {url}")
    match = ACCESSION_RE.search(parsed.path)
    if not match:
        raise ValueError(f"cannot parse SEC accession/document from {url}")
    accession_path, document = match.groups()
    accession = f"{accession_path[:10]}-{accession_path[10:12]}-{accession_path[12:]}"
    return accession, document


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("schema_version") != 1:
        raise ValueError("unsupported ledger schema_version")
    events = ledger.get("events") or []
    if not events:
        raise ValueError("ledger has no events")
    ids: set[str] = set()
    for event in events:
        event_id = str(event.get("id") or "")
        if not event_id or event_id in ids:
            raise ValueError(f"duplicate or missing event id: {event_id!r}")
        ids.add(event_id)
        effective = parse_time(str(event["effective_at"]))
        filed = parse_time(str(event["filed_at"]))
        observed = parse_time(str(event["observed_at"]))
        if filed < effective:
            raise ValueError(f"{event_id}: filed_at precedes effective_at")
        if observed < filed:
            raise ValueError(f"{event_id}: observed_at precedes filed_at")
        source_identity(str(event["source_url"]))
        if not event.get("facts"):
            raise ValueError(f"{event_id}: no facts")
        for fact in event["facts"]:
            if fact.get("fact_class") not in {
                "event",
                "state",
                "instrument_term",
                "authorization",
                "historical_adjustment",
            }:
                raise ValueError(
                    f"{event_id}: unsupported fact_class {fact.get('fact_class')}"
                )
            if fact.get("value") is None or not fact.get("unit") or not fact.get("name"):
                raise ValueError(f"{event_id}: incomplete fact {fact}")


def flatten_recent(payload: dict[str, Any]) -> list[dict[str, Any]]:
    recent = payload.get("filings", {}).get("recent", {})
    accessions = recent.get("accessionNumber", [])
    rows: list[dict[str, Any]] = []
    for index, accession in enumerate(accessions):
        rows.append(
            {
                "accession_number": accession,
                "filing_date": recent.get("filingDate", [None] * len(accessions))[index],
                "report_date": recent.get("reportDate", [None] * len(accessions))[index],
                "acceptance_datetime": recent.get(
                    "acceptanceDateTime", [None] * len(accessions)
                )[index],
                "form": recent.get("form", [None] * len(accessions))[index],
                "primary_document": recent.get(
                    "primaryDocument", [None] * len(accessions)
                )[index],
            }
        )
    return rows


def verify_and_store(
    ledger: dict[str, Any], evidence_dir: Path
) -> dict[str, dict[str, Any]]:
    raw = fetch(SUBMISSIONS_URL)
    payload = json.loads(raw)
    if str(payload.get("cik")) not in {"1050446", CIK}:
        raise ValueError(f"SEC submissions returned unexpected CIK {payload.get('cik')}")
    rows = flatten_recent(payload)
    by_accession = {str(row["accession_number"]): row for row in rows}
    missing: list[str] = []
    verified: dict[str, dict[str, Any]] = {}
    submissions_sha = sha256(raw)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = evidence_dir / f"sec-submissions-{submissions_sha}.json"
    if not snapshot_path.exists():
        snapshot_path.write_bytes(raw)
    for event in ledger["events"]:
        accession, document = source_identity(str(event["source_url"]))
        filing = by_accession.get(accession)
        if filing is None:
            missing.append(f"{event['id']}:{accession}")
            continue
        if str(filing["filing_date"]) != str(event["filed_at"]):
            raise ValueError(
                f"{event['id']}: ledger filed_at={event['filed_at']} "
                f"but SEC submissions says {filing['filing_date']}"
            )
        verified[str(event["id"])] = {
            "accession_number": accession,
            "document": document,
            "form": filing["form"],
            "filing_date": filing["filing_date"],
            "report_date": filing["report_date"],
            "acceptance_datetime": filing["acceptance_datetime"],
            "primary_document": filing["primary_document"],
            "source_url": event["source_url"],
            "submissions_source_url": SUBMISSIONS_URL,
            "submissions_sha256": submissions_sha,
            "submissions_evidence": f"data/treasury/evidence/{snapshot_path.name}",
        }
    if missing:
        raise ValueError(
            "ledger accessions not present in current SEC submissions snapshot: "
            + ", ".join(missing)
        )
    manifest = {
        "schema_version": 2,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "source_url": SUBMISSIONS_URL,
        "source_sha256": submissions_sha,
        "snapshot": f"data/treasury/evidence/{snapshot_path.name}",
        "events": verified,
    }
    (evidence_dir / "manifest.json").write_bytes(canonical_json(manifest))
    return verified


def verify_offline(evidence_dir: Path) -> dict[str, dict[str, Any]]:
    manifest = json.loads((evidence_dir / "manifest.json").read_text(encoding="utf-8"))
    snapshot = ROOT / str(manifest["snapshot"])
    if not snapshot.exists() or sha256(snapshot.read_bytes()) != manifest["source_sha256"]:
        raise ValueError("cached SEC submissions evidence hash mismatch")
    return manifest["events"]


def enrich_events(
    ledger: dict[str, Any], verified: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for source in ledger["events"]:
        event = {key: value for key, value in source.items() if key != "evidence_tokens"}
        evidence = verified.get(str(event["id"]))
        if not evidence:
            raise ValueError(f"{event['id']}: no verified SEC filing metadata")
        event["accession_number"] = evidence["accession_number"]
        event["source_document"] = evidence["document"]
        event["sec_form"] = evidence["form"]
        event["sec_acceptance_datetime"] = evidence["acceptance_datetime"]
        event["sec_primary_document"] = evidence["primary_document"]
        event["sec_submissions_sha256"] = evidence["submissions_sha256"]
        event["sec_submissions_evidence"] = evidence["submissions_evidence"]
        events.append(event)
    return sorted(events, key=lambda item: (parse_time(item["observed_at"]), item["id"]))


def point_in_time_snapshots(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}
    snapshots: list[dict[str, Any]] = []
    for event in events:
        for fact in event["facts"]:
            if fact["fact_class"] != "state":
                continue
            key = str(fact["name"])
            if fact.get("instrument"):
                key = f"{key}:{fact['instrument']}"
            state[key] = {
                **fact,
                "effective_at": event["effective_at"],
                "known_at": event["observed_at"],
                "source_event_id": event["id"],
                "source_url": event["source_url"],
                "accession_number": event["accession_number"],
                "sec_submissions_sha256": event["sec_submissions_sha256"],
            }
        snapshots.append(
            {
                "known_at": event["observed_at"],
                "trigger_event_id": event["id"],
                "state": dict(sorted(state.items())),
            }
        )
    return snapshots


def instrument_view(events: list[dict[str, Any]]) -> dict[str, Any]:
    instruments: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        for fact in event["facts"]:
            instrument = fact.get("instrument")
            if not instrument:
                continue
            instruments.setdefault(str(instrument), []).append(
                {
                    **fact,
                    "event_id": event["id"],
                    "effective_at": event["effective_at"],
                    "known_at": event["observed_at"],
                    "source_url": event["source_url"],
                    "accession_number": event["accession_number"],
                    "sec_submissions_sha256": event["sec_submissions_sha256"],
                }
            )
    return {"schema_version": 1, "instruments": dict(sorted(instruments.items()))}


def build_views(
    ledger: dict[str, Any], verified: dict[str, dict[str, Any]], api_dir: Path
) -> dict[str, Any]:
    validate_ledger(ledger)
    events = enrich_events(ledger, verified)
    snapshots = point_in_time_snapshots(events)
    api_dir.mkdir(parents=True, exist_ok=True)
    (api_dir / "events.json").write_bytes(
        canonical_json({"schema_version": 1, "entity": ledger["entity"], "events": events})
    )
    (api_dir / "snapshots.json").write_bytes(
        canonical_json(
            {
                "schema_version": 1,
                "entity": ledger["entity"],
                "rule": (
                    "A fact becomes visible only at known_at; future filings are never "
                    "backfilled into earlier snapshots."
                ),
                "snapshots": snapshots,
            }
        )
    )
    instruments = instrument_view(events)
    (api_dir / "instruments.json").write_bytes(canonical_json(instruments))
    latest = {
        "schema_version": 1,
        "entity": ledger["entity"],
        "known_at": snapshots[-1]["known_at"],
        "state": snapshots[-1]["state"],
    }
    (api_dir / "latest.json").write_bytes(canonical_json(latest))
    index = {
        "schema_version": 1,
        "dataset": "Strategy Bitcoin treasury point-in-time evidence",
        "entity": ledger["entity"],
        "coverage": {
            "first_effective_at": events[0]["effective_at"],
            "last_effective_at": events[-1]["effective_at"],
            "event_count": len(events),
            "source_accession_count": len(verified),
        },
        "views": {
            "events": "events.json",
            "snapshots": "snapshots.json",
            "instruments": "instruments.json",
            "latest": "latest.json",
        },
        "rules": [
            "company disclosure facts are separate from market observations and derived metrics",
            "effective_at is the economic/event date; known_at/observed_at gates point-in-time availability",
            "share counts are never applied before the filing that disclosed them",
            "historical stock-split adjustments are labeled and do not mutate prior raw disclosures",
            "every event is bound to an SEC accession verified against a hashed SEC submissions snapshot",
            "SEC Archives document HTML is referenced by immutable URL but is not scraped by GitHub Actions",
        ],
    }
    (api_dir / "index.json").write_bytes(canonical_json(index))
    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--api-dir", type=Path, default=DEFAULT_API)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    validate_ledger(ledger)
    verified = verify_offline(args.evidence_dir) if args.offline else verify_and_store(
        ledger, args.evidence_dir
    )
    index = build_views(ledger, verified, args.api_dir)
    print(json.dumps(index["coverage"], sort_keys=True))


if __name__ == "__main__":
    main()
