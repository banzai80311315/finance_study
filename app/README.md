# Stock Research Studio

個別株の企業情報、財務、価格を確認し、価格系列の基礎的な統計診断を学ぶためのStreamlitアプリです。表示内容は投資判断の補助を目的とし、投資助言ではありません。

## 実行環境と役割

| マシン | 役割 | 実行する操作 |
| --- | --- | --- |
| Linuxサーバー | アプリを動かす | ソースコードの配置・更新、起動、ログ確認、停止 |
| Windowsサーバー | アプリを利用する | ブラウザでLinuxサーバーに接続 |

以下の起動コマンドは、Linuxサーバー上のシェルで実行します。WindowsからSSH接続して操作する場合も、SSH接続後のLinux側で実行してください。Windowsサーバーには、このアプリのためにPythonやDockerをインストールする必要はありません。

Linuxサーバーにこのリポジトリを配置してから、次のいずれかの方法で起動します。各手順の`cd app`はリポジトリのルートから実行する想定です。すでに`app`ディレクトリにいる場合は不要です。

## Linuxサーバー：Pythonで直接起動する場合

Python 3.11とvenvを利用できる環境で実行します。

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
```

停止する場合は、起動したLinux側のターミナルで`Ctrl+C`を押します。

## Linuxサーバー：Dockerで起動する場合

LinuxサーバーにDocker Engineがインストールされ、Dockerサービスが稼働していることが前提です。Pythonでの直接起動とは同じ8501番ポートを使うため、どちらか一方を起動してください。

```bash
cd app
docker build -t stock-research-studio .
docker run -d --rm --name stock-research-studio -p 8501:8501 stock-research-studio
```

`-d`でバックグラウンド起動するため、SSH接続を終了してもコンテナは動き続けます。ログはLinuxサーバーで次のコマンドを実行して確認します。

```bash
docker logs -f stock-research-studio
```

ログ表示は`Ctrl+C`で終了できます（コンテナは停止しません）。アプリを停止するには、Linuxサーバーで次を実行します。`--rm`を指定しているため、停止後にコンテナは自動削除されます。

```bash
docker stop stock-research-studio
```

再度起動する場合は、上記の`docker run`を実行します。ソースコードや依存パッケージを変更した場合は、Linuxサーバー上のソースコードを更新し、コンテナを停止して`docker build`からやり直してください。

## Windowsサーバー：ブラウザから接続

Linuxサーバーでアプリを起動した後、Windowsサーバーのブラウザで次のURLを開きます。

```text
http://<LinuxサーバーのIPアドレスまたはホスト名>:8501
```

例えば、LinuxサーバーのIPアドレスが`192.168.1.100`なら、`http://192.168.1.100:8501`です。`localhost`はブラウザを動かしているWindows自身を指すため、ここではLinuxサーバーのアドレスを指定します。

WindowsサーバーからLinuxサーバーのTCP 8501番ポートへ接続できるネットワーク設定が必要です。ファイアウォール等で制限している場合は、Windowsサーバーからの接続を許可してください。

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
