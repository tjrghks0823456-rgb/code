import json
import os

ITEMS_FILE = r"c:\Users\User\13124\MAIN_flask1\items.json"

def clean_items():
    if not os.path.exists(ITEMS_FILE):
        print("items.json not found")
        return

    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        try:
            items = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON")
            return

    print(f"Original count: {len(items)}")
    
    # Deduplicate keeping the last occurrence (which has the dates)
    unique_items = {}
    for item in items:
        unique_items[item["id"]] = item
    
    cleaned_items = list(unique_items.values())
    # Sort by ID just in case
    cleaned_items.sort(key=lambda x: x["id"])
    
    print(f"Cleaned count: {len(cleaned_items)}")

    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_items, f, ensure_ascii=False, indent=4)
    print("items.json cleaned and saved.")

if __name__ == "__main__":
    clean_items()
