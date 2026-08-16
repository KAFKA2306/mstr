import json

from scripts.collect_sec_filings import normalize


def test_normalize_keeps_filing_date_report_date_and_acceptance_time():
    raw = json.dumps({
        "name": "Strategy Inc",
        "tickers": ["MSTR"],
        "filings": {"recent": {
            "form": ["8-K", "4"],
            "accessionNumber": ["0001050446-26-000001", "0001050446-26-000002"],
            "filingDate": ["2026-07-06", "2026-07-06"],
            "reportDate": ["2026-07-05", "2026-07-05"],
            "acceptanceDateTime": ["20260706120000", "20260706130000"],
            "primaryDocument": ["mstr-20260706.htm", "xslF345X05/doc.xml"]
        }}
    }).encode()
    result = normalize(raw)
    assert len(result["filings"]) == 1
    row = result["filings"][0]
    assert row["form"] == "8-K"
    assert row["filing_date"] == "2026-07-06"
    assert row["report_date"] == "2026-07-05"
    assert row["acceptance_datetime"] == "20260706120000"
    assert row["source_url"].startswith("https://www.sec.gov/Archives/edgar/data/1050446/")
