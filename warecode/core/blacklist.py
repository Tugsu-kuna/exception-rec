import json
import os

BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "resources", "blacklist.json")

def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r") as f:
            data = json.load(f)
            return data.get("ranges", [])
    except Exception as e:
        print(f"⚠️ Could not load blacklist: {e}")
        return []

def save_blacklist(ranges):
    try:
        with open(BLACKLIST_FILE, "w") as f:
            json.dump({"ranges": ranges}, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save blacklist: {e}")

def is_blacklisted(robot_code, blacklist_ranges):
    try:
        num = int(robot_code.split("-")[1])
    except (IndexError, ValueError):
        return False

    for start, end in blacklist_ranges:
        if end is None:
            if num >= start:
                return True
        elif start <= num <= end:
            return True
    return False