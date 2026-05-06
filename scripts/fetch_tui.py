import requests
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import os

FEED_URL = os.getenv("TUI_FEED_URL")

LATEST_DIR = Path("snapshots/tui/latest")
LATEST_DIR.mkdir(parents=True, exist_ok=True)


def fetch_feed():
    if not FEED_URL:
        raise Exception("TUI_FEED_URL is missing. Add it as a GitHub Secret.")

    print("Fetching TUI feed...")

    response = requests.get(
        FEED_URL,
        timeout=180
    )

    if response.status_code != 200:
        raise Exception(f"Feed error: {response.status_code}")

    return response.text


def create_ids(xml_data):
    ids = []

    for line in xml_data.splitlines():
        if "<product_id>" in line:
            value = (
                line.replace("<product_id>", "")
                .replace("</product_id>", "")
                .strip()
            )

            if value:
                ids.append(value)

    return sorted(list(set(ids)))


def create_changes(current_ids, previous_ids):
    current_set = set(current_ids)
    previous_set = set(previous_ids)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "added_ids": sorted(list(current_set - previous_set)),
        "removed_ids": sorted(list(previous_set - current_set)),

        "added_count": len(current_set - previous_set),
        "removed_count": len(previous_set - current_set)
    }


def create_meta(xml_data, ids):
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "item_count": len(ids),
        "feed_hash": hashlib.md5(xml_data.encode()).hexdigest()
    }


def load_previous_ids():
    previous_path = Path("snapshots/tui/previous/snapshot_ids.json")

    if not previous_path.exists():
        return []

    with open(previous_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    xml_data = fetch_feed()

    ids = create_ids(xml_data)

    previous_ids = load_previous_ids()

    changes = create_changes(ids, previous_ids)

    meta = create_meta(xml_data, ids)

    snapshot_path = LATEST_DIR / "snapshot.json"
    ids_path = LATEST_DIR / "snapshot_ids.json"
    meta_path = LATEST_DIR / "snapshot_meta.json"
    changes_path = LATEST_DIR / "changes_since_previous.json"

    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "raw_xml": xml_data
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    with open(ids_path, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    with open(changes_path, "w", encoding="utf-8") as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)

    print("Snapshot files updated successfully.")


if __name__ == "__main__":
    main()
