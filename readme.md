# MSTR・Bitcoin分析snapshot

> **状態: 2020年から2024年を中心に作成された過去の探索的分析です。現在の保有量・株価・財務状態を示すものではありません。**

このリポジトリは、MSTR株価、Bitcoin価格、Bitcoin保有量、財務データを結合し、時価総額とBitcoin保有価値の関係やrolling指標を可視化した研究snapshotです。継続更新中の企業データベース、現在値dashboard、投資判断systemではありません。

## 現在確認できる構成

| パス | 役割 |
|---|---|
| `src/yf.py` | yfinanceと入力CSVを結合し、日次・月次metricsを生成 |
| `src/graph.py` | 過去の分析図を生成 |
| `data/btcholdings.csv` | Bitcoin保有量の入力 |
| `data/mstr_financial_data.csv` | 財務項目の入力 |
| `output/` | 過去に生成されたCSV・画像・report |
| `stats.md` | rolling return、beta、volatility、correlation、Sharpe ratioの過去解釈 |

## 処理の概要

`src/yf.py`は次を結合します。

```text
MSTR close
BTC-USD close
S&P 500 close
Bitcoin保有量CSV
財務CSV
yfinanceのquarterly balance sheet
```

その後、Bitcoin保有価値、時価総額比率、financial leverage等を計算し、日次・月次CSVを生成します。

## 重要な制約

### 図表と数値は現在値ではない

旧READMEに記載されていたBitcoin保有量、投資額、比率、過去最高値等は、2024年までの生成物を読んだ過去の記述です。2026年8月5日時点の公式開示や市場価格と照合していないため、現在の企業状態として利用できません。

### point-in-time整合を保証しない

`src/yf.py`は実行時に取得した`sharesOutstanding`を時系列全体の時価総額計算へ使用します。過去時点ごとの株式数、株式分割、増資、転換、企業actionを保持するpoint-in-time modelではありません。

### forward fill

異なる頻度の価格・保有量・財務データをouter joinし、欠損をforward fillします。公表日と対象期間、情報が市場で利用可能になった時点を区別していないため、backtestや因果評価には利用できません。

### 入力と依存

- `data/*.csv`の全行に一次source、取得日時、document ID、単位、訂正版identityが付与されているわけではありません
- `requirements.txt`を確認できず、依存versionは固定されていません
- CI、自動test、再生成hash、data freshness監査を確認できません
- yfinanceの応答・schema・補正方法は将来変わる可能性があります

## 現在できること

- 過去に作成されたcode、CSV、図表を研究履歴として読む
- MSTRとBitcoinの関係を分析する際に必要な変数候補を確認する
- point-in-time data modelを再設計するための参考にする

## 現在できないこと

- 現在のBitcoin保有量、NAV、premium、leverageの確認
- 公式開示と一致する時系列財務分析
- 再現可能なbacktestや投資performanceの保証
- 投資助言、売買判断、企業価値評価への直接利用

## 再開する場合の最低条件

1. 企業の公式開示を正準sourceとして、document ID・公表日時・訂正版を保存する
2. Bitcoin取得ごとの数量、取得価額、資金調達、株式数、債務をpoint-in-timeで保持する
3. 株式分割・希薄化・転換可能証券を時点別に反映する
4. 実績、会社開示、外部市場data、独自推計を分離する
5. raw data、変換、code commit、設定、生成物hashを結ぶprovenanceを追加する
6. clean environmentで依存・test・再生成をCI検証する

## 注意

このrepositoryの生成物と記述は投資助言ではありません。過去の価格関係は将来のperformanceを保証せず、固定されたsnapshotから現在の企業状態を推測しないでください。

**README監査日:** 2026-08-05
