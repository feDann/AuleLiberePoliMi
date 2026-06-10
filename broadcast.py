"""
One-shot broadcast script.
Reads all user IDs from PicklePersistence + users.json and sends a message.

Usage:
    python broadcast.py "Your message here"
    python broadcast.py  # uses default update message
"""

import os
import sys
import time
import pickle
import json
import logging
from os.path import join, dirname
from dotenv import load_dotenv
import telegram

load_dotenv(join(dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOKEN = os.environ.get("TOKEN")
PICKLE_PATH = "data/aulelibere_pp"
USERS_JSON_PATH = "data/users.json"

DEFAULT_MESSAGE = (
    "👋 <b>Aule Libere PoliMi — Update!</b>\n\n"
    "Il bot è stato aggiornato. Premi /start per ricominciare la chat e accedere alle nuove funzionalità! 🚀"
)

DELAY_BETWEEN_MESSAGES = 0.05  # 20 msg/sec, well under Telegram's 30/sec limit


def collect_user_ids() -> set:
    ids = set()

    # From PicklePersistence
    if os.path.exists(PICKLE_PATH):
        try:
            with open(PICKLE_PATH, "rb") as f:
                data = pickle.load(f)
            user_data = data.get("user_data", {})
            ids.update(user_data.keys())
            logging.info("Pickle: found %d users", len(user_data))
        except Exception as e:
            logging.error("Failed to read pickle: %s", e)

    # From users.json (newer entries)
    if os.path.exists(USERS_JSON_PATH):
        try:
            with open(USERS_JSON_PATH, "r") as f:
                users = json.load(f)
            json_ids = {int(uid) for uid in users.keys()}
            ids.update(json_ids)
            logging.info("users.json: found %d users", len(json_ids))
        except Exception as e:
            logging.error("Failed to read users.json: %s", e)

    return ids


def broadcast(message: str):
    bot = telegram.Bot(token=TOKEN)
    user_ids = collect_user_ids()

    if not user_ids:
        logging.warning("No users found. Aborting.")
        return

    logging.info("Broadcasting to %d users...", len(user_ids))

    sent = 0
    blocked = 0
    errors = 0

    for uid in user_ids:
        try:
            bot.send_message(
                chat_id=uid,
                text=message,
                parse_mode=telegram.ParseMode.HTML,
                disable_web_page_preview=True,
            )
            sent += 1
        except telegram.error.Forbidden:
            # User blocked the bot
            blocked += 1
        except Exception as e:
            logging.error("Failed to send to %d: %s", uid, e)
            errors += 1
        time.sleep(DELAY_BETWEEN_MESSAGES)

    logging.info("Done. Sent: %d | Blocked: %d | Errors: %d", sent, blocked, errors)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MESSAGE
    broadcast(msg)
