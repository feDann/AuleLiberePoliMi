from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.keyboards.keyboards import get_keyboard
from bot.utils.messages import get_text

from mongo.mongo.models.user_models import User

async def start(update: Update, context: ContextTypes):
    """
    Send a welcome message when the command /start is issued.
    If it's the first time the user uses the bot, it will be added to the database.
    """
    welcome_message = get_text("welcome")
    user = update.effective_user
    user_exists = await User.find_one(User.telegram_id == user.id)
    if not user_exists:
        await User(
            telegram_id=user.id,
            chat_id=update.effective_chat.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        ).save()
    await update.message.reply_text(welcome_message.format(user.username), reply_markup=get_keyboard("initial_keyboard"))


async def cancel(update: Update, context: ContextTypes):
    """
    Fallback command used to cancel the current conversation,
    Reset the last search and send the initial keyboard
    """
    assert False, "ERROR: Not implemented yet"
