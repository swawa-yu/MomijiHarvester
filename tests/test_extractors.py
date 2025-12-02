# tests/test_extractors.py
import logging

import pytest
from bs4 import BeautifulSoup

from extractors import HeaderMismatchError, extract_headers, extract_subject_data, validate_headers
from models import Subject

# --- Test extract_headers ---


def test_extract_headers_valid(sample_soup_aa10000100: BeautifulSoup, valid_headers: list[str]):
    """Test extracting headers from a valid sample HTML."""
    extracted = extract_headers(sample_soup_aa10000100)
    # 抽出されたヘッダー数が期待値と同じか
    assert len(extracted) == len(valid_headers)
    # 抽出されたヘッダーの内容が期待値(順序無視で)と一致するか
    assert set(extracted) == set(valid_headers)
    # 必要であれば順序もチェック
    # assert extracted == valid_headers


# --- Test validate_headers ---


def test_validate_headers_success(valid_headers: list[str]):
    """Test header validation with matching headers."""
    try:
        validate_headers(valid_headers, file_identifier="test_success")
    except HeaderMismatchError:
        pytest.fail("validate_headers raised HeaderMismatchError unexpectedly.")


def test_validate_headers_unexpected(headers_with_unexpected: list[str]):
    """Test header validation with unexpected headers, expecting an error."""
    with pytest.raises(HeaderMismatchError, match="Header mismatch detected"):
        validate_headers(headers_with_unexpected, file_identifier="test_unexpected")


def test_validate_headers_missing(headers_with_missing: list[str], caplog):
    """Test header validation with missing headers, expecting a warning log."""
    # エラーは発生しない想定
    try:
        validate_headers(headers_with_missing, file_identifier="test_missing")
    except HeaderMismatchError:
        pytest.fail("validate_headers raised HeaderMismatchError unexpectedly for missing headers.")
    # 警告ログが出力されているか確認
    assert "Expected headers missing" in caplog.text
    assert "WARNING" in caplog.text


# def test_validate_headers_order_mismatch(headers_with_order_mismatch: list[str], caplog):
#     """Test header validation with order mismatch (if order validation is enabled)."""
#     # If order mismatch should raise error or warning, adjust the test accordingly.
#     try:
#         validate_headers(headers_with_order_mismatch, file_identifier="test_order")
#     except HeaderMismatchError:
#         pytest.fail("validate_headers raised HeaderMismatchError unexpectedly for order mismatch (if only warning).")
#     # assert "Header order mismatch" in caplog.text # If it's a warning
#     # assert "WARNING" in caplog.text

# --- Test extract_subject_data ---


EXPECTED_CREDITS = 2


def test_extract_subject_data_valid(sample_html_content_aa10000100: str):
    """Test extracting full subject data from a valid sample HTML."""
    subject = extract_subject_data(sample_html_content_aa10000100, "AA10000100")
    assert subject is not None
    assert isinstance(subject, Subject)
    # --- Assert specific fields ---
    assert subject.year == "2025年度"
    assert subject.lecture_code == "10000100"
    assert subject.subject_name == "大学教育入門[1総総,1文,1経]"
    assert subject.instructor_name == "林 光緒"
    assert subject.campus == "東広島"
    assert subject.term == "1年次生 前期 １ターム"  # 空白に注意
    assert subject.lecture_type == "講義"
    assert subject.lecture_type_detail_1 == "対面, オンライン(オンデマンド型)"  # カンマ区切りで取得される想定
    assert isinstance(subject.credits, int)
    assert subject.credits == EXPECTED_CREDITS
    assert subject.language == "B : 日本語・英語"
    # media_equipment is stored as a string now — check for substrings
    assert isinstance(subject.media_equipment, str)
    assert "テキスト" in subject.media_equipment
    assert "moodle" in subject.media_equipment
    # keywords should be a comma-separated string; check for substrings
    assert isinstance(subject.keywords, str)
    assert "大学での学び" in subject.keywords
    # ... 他のフィールドも必要に応じて検証 ...
    # With the current model, `other` is a required string field; empty or &nbsp; should
    # normalize to an empty string rather than None.
    assert subject.other == ""


def test_extract_subject_data_invalid_html():
    """Test extraction with invalid or incomplete HTML content."""
    invalid_html = "<html><body><p>This is not a syllabus table.</p></body></html>"
    subject = extract_subject_data(invalid_html, "invalid_html_test")
    # ヘッダー検証で失敗するか、テーブルが見つからず None が返るはず
    assert subject is None


def test_extract_subject_data_index_page(sample_html_content_index: str, caplog):
    """Index pages without detail tables should be skipped without ERROR logs."""
    caplog.set_level(logging.INFO)
    subject = extract_subject_data(sample_html_content_index, "index_test")
    assert subject is None
    # Ensure no ERROR logs were emitted for missing detail table
    assert "Detail table not found or is not a Tag in HTML." not in caplog.text
    assert "ERROR" not in caplog.text


def test_extract_subject_data_header_mismatch(sample_html_content_aa10000100: str):
    """Test extraction when headers do not match the canonical list."""
    # ヘッダーを意図的に変更したHTMLを準備するか、
    # ここでは validate_headers が内部でエラーを出すことを確認
    # (個別の validate_headers テストでカバーされているため、ここでは簡易的に)
    # 例: CANONICAL_HEADERS を一時的に変更してテストする(モンキーパッチング)などは可能だが、
    # validate_headers の個別テストの方がクリーン。
    # ここでは、もし HeaderMismatchError が発生したら None が返ることを確認。
    # ※実際にヘッダーが異なるHTMLを用意するのが最も確実
    # temp_html = sample_html_content_aa10000100.replace(
    #     '<TH class="detail-head" align="center" width="150">年度</TH>',
    #     '<TH class="detail-head" align="center" width="150">間違った年度</TH>'
    # )
    # subject = extract_subject_data(temp_html, "header_mismatch_test")
    # assert subject is None
    # Modify the HTML to cause a header mismatch: change "年度" to an unexpected header
    temp_html = sample_html_content_aa10000100.replace(
        '<TH class="detail-head" align="center" width="150">年度</TH>',
        '<TH class="detail-head" align="center" width="150">間違った年度</TH>',
    )
    import pytest

    with pytest.raises(HeaderMismatchError):
        extract_subject_data(temp_html, "header_mismatch_test")
