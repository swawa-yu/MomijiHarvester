from pathlib import Path
import json

from harvester import Harvester
from settings import get_settings
from models import Subject


def test_save_results_credits_integer(tmp_path: Path):
    settings = get_settings(None)
    harv = Harvester(settings)
    subjects = [Subject(lecture_code="10000100", credits=2.0, subject_name="テスト科目")]
    out = tmp_path / "test_output.json"
    harv.save_results(subjects, out)
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    # Credits in JSON should be in the original string format (e.g., "2.0")
    assert isinstance(data[0]["credits"], int)
    assert data[0]["credits"] == 2


def test_fractional_credits_writes_issues(tmp_path: Path):
    settings = get_settings(None)
    harv = Harvester(settings)
    subjects = [Subject(lecture_code="20000200", credits=1.5, subject_name="テスト_科目_単位数_非整数")]
    out = tmp_path / "test_output_fractional.json"
    harv.save_results(subjects, out)
    issues = out.parent / "credits_issues.json"
    assert issues.exists()
    payload = json.loads(issues.read_text(encoding="utf-8"))
    assert payload[0]["credits"] == 1.5


def test_fail_on_fractional(tmp_path: Path):
    settings = get_settings(None)
    settings.fail_on_fractional_credits = True
    harv = Harvester(settings)
    subjects = [Subject(lecture_code="20000200", credits=1.5, subject_name="テスト_科目_単位数_非整数")]
    out = tmp_path / "test_output_fractional2.json"
    try:
        harv.save_results(subjects, out)
        assert False, "Expected ValueError when fail_on_fractional_credits is True"
    except ValueError:
        # expected
        pass
