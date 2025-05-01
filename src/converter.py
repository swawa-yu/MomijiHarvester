"""DataConverterクラス

抽出データをCSV/JSON形式に変換し、ファイル出力を行うクラス。
"""

from typing import List, Dict, Any
import csv
import json


class DataConverter:
    """抽出データのCSV/JSON変換・ファイル出力を行うクラス。"""

    @staticmethod
    def to_csv(data: List[Dict[str, Any]], filepath: str) -> None:
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
    def to_json(data: List[Dict[str, Any]], filepath: str) -> None:
        """データをJSONファイルとして保存する

        Args:
            data (List[Dict[str, Any]]): 保存するデータ
            filepath (str): 出力先ファイルパス
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
