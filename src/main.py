"""MomijiHarvester メインモジュール

シラバスHTMLから情報を抽出し、CSV/JSON形式で出力するエントリーポイント。
"""

import argparse
import yaml
from typing import Any, Dict, List
from extractor import SyllabusExtractor
from converter import DataConverter


def load_config(config_path: str) -> Dict[str, Any]:
    """設定ファイル（YAML）を読み込む

    Args:
        config_path (str): 設定ファイルのパス

    Returns:
        Dict[str, Any]: 設定内容
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする

    Returns:
        argparse.Namespace: パース結果
    """
    parser = argparse.ArgumentParser(description="MomijiHarvester: シラバス情報抽出ツール")
    parser.add_argument("--config", type=str, default="config.yaml", help="設定ファイルパス")
    parser.add_argument("--mode", type=str, choices=["sample", "all"], default="sample", help="取得モード")
    parser.add_argument("--output-dir", type=str, default="output", help="出力ディレクトリ")
    return parser.parse_args()


def main() -> None:
    """メイン処理"""
    args = parse_args()
    config = load_config(args.config)

    # サンプルHTMLファイルのパス（例: docs/syllabusHtml-small/2025_AA.html）
    html_path = config.get("html_path", "docs/syllabusHtml-small/2025_AA.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    extractor = SyllabusExtractor(html_content)
    departments = extractor.extract_departments()
    lectures = extractor.extract_lectures()
    # 講義詳細情報の抽出例
    # lecture_detail = extractor.extract_lecture_detail()

    # CSV/JSON出力例
    DataConverter.to_csv(lectures, f"{args.output_dir}/syllabus_data.csv")
    DataConverter.to_json(lectures, f"{args.output_dir}/syllabus_data.json")


if __name__ == "__main__":
    main()
