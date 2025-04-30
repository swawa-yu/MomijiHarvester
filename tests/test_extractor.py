from pathlib import Path

from bs4 import BeautifulSoup

from src.extractor import SyllabusExtractor


def load_html(filename):
    """Helper function to load HTML content from docs/syllabusHtml-small."""
    html_path = Path(f"docs/syllabusHtml-small/{filename}")
    with open(html_path, encoding="utf-8") as f:
        return f.read()


def test_extract_subject_detail_data():
    """Test extraction of subject detail data."""
    html_content = load_html("2025_AA_10000100.html")
    soup = BeautifulSoup(html_content, "html.parser")
    extractor = SyllabusExtractor()
    data = extractor.extract_subject_detail_data(soup)

    # TODO: Assertions based on the expected data from the HTML file
    # Example assertion (replace with actual expected data):
    # assert len(data) > 0
    # assert data[0] == "Expected Value"
    print("\nExtracted Data:", data)  # For inspection during development
    assert isinstance(data, list)
    assert len(data) > 0  # Basic check that some data was extracted


def test_get_subject_detail_head():
    """Test extraction of subject detail headers."""
    html_content = load_html("2025_AA_10000100.html")
    soup = BeautifulSoup(html_content, "html.parser")
    extractor = SyllabusExtractor()
    headers = extractor.get_subject_detail_head(soup)

    # TODO: Assertions based on the expected headers from the HTML file
    # Example assertion (replace with actual expected headers):
    # assert len(headers) > 0
    # assert headers[0] == "Expected Header"
    print("\nExtracted Headers:", headers)  # For inspection during development
    assert isinstance(headers, list)
    assert len(headers) > 0  # Basic check that some headers were extracted
