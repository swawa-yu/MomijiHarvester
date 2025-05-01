# ruff: noqa: PLR2004
"""DataConverterのテスト"""

import csv
import json

from converter import DataConverter


def test_to_csv_and_json(tmp_path) -> None:
    """to_csvおよびto_jsonが正常にファイル出力できることをテスト"""
    data = [
        {"code": "A001", "name": "テスト講義", "teacher": "山田太郎"},
        {"code": "A002", "name": "サンプル講義", "teacher": "佐藤花子"},
    ]
    csv_path = tmp_path / "test.csv"
    json_path = tmp_path / "test.json"

    DataConverter.to_csv(data, str(csv_path))
    DataConverter.to_json(data, str(json_path))

    # CSVファイルの存在と内容の簡易検証
    assert csv_path.exists()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["code"] == "A001"

    # JSONファイルの存在と内容の簡易検証
    assert json_path.exists()
    with open(json_path, encoding="utf-8") as f:
        loaded = json.load(f)
        assert isinstance(loaded, list)
        assert loaded[1]["teacher"] == "佐藤花子"
