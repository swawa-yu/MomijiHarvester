import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd  # pandasをインポート

# テスト対象のモジュールをインポート
from src.main import main, get_kaikoubukyoku_urls, get_subject_urls_from_kaikoubukyoku_page, load_config
from src.converter import DataConverter


# テスト用の設定ファイルを作成
@pytest.fixture
def config_file(tmp_path):
    config_content = """
small_lecture_codes:
  - "10000100" # テストケース1用に講義コードを1つのみに
full_lecture_codes: [] # fullモードのテストではリンク収集機能を使うため空
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_content, encoding="utf-8")
    return config_path


# テスト用のダミーHTMLコンテンツを返すヘルパー関数
def read_dummy_html(filename):
    # docs/syllabusHtml-small ディレクトリからHTMLファイルを読み込む
    html_path = Path(__file__).parent.parent / "docs" / "syllabusHtml-small" / filename
    if not html_path.exists():
        pytest.skip(f"Dummy HTML file not found: {html_path}")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


# requests.get をモック化するためのフィクスチャ
@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


import re  # reモジュールをインポート


# get_html_content 関数をモック化するためのフィクスチャ
@pytest.fixture
def mock_get_html_content():
    with patch("src.main.get_html_content") as mock_get:
        # URLとHTMLコンテンツのマッピングを設定
        def side_effect(url):
            print(f"Debug: mock_get_html_content called with URL: {url}")  # デバッグprint
            # 本番環境のベースURLに対するモック (ルートページ)
            if url == "https://momiji.hiroshima-u.ac.jp/syllabusHtml/":
                print("Debug: Returning index.html for base URL")  # デバッグprint
                return read_dummy_html("index.html")
            # 開講部局ページのサンプルHTML (正規表現でマッチさせる)
            # get_kaikoubukyoku_urls関数が抽出するパターンに合わせる
            kaikoubukyoku_pattern = re.compile(r"2025_[A-Z0-9]{2}\.html")
            if kaikoubukyoku_pattern.search(url):
                print(f"Debug: Returning 2025_AA.html for opening department URL: {url}")  # デバッグprint
                return read_dummy_html("2025_AA.html")  # 全ての開講部局ページに対して同じダミーHTMLを返す
            # 開講部局ページに含まれる講義URLに対するモック
            elif any(suffix in url for suffix in ["2025_AA_10000100.html", "2025_AA_10000103.html", "2025_AA_10000104.html", "71001051.html", "71001052.html", "71801001.html"]):
                print(f"Debug: Returning 2025_AA_10000100.html for subject URL: {url}")  # デバッグprint
                return read_dummy_html("2025_AA_10000100.html")  # 同じHTMLコンテンツを返す
            # 他のURLに対するモックが必要な場合はここに追加
            print(f"Debug: No mock response for URL: {url}")  # デバッグprint
            return None

        mock_get.side_effect = side_effect
        yield mock_get


# テストケース1: 一つの講義リンクから情報を正確に抽出し保存できているか
def test_extract_single_subject_data(tmp_path, mock_get_html_content, config_file):
    # load_config 関数が一時ディレクトリのconfig.yamlを読み込むようにモックを設定
    with patch("src.main.load_config") as mock_load_config:
        mock_load_config.return_value = load_config(config_file)  # 一時ファイルから設定を読み込む

        # main関数をsmallモードで実行
        with patch("sys.argv", ["src/main.py", "--mode", "small"]):
            # converter.to_csv と converter.csv_to_json の出力パスを一時ディレクトリに設定
            with patch("src.main.DataConverter") as MockConverter:
                mock_converter_instance = MockConverter.return_value

                # to_csv メソッドが呼び出されたら、一時ディレクトリ内のパスに書き込むように設定
                def mock_to_csv(data, output_path):
                    df = pd.DataFrame(data)
                    df.to_csv(tmp_path / "output" / Path(output_path).name, index=False, encoding="utf-8")

                mock_converter_instance.to_csv.side_effect = mock_to_csv

                # csv_to_json メソッドが呼び出されたら、入力CSVパスと出力JSONパスを一時ディレクトリ内のパスに設定
                def mock_csv_to_json(csv_file_path, json_file_path, drop_columns=[]):
                    df = pd.read_csv(tmp_path / "output" / Path(csv_file_path).name, dtype=str, keep_default_na=False, encoding="utf-8")
                    df = df.drop(columns=drop_columns, errors="ignore")
                    df = df.set_index("講義コード", drop=False)
                    d = df.T.to_dict()
                    with open(tmp_path / "output" / Path(json_file_path).name, mode="w", encoding="utf-8") as f:
                        json.dump(d, f, indent=2, ensure_ascii=False)

                mock_converter_instance.csv_to_json.side_effect = mock_csv_to_json

                # 出力ディレクトリを作成
                (tmp_path / "output").mkdir(exist_ok=True)

                main()

        # 出力ファイルが生成されたか確認
        csv_output = tmp_path / "output" / "syllabus_data.csv"
        json_output = tmp_path / "output" / "syllabus_data.json"
        assert csv_output.exists()
        assert json_output.exists()

        # CSVファイルの内容を確認 (データ行の数を検証)
        df_csv = pd.read_csv(csv_output, encoding="utf-8")
        assert len(df_csv) == 1  # 1件のデータ行があるか

        # JSONファイルの内容を確認 (1件のデータがあるか)
        with open(json_output, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 1
            assert "10000100" in data


# テストケース2: 一つの開講部局リンクから、その中にある講義リンクを取得し、複数(負荷をかけない程度に3つなど)の講義情報を抽出・保存できているか
def test_extract_subjects_from_kaikoubukyoku_page(tmp_path, mock_get_html_content):
    # 開講部局ページのURL (ダミー)
    kaikoubukyoku_url = "https://momiji.hiroshima-u.ac.jp/syllabusHtml/2025_AA.html"

    # get_subject_urls_from_kaikoubukyoku_page 関数をテスト
    subject_urls = get_subject_urls_from_kaikoubukyoku_page(kaikoubukyoku_url)

    # 講義リンクが6つ取得できているか確認 (2025_AA.html の内容に基づく)
    assert len(subject_urls) == 6
    expected_subject_suffixes = ["10000100.html", "10000103.html", "10000104.html", "71001051.html", "71001052.html", "71801001.html"]
    for suffix in expected_subject_suffixes:
        assert any(url.endswith(suffix) for url in subject_urls)


# テストケース3: ルートページから開講部局リンクを取得し、いくつかの開講部局ページから講義リンクを取得・処理できているか
def test_extract_subjects_from_root_page(tmp_path, mock_get_html_content, config_file):
    # load_config 関数が一時ディレクトリのconfig.yamlを読み込むようにモックを設定
    with patch("src.main.load_config") as mock_load_config:
        mock_load_config.return_value = load_config(config_file)  # 一時ファイルから設定を読み込む

        # main関数をfullモードで実行
        with patch("sys.argv", ["src/main.py", "--mode", "full"]):
            # converter.to_csv と converter.csv_to_json の出力パスを一時ディレクトリに設定
            with patch("src.main.DataConverter") as MockConverter:
                mock_converter_instance = MockConverter.return_value

                # to_csv メソッドが呼び出されたら、一時ディレクトリ内のパスに書き込むように設定
                def mock_to_csv(data, output_path):
                    df = pd.DataFrame(data)
                    df.to_csv(tmp_path / "output" / Path(output_path).name, index=False, encoding="utf-8")

                mock_converter_instance.to_csv.side_effect = mock_to_csv

                # csv_to_json メソッドが呼び出されたら、入力CSVパスと出力JSONパスを一時ディレクトリ内のパスに設定
                def mock_csv_to_json(csv_file_path, json_file_path, drop_columns=[]):
                    df = pd.read_csv(tmp_path / "output" / Path(csv_file_path).name, dtype=str, keep_default_na=False, encoding="utf-8")
                    df = df.drop(columns=drop_columns, errors="ignore")
                    df = df.set_index("講義コード", drop=False)
                    d = df.T.to_dict()
                    with open(tmp_path / "output" / Path(json_file_path).name, mode="w", encoding="utf-8") as f:
                        json.dump(d, f, indent=2, ensure_ascii=False)

                mock_converter_instance.csv_to_json.side_effect = mock_csv_to_json

                # 出力ディレクトリを作成
                (tmp_path / "output").mkdir(exist_ok=True)

                main()

        # 出力ファイルが生成されたか確認
        csv_output = tmp_path / "output" / "syllabus_data.csv"
        json_output = tmp_path / "output" / "syllabus_data.json"
        assert csv_output.exists()
        assert json_output.exists()

        # CSVファイルの内容を確認 (データ行の数を検証)
        # 抽出される開講部局数は43個、各開講部局ページから抽出される講義リンクは6個と想定
        df_csv = pd.read_csv(csv_output, encoding="utf-8")
        assert len(df_csv) == 43 * 6

        # JSONファイルの内容を確認 (期待される講義数 のデータがあるか)
        with open(json_output, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 43 * 6
            # 期待される講義コードが含まれているか確認 (一部の例)
            expected_lecture_codes_subset = ["10000100", "10000103", "10000104", "71001051", "71001052", "71801001"]
            for code in expected_lecture_codes_subset:
                # 全ての開講部局ページで同じ講義コードが抽出されるため、いずれかのエントリが存在すればOK
                assert any(key.startswith(code) for key in data.keys())
