# MomijiHarvester

広島大学のシラバスサイトから情報を抽出し、CSVおよびJSONファイルとして出力するツールです。

## 概要

本ツールは、広島大学のシラバスサイト (`https://momiji.hiroshima-u.ac.jp/syllabusHtml/`) から個別のシラバスHTMLを取得し、BeautifulSoupを使用して必要な情報を抽出します。抽出されたデータはPandas DataFrameとして処理され、最終的にCSVおよびJSON形式で出力されます。

少量ケースでの試行と本番環境での実行を切り替えられるように設計されています。

## セットアップ (Quick Start)

1. このリポジトリをクローンします。

```bash
git clone <リポジトリのURL>
cd MomijiHarvester
```

2. Python 開発用依存関係をインストールします（仮想環境推奨）。

```bash
# dev環境で必要な依存も含めてインストール
python -m pip install -e .[dev]
```

注: このプロジェクトは Python 3.11 以上で動作するように構成されています。

## 使用方法

本ツールはコマンドラインから実行します。実行時にモードを指定することで、処理対象の講義コードリストを切り替えることができます。

```bash
python -m src.cli --mode <mode>
```

`<mode>` には以下のいずれかを指定します。

* `local-small`: `tests/fixtures/html/small` にあるサンプル HTML を対象に小規模実行を行います。開発や少量のデータでの試行に使用します。
* `local-full`: ローカルにある全 HTML を対象に実行します（`src/settings.py` にある `local_html_dir_full` を参照）。
* `live-small`: 少量の講義コードでライブサイト (`momiji.hiroshima-u.ac.jp`) を取得して実行するためのモード (事前に `src/settings.py` の `live_small_codes` を編集して、対象の講義コードを設定してください)。
* `live-full`: ライブサイトから全件取得して実行するモード（未実装/リスクあり：サイトへの影響や取得ロジックの追加が必要です）。

### 設定ファイル (`config.yaml`)

プロジェクトのルートディレクトリにある `config.yaml` ファイルで、各モードで処理する講義コードリストを管理します。

# 設定ファイルの位置: `config.yaml` を使えますが、現在の実装では `src/settings.py` の設定が優先されます。
```yaml
# MomijiHarvester Configuration

# List of lecture codes for small mode (testing/development)
small_lecture_codes:
  - "10000100"
  # Add more lecture codes for small testing if needed

# List of all lecture codes for full mode (production)
# TODO: Implement a way to automatically generate or obtain the full list of lecture codes
full_lecture_codes:
  # - "..."
```

必要に応じて `small_lecture_codes` に講義コードを追加してください。ライブ（`live-small`）を使う場合は `src/settings.py` に `live_small_codes` を設定するか、このモードを実行する前に `src/settings.py` を編集してください。

## 出力ファイル

実行結果は `output/` ディレクトリに以下のファイルとして出力されます。

* `output/syllabus_data.csv`: 抽出されたシラバス情報がCSV形式で保存されます。
* `output/syllabus_data.json`: 抽出されたシラバス情報がJSON形式で保存されます。

CLI の例:

```bash
# ローカルのサンプルHTMLからスモール実行
python -m src.cli --mode local-small --local-dir tests/fixtures/html/small --output output/test_output.json

# 保存されるのは output ディレクトリ下の JSON と CSV
```

注: `live-small` / `live-full` はライブ取得に依存するため、用途と負荷について慎重に利用してください。

## 今後の課題 / TODO

* 全ての講義コードを自動的に取得する方法の実装 (full/live対応)
* 年度や学科コードを動的に設定できるようにする
* `harvest_from_web` の安定化（リトライ/タイムアウト/バックオフ、並列取得など）
* 設定周りの強化（`.env` あるいは `pydantic-settings` の導入）
* HTML 構造の変更に対する堅牢性の向上と追加の E2E テスト

## pre-commit の導入

このリポジトリは `pre-commit` によるコード品質フックが導入されています。ローカルで作業する前に以下の手順で導入してください。

```bash
# 仮想環境を有効化している前提
python -m pip install pre-commit
pre-commit install
# 手元の全ファイルに対して自動修正を実行 (初回または追従後におすすめ)
pre-commit run --all-files
```

CI（GitHub Actions）にも `pre-commit` が組み込まれており、Push / PR 時にフックが実行されます。

**注意**: `pre-commit` はフォーマッタやリンタでファイルを自動修正します。初回では差分が大量に発生する可能性があるので、差分を確認してからコミットしてください。


## ライセンス

[ここにライセンス情報を記述]
