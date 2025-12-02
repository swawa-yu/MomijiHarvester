from pathlib import Path

import config


class Settings:
    """Simple settings container for MomijiHarvester.

    This intentionally avoids pydantic BaseSettings to keep dependencies
    light within this repository environment. It loads defaults from
    `src/config.py` and can be extended to parse an env file later.
    """

    def __init__(self, _env_file: str | None = None):
        self.local_html_dir_full: Path = Path(config.LOCAL_HTML_DIR_FULL)
        self.local_html_dir_small: Path = Path(config.LOCAL_HTML_DIR_SMALL)
        self.live_small_codes: list[str] | None = None
        # Controls whether a fractional credit (e.g. 0.5 or 1.5) should cause a hard failure
        # when creating final JSON/CSV outputs. Default false -> warn and emit an issues file.
        self.fail_on_fractional_credits: bool = False


def get_settings(env_file: str | Path | None = None) -> Settings:
    return Settings(_env_file=str(env_file) if env_file is not None else None)

