import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# 🔑 TUI FEED URL
FEED_URL = "https://pf.tradetracker.net/?aid=172268&encoding=utf-8&type=xml-v2&fid=1564650&filter_html=1&categoryType=2&additionalType=2"


def fetch_feed():
    print("Fetching TUI feed...")
    response = requests.get(FEED_URL, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Feed error: {response.status_code}")

    return response.text


def get_text(product, tag):
    el = product.find(tag)
    return el.text.strip() if el is not None and el.text else None


def extract_items(xml_data):
    print("Parsing XML...")
    root = ET.fromstring(xml_data)

    items = []

    for product in root.findall(".//product"):
        raw_id = get_text(product, "ID") or get_text(product, "id")

        external_id = f"tui-{raw_id}".lower().strip() if raw_id else None

        item = {
            "external_id": external_id,
            "title": get_text(product, "name") or get_text(product, "Name"),
            "price": get_text(product, "price") or get_text(product, "Price"),
            "affiliate_url": get_text(product, "URL") or get_text(product, "productURL"),
            "image_url": get_text(product, "imageURL") or get_text(product, "ImageURL"),
        }

        if external_id:
            items.append(item)

    print(f"✅ {len(items)} items parsed")
    return items


# 🔥 NIEUW: changes berekenen
def create_changes_file(items):
    new_ids = set([item["external_id"] for item in items if item.get("external_id")])
    old_ids = set()

    if os.path.exists("snapshot_ids.json"):
        try:
            with open("snapshot_ids.json", "r", encoding="utf-8") as f:
                old_ids = set(json.load(f))
        except Exception:
            old_ids = set()

    added = sorted(list(new_ids - old_ids))
    removed = sorted(list(old_ids - new_ids))

    changes = {
        "generated_at": datetime.utcnow().isoformat(),
        "added_ids": added,
        "removed_ids": removed,
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged_count": len(new_ids & old_ids)
    }

    with open("changes_since_previous.json", "w", encoding="utf-8") as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)

    print("✅ changes_since_previous.json opgeslagen")


def create_files(items):
    now = datetime.utcnow().isoformat()

    snapshot = {
        "fetched_at": now,
        "total_items": len(items),
        "items": items
    }

    snapshot_ids = [item["external_id"] for item in items if item.get("external_id")]

    meta = {
        "generated_at": now,
        "fetched_at": now,
        "total_items": len(items),
        "total_external_ids": len(snapshot_ids),
        "merchant": "tui",
        "source": "tradetracker"
    }

    with open("snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    with open("snapshot_ids.json", "w", encoding="utf-8") as f:
        json.dump(snapshot_ids, f, ensure_ascii=False, indent=2)

    with open("snapshot_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("✅ snapshot.json opgeslagen")
    print("✅ snapshot_ids.json opgeslagen")
    print("✅ snapshot_meta.json opgeslagen")


def main():
    xml = fetch_feed()
    items = extract_items(xml)

    # 🔥 VOLGORDE BELANGRIJK
    create_changes_file(items)   # eerst vergelijken met vorige
    create_files(items)          # daarna nieuwe snapshot opslaan


if __name__ == "__main__":
    main()
