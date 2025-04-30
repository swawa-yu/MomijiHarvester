from pathlib import Path

from bs4 import BeautifulSoup

from .converter import DataConverter
from .extractor import SyllabusExtractor


def main():
    """
    シラバスHTMLファイルを読み込み、情報を抽出してCSVおよびJSON形式で出力するメイン処理。
    """
    # 入力ディレクトリと出力ディレクトリの設定
    input_dir = Path("docs/syllabusHtml-small")  # テスト用の小さいHTMLファイルを使用
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)  # 出力ディレクトリが存在しない場合は作成

    csv_output_path = output_dir / "syllabus_data.csv"
    json_output_path = output_dir / "syllabus_data.json"

    extractor = SyllabusExtractor()
    converter = DataConverter()

    all_syllabus_data = []
    headers = []

    # 入力ディレクトリ内のHTMLファイルを処理
    for html_file in input_dir.glob("*.html"):
        if html_file.name == "index.html":  # index.htmlはスキップ
            continue

        print(f"Processing {html_file}...")
        with open(html_file, encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # ヘッダーの抽出 (最初のファイルからのみ取得を試みる)
        if not headers:
            headers = extractor.get_subject_detail_head(soup)
            # 講義コードをヘッダーに追加 (HTMLからは直接取得できないため)
            if "講義コード" not in headers:
                headers.insert(0, "講義コード")

        # データの抽出
        datas = extractor.extract_subject_detail_data(soup)

        # 講義コードの取得 (ファイル名から抽出)
        # 例: 2025_AA_10000100.html -> 10000100
        lecture_code = html_file.stem.split("_")[-1]

        # ヘッダーとデータを組み合わせて辞書形式にする
        # データの数がヘッダーの数より1少ない場合 (講義コード分)、講義コードを先頭に追加
        if len(datas) == len(headers) - 1:
            datas.insert(0, lecture_code)
        elif len(datas) != len(headers):
            print(f"Warning: Header/Data mismatch in {html_file}. Headers: {len(headers)}, Data: {len(datas)}")
            # TODO: ヘッダーとデータの数が一致しない場合のより良いハンドリング

        if len(headers) == len(datas):
            syllabus_dict = dict(zip(headers, datas))
            all_syllabus_data.append(syllabus_dict)
        else:
            print(f"Skipping {html_file} due to header/data mismatch.")

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
