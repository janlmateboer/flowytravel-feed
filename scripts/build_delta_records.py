import json
from pathlib import Path
from datetime import datetime, timezone

CHANGES_FILE = Path("snapshots/tui/latest/changes_since_previous.json")
PRICE_CHANGES_FILE = Path("audits/tui/price_changes.json")

OUTPUT_FILE = Path("snapshots/tui/latest/delta_records.json")


def load_json(path):
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    changes = load_json(CHANGES_FILE)
    price_changes = load_json(PRICE_CHANGES_FILE)

    records = []

    for item_id in changes.get("added_ids", []):
        records.append({
            "action": "add",
            "id": item_id
        })

    for item_id in changes.get("removed_ids", []):
        records.append({
            "action": "remove",
            "id": item_id
        })

    for item in price_changes.get("price_changes", []):
        records.append({
            "action": "price_update",
            "id": item.get("id"),
            "old_price": item.get("old_price"),
            "new_price": item.get("new_price")
        })

    payload = {
        "merchant": "tui",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "records": records
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Created delta_records.json with {len(records)} records")


if __name__ == "__main__":
    main()
