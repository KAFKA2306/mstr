#!/usr/bin/env python3
"""Publish Strategy treasury views while recording primary-origin accessibility honestly."""
from __future__ import annotations

import argparse
import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path

from update_treasury import (
    DEFAULT_API,
    DEFAULT_EVIDENCE,
    DEFAULT_LEDGER,
    ISSUER_ARCHIVE_URL,
    build_views,
    canonical_json,
    event_references,
    issuer_archive_snapshot,
    validate_ledger,
)


def verify_sources(ledger: dict, evidence_dir: Path) -> tuple[dict, dict]:
    refs = event_references(ledger)
    try:
        archive = issuer_archive_snapshot(evidence_dir)
        archive["retrieval_status"] = "ok"
        archive["http_status"] = 200
    except urllib.error.HTTPError as exc:
        if exc.code != 403:
            raise
        archive = {
            "source_url": ISSUER_ARCHIVE_URL,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "retrieval_status": "origin_blocked_403",
            "http_status": 403,
            "sha256": None,
            "evidence": None,
            "verified_markers": [],
        }

    manifest = {
        "schema_version": 4,
        "retrieved_at": archive["retrieved_at"],
        "issuer_archive": archive,
        "events": refs,
        "provenance_rule": (
            "Curated facts are bound to immutable SEC Archives URLs and accession identities. "
            "Strategy's issuer-hosted SEC filing archive is monitored when reachable; an HTTP 403 "
            "from GitHub-hosted runners is recorded explicitly and never replaced with third-party data."
        ),
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "manifest.json").write_bytes(canonical_json(manifest))
    return refs, archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--api-dir", type=Path, default=DEFAULT_API)
    args = parser.parse_args()

    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    validate_ledger(ledger)
    refs, archive = verify_sources(ledger, args.evidence_dir)
    index = build_views(ledger, refs, archive, args.api_dir)
    print(
        json.dumps(
            {
                **index["coverage"],
                "issuer_archive_retrieval_status": archive["retrieval_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
