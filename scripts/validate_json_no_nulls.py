import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


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
        logger.error("Usage: validate_json_no_nulls.py <json-file>")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        logger.error("File not found: %s", p)
        return 2
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to load JSON: %s", e)
        return 2

    problems = []
    if isinstance(data, list):
        for i, rec in enumerate(data):
            if has_null(rec):
                problems.append((i, rec))

    if problems:
        logger.error("Found %d records containing nulls or empty strings", len(problems))
        for idx, rec in problems[:10]:
            logger.error("Record %d: %s", idx, rec)
        return 1

    logger.info("No nulls found in JSON.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
