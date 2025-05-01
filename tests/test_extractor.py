"""SyllabusExtractorのテスト"""

import pytest
from src.extractor import SyllabusExtractor


def test_extractor_init() -> None:
    """SyllabusExtractorの初期化が正しく行われることをテスト"""
    html = "<html><body><p>test</p></body></html>"
    extractor = SyllabusExtractor(html)
    assert extractor.html_content == html


def test_extract_departments_empty() -> None:
    """extract_departmentsが空リストを返す（雛形）"""
    extractor = SyllabusExtractor("<html></html>")
    assert extractor.extract_departments() == []


def test_extract_lectures_empty() -> None:
    """extract_lecturesが空リストを返す（雛形）"""
    extractor = SyllabusExtractor("<html></html>")
    assert extractor.extract_lectures() == []


def test_extract_lecture_detail_empty() -> None:
    """extract_lecture_detailが空dictを返す（雛形）"""
    extractor = SyllabusExtractor("<html></html>")
    assert extractor.extract_lecture_detail() == {}
