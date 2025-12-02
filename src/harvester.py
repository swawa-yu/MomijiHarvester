from pathlib import Path

import pandas as pd

import config
from extractors import extract_subject_data
from models import Subject


class Harvester:
    def __init__(self, settings):
        self.settings = settings

    def harvest_from_local(self, html_dir: Path) -> list[Subject]:
        subjects: list[Subject] = []
        if not html_dir or not html_dir.is_dir():
            config.logger.error(f"Invalid html_dir passed to harvest_from_local: {html_dir}")
            return subjects
        for p in sorted(html_dir.glob("*.html")):
            try:
                html = p.read_text(encoding="utf-8")
                subject = extract_subject_data(html, p.name)
                if subject:
                    subjects.append(subject)
            except Exception as e:
                config.logger.exception(f"Error reading/parsing {p}: {e}")
        return subjects

    def harvest_from_web(self, target_codes: list[str] | None = None) -> list[Subject]:
        # Placeholder: Implement web scraping for the live site. For now return empty.
        config.logger.info("harvest_from_web is not implemented; returning empty results.")
        return []

    def save_results(self, subjects: list[Subject], output_file: Path) -> None:
        # Write JSON and CSV files
        # model_dump returns serialized dictionaries for Pydantic v2 models
        # Ensure final JSON preserves historical data formats: cast credits to integer
        # when they represent whole numbers, to maintain compatibility with existing
        # downstream consumers that expect integers.
        serialized = []
        for s in subjects:
            d = s.model_dump()
            if "credits" in d and d.get("credits") is not None:
                try:
                    v = d["credits"]
                    # For backward compatibility with historical JSON, keep credits
                    # as string formatted with one decimal place ("2.0", "3.5", etc.).
                    try:
                        fv = float(v)
                        # If fractional (not integer), keep float; otherwise cast to int
                        if abs(fv - round(fv)) > 1e-8:
                            # Fractional credits; store as float (consistent typed JSON)
                            d["credits"] = float(fv)
                        else:
                            # Whole number: store as int to match strict-typed JSON
                            d["credits"] = int(round(fv))
                    except Exception:
                        # If it's not a number, leave original value as-is
                        d["credits"] = v
                except Exception:
                    # If anything unexpected happens, leave it as-is
                    pass
            serialized.append(d)
        df = pd.DataFrame(serialized)
        # Find fractional credits and optionally fail
        fractional_issues: list[dict] = []
        for rec in serialized:
            credits_value = rec.get("credits")
            if isinstance(credits_value, float) and not float(credits_value).is_integer():
                fractional_issues.append({"lecture_code": rec.get("講義コード") or rec.get("lecture_code"), "credits": credits_value})
        if fractional_issues:
            # Write issues file for downstream inspection
            issues_path = output_file.parent / "credits_issues.json"
            pd.Series(fractional_issues).to_json(issues_path, force_ascii=False, orient="records", indent=2)
            if getattr(self.settings, "fail_on_fractional_credits", False):
                config.logger.error("Fractional credits found and 'fail_on_fractional_credits' is set. Aborting save.")
                raise ValueError("Fractional credits detected in data; aborting due to settings.")
            else:
                config.logger.warning(f"Fractional credits detected. Details written to {issues_path}")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_json(output_file, orient="records", force_ascii=False, indent=2)
        csv_path = output_file.with_suffix('.csv')
        # Use to_csv for CSV; convert list fields into joined strings
        df2 = df.copy()
        for c in df2.columns:
            if df2[c].apply(lambda x: isinstance(x, list)).any():
                df2[c] = df2[c].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        df2.to_csv(csv_path, index=False)
