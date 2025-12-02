from models import Subject

EXPECTED_CREDITS = 2


def test_credits_parsing_variants():
    assert Subject(credits="2.0").credits == EXPECTED_CREDITS
    assert Subject(credits="2").credits == EXPECTED_CREDITS
    assert Subject(credits=2).credits == EXPECTED_CREDITS
    assert Subject(credits="(2)").credits == EXPECTED_CREDITS


def test_subject_rejects_fractional_credits():
    import pytest
    with pytest.raises(ValueError):
        Subject(credits=1.5)


def test_list_field_parsing():
    s = Subject(keywords="大学での学び, 持続可能性")
    assert isinstance(s.keywords, list)
    assert "大学での学び" in s.keywords

    s2 = Subject(media_equipment=["テキスト", "moodle"])
    assert isinstance(s2.media_equipment, list)
    assert "moodle" in s2.media_equipment
