import json, os, datetime

SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "resources", "session.json")

def start_session(employee_name):
    session = {
        "employee": employee_name,
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed_exceptions": []
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)
    return session

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_session(session):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
