# Strategy / Bitcoin 分析

[![Verified Strategy BTC disclosures](https://github.com/KAFKA2306/mstr/actions/workflows/verified-btc-disclosures.yml/badge.svg)](https://github.com/KAFKA2306/mstr/actions/workflows/verified-btc-disclosures.yml)

> **状態:** このrepositoryには、(1) 2020〜2024年を中心に作成された探索的分析と、(2) 2026年のStrategy Inc.公式開示をpoint-in-timeで保存する限定的な一次資料ledgerが共存しています。旧分析のCSV・図表を現在値として使わないでください。

## Vision

Strategy Inc.とBitcoinの関係を分析するとき、**過去に何が分かっていたか、どの値が後から追加されたか、どの計算が現在の判断には再利用できないか**を区別できるresearch archiveにします。

## Design philosophy

- 企業開示、market data、独自CSVを分離する
- `effective_at`、`filed_at`、`observed_at`を混同しない
- 過去の保有量・株価・ratioを現在値として表示しない
- current shares outstandingをhistorical market capへ適用しない
- forward fillをinformation availabilityの証明にしない
- 公式開示を保存する場合はSEC accessionや発行体URLを保持する
- 未確認のNAV、premium、leverage、投資判断をこのrepositoryから推定しない

## Why

このrepositoryの価値は、古いnotebookをそのまま残すことではなく、**historical exploratory analysisと、後から追加したpoint-in-time一次資料を明確に分離し、どの結論が再利用可能かを判断できること**です。

## 現在確認できる構成

| パス | 役割 |
|---|---|
| `src/yf.py` | yfinanceと旧入力CSVを結合し、日次・月次metricsを生成する探索コード |
| `src/graph.py` | 過去の分析図を生成 |
| `data/btcholdings.csv` | 旧Bitcoin保有量入力 |
| `data/mstr_financial_data.csv` | 旧財務入力 |
| `data/official/` | Strategy公式開示から保存した限定的な一次資料snapshot |
| `data/treasury/major-events.json` | SEC accession等へ結び付けたtreasury event ledger |
| `data/verified_btc_disclosures_2026.json` | 2026年の検証対象BTC開示 |
| `src/current_btc_state.py` | 検証済み開示から指定時点のBTC stateを再構成 |
| `output/` | 過去に生成されたCSV・画像・report |
| `stats.md` | rolling return、beta、volatility、correlation、Sharpe ratioの過去解釈 |

## 2026年に検証済みの限定的な現在情報

Strategy Inc.は、2026年7月6日提出のForm 8-Kで、**2026年7月5日時点のBitcoin保有量843,775 BTC、aggregate purchase price $63.69 billion、average purchase price $75,476**を開示しています。

- SEC filing: https://www.sec.gov/Archives/edgar/data/1050446/000119312526295586/mstr-20260706.htm
- repository snapshot: `data/official/strategy-btc-2026-07-05.json`

この値は上記開示日時点のsnapshotです。現在の保有量を意味しません。新しい開示がある場合は、必ず新しいSEC filingまたはStrategy公式開示を確認してください。

## Historical analysis の処理

`src/yf.py`は次を結合します。

```text
MSTR close
BTC-USD close
S&P 500 close
Bitcoin保有量CSV
財務CSV
yfinanceのquarterly balance sheet
```

その後、Bitcoin保有価値、時価総額比率、financial leverage等を計算し、日次・月次CSVを生成します。この経路はpoint-in-time整合を保証しません。

## 重要な制約

### 旧図表と数値は現在値ではない

`output/`、旧CSV、`stats.md`にある値は主に2020〜2024年の探索結果です。2026年の企業状態として利用できません。

### point-in-time整合を保証しない旧計算

`src/yf.py`は実行時に取得した`sharesOutstanding`を時系列全体の時価総額計算へ使用します。過去時点ごとの株式数、株式分割、増資、転換、企業actionを完全に保持するmodelではありません。

### forward fill

旧分析は異なる頻度の価格・保有量・財務データをouter joinし、欠損をforward fillします。公表日、対象期間、情報が市場で利用可能になった時点を区別していないため、backtestや因果評価には利用できません。

### provenance

- 旧`data/*.csv`の全行に一次source、取得日時、document ID、単位、訂正版identityが付いているわけではありません
- `requirements.txt`は存在せず、旧探索分析の依存versionは固定されていません
- 旧探索分析全体には再現可能な自動test、再生成hash、data freshness監査がありません
- 2026年の限定的なtreasury dataは、`Verified Strategy BTC disclosures` workflowとpoint-in-time ledgerで別管理しています
- yfinanceの応答・schema・補正方法は将来変わる可能性があります

## 現在できること

- 2020〜2024年中心の探索コード・CSV・図表を研究履歴として読む
- 旧分析のpoint-in-time不整合を確認する
- repositoryに保存された2026年の限定的なStrategy公式開示をSEC filingへ追跡する
- `data/treasury/major-events.json`から保存済みeventのeffective / filing時点を確認する
- point-in-time data modelを再設計する材料にする

## 現在できないこと

- repositoryだけから現在時点のBitcoin保有量、NAV、premium、leverageを断定する
- 旧探索CSVから公式開示と一致するhistorical market capやdilutionを再現する
- 旧forward-filled outputを再現可能なbacktestへ利用する
- 投資助言、売買判断、企業価値評価を保証する

## 再構築・拡張する場合

1. SEC / Strategy公式開示を正準sourceとして、accession、document URL、公表日時、訂正版を保存する
2. Bitcoin取得・売却、数量、取得価額、資金調達、株式数、債務・優先株をpoint-in-timeで保持する
3. corporate action、希薄化、転換可能証券を時点別に反映する
4. 実績、会社開示、外部market data、独自推計を分離する
5. raw data、変換、code commit、設定、生成物hashを結ぶprovenanceを維持する
6. clean environmentで依存・test・再生成を検証する

## 注意

このrepositoryの生成物と記述は投資助言ではありません。固定されたsnapshotから現在の企業状態を推測せず、現在値が必要な場合は最新のSEC filingまたはStrategy公式開示を確認してください。

**README監査日:** 2026-08-18
