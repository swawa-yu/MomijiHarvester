# tests/conftest.py
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

# --- 定数 ---
# ディレクトリ構成変更後のパスを参照
FIXTURES_DIR = Path(__file__).parent / "fixtures"
HTML_DIR_FULL = FIXTURES_DIR / "html" / "full"
HTML_DIR_SMALL = FIXTURES_DIR / "html" / "small"

# --- フィクスチャ ---


@pytest.fixture(scope="module")
def sample_html_small_dir() -> Path:
    """Small sample HTML directory path."""
    return HTML_DIR_SMALL


@pytest.fixture(scope="module")
def sample_html_full_dir() -> Path:
    """Full sample HTML directory path."""
    return HTML_DIR_FULL


@pytest.fixture(scope="module")
def sample_html_content_aa10000100() -> str:
    """Content of a specific sample HTML file (small)."""
    file_path = HTML_DIR_SMALL / "2025_AA_10000100.html"
    if not file_path.is_file():
        pytest.skip(f"Sample HTML file not found: {file_path}")
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        pytest.fail(f"Failed to read sample HTML file {file_path}: {e}")
    return ""


@pytest.fixture(scope="module")
def sample_html_content_index() -> str:
    """Content of index.html sample (small)."""
    file_path = HTML_DIR_SMALL / "index.html"
    if not file_path.is_file():
        pytest.skip(f"Sample HTML file not found: {file_path}")
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        pytest.fail(f"Failed to read sample HTML file {file_path}: {e}")
    return ""


@pytest.fixture(scope="module")
def sample_soup_aa10000100(sample_html_content_aa10000100: str) -> BeautifulSoup:
    """BeautifulSoup object for a specific sample HTML file (small)."""
    return BeautifulSoup(sample_html_content_aa10000100, "html5lib")


# --- ヘッダー検証用のフィクスチャ ---
@pytest.fixture
def valid_headers() -> list[str]:
    """Canonical header list for testing."""
    # config.py からインポートするのが望ましいが、テスト独立性のためここで定義も可
    # from src.momijiharvester.config import CANONICAL_HEADERS
    # return CANONICAL_HEADERS
    # とりあえずサンプルHTMLから取得したものをベースに(要調整)
    return [
        "年度",
        "開講部局",
        "講義コード",
        "科目区分",
        "授業科目名",
        "授業科目名（フリガナ）",
        "英文授業科目名",
        "担当教員名",
        "担当教員名(フリガナ)",
        "開講キャンパス",
        "開設期",
        "曜日・時限・講義室",
        "授業の方法",
        "授業の方法【詳細情報】",
        "単位",
        "週時間",
        "使用言語",
        "学習の段階",
        "学問分野（分野）",
        "学問分野（分科）",
        "対象学生",
        "授業のキーワード",
        "教職専門科目",
        "教科専門科目",
        "教養教育でのこの授業の位置づけ",
        "学習の成果",
        "授業の目標・概要等",
        "授業計画",
        "教科書・参考書等",
        "授業で使用するメディア・機器等",
        "【詳細情報】",
        "授業で取り入れる学習手法",
        "予習・復習へのアドバイス",
        "履修上の注意受講条件等",
        "成績評価の基準等",
        "実務経験",
        "実務経験の概要とそれに基づく授業内容",
        "メッセージ",
        "その他",
    ]


@pytest.fixture
def headers_with_unexpected(valid_headers: list[str]) -> list[str]:
    """Headers containing an unexpected item."""
    headers = valid_headers.copy()
    headers.insert(5, "予期しないヘッダー")
    return headers


@pytest.fixture
def headers_with_missing(valid_headers: list[str]) -> list[str]:
    """Headers missing an expected item."""
    headers = valid_headers.copy()
    headers.pop(10)  # 例として '開設期' を削除
    return headers


@pytest.fixture
def headers_with_order_mismatch(valid_headers: list[str]) -> list[str]:
    """Headers with a different order."""
    headers = valid_headers.copy()
    headers[0], headers[1] = headers[1], headers[0]  # 年度と開講部局を入れ替え
    return headers


@pytest.fixture
def minimal_subject_data() -> dict:
    """Return a minimal valid subject data dict containing all required fields.
    This helps tests instantiate Subjects without repeating all fields in each test.
    """
    return {
        "年度": "2025年度",
        "開講部局": "文学部",
        "講義コード": "10000100",
        "科目区分": "選択",
        "授業科目名": "テスト科目",
        "授業科目名（フリガナ）": "",
        "英文授業科目名": "Test Subject",
        "担当教員名": "林 光緒",
        "担当教員名(フリガナ)": "",
        "開講キャンパス": "東広島",
        "開設期": "前期",
        "曜日・時限・講義室": "",
        "授業の方法": "講義",
        "授業の方法【詳細情報】": "",
        "単位": 2,
        "週時間": 2,
        "使用言語": "日本語",
        "学習の段階": "",
        "学問分野（分野）": "",
        "学問分野（分科）": "",
        "対象学生": "",
        "授業のキーワード": "",
        "教職専門科目": "",
        "教科専門科目": "",
        "教養教育でのこの授業の位置づけ": "",
        "学習の成果": "",
        "授業の目標・概要等": "",
        "授業計画": "",
        "教科書・参考書等": "",
        "授業で使用するメディア・機器等": "",
        "【詳細情報】": "",
        "授業で取り入れる学習手法": "",
        "予習・復習へのアドバイス": "",
        "履修上の注意受講条件等": "",
        "成績評価の基準等": "",
        "実務経験": "",
        "実務経験の概要とそれに基づく授業内容": "",
        "メッセージ": "",
        "その他": "",
    }
