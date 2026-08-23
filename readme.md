# Strategy Bitcoin Treasury Evidence

[![Verified Strategy BTC disclosures](https://github.com/KAFKA2306/mstr/actions/workflows/verified-btc-disclosures.yml/badge.svg)](https://github.com/KAFKA2306/mstr/actions/workflows/verified-btc-disclosures.yml)
[![Deploy Pages](https://github.com/KAFKA2306/mstr/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/mstr/actions/workflows/pages.yml)

Strategy Inc. のBitcoin treasuryを、SEC / Strategy公式開示のpoint-in-time ledgerとして追跡します。

**Public dashboard:** https://kafka2306.github.io/mstr/

## Current authority

Bitcoin holdingsのcurrent-facing authorityは [`data/verified_btc_disclosures_2026.json`](data/verified_btc_disclosures_2026.json) です。

- `reported_date`: 開示日
- `as_of_date`: 開示が対象とする状態日
- `event_type`: `acquisition` / `sale` / `no_change`
- `btc_delta`: その開示で明示された増減
- `total_btc`: 開示されたaggregate BTC holdings
- `source_url`: SEC ArchivesまたはStrategy公式一次情報
- `verification_status`: primary source確認状態

報告されたaggregate holdingsをauthorityとし、隣接する`btc_delta`の算術差から未開示調整を補完しません。

## Public dashboard contract

[`web/index.html`](web/index.html) はverified disclosure ledgerだけをcurrent BTC stateとして読みます。

- latest verified BTC holdings
- aggregate purchase price / average purchase price（最新recordに一次開示がある場合）
- previous verified stateとの差分
- `as_of_date` / `reported_date`
- recent acquisition / sale / no-change timeline
- primary sourceへの直接link
- last verified stateのage

**古い開示を今日の状態としてforward-fillしません。** 新しい一次開示がledgerに存在しない場合は、最後に確認できた状態とその古さをそのまま表示します。

## Historical archive

このrepositoryには2020〜2024年中心の探索的分析も残っています。

- `src/yf.py`
- `src/graph.py`
- `data/btcholdings.csv`
- `data/mstr_financial_data.csv`
- `output/`
- `stats.md`

これらはresearch historyであり、current holdings / NAV / premium / leverageのauthorityではありません。旧forward-filled outputや実行時shares outstandingをpoint-in-time current stateへ再利用しません。

## Other treasury evidence

[`data/treasury/major-events.json`](data/treasury/major-events.json) と `api/v1/bitcoin-treasury/` はcapital structureを含む広いtreasury event modelです。週次BTC holdingsのcurrent-facing authorityとは責務を分けています。

二つのledgerで同じcurrent BTC valueを手作業同期することを前提にしません。統合する場合は、verified disclosure ledgerをBTC holdings sourceとして生成する形に寄せます。

## Validation

```bash
python scripts/verify_btc_disclosures.py
python src/current_btc_state.py
python -m unittest discover -s tests -v
```

`Deploy Pages` workflowはPRでledger semanticsとdashboard JavaScriptを検証し、mainでは同じverified ledgerをGitHub Pagesへdeployします。deploy後に公開`deployment.json`のcommit SHAとlatest disclosure identityを照合します。

## Source policy

- SEC Archives / Strategy公式開示を優先する
- `effective/as-of` と `reported/known` を分離する
- acquisition / sale / no-changeを別eventとして保持する
- historical exploratory outputをcurrent stateへ昇格しない
- sourceにないNAV、premium、leverage、現在株式数を推測しない
- 新しい開示が未収録ならstaleをstaleのまま示す

このrepositoryは投資助言・売買signalを提供しません。
