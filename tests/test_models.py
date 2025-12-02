import pytest

from models import Subject


def test_credits_parsing_variants():
    assert Subject(credits="2.0").credits == 2.0
    assert Subject(credits="2").credits == 2.0
    assert Subject(credits=2).credits == 2.0
    assert Subject(credits="(2)").credits == 2.0


def test_list_field_parsing():
    s = Subject(keywords="大学での学び, 持続可能性")
    assert isinstance(s.keywords, list)
    assert "大学での学び" in s.keywords

    s2 = Subject(media_equipment=["テキスト", "moodle"])
    assert isinstance(s2.media_equipment, list)
    assert "moodle" in s2.media_equipment
