import json
from datetime import datetime, timezone
from pathlib import Path

CHANGES_FILE = Path("snapshots/tui/latest/changes_since_previous.json")
DELTA_FILE = Path("snapshots/tui/latest/delta_import.json")


def load_json(path):
    if not path.exists():
        raise Exception(f"{path} not found")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    changes = load_json(CHANGES_FILE)

    added_ids = changes.get("added_ids", [])
    removed_ids = changes.get("removed_ids", [])

    delta = {
        "merchant": "tui",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "delta",
        "added_count": len(added_ids),
        "removed_count": len(removed_ids),
        "updated_count": 0,
        "added_ids": added_ids,
        "removed_ids": removed_ids,
        "updated_ids": [],
        "should_import_full_snapshot": False,
        "note": "updated_ids not implemented yet; this file currently supports added and removed IDs only."
    }

    save_json(DELTA_FILE, delta)

    print("Delta import file generated.")
    print(json.dumps({
        "added_count": delta["added_count"],
        "removed_count": delta["removed_count"],
        "updated_count": delta["updated_count"],
        "should_import_full_snapshot": delta["should_import_full_snapshot"]
    }, indent=2))


if __name__ == "__main__":
    main()
