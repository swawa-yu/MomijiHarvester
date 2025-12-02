import time
from pathlib import Path

import pandas as pd
import requests  # type: ignore[import]
from requests.adapters import HTTPAdapter, Retry  # type: ignore[import]

import config
from extractors import extract_subject_data
from models import Subject

BASE_URL = config.BASE_URL


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

    def harvest_from_web(
        self,
        target_codes: list[str] | None = None,
        allow_full: bool = False,
        delay: float = 0.5,
    ) -> list[Subject]:
        """Harvest syllabus pages from the live website.

        If `target_codes` is provided, harvest those lecture codes.
        If `target_codes` is None and `allow_full` is False, use
        `self.settings.live_small_codes` if present and return.
        If `allow_full` is True and `target_codes` is None, crawl the index
        page to collect all available detail pages (use with care).

        The function is rate-limited by `delay` between requests to reduce
        the impact on the upstream site. Uses a small retry policy.
        """
        subjects: list[Subject] = []
        # Prepare codes list
        codes: list[str] | None = target_codes
        if codes is None and not allow_full:
            codes = self.settings.live_small_codes
        # If still None and allow_full is True, attempt to crawl index page
        if codes is None and allow_full:
            index_url = f"{BASE_URL}2025_AA.html"
            config.logger.info("Attempting to fetch index page for full harvest: %s", index_url)
            try:
                session = requests.Session()
                retries = Retry(total=3, backoff_factor=0.5)
                session.mount("https://", HTTPAdapter(max_retries=retries))
                r = session.get(index_url, timeout=10)
                if r.status_code != 200:
                    config.logger.error("Index page fetch failed: %s %s", index_url, r.status_code)
                    return subjects
                html = r.text
                import re

                from bs4 import BeautifulSoup

                soup = BeautifulSoup(html, "html5lib")
                links = [a.get("href") for a in soup.select("a[href]") if a.get("href")]
                codes = []
                for href in links:
                    m = re.search(r"2025_AA_([0-9]+)\.html$", href)
                    if m:
                        codes.append(m.group(1))
                codes = sorted(set(codes))
            except Exception as e:
                config.logger.exception("Failed to fetch/parse index page: %s", e)
                return subjects

        if not codes:
            config.logger.info("No target codes supplied or found; skipping web harvest.")
            return subjects

        # Setup HTTP session and retry policy
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        headers = {"User-Agent": "MomijiHarvester/0.1 (+https://github.com/swawa-yu/MomijiHarvester)"}

        for code in codes:
            # Construct URL
            url = f"{BASE_URL}2025_AA_{code}.html"
            try:
                config.logger.info("Fetching %s", url)
                r = session.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    config.logger.warning("Failed to fetch %s: %s", url, r.status_code)
                    continue
                html = r.text
                subject = extract_subject_data(html, f"live:{code}")
                if subject:
                    subjects.append(subject)
            except Exception as e:
                config.logger.exception("Error fetching/parsing %s: %s", url, e)
            time.sleep(delay)
        return subjects

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
            # Remove keys that are None only (keep empty strings; required fields
            # must exist as empty strings if no value was present).
            cleaned = {k: v for k, v in d.items() if v is not None}
            serialized.append(cleaned)
        df = pd.DataFrame(serialized)
        # At this point, models enforce integer credits; serialized values should be int for credits
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_json(output_file, orient="records", force_ascii=False, indent=2)
        csv_path = output_file.with_suffix(".csv")
        # Use to_csv for CSV; all fields are strings or ints now
        df2 = df.copy()
        df2.to_csv(csv_path, index=False)
