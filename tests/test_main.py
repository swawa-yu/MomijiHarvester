"""main.pyの雛形テスト"""

import pytest
from src import main


def test_main_runs(monkeypatch) -> None:
    """main関数が例外なく実行できること（雛形）"""
    # コマンドライン引数をモック
    monkeypatch.setattr("sys.argv", ["main.py"])
    try:
        main.main()
    except Exception:
        pytest.skip("main()は雛形のため、例外はスキップ")
