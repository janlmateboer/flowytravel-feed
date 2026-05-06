import json
from pathlib import Path
from datetime import datetime, timezone

LATEST_META = Path("snapshots/tui/latest/snapshot_meta.json")
PREVIOUS_META = Path("snapshots/tui/previous/snapshot_meta.json")

OUTPUT_FILE = Path("audits/tui/price_changes.json")


def load_json(path):
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    latest = load_json(LATEST_META)
    previous = load_json(PREVIOUS_META)

    latest_count = latest.get("item_count", 0)
    previous_count = previous.get("item_count", 0)

    difference = latest_count - previous_count

    percentage = 0

    if previous_count > 0:
        percentage = round((difference / previous_count) * 100, 2)

    price_changes = []

    if difference != 0:
        price_changes.append({
            "id": "feed-total",
            "old_price": previous_count,
            "new_price": latest_count,
            "difference": difference,
            "difference_percentage": percentage,
            "direction": "increase" if difference > 0 else "decrease"
        })

    payload = {
        "merchant": "tui",
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "price_change_count": len(price_changes),

        "price_drop_count": len([
            x for x in price_changes
            if x["direction"] == "decrease"
        ]),

        "price_increase_count": len([
            x for x in price_changes
            if x["direction"] == "increase"
        ]),

        "price_changes": price_changes
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(price_changes)} price changes")


if __name__ == "__main__":
    main()
