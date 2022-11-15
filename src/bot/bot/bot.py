import logging
import os
from telegram import __version__ as TG_VER


try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0) 

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(f"This bot is not compatible with your current PTB version {TG_VER}")
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bot.commands import start
# Enable logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

def run():
    logger.info("Starting AuleLiberePolimi...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))

    app.run_polling()
