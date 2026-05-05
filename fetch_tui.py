import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import os

FEED_URL = "https://pf.tradetracker.net/?aid=172268&encoding=utf-8&type=xml-v2&fid=1564650&filter_html=1&categoryType=2&additionalType=2"


def fetch_feed():
    print("Fetching TUI feed...")
    response = requests.get(FEED_URL, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Feed error: {response.status_code}")

    print(f"✅ Feed fetched: {len(response.text)} chars")
    return response.text


def get_text(product, tag):
    el = product.find(tag)
    return el.text.strip() if el is not None and el.text else None


def get_prop(product, prop_name):
    for prop in product.findall(".//property"):
        if prop.get("name") == prop_name:
            val = prop.find("value")
            return val.text.strip() if val is not None and val.text else None
    return None


def extract_items(xml_data):
    print("Parsing XML...")
    root = ET.fromstring(xml_data)

    items = []

    for product in root.findall(".//product"):
        raw_id = product.get("ID") or product.get("id")
        external_id = f"tui-{raw_id}".lower().strip() if raw_id else None

        price_el = product.find("price")
        price = price_el.text.strip() if price_el is not None and price_el.text else None

        image_url = None
        image_el = product.find(".//images/image")
        if image_el is not None and image_el.text:
            image_url = image_el.text.strip()

        category_el = product.find(".//category")
        travel_type = None
        if category_el is not None:
            travel_type = (category_el.get("path") or category_el.text or "").strip().lower()

        item = {
            "external_id": external_id,
            "title": get_text(product, "name") or get_text(product, "Name"),
            "price": price,
            "affiliate_url": get_text(product, "URL") or get_text(product, "productURL"),
            "image_url": image_url,
            "travel_type": travel_type,
            "country": get_prop(product, "country"),
            "city": get_prop(product, "city"),
            "region": get_prop(product, "region"),
            "accommodation_type": get_prop(product, "accommodationType"),
            "duration": get_prop(product, "duration"),
            "departure_date": get_prop(product, "departureDate"),
            "rating": get_prop(product, "rating"),
        }

        if external_id:
            items.append(item)

    print(f"✅ {len(items)} items parsed")

    if len(items) == 0:
        raise Exception("ABORT: 0 items parsed — refusing to overwrite snapshot with empty data")

    return items


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

    print(f"✅ changes opgeslagen: +{len(added)} / -{len(removed)}")


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

    print(f"✅ snapshot bestanden opgeslagen met {len(items)} items")


def main():
    xml = fetch_feed()
    items = extract_items(xml)

    create_changes_file(items)
    create_files(items)


if __name__ == "__main__":
    main()
