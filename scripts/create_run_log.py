import json
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_META = Path("snapshots/tui/latest/snapshot_meta.json")
DELTA_IMPORT = Path("snapshots/tui/latest/delta_import.json")
PRICE_CHANGES = Path("audits/tui/price_changes.json")
VALIDATION_REPORT = Path("audits/tui/validation_report.json")

LOG_DIR = Path("logs/tui")


def load_json(path):
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_meta = load_json(SNAPSHOT_META)
    delta_import = load_json(DELTA_IMPORT)
    price_changes = load_json(PRICE_CHANGES)
    validation_report = load_json(VALIDATION_REPORT)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")

    log = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feed": "tui",
        "status": validation_report.get("status", "unknown"),

        "snapshot": {
            "item_count": snapshot_meta.get("item_count"),
            "fetched_at": snapshot_meta.get("fetched_at")
        },

        "delta": {
            "added_count": delta_import.get("added_count", 0),
            "removed_count": delta_import.get("removed_count", 0),
            "updated_count": delta_import.get("updated_count", 0)
        },

        "prices": {
            "price_change_count": price_changes.get("price_change_count", 0),
            "price_drop_count": price_changes.get("price_drop_count", 0),
            "price_increase_count": price_changes.get("price_increase_count", 0)
        },

        "validation": {
            "duplicate_group_count": validation_report.get("duplicate_group_count", 0),
            "missing_fields_count": validation_report.get("missing_fields_count", 0)
        }
    }

    log_file = LOG_DIR / f"{timestamp}_run.json"

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print(f"Run log created: {log_file}")


if __name__ == "__main__":
    main()
