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
    assert isinstance(data[0]["credits"], str)
    assert data[0]["credits"] == "2.0"
