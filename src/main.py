import requests
import yaml
import argparse
from pathlib import Path

from bs4 import BeautifulSoup

from .converter import DataConverter
from .extractor import SyllabusExtractor


def load_config(config_path: Path):
    """
    設定ファイルを読み込む。
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def main():
    """
    本番環境のシラバスHTMLを取得し、情報を抽出してCSVおよびJSON形式で出力するメイン処理。
    設定ファイルとコマンドライン引数で動作モードを切り替え可能。
    """
    parser = argparse.ArgumentParser(description="MomijiHarvester: Extract syllabus data from Momiji.")
    parser.add_argument(
        "--mode",
        type=str,
        default="small",
        choices=["small", "full"],
        help="Operation mode: 'small' for a small set of data, 'full' for all data.",
    )
    args = parser.parse_args()

    # 設定ファイルの読み込み
    config_path = Path("config.yaml")
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        return

    config = load_config(config_path)

    # 動作モードに応じた講義コードリストの取得
    if args.mode == "small":
        lecture_codes = config.get("small_lecture_codes", [])
        print("Running in small mode.")
    elif args.mode == "full":
        # TODO: 全ての講義コードを取得する方法を実装し、configから読み込むように変更
        lecture_codes = config.get("full_lecture_codes", [])
        print("Running in full mode.")
        if not lecture_codes:
            print("Warning: 'full_lecture_codes' not found or empty in config.yaml. No data will be processed in full mode yet.")

    # 本番環境のベースURL
    base_url = "https://momiji.hiroshima-u.ac.jp/syllabusHtml/"
    # 出力ディレクトリの設定
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)  # 出力ディレクトリが存在しない場合は作成

    csv_output_path = output_dir / "syllabus_data.csv"
    json_output_path = output_dir / "syllabus_data.json"

    extractor = SyllabusExtractor()
    converter = DataConverter()

    all_syllabus_data = []
    headers = []

    if not lecture_codes:
        print("No lecture codes to process. Exiting.")
        return

    for lecture_code in lecture_codes:
        # HTMLファイルのURLを生成 (例: 2025_AA_10000100.html)
        # 年度は仮に2025とする。学科コード(AA)も仮とする。
        # TODO: 年度や学科コードを動的に取得または設定できるようにする
        html_filename = f"2025_AA_{lecture_code}.html"
        syllabus_url = f"{base_url}{html_filename}"

        print(f"Processing {syllabus_url}...")

        try:
            response = requests.get(syllabus_url)
            response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
            response.encoding = "utf-8"  # エンコーディングをUTF-8に設定
            html_content = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {syllabus_url}: {e}")
            continue  # 次の講義コードへスキップ

        soup = BeautifulSoup(html_content, "html.parser")

        # ヘッダーの抽出 (最初のファイルからのみ取得を試みる)
        if not headers:
            headers = extractor.get_subject_detail_head(soup)
            # 講義コードをヘッダーに追加 (HTMLからは直接取得できないため)
            if "講義コード" not in headers:
                headers.insert(0, "講義コード")

        # データの抽出
        datas = extractor.extract_subject_detail_data(soup)

        # ヘッダーとデータを組み合わせて辞書形式にする
        # データの数がヘッダーの数より1少ない場合 (講義コード分)、講義コードを先頭に追加
        if len(datas) == len(headers) - 1:
            datas.insert(0, lecture_code)
        elif len(datas) != len(headers):
            print(f"Warning: Header/Data mismatch in {syllabus_url}. Headers: {len(headers)}, Data: {len(datas)}")
            # TODO: ヘッダーとデータの数が一致しない場合のより良いハンドリング

        if len(headers) == len(datas):
            syllabus_dict = dict(zip(headers, datas))
            all_syllabus_data.append(syllabus_dict)
        else:
            print(f"Skipping {syllabus_url} due to header/data mismatch.")

    # CSV出力
    if all_syllabus_data:
        converter.to_csv(all_syllabus_data, csv_output_path)
    else:
        print("No syllabus data extracted to write to CSV.")

    # JSON出力 (CSVファイルが存在する場合)
    if csv_output_path.exists():
        # JSON変換時に削除する列を指定 (例: 不要な列があればここにリストで指定)
        columns_to_drop_for_json = []
        converter.csv_to_json(csv_output_path, json_output_path, drop_columns=columns_to_drop_for_json)
    else:
        print("CSV file not created, skipping JSON conversion.")


if __name__ == "__main__":
    main()
