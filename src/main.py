"""MomijiHarvester メインモジュール

HTMLファイルを元に開講部局一覧と講義データヘッダー一覧を生成して表示・保存します。
"""

import sys
import os
import glob
import json
from typing import List
from extractor import SyllabusExtractor
from models import Department, LectureDetail

OUTPUT_DIR = "output"


def main() -> None:
    """メイン処理"""
    # 出力ディレクトリ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 開講部局一覧の抽出
    index_path = "docs/syllabusHtml-small/index.html"
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_html = f.read()
    except FileNotFoundError:
        print(f"エラー: インデックスHTMLが見つかりません: {index_path}", file=sys.stderr)
        sys.exit(1)

    extractor = SyllabusExtractor(index_html)
    try:
        departments: List[Department] = extractor.extract_departments()
    except Exception as e:
        print(f"開講部局抽出中にエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

    # 表示
    print("開講部局一覧:")
    for dept in departments:
        print(f"  - {dept.name} (code: {dept.code}, url: {dept.url})")

    # CSV/JSON 保存
    dept_csv = os.path.join(OUTPUT_DIR, "departments.csv")
    dept_json = os.path.join(OUTPUT_DIR, "departments.json")
    # CSV
    with open(dept_csv, "w", encoding="utf-8") as f:
        f.write("name,code,url\n")
        for d in departments:
            f.write(f"{d.name},{d.code},{d.url}\n")
    # JSON
    with open(dept_json, "w", encoding="utf-8") as f:
        json.dump([d.__dict__ for d in departments], f, ensure_ascii=False, indent=2)

    # 講義データヘッダーの抽出
    header_set = set()
    pattern = "docs/syllabusHtml-small/*.html"
    for html_file in glob.glob(pattern):
        # 詳細ページのみ処理: index.html および *_AA.html（部局一覧）をスキップ
        if html_file.endswith("index.html") or html_file.endswith("_AA.html"):
            continue
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                detail_html = f.read()
            detail_extractor = SyllabusExtractor(detail_html)
            lecture: LectureDetail = detail_extractor.extract_lecture_detail()
            header_set.update(vars(lecture).keys())
        except Exception as e:
            print(f"ヘッダー抽出中にエラー: {html_file} -> {e}", file=sys.stderr)

    headers = sorted(header_set)
    print("講義データヘッダー一覧:")
    for h in headers:
        print(f"  {h}")

    # ヘッダーJSON保存
    header_json = os.path.join(OUTPUT_DIR, "lecture_headers.json")
    with open(header_json, "w", encoding="utf-8") as f:
        json.dump(headers, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
