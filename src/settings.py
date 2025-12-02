from pathlib import Path
from typing import List, Optional

import config


class Settings:
    """Simple settings container for MomijiHarvester.

    This intentionally avoids pydantic BaseSettings to keep dependencies
    light within this repository environment. It loads defaults from
    `src/config.py` and can be extended to parse an env file later.
    """

    def __init__(self, _env_file: Optional[str] = None):
        self.local_html_dir_full: Path = Path(config.LOCAL_HTML_DIR_FULL)
        self.local_html_dir_small: Path = Path(config.LOCAL_HTML_DIR_SMALL)
        self.live_small_codes: Optional[List[str]] = None


def get_settings(env_file: str | Path | None = None) -> Settings:
    return Settings(_env_file=str(env_file) if env_file is not None else None)

