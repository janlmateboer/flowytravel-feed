import json
from pathlib import Path

CONFIGS_DIR = Path("configs")


def load_config(feed_name):
    config_path = CONFIGS_DIR / f"{feed_name}.json"

    if not config_path.exists():
        raise Exception(f"Config not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
