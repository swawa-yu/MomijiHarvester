"""DataConverterクラス

抽出データをCSV/JSON形式に変換し、ファイル出力を行うクラス。
"""

import csv
import json
from typing import Any

import pandas as pd


class DataConverter:
    """抽出データのCSV/JSON変換・ファイル出力を行うクラス。"""

    @staticmethod
    def to_csv(data: list[dict[str, Any]], filepath: str) -> None:
        """データをCSVファイルとして保存する

        Args:
            data (List[Dict[str, Any]]): 保存するデータ
            filepath (str): 出力先ファイルパス
        """
        if not data:
            return
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def to_json(data: list[dict[str, Any]], filepath: str, drop_columns: list[str] = []) -> None:
        """CSVデータをJSONファイルとして保存する

        Args:
            data (List[Dict[str, Any]]): 保存するデータ
            filepath (str): 出力先ファイルパス
            drop_columns (List[str], optional): JSONに変換する際に削除する列名リスト。デフォルトは空リスト。

        Raises:
            ValueError: データが空の場合
            IOError: ファイル書き込み時の入出力エラー
        """
        if not data:
            raise ValueError("空のデータはJSONに変換できません。")
        try:
            df = pd.DataFrame(data)
            if drop_columns:
                df = df.drop(columns=drop_columns, errors="ignore")
            try:
                df = df.set_index("講義コード", drop=False)
                d = df.T.to_dict()
            except KeyError:
                # 講義コード列が存在しない場合はそのままリストを出力
                d = data
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise OSError(f"JSONファイルの書き込みに失敗しました: {e}")
