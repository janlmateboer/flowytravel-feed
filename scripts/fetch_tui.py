import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

FEED_URL = os.environ.get("TUI_FEED_URL")

BASE_DIR = Path("snapshots/tui/latest")
SNAPSHOT_FILE = BASE_DIR / "snapshot.json"
META_FILE = BASE_DIR / "snapshot_meta.json"
IDS_FILE = BASE_DIR / "snapshot_ids.json"
CHANGES_FILE = BASE_DIR / "changes_since_previous.json"


def ensure_dirs():
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_feed():
    if not FEED_URL:
        raise Exception("TUI_FEED_URL is missing. Add it as a GitHub Secret.")

    response = requests.get(FEED_URL, timeout=60)

    if response.status_code != 200:
        raise Exception(f"TUI feed error: HTTP {response.status_code}")

    return response.text


def parse_xml_items(xml_data):
    root = ET.fromstring(xml_data)
    items = []

    for product in root.findall(".//product"):
        item = {}

        for child in product:
            key = child.tag
            value = child.text.strip() if child.text else None
            item[key] = value

        external_id = (
            item.get("external_id")
            or item.get("id")
            or item.get("product_id")
            or item.get("program_id")
        )

        if external_id:
            item["external_id"] = f"tui-{external_id}"

        items.append(item)

    return items


def load_previous_ids():
    if not IDS_FILE.exists():
        return []

    try:
        with open(IDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("ids", [])
    except Exception:
        return []


def calculate_changes(current_ids, previous_ids):
    current_set = set(current_ids)
    previous_set = set(previous_ids)

    added = sorted(list(current_set - previous_set))
    removed = sorted(list(previous_set - current_set))
    unchanged = sorted(list(current_set & previous_set))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged_count": len(unchanged),
        "added_ids": added,
        "removed_ids": removed
    }


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    ensure_dirs()

    fetched_at = datetime.now(timezone.utc).isoformat()

    print("Fetching TUI feed...")
    xml_data = fetch_feed()

    print("Parsing XML...")
    items = parse_xml_items(xml_data)

    current_ids = [
        item["external_id"]
        for item in items
        if item.get("external_id")
    ]

    previous_ids = load_previous_ids()
    changes = calculate_changes(current_ids, previous_ids)

    snapshot = {
        "merchant": "tui",
        "fetched_at": fetched_at,
        "item_count": len(items),
        "items": items
    }

    meta = {
        "merchant": "tui",
        "fetched_at": fetched_at,
        "status": "success",
        "raw_item_count": len(items),
        "unique_external_id_count": len(set(current_ids)),
        "duplicate_external_id_count": len(current_ids) - len(set(current_ids)),
        "changes": {
            "added_count": changes["added_count"],
            "removed_count": changes["removed_count"],
            "unchanged_count": changes["unchanged_count"]
        }
    }

    ids = {
        "merchant": "tui",
        "generated_at": fetched_at,
        "count": len(current_ids),
        "ids": sorted(current_ids)
    }

    print("Saving snapshot files...")
    save_json(SNAPSHOT_FILE, snapshot)
    save_json(META_FILE, meta)
    save_json(IDS_FILE, ids)
    save_json(CHANGES_FILE, changes)

    print("Done.")
    print(f"Items: {len(items)}")
    print(f"IDs: {len(current_ids)}")
    print(f"Added: {changes['added_count']}")
    print(f"Removed: {changes['removed_count']}")


if __name__ == "__main__":
    main()
