import json
import sys
from pathlib import Path


def has_null(obj):
    """Return True if any value is None in obj (recursively), False otherwise.

    Empty strings are permitted; this function only detects null/None values.
    """
    if obj is None:
        return True
    if isinstance(obj, dict):
        for v in obj.values():
            if has_null(v):
                return True
    if isinstance(obj, list):
        for v in obj:
            if has_null(v):
                return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_json_no_nulls.py <json-file>")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}")
        return 2
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return 2

    problems = []
    if isinstance(data, list):
        for i, rec in enumerate(data):
            if has_null(rec):
                problems.append((i, rec))

    if problems:
        print(f"Found {len(problems)} records containing nulls or empty strings")
        for idx, rec in problems[:10]:
            print(f"Record {idx}: {rec}")
        return 1

    print("No nulls or empty strings found in JSON.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
