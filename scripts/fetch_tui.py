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

    ids = sorted(list(set(ids)))

    return ids


def create_changes(current_ids, previous_ids):
    current_set = set(current_ids)
    previous_set = set(previous_ids)

    added_ids = sorted(list(current_set - previous_set))
    removed_ids = sorted(list(previous_set - current_set))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "added_ids": added_ids,
        "removed_ids": removed_ids,

        "added_count": len(added_ids),
        "removed_count": len(removed_ids)
    }


def create_meta(xml_data, ids):
    return {
        "merchant": "tui",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "item_count": len(ids),
        "feed_hash": hashlib.md5(xml_data.encode()).hexdigest()
    }


def load_previous_ids():
    previous_path = Path("snapshots/tui/previous/snapshot_ids.json")

    if not previous_path.exists():
        return []

    with open(previous_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("ids", [])

    if isinstance(data, list):
        return data

    return []


def save_snapshot(xml_data):
    snapshot_path = LATEST_DIR / "snapshot.json"

    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "merchant": "tui",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "raw_xml": xml_data
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Saved snapshot.json")


def save_ids(ids):
    ids_path = LATEST_DIR / "snapshot_ids.json"

    payload = {
        "merchant": "tui",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(ids),
        "ids": ids
    }

    with open(ids_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("Saved snapshot_ids.json")


def save_meta(meta):
    meta_path = LATEST_DIR / "snapshot_meta.json"

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("Saved snapshot_meta.json")


def save_changes(changes):
    changes_path = LATEST_DIR / "changes_since_previous.json"

    with open(changes_path, "w", encoding="utf-8") as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)

    print("Saved changes_since_previous.json")


def main():
    xml_data = fetch_feed()

    current_ids = create_ids(xml_data)

    previous_ids = load_previous_ids()

    changes = create_changes(current_ids, previous_ids)

    meta = create_meta(xml_data, current_ids)

    save_snapshot(xml_data)

    save_ids(current_ids)

    save_meta(meta)

    save_changes(changes)

    print("TUI snapshot pipeline completed successfully.")


if __name__ == "__main__":
    main()
