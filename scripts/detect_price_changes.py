import json
import re
from datetime import datetime, timezone
from pathlib import Path

PREVIOUS_SNAPSHOT = Path("snapshots/tui/previous/snapshot.json")
LATEST_SNAPSHOT = Path("snapshots/tui/latest/snapshot.json")
PRICE_CHANGES_FILE = Path("audits/price_changes.json")


PRICE_FIELDS = [
    "price",
    "prijs",
    "price_from",
    "from_price",
    "current_price",
    "lowest_price"
]


def load_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_price(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = re.sub(r"[^\d,\.]", "", value)

    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None


def get_price(item):
    for field in PRICE_FIELDS:
        if field in item:
            price = parse_price(item.get(field))
            if price is not None:
                return price

    return None


def index_items(snapshot):
    items = snapshot.get("items", [])
    return {
        item.get("external_id"): item
        for item in items
        if item.get("external_id")
    }


def main():
    previous = load_json(PREVIOUS_SNAPSHOT)
    latest = load_json(LATEST_SNAPSHOT)

    if not previous or not latest:
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "skipped",
            "reason": "previous or latest snapshot missing",
            "price_change_count": 0,
            "price_drop_count": 0,
            "price_increase_count": 0,
            "updated_ids": [],
            "price_changes": []
        }

        PRICE_CHANGES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PRICE_CHANGES_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("Price change detection skipped.")
        return

    previous_items = index_items(previous)
    latest_items = index_items(latest)

    price_changes = []

    for external_id, latest_item in latest_items.items():
        previous_item = previous_items.get(external_id)

        if not previous_item:
            continue

        old_price = get_price(previous_item)
        new_price = get_price(latest_item)

        if old_price is None or new_price is None:
            continue

        if old_price != new_price:
            difference = round(new_price - old_price, 2)

            price_changes.append({
                "external_id": external_id,
                "old_price": old_price,
                "new_price": new_price,
                "difference": difference,
                "direction": "down" if difference < 0 else "up"
            })

    updated_ids = sorted([
        change["external_id"]
        for change in price_changes
    ])

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        "previous_fetched_at": previous.get("fetched_at"),
        "latest_fetched_at": latest.get("fetched_at"),
        "price_change_count": len(price_changes),
        "price_drop_count": len([c for c in price_changes if c["direction"] == "down"]),
        "price_increase_count": len([c for c in price_changes if c["direction"] == "up"]),
        "updated_ids": updated_ids,
        "price_changes": price_changes
    }

    PRICE_CHANGES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PRICE_CHANGES_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Price change detection done.")
    print(json.dumps({
        "price_change_count": report["price_change_count"],
        "price_drop_count": report["price_drop_count"],
        "price_increase_count": report["price_increase_count"]
    }, indent=2))


if __name__ == "__main__":
    main()
