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
                        # Format with one decimal to match historical representation
                        d["credits"] = f"{fv:.1f}"
                    except Exception:
                        # If it's not a number, leave original value as-is
                        d["credits"] = v
                except Exception:
                    # If anything unexpected happens, leave it as-is
                    pass
            serialized.append(d)
        df = pd.DataFrame(serialized)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_json(output_file, orient="records", force_ascii=False, indent=2)
        csv_path = output_file.with_suffix('.csv')
        # Use to_csv for CSV; convert list fields into joined strings
        df2 = df.copy()
        for c in df2.columns:
            if df2[c].apply(lambda x: isinstance(x, list)).any():
                df2[c] = df2[c].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        df2.to_csv(csv_path, index=False)
