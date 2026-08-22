# Stock Research Studio

個別株の企業情報、財務、価格、リスクを確認し、時系列モデルを共通の検証方法で比較するためのStreamlitアプリです。表示内容は投資判断の補助を目的とし、投資助言ではありません。

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
├── lib/time_series/           # 時系列モデル・診断・検証（UI非依存）
├── services/                  # データ取得と業務処理
├── views/dashboard_tabs/      # 分析画面
└── tests/                     # 自動テスト
```

## 時系列モデルの追加方法

モデルは `ForecastModel` の共通契約に従います。論文の再現モデルは、モデル固有の前処理・推定・予測をクラス内へ閉じ込めてください。

1. `lib/time_series/models.py` に `ForecastModel` のサブクラスを作る
2. `metadata` に識別子、表示名、説明、仮定、文献情報を書く
3. `minimum_observations` と `forecast(train, horizon)` を実装する
4. ファイル末尾の `register_models(...)` にインスタンスを追加する
5. 未来情報を使わないテストを `tests/` に追加する

最小例：

```python
class PaperModel(ForecastModel):
    metadata = ModelMetadata(
        key="paper_model",
        name="論文モデル",
        description="モデルが表す現象と推定方法",
        assumptions=("定常性", "有限分散"),
        reference="Author (Year), title, DOI",
    )
    minimum_observations = 100

    def forecast(self, train: pd.Series, horizon: int) -> pd.Series:
        clean = self.validate(train, horizon)
        # 論文の推定・予測処理
        return pd.Series(..., dtype=float)
```

時系列ラボは登録モデルを自動的に列挙し、ローリング・オリジン法でMAE、RMSE、MAPE、Biasを計算します。モデル選択に検証期間を使う場合は、最終評価用のホールドアウト期間を別に確保してください。

## 検証

```powershell
python -m pytest app/tests
```

Yahoo Financeの仕様や取得値は変更されることがあります。研究で結果を再現する場合は、取得日時、対象期間、調整済み価格の扱い、欠損処理、パッケージバージョンを保存してください。
