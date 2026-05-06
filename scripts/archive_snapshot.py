import shutil
from datetime import datetime, timezone
from pathlib import Path

LATEST_DIR = Path("snapshots/tui/latest")
ARCHIVE_DIR = Path("snapshots/tui/archive")


def main():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")

    files_to_archive = [
        "snapshot.json",
        "snapshot_meta.json",
        "snapshot_ids.json",
        "changes_since_previous.json",
        "delta_import.json"
    ]

    for filename in files_to_archive:
        source = LATEST_DIR / filename

        if source.exists():
            target = ARCHIVE_DIR / f"{timestamp}_{filename}"
            shutil.copy2(source, target)
            print(f"Archived {source} → {target}")
        else:
            print(f"Skipped missing file: {source}")

    print("Archive complete.")


if __name__ == "__main__":
    main()
