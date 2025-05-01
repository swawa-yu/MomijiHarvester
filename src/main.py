import requests
import yaml
import argparse
import time
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

from .converter import DataConverter
from .extractor import SyllabusExtractor


def load_config(config_path: Path):
    """
    設定ファイルを読み込む。
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def get_html_content(url: str) -> str | None:
    """
    指定されたURLからHTMLコンテンツを取得する。
    """
    print(f"Fetching {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
        response.encoding = "utf-8"  # エンコーディングをUTF-8に設定
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_kaikoubukyoku_urls(base_url: str) -> list[str]:
    """
    ルートページから開講部局のURLリストを取得する。
    """
    root_url = base_url  # ルートページのURLはベースURLと同じと仮定
    html_content = get_html_content(root_url)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, "html.parser")


import re  # reモジュールをインポート


def get_kaikoubukyoku_urls(base_url: str) -> list[str]:
    """
    ルートページから開講部局のURLリストを取得する。
    """
    root_url = base_url  # ルートページのURLはベースURLと同じと仮定
    html_content = get_html_content(root_url)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    kaikoubukyoku_urls = set()  # 重複を避けるためにsetを使用

    # href属性が'2025_'に続き英数字2文字があり'.html'で終わるパターンに一致するaタグを検索 (学部・研究科レベルを想定)
    # 例: 2025_AA.html, 2025_01.html, 2025_E5.html など
    pattern = re.compile(r"2025_[A-Z0-9]{2}\.html")

    extracted_hrefs = []  # デバッグ用リスト
    for a_tag in soup.find_all("a", href=pattern):
        href = a_tag.get("href")
        if isinstance(href, str):
            kaikoubukyoku_urls.add(f"{base_url}{href}")
            extracted_hrefs.append(href)  # デバッグ用に追加

    print(f"Debug: Found {len(kaikoubukyoku_urls)} potential opening department pages.")  # デバッグprint
    print(f"Debug: Kaikoubukyoku URLs: {kaikoubukyoku_urls}")  # デバッグprint
    print(f"Debug: Extracted hrefs matching pattern: {extracted_hrefs}")  # デバッグprint

    return list(kaikoubukyoku_urls)  # リストに変換して返す


def get_subject_urls_from_kaikoubukyoku_page(kaikoubukyoku_url: str) -> list[str]:
    """
    開講部局のページから講義シラバスのURLリストを取得する。
    """
    print(f"Debug: get_subject_urls_from_kaikoubukyoku_page called with URL: {kaikoubukyoku_url}")  # デバッグprint
    html_content = get_html_content(kaikoubukyoku_url)
    if html_content is None:
        print(f"Debug: Failed to get HTML content for {kaikoubukyoku_url}")  # デバッグprint
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    subject_urls = []

    # ページの最後のtableタグを講義一覧テーブルと仮定
    # TODO: より堅牢な方法で講義一覧テーブルを特定する
    # ページの最後のtableタグを講義一覧テーブルと仮定
    # TODO: より堅牢な方法で講義一覧テーブルを特定する
    subject_tables = soup.find_all("table")
    if not subject_tables:
        return []  # テーブルが見つからない場合は空リストを返す

    subject_table = subject_tables[-1]

    # ページの最後のtableタグを講義一覧テーブルと仮定
    # TODO: より堅牢な方法で講義一覧テーブルを特定する
    subject_tables = soup.find_all("table")
    if not subject_tables:
        return []  # テーブルが見つからない場合は空リストを返す

    subject_table = subject_tables[-1]

    # subject_tableがTagオブジェクトであり、Noneでないことを確認してからfind_allを呼び出し
    if isinstance(subject_table, Tag):
        # テーブルの各行から講義リンクを抽出 (ヘッダー行を除く)
        rows = subject_table.find_all("tr")
        if rows and len(rows) > 1:  # ヘッダー行以外の行が存在するか確認
            for row in rows[1:]:
                if isinstance(row, Tag):  # rowがTagオブジェクトであることを確認
                    cells = row.find_all("td")
                    if cells and len(cells) > 4:  # 少なくとも5つのセルがあり、cellsがNoneでないことを確認
                        # 講義リンクが含まれている可能性のあるセル（例: 5番目のセル）からaタグを検索
                        # TODO: 講義リンクが含まれるセルのインデックスが固定になっているため、HTML構造の変更に弱い
                        target_cell = cells[4]
                        if isinstance(target_cell, Tag):  # target_cellがTagオブジェクトであることを確認
                            subject_link_tag = target_cell.find("a")
                            if subject_link_tag and isinstance(subject_link_tag, Tag):  # subject_link_tagがTagオブジェクトであることを確認
                                href = subject_link_tag.get("href")
                                if isinstance(href, str):  # hrefが文字列であることを確認
                                    # 相対URLを絶対URLに変換
                                    # 開講部局URLのディレクトリ部分と結合
                                    base_dir = "/".join(kaikoubukyoku_url.split("/")[:-1]) + "/"
                                    subject_urls.append(f"{base_dir}{href}")

    return subject_urls


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

    syllabus_urls_to_process = []

    # 動作モードに応じた講義コードリストの取得またはリンク収集
    if args.mode == "small":
        lecture_codes_to_process = config.get("small_lecture_codes", [])
        print("Running in small mode.")
        # smallモードでは講義コードから直接URLを生成
        syllabus_urls_to_process = [f"{base_url}2025_AA_{code}.html" for code in lecture_codes_to_process]  # TODO: 年度や学科コードを動的に取得または設定できるようにする
    elif args.mode == "full":
        print("Running in full mode. Collecting all lecture links...")
        kaikoubukyoku_urls = get_kaikoubukyoku_urls(base_url)
        print(f"Found {len(kaikoubukyoku_urls)} opening department pages.")

        # 各開講部局ページから講義リンクを収集
        for i, kaikoubukyoku_url in enumerate(kaikoubukyoku_urls):
            print(f"Debug: Processing opening department page {i + 1}/{len(kaikoubukyoku_urls)}: {kaikoubukyoku_url}")  # デバッグprint
            subject_urls = get_subject_urls_from_kaikoubukyoku_page(kaikoubukyoku_url)
            print(f"Debug: Found {len(subject_urls)} subject URLs on this page.")  # デバッグprint
            syllabus_urls_to_process.extend(subject_urls)
            time.sleep(0.1)  # サーバー負荷軽減のため待機

        print(f"Collected {len(syllabus_urls_to_process)} syllabus URLs.")

    if not syllabus_urls_to_process:
        print("No syllabus URLs to process. Exiting.")
        return

    # シラバスHTMLを取得し、データを抽出
    for i, syllabus_url in enumerate(syllabus_urls_to_process):
        print(f"Debug: --- Start processing URL {i + 1}/{len(syllabus_urls_to_process)}: {syllabus_url} ---")  # ループ開始時のprint

        html_content = get_html_content(syllabus_url)
        # html_contentがNoneの場合はエラーとしてassert
        assert html_content is not None, f"Failed to fetch HTML content for {syllabus_url}"

        soup = BeautifulSoup(html_content, "html.parser")

        # ヘッダーの抽出 (最初のファイルからのみ取得を試みる)
        if not headers:
            headers = extractor.get_subject_detail_head(soup)
            # 講義コードをヘッダーに追加 (HTMLからは直接取得できないため、URLから抽出)
            if "講義コード" not in headers:
                headers.insert(0, "講義コード")

        # データの抽出
        datas = extractor.extract_subject_detail_data(soup)

        # 講義コードの取得 (URLから抽出)
        # 例: https://momiji.hiroshima-u.ac.jp/syllabusHtml/2025_AA_10000100.html -> 10000100
        lecture_code = Path(syllabus_url).stem.split("_")[-1]

        # ヘッダーとデータを組み合わせて辞書形式にする
        # データの数がヘッダーの数より1少ない場合 (講義コード分)、講義コードを先頭に追加
        if len(datas) == len(headers) - 1:
            datas.insert(0, lecture_code)
        elif len(datas) != len(headers):
            print(f"Warning: Header/Data mismatch in {syllabus_url}. Headers: {len(headers)}, Data: {len(datas)}")
            # TODO: ヘッダーとデータの数が一致しない場合のより良いハンドリング

        if len(headers) == len(datas):
            syllabus_dict = dict(zip(headers, datas))
            print(f"Debug: Appending data for lecture code {lecture_code}. Current all_syllabus_data length before append: {len(all_syllabus_data)}")  # 追加前のprint
            all_syllabus_data.append(syllabus_dict)
            print(f"Debug: all_syllabus_data length after append: {len(all_syllabus_data)}")  # 追加後のprint
        else:
            print(f"Skipping {syllabus_url} due to header/data mismatch.")

        time.sleep(0.1)  # サーバー負荷軽減のため待機
        print(f"Debug: --- Finished processing URL {i + 1}. Moving to next. ---")  # ループ終了時のprint
        print(f"Debug: End of loop iteration {i + 1}")  # デバッグprint

    print(f"Debug: Finished processing all URLs. Final all_syllabus_data length: {len(all_syllabus_data)}")
    print(f"Debug: Final all_syllabus_data content: {all_syllabus_data}")

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
