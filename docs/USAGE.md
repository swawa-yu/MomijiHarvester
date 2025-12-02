# Usage Guide — MomijiHarvester

このドキュメントはローカル・開発者のための使い方とトラブルシューティングのクイックガイドです。

## クイックスタート

1. リポジトリをクローン

```bash
git clone <repo-url>
cd MomijiHarvester
```

2. 開発環境の依存関係をインストール（仮想環境推奨）

```bash
python -m pip install -e .[dev]
```

3. サンプル HTML（`tests/fixtures/html/small`）から抽出する

```bash
python -m src.cli --mode local-small --local-dir tests/fixtures/html/small --output output/test_output.json
```

出力: `output/test_output.json`（JSON）と `output/test_output.csv`（CSV）

## CLI のモード
`--mode` には以下を指定できます（現状の実装）:

- `local-small`: `tests/fixtures/html/small` などのローカルのサンプル HTML を処理
- `local-full`: ローカルのすべての HTML を処理（settings で `local_html_dir_full` を確認）
- `live-small`: 少量の講義コードでライブサイトから取得 （`src/settings.py` に `live_small_codes` を手で設定）
- `live-full`: すべてのライブサイトの講義を収集（未完全・要注意）

## 設定
- `src/settings.py` にデフォルトの dir / list 設定があり、ローカル用のパス等はそこを確認してください。
- `config.py` の `CANONICAL_HEADERS` がモデル alias と一致するようになっています。

## テスト / 静的解析

```bash
# 単体テスト
python -m pytest -q

# 型チェック
mypy src

# ルールチェック (ruff)
ruff check src tests --select F,E,W
```

## 開発フロー（新しい extractor を作る場合）
1. `tests/fixtures/html/small` にあるようなサンプル HTML を追加
2. `extractors.py` にパースロジックの追加
3. `tests/test_extractors.py` にケースを追加
4. `python -m pytest` で動作確認

## 出力ファイルの構成
- JSON: 1 件の配列（records）
- CSV: 値はカンマ区切りで保存、リスト系フィールドはカンマ区切りの文字列として保存されます

## よくある問題・トラブルシュート
- `BaseSettings` のエラー: `pydantic v2` は `BaseSettings` を別パッケージ（pydantic-settings）へ移動しています。現状の実装では `src/settings.py` を軽量なクラスで代替しています。
- ヘッダー（`CANONICAL_HEADERS`）が変更された場合: `models.py` の alias を更新し、`extractors.py` の `validate_headers` の警告/エラーの範囲を確認してください。

## 追加のリソース / TODO
- `harvest_from_web` の改善 (retry/backoff、並列取得)
- CI 用の GitHub Actions を追加する（`pytest`, `mypy`, `ruff`）

---

本ガイドを README に追加しました。必要なら CLI 動作確認のためのサンプルコマンドや、`settings` の `.env` からの読み込み対応の追加も行えます。
