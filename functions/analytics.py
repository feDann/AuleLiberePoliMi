import json
import logging
import threading
from datetime import datetime, timezone
from os import path

_lock = threading.Lock()
_ANALYTICS_PATH = None


def init(data_dir: str):
    global _ANALYTICS_PATH
    _ANALYTICS_PATH = path.join(data_dir, "users.json")


def track(user_id: int, username):
    """Records a user interaction. Thread-safe."""
    if _ANALYTICS_PATH is None:
        return

    now = datetime.now(timezone.utc).isoformat()
    user_key = str(user_id)

    with _lock:
        try:
            if path.exists(_ANALYTICS_PATH):
                with open(_ANALYTICS_PATH, "r") as f:
                    data = json.load(f)
            else:
                data = {}

            if user_key not in data:
                data[user_key] = {
                    "username": username,
                    "first_seen": now,
                    "last_seen": now,
                    "actions": 1,
                }
                logging.info("analytics: new user %d (%s)", user_id, username)
            else:
                data[user_key]["username"] = username
                data[user_key]["last_seen"] = now
                data[user_key]["actions"] += 1

            with open(_ANALYTICS_PATH, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logging.error("analytics track error: %s", e)
