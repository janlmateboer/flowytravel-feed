import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_FILE = Path("snapshots/tui/latest/snapshot.json")

AUDIT_DIR = Path("audits")
VALIDATION_REPORT_FILE = AUDIT_DIR / "validation_report.json"
DUPLICATE_IDS_FILE = AUDIT_DIR / "duplicate_ids.json"
MISSING_FIELDS_FILE = AUDIT_DIR / "missing_fields.json"

REQUIRED_FIELDS = [
    "external_id",
    "name",
    "url"
]


def load_snapshot():
    if not SNAPSHOT_FILE.exists():
        raise Exception("snapshot.json not found")

    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = load_snapshot()
    items = snapshot.get("items", [])

    external_ids = [
        item.get("external_id")
        for item in items
        if item.get("external_id")
    ]

    id_counts = Counter(external_ids)

    duplicate_ids = {
        external_id: count
        for external_id, count in id_counts.items()
        if count > 1
    }

    missing_fields = []

    for index, item in enumerate(items):
        missing = [
            field for field in REQUIRED_FIELDS
            if not item.get(field)
        ]

        if missing:
            missing_fields.append({
                "index": index,
                "external_id": item.get("external_id"),
                "missing": missing
            })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "merchant": snapshot.get("merchant", "tui"),
        "status": "success" if not duplicate_ids else "warning",
        "item_count": len(items),
        "external_id_count": len(external_ids),
        "unique_external_id_count": len(set(external_ids)),
        "duplicate_external_id_count": sum(duplicate_ids.values()),
        "duplicate_group_count": len(duplicate_ids),
        "missing_fields_count": len(missing_fields),
        "required_fields": REQUIRED_FIELDS
    }

    with open(VALIDATION_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(DUPLICATE_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(duplicate_ids, f, ensure_ascii=False, indent=2)

    with open(MISSING_FIELDS_FILE, "w", encoding="utf-8") as f:
        json.dump(missing_fields, f, ensure_ascii=False, indent=2)

    print("Validation done.")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
