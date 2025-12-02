import enum
from pathlib import Path
from typing import Annotated

import typer

import config
from harvester import Harvester
from settings import get_settings

settings = get_settings()
harvester = Harvester(settings)


# --- 実行モード定義 ---
class RunMode(str, enum.Enum):
    LOCAL_FULL = "local-full"
    LOCAL_SMALL = "local-small"
    LIVE_SMALL = "live-small"
    LIVE_FULL = "live-full"


# --- Typer アプリケーション定義 ---
app = typer.Typer(help="MomijiHarvester: Hiroshima University Syllabus Scraper CLI")


# --- メインコマンド ---
@app.command()
def main(
    mode: Annotated[RunMode, typer.Option("--mode", "-m", help="Execution mode.")] = RunMode.LOCAL_SMALL,
    local_dir: Annotated[
        Path | None, typer.Option("--local-dir", help="Directory containing local HTML files (for local modes).")
    ] = None,
    output_file: Annotated[Path, typer.Option("--output", "-o", help="Output JSON file path.")] = Path(
        "output/syllabus_data.json"
    ),
    config_file: Annotated[
        Path | None, typer.Option("--config", help="Path to configuration file (e.g., .env).")
    ] = None,
):
    """
    Run the MomijiHarvester to scrape syllabus data.
    """
    try:
        # --- 設定の読み込み ---
        # settings.py の Settings クラスを使う
        app_settings = get_settings(config_file if config_file else ".env")

        # --- 出力ディレクトリ作成 ---
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # --- Harvester インスタンス化 ---
        # harvester.py の Harvester クラスを使う
        harv = Harvester(app_settings)
        subjects = []

        # No config flag for fractional credits; model validation enforces integer credits
        # --- ロギング開始 ---
        # config.py で定義されたロガーを使う想定
        config.logger.info(f"Starting harvester in {mode.value} mode.")

        # --- モードに応じた処理 ---
        if mode == RunMode.LOCAL_FULL:
            html_dir = local_dir if local_dir else app_settings.local_html_dir_full
            if not html_dir or not html_dir.is_dir():
                config.logger.error(f"Local HTML directory not found or invalid: {html_dir}")
                raise typer.Exit(code=1)
            subjects = harv.harvest_from_local(html_dir)
        elif mode == RunMode.LOCAL_SMALL:
            html_dir = local_dir if local_dir else app_settings.local_html_dir_small
            if not html_dir or not html_dir.is_dir():
                config.logger.error(f"Local HTML directory not found or invalid: {html_dir}")
                raise typer.Exit(code=1)
            subjects = harv.harvest_from_local(html_dir)
        elif mode == RunMode.LIVE_SMALL:
            if not app_settings.live_small_codes:
                config.logger.error("live_small_codes is not defined in settings.")
                raise typer.Exit(code=1)
            subjects = harv.harvest_from_web(target_codes=app_settings.live_small_codes)
        elif mode == RunMode.LIVE_FULL:
            # 全件取得ロジックは harvester 側で実装する想定
            subjects = harv.harvest_from_web(target_codes=None)

        # --- 結果の保存 ---
        if subjects:
            harv.save_results(subjects, output_file)
            config.logger.info(f"Successfully harvested {len(subjects)} subjects and saved to {output_file}")
        else:
            config.logger.warning("No subjects were harvested.")

        config.logger.info("Harvester finished.")

    except FileNotFoundError as e:
        config.logger.error(f"Configuration file not found: {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        config.logger.exception(f"An unexpected error occurred during harvesting: {e}")
        raise typer.Exit(code=1) from e


# --- スクリプトとして直接実行された場合 ---
if __name__ == "__main__":
    app()
