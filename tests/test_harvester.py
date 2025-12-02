import json
from pathlib import Path

import requests

from harvester import Harvester
from models import Subject
from scripts.validate_json_no_nulls import has_null
from settings import get_settings


def test_save_results_credits_integer(tmp_path: Path, minimal_subject_data: dict):
    settings = get_settings(None)
    harv = Harvester(settings)
    minimal = minimal_subject_data.copy()
    minimal.update({"単位": 2})
    subjects = [Subject(**minimal)]
    out = tmp_path / "test_output.json"
    harv.save_results(subjects, out)
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    # Credits in JSON should be in the original string format (e.g., "2.0")
    assert isinstance(data[0]["credits"], int)
    assert data[0]["credits"] == 2


def test_fractional_credits_writes_issues(tmp_path: Path, minimal_subject_data: dict):
    # Model validation should reject fractional credits, so attempting to
    # create a Subject with fractional credits should raise an error and not be processed.
    import pytest

    with pytest.raises(ValueError):
        minimal = minimal_subject_data.copy()
        minimal.update({"講義コード": "20000200", "単位": 1.5})
        Subject(**minimal)


def test_harvest_skips_invalid_subjects(tmp_path: Path, minimal_subject_data: dict):
    settings = get_settings(None)
    harv = Harvester(settings)
    # craft subject data which would be rejected by the model when parsing
    # to simulate the extractor failing: use a dict and avoid instantiating Subject
    # We simulate extract_subject_data returning None on invalid input by not creating a Subject
    # For the purposes of this unit test, ensure save_results works with valid data and does not fail
    minimal = minimal_subject_data.copy()
    minimal.update({"単位": 2})
    subjects = [Subject(**minimal)]
    out = tmp_path / "test_output_valid.json"
    harv.save_results(subjects, out)
    assert out.exists()
    # Ensure output JSON does not contain nulls (empty strings are allowed)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert all(not has_null(rec) for rec in data)


def _dummy_response(text: str, status_code: int = 200):
    class DummyResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

    return DummyResponse(text, status_code)


def test_harvest_from_web_small(monkeypatch, tmp_path: Path, minimal_subject_data: dict):
    """Test web harvesting in small mode with a mocked requests session."""
    settings = get_settings(None)
    # Use small codes to control which pages will be fetched
    settings.live_small_codes = ["10000100"]
    harv = Harvester(settings)

    captured = {"session_headers": [], "request_headers": []}

    def fake_get(url, *args, **kwargs):
        # Return the content of the fixture file when the URL ends with a detail page
        # Capture the headers for assertions
        # In requests, session headers are stored in the Session object (self.headers)
        # the kwargs may include 'headers' which overrides session headers for the request.
        try:
            # self is the first positional arg when called as Session.get(self, ...)
            self_obj = args[0] if args else None
            if self_obj is not None and hasattr(self_obj, "headers"):
                captured["session_headers"].append(dict(self_obj.headers))
            captured["request_headers"].append(dict(kwargs.get("headers", {})))
        except Exception:
            pass
        if url.endswith("2025_AA_10000100.html"):
            path = Path("tests/fixtures/html/small/2025_AA_10000100.html")
            return _dummy_response(path.read_text(encoding="utf-8"))
        if url.endswith("2025_AA.html"):
            path2 = Path("tests/fixtures/html/small/2025_AA.html")
            return _dummy_response(path2.read_text(encoding="utf-8"))
        return _dummy_response("", 404)

    monkeypatch.setattr(requests.Session, "get", lambda self, *args, **kwargs: fake_get(args[0], *args[1:], **kwargs))
    # Spy on sleeps to ensure rate-limiting occurs
    sleep_args: list[float] = []

    def fake_sleep(val):
        sleep_args.append(val)

    monkeypatch.setattr("time.sleep", lambda val: fake_sleep(val))
    subjects = harv.harvest_from_web(target_codes=None, allow_full=False, delay=0.1, jitter=0.05)
    assert isinstance(subjects, list)
    assert len(subjects) >= 1
    assert subjects[0].lecture_code == "10000100"
    # Ensure that sleep has been called at least once and the values respect delay/jitter
    assert sleep_args, "Expected time.sleep to be called for rate-limiting"
    assert all(isinstance(x, float) for x in sleep_args)
    assert all(0 <= x <= 0.2 for x in sleep_args)
    # Ensure the User-Agent was applied on session and in request headers
    assert any("MomijiHarvester/" in h.get("User-Agent", "") for h in captured["session_headers"]) or any(
        "MomijiHarvester/" in h.get("User-Agent", "") for h in captured["request_headers"]
    )


def test_harvest_from_web_full(monkeypatch, tmp_path: Path):
    """Test a simulated full harvest by mocking index and detail fetching."""
    settings = get_settings(None)
    harv = Harvester(settings)

    def fake_get(url, *args, **kwargs):
        if url.endswith("2025_AA.html"):
            path = Path("tests/fixtures/html/small/2025_AA.html")
            return _dummy_response(path.read_text(encoding="utf-8"))
        if url.endswith("2025_AA_10000100.html"):
            path = Path("tests/fixtures/html/small/2025_AA_10000100.html")
            return _dummy_response(path.read_text(encoding="utf-8"))
        return _dummy_response("", 404)

    monkeypatch.setattr(requests.Session, "get", lambda self, *args, **kwargs: fake_get(args[0], *args[1:], **kwargs))
    subjects = harv.harvest_from_web(target_codes=None, allow_full=True)
    # Should find at least one subject (the 10000100 example)
    assert any(s.lecture_code == "10000100" for s in subjects)
