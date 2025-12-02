import pytest

from models import Subject

EXPECTED_CREDITS = 2


def test_credits_parsing_variants(minimal_subject_data: dict):
    minimal = minimal_subject_data.copy()
    minimal.update({"単位": "2.0"})
    assert Subject(**minimal).credits == EXPECTED_CREDITS
    minimal.update({"単位": "2"})
    assert Subject(**minimal).credits == EXPECTED_CREDITS
    minimal.update({"単位": 2})
    assert Subject(**minimal).credits == EXPECTED_CREDITS
    minimal.update({"単位": "(2)"})
    assert Subject(**minimal).credits == EXPECTED_CREDITS


def test_subject_rejects_fractional_credits(minimal_subject_data: dict):
    minimal = minimal_subject_data.copy()
    minimal.update({"単位": 1.5})
    with pytest.raises(ValueError):
        Subject(**minimal)


def test_missing_credits_raises(minimal_subject_data: dict):
    minimal = minimal_subject_data.copy()
    # Remove 単位 field to simulate missing credits
    minimal.pop("単位", None)
    with pytest.raises(Exception):
        Subject(**minimal)


def test_list_field_parsing(minimal_subject_data: dict):
    minimal = minimal_subject_data.copy()
    minimal.update({"授業のキーワード": "大学での学び, 持続可能性"})
    s = Subject(**minimal)
    assert isinstance(s.keywords, str)
    assert "大学での学び" in s.keywords

    minimal2 = minimal_subject_data.copy()
    minimal2.update({"授業で使用するメディア・機器等": ["テキスト", "moodle"]})
    s2 = Subject(**minimal2)
    assert isinstance(s2.media_equipment, str)
    assert "moodle" in s2.media_equipment
