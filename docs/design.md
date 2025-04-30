# MomijiHarvester 設計書

## 1. 要件定義

*   広島大学のシラバスサイト (`https://momiji.hiroshima-u.ac.jp/syllabusHtml`) から情報を抽出する。
*   抽出した情報をCSV形式で出力する。
*   抽出した情報をJSON形式で出力する。
*   HTML構造は `docs/syllabusHtml-small/` のファイルを参考にする。

## 2. 設計

### 2.1. 概略設計

1.  シラバスHTMLファイルを入力として受け取る。
2.  HTMLパーサー（BeautifulSoupを想定）を使用して必要な情報を抽出する。
3.  抽出した情報を構造化し、CSVデータとして整形する。
4.  CSVデータをファイルに書き出す。
5.  CSVデータを読み込み、JSONデータとして整形する。
6.  JSONデータをファイルに書き出す。

### 2.2. 機能設計

*   HTMLファイル読み込み機能
*   HTMLパース機能
*   情報抽出機能（講義コード、科目名、担当教員など）
*   CSV出力機能
*   JSON出力機能

### 2.3. クラス構成

*   `SyllabusExtractor`: HTMLファイルからシラバス情報を抽出するクラス。
*   `DataConverter`: 抽出したデータをCSV/JSON形式に変換するクラス。
*   `main` 関数またはスクリプト: 処理フローを制御する。
