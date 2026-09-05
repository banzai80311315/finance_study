# Stock Research Studio

個別株の企業情報、財務、価格を確認し、価格系列の基礎的な統計診断を学ぶためのStreamlitアプリです。表示内容は投資判断の補助を目的とし、投資助言ではありません。

## 起動

```powershell
cd app
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 構成

```text
app/
├── app.py                     # 初期化と画面ルーティング
├── data/stock_master.csv      # 対象銘柄
├── lib/time_series/           # 時系列診断（UI非依存）
├── services/                  # データ取得と業務処理
├── views/dashboard_tabs/      # 分析画面
└── tests/                     # 自動テスト
```

## 検証

```powershell
python -m pytest app/tests
```

Yahoo Financeの仕様や取得値は変更されることがあります。研究で結果を再現する場合は、取得日時、対象期間、調整済み価格の扱い、欠損処理、パッケージバージョンを保存してください。
