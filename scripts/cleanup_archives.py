from pathlib import Path

ARCHIVE_DIR = Path("snapshots/tui/archive")

KEEP_LATEST = 30


def main():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(
        ARCHIVE_DIR.glob("*"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    old_files = files[KEEP_LATEST:]

    deleted = 0

    for file in old_files:
        if file.is_file():
            file.unlink()
            deleted += 1
            print(f"Deleted old archive: {file.name}")

    print(f"Cleanup complete. Deleted {deleted} old archive files.")


if __name__ == "__main__":
    main()
