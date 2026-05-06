import json
import subprocess
import sys
from pathlib import Path


CONFIGS_DIR = Path("configs")


def load_config(feed_name):
    config_path = CONFIGS_DIR / f"{feed_name}.json"

    if not config_path.exists():
        raise Exception(f"Config not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_step(label, command):
    print(f"\n=== {label} ===")

    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        raise Exception(f"Step failed: {label}")


def main():
    if len(sys.argv) < 2:
        raise Exception("Usage: python run_pipeline.py tui")

    feed_name = sys.argv[1]

    config = load_config(feed_name)

    merchant = config["merchant"]

    print(f"\nRunning pipeline for: {merchant}")

    run_step(
        "Archive snapshot",
        "python scripts/archive_snapshot.py"
    )

    run_step(
        "Cleanup archives",
        "python scripts/cleanup_archives.py"
    )

    run_step(
        "Fetch feed",
        "python scripts/fetch_tui.py"
    )

    run_step(
        "Validate snapshot",
        "python scripts/validate_snapshot.py"
    )

    run_step(
        "Detect price changes",
        "python scripts/detect_price_changes.py"
    )

    run_step(
        "Generate delta import",
        "python scripts/generate_delta_import.py"
    )

    run_step(
        "Build delta records",
        "python scripts/build_delta_records.py"
    )

    run_step(
        "Create run log",
        "python scripts/create_run_log.py"
    )

    print(f"\nPipeline completed for: {merchant}")


if __name__ == "__main__":
    main()
