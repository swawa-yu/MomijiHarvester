"""MomijiHarvester メインモジュール

HTMLファイルを元に開講部局一覧と講義データヘッダー一覧を生成して表示・保存します。
"""

import os
import sys
import glob
import json
import datetime
import yaml
from typing import List

from extractor import SyllabusExtractor
from models import Department, LectureDetail
from converter import DataConverter

CONFIG_PATH = "config.yaml"
OUTPUT_ROOT = "output"


def main() -> None:
    """メイン処理"""
    # 設定読み込み
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"設定ファイルが見つかりません: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    # 日付とモード設定
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # sample: 少量検証用、小HTMLを優先
    if os.path.exists("docs/syllabusHtml-small/index.html"):
        index_path = "docs/syllabusHtml-small/index.html"
        mode = "sample"
    else:
        index_path = "docs/syllabusHtml/index.html"
        mode = "all"
    suffix = f"_{mode}" if mode == "sample" else ""

    # 出力ディレクトリ
    out_dir = os.path.join(OUTPUT_ROOT, date_str, mode)
    os.makedirs(out_dir, exist_ok=True)

    # 抽出
    try:
        with open(index_path, encoding="utf-8") as f:
            html = f.read()
        extractor = SyllabusExtractor(html)
        departments: List[Department] = extractor.extract_departments()
    except Exception as e:
        print(f"開講部局抽出中にエラー: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"開講部局一覧を {out_dir}/departments{suffix}.csv に出力しました")

    # ファイル出力: 部局
    dept_csv = os.path.join(out_dir, f"departments{suffix}.csv")
    dept_json = os.path.join(out_dir, f"departments{suffix}.json")
    # CSV
    with open(dept_csv, "w", encoding="utf-8") as f:
        f.write("name,code,url\n")
        for d in departments:
            f.write(f"{d.name},{d.code},{d.url}\n")
    # JSON
    DataConverter.to_json([d.__dict__ for d in departments], dept_json)

    # 講義一覧取得
    lectures = []
    for dept in departments:
        rel = dept.url
        try:
            # HTML取得
            url = f"https://momiji.hiroshima-u.ac.jp/syllabusHtml/{rel}"
            import requests
            r = requests.get(url)
            r.encoding = r.apparent_encoding
            lec_html = r.text
            lecturer = SyllabusExtractor(lec_html)
            lectures.append(lecturer.extract_lecture_detail())
        except Exception:
            continue

    # 全情報CSV/JSON出力
    lec_csv = os.path.join(out_dir, f"syllabus_data{suffix}.csv")
    lec_json = os.path.join(out_dir, f"syllabus_data{suffix}.json")
    # to list of dict
    lec_dicts = [vars(ld) for ld in lectures]
    DataConverter.to_csv(lec_dicts, lec_csv)
    DataConverter.to_json(lec_dicts, lec_json)

    print(f"講義情報({len(lectures)} 件)を {lec_csv}, {lec_json} に出力しました")

    # 不要カラム削除版出力
    drop_cols = config.get("drop_columns", {}).get(mode, [])
    if drop_cols:
        filtered = [
            {k: v for k, v in lec.items() if k not in drop_cols}
            for lec in lec_dicts
        ]
        filt_csv = os.path.join(out_dir, f"syllabus_data_filtered{suffix}.csv")
        filt_json = os.path.join(out_dir, f"syllabus_data_filtered{suffix}.json")
        DataConverter.to_csv(filtered, filt_csv)
        DataConverter.to_json(filtered, filt_json)
        print(f"不要カラム削除版を {filt_csv}, {filt_json} に出力しました")


if __name__ == "__main__":
