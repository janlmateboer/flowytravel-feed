import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# 🔑 TUI FEED URL
FEED_URL = "https://pf.tradetracker.net/?aid=172268&encoding=utf-8&type=xml-v2&fid=1564650&filter_html=1&categoryType=2&additionalType=2"

def fetch_feed():
    print("Fetching TUI feed...")
    response = requests.get(FEED_URL)

    if response.status_code != 200:
        raise Exception(f"Feed error: {response.status_code}")

    return response.text


def extract_items(xml_data):
    print("Parsing XML...")
    root = ET.fromstring(xml_data)

    items = []

    for product in root.findall(".//product"):
        external_id = product.findtext("id")

        item = {
            "external_id": f"tui-{external_id}" if external_id else None,
            "title": product.findtext("name"),
            "price": product.findtext("price"),
            "affiliate_url": product.findtext("productURL"),
            "image_url": product.findtext("imageURL"),
        }

        items.append(item)

    print(f"{len(items)} items parsed")
    return items


def create_snapshot(items, xml_data):
    now = datetime.utcnow().isoformat()

    # --- snapshot.json ---
    snapshot = {
        "fetched_at": now,
        "total_items": len(items),
        "items": items
    }

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    # --- snapshot_ids.json ---
    snapshot_ids = [item["external_id"] for item in items if item["external_id"]]

    with open("snapshot_ids.json", "w") as f:
        json.dump(snapshot_ids, f, indent=2)

    # --- snapshot_meta.json ---
    meta = {
        "generated_at": now,
        "total_items": len(items),
        "total_external_ids": len(snapshot_ids),
        "source": "tui"
    }

    with open("snapshot_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("✅ Snapshot + IDs + Meta opgeslagen")


def main():
    xml = fetch_feed()
    items = extract_items(xml)
    create_snapshot(items, xml)


if __name__ == "__main__":
    main()
