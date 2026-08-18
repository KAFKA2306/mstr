#!/usr/bin/env python3
"""Verify Strategy treasury facts against SEC documents and publish point-in-time views."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "treasury" / "major-events.json"
DEFAULT_EVIDENCE = ROOT / "data" / "treasury" / "evidence"
DEFAULT_API = ROOT / "api" / "v1" / "bitcoin-treasury"
USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "KAFKA2306/mstr github.com/KAFKA2306/mstr",
)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalized_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text).replace("\xa0", " ")).strip()


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
        if not str(event["source_url"]).startswith("https://www.sec.gov/"):
            raise ValueError(f"{event_id}: non-SEC source in canonical ledger")
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
                raise ValueError(f"{event_id}: unsupported fact_class {fact.get('fact_class')}")
            if fact.get("value") is None or not fact.get("unit") or not fact.get("name"):
                raise ValueError(f"{event_id}: incomplete fact {fact}")


def verify_and_store(
    ledger: dict[str, Any], evidence_dir: Path
) -> dict[str, dict[str, Any]]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    verified: dict[str, dict[str, Any]] = {}
    for event in ledger["events"]:
        raw = fetch(str(event["source_url"]))
        text = normalized_text(raw)
        missing = [
            token
            for token in event.get("evidence_tokens", [])
            if re.sub(r"\s+", " ", str(token)).strip() not in text
        ]
        if missing:
            raise ValueError(f"{event['id']}: source is missing evidence tokens {missing}")
        digest = sha256(raw)
        suffix = ".htm" if b"<html" in raw[:1000].lower() or b"<!doctype" in raw[:1000].lower() else ".bin"
        path = evidence_dir / f"{digest}{suffix}"
        if not path.exists():
            path.write_bytes(raw)
        verified[str(event["id"])] = {
            "sha256": digest,
            "path": path.name,
            "bytes": len(raw),
            "source_url": event["source_url"],
        }
    manifest = {
        "schema_version": 1,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "documents": verified,
    }
    (evidence_dir / "manifest.json").write_bytes(canonical_json(manifest))
    return verified


def enrich_events(
    ledger: dict[str, Any], verified: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for source in ledger["events"]:
        event = {key: value for key, value in source.items() if key != "evidence_tokens"}
        evidence = verified.get(str(event["id"]))
        if not evidence:
            raise ValueError(f"{event['id']}: no verified source evidence")
        event["source_sha256"] = evidence["sha256"]
        event["source_evidence"] = f"data/treasury/evidence/{evidence['path']}"
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
                "source_sha256": event["source_sha256"],
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
                    "source_sha256": event["source_sha256"],
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
    events_view = {
        "schema_version": 1,
        "entity": ledger["entity"],
        "events": events,
    }
    snapshots_view = {
        "schema_version": 1,
        "entity": ledger["entity"],
        "rule": "A fact becomes visible only at known_at; future filings are never backfilled into earlier snapshots.",
        "snapshots": snapshots,
    }
    instruments = instrument_view(events)
    latest = {
        "schema_version": 1,
        "entity": ledger["entity"],
        "known_at": snapshots[-1]["known_at"],
        "state": snapshots[-1]["state"],
    }
    (api_dir / "events.json").write_bytes(canonical_json(events_view))
    (api_dir / "snapshots.json").write_bytes(canonical_json(snapshots_view))
    (api_dir / "instruments.json").write_bytes(canonical_json(instruments))
    (api_dir / "latest.json").write_bytes(canonical_json(latest))
    index = {
        "schema_version": 1,
        "dataset": "Strategy Bitcoin treasury point-in-time evidence",
        "entity": ledger["entity"],
        "coverage": {
            "first_effective_at": events[0]["effective_at"],
            "last_effective_at": events[-1]["effective_at"],
            "event_count": len(events),
            "source_document_count": len(verified),
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
            "source bytes are stored by SHA-256 and every event points to the exact SEC document",
        ],
    }
    (api_dir / "index.json").write_bytes(canonical_json(index))
    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--api-dir", type=Path, default=DEFAULT_API)
    parser.add_argument("--offline", action="store_true", help="reuse evidence manifest and files")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    validate_ledger(ledger)
    if args.offline:
        manifest = json.loads((args.evidence_dir / "manifest.json").read_text(encoding="utf-8"))
        verified = manifest["documents"]
        for event_id, item in verified.items():
            path = args.evidence_dir / item["path"]
            if not path.exists() or sha256(path.read_bytes()) != item["sha256"]:
                raise ValueError(f"{event_id}: cached SEC evidence hash mismatch")
    else:
        verified = verify_and_store(ledger, args.evidence_dir)
    index = build_views(ledger, verified, args.api_dir)
    print(json.dumps(index["coverage"], sort_keys=True))


if __name__ == "__main__":
    main()
