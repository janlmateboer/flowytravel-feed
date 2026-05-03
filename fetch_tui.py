import requests
import json
from datetime import datetime

# 🔑 HIER JOUW TUI FEED URL INVULLEN
FEED_URL = "https://jouw-echte-feed-url.xml"

def fetch_feed():
    print("Fetching TUI feed...")
    response = requests.get(FEED_URL)
    
    if response.status_code != 200:
        raise Exception(f"Feed error: {response.status_code}")
    
    return response.text

def create_snapshot(xml_data):
    snapshot = {
        "fetched_at": datetime.utcnow().isoformat(),
        "raw_data": xml_data
    }

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f)

    print("Snapshot opgeslagen")

def main():
    xml = fetch_feed()
    create_snapshot(xml)

if __name__ == "__main__":
    main()
