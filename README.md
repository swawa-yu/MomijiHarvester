# MomijiHarvester

広島大学のシラバスサイトから情報を抽出し、CSVおよびJSONファイルとして出力するツールです。

## 概要

本ツールは、広島大学のシラバスサイト (`https://momiji.hiroshima-u.ac.jp/syllabusHtml/`) から個別のシラバスHTMLを取得し、BeautifulSoupを使用して必要な情報を抽出します。抽出されたデータはPandas DataFrameとして処理され、最終的にCSVおよびJSON形式で出力されます。

少量ケースでの試行と本番環境での実行を切り替えられるように設計されています。

## セットアップ

1.  このリポジトリをクローンします。
    ```bash
    git clone <リポジトリのURL>
    cd MomijiHarvester
    ```
2.  依存関係をインストールします。`uv` がインストールされている必要があります。
    ```bash
    uv pip install .
    ```

## 使用方法

本ツールはコマンドラインから実行します。実行時にモードを指定することで、処理対象の講義コードリストを切り替えることができます。

```bash
python -m src.main --mode <mode>
```

`<mode>` には以下のいずれかを指定します。

*   `small`: 設定ファイル (`config.yaml`) の `small_lecture_codes` に記述された講義コードのみを処理します。開発や少量のデータでの試行に使用します。
*   `full`: 設定ファイル (`config.yaml`) の `full_lecture_codes` に記述された講義コードを処理します。現時点では `full_lecture_codes` は空リストとしていますが、全ての講義コードを取得する機能が実装され次第、ここに記述された講義コードが処理されます。

### 設定ファイル (`config.yaml`)

プロジェクトのルートディレクトリにある `config.yaml` ファイルで、各モードで処理する講義コードリストを管理します。

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

必要に応じて `small_lecture_codes` に講義コードを追加してください。

## 出力ファイル

実行結果は `output/` ディレクトリに以下のファイルとして出力されます。

*   `output/syllabus_data.csv`: 抽出されたシラバス情報がCSV形式で保存されます。
*   `output/syllabus_data.json`: 抽出されたシラバス情報がJSON形式で保存されます。

## 今後の課題

*   全ての講義コードを自動的に取得する方法の実装。
*   年度や学科コードを動的に設定できるようにする。
*   URLからHTMLを取得する機能に関するテストコードの追加。
*   HTML構造の変更に対する堅牢性の向上。

## ライセンス

[ここにライセンス情報を記述]
