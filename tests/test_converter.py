import json

import pandas as pd
import pytest

from src.converter import DataConverter


# テスト用の一時ディレクトリを作成
@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


def test_to_csv(temp_output_dir):
    """Test CSV output."""
    converter = DataConverter()
    sample_data = [
        {"Header1": "Data1_1", "Header2": "Data1_2"},
        {"Header1": "Data2_1", "Header2": "Data2_2"},
    ]
    csv_output_path = temp_output_dir / "test_output.csv"
    converter.to_csv(sample_data, csv_output_path)

    assert csv_output_path.exists()

    # Read the CSV and check content
    df = pd.read_csv(csv_output_path)
    assert list(df.columns) == ["Header1", "Header2"]
    assert df.iloc[0].tolist() == ["Data1_1", "Data1_2"]
    assert df.iloc[1].tolist() == ["Data2_1", "Data2_2"]


def test_csv_to_json(temp_output_dir):
    """Test CSV to JSON conversion."""
    converter = DataConverter()
    # Create a dummy CSV file for testing
    csv_content = """講義コード,Header1,Header2
10000100,Data1_1,Data1_2
10000101,Data2_1,Data2_2
"""
    csv_input_path = temp_output_dir / "test_input.csv"
    with open(csv_input_path, "w", encoding="utf-8") as f:
        f.write(csv_content)

    json_output_path = temp_output_dir / "test_output.json"
    converter.csv_to_json(csv_input_path, json_output_path)

    assert json_output_path.exists()

    # Read the JSON and check content
    with open(json_output_path, encoding="utf-8") as f:
        json_data = json.load(f)

    expected_json_data = {
        "10000100": {"講義コード": "10000100", "Header1": "Data1_1", "Header2": "Data1_2"},
        "10000101": {"講義コード": "10000101", "Header1": "Data2_1", "Header2": "Data2_2"},
    }
    assert json_data == expected_json_data


def test_csv_to_json_with_drop_columns(temp_output_dir):
    """Test CSV to JSON conversion with dropping columns."""
    converter = DataConverter()
    # Create a dummy CSV file for testing
    csv_content = """講義コード,Header1,Header2,Header3
10000100,Data1_1,Data1_2,Data1_3
10000101,Data2_1,Data2_2,Data2_3
"""
    csv_input_path = temp_output_dir / "test_input_drop.csv"
    with open(csv_input_path, "w", encoding="utf-8") as f:
        f.write(csv_content)

    json_output_path = temp_output_dir / "test_output_drop.json"
    columns_to_drop = ["Header3"]
    converter.csv_to_json(csv_input_path, json_output_path, drop_columns=columns_to_drop)

    assert json_output_path.exists()

    # Read the JSON and check content
    with open(json_output_path, encoding="utf-8") as f:
        json_data = json.load(f)

    expected_json_data = {
        "10000100": {"講義コード": "10000100", "Header1": "Data1_1", "Header2": "Data1_2"},
        "10000101": {"講義コード": "10000101", "Header1": "Data2_1", "Header2": "Data2_2"},
    }
    assert json_data == expected_json_data
