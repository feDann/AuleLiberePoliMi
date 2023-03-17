import logging
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    ContextTypes
)
from bot.keyboards.keyboards import get_keyboard
from bot.utils.locations import locations
from bot.utils.keys import get_keys
from bot.utils.messages import get_text
from mongo.mongo.models import User, SearchHistory

"""
States for the conversation handler
"""
(    
    SET_LOCATION,
    SET_DAY,
    SET_START_TIME,
    SET_END_AND_SEND,
) = range(4)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    First state of the search process, send the campus lists and goes to the SET_LOCATION state
    create a new search object in the db
    """
    user = update.message.from_user
    locations_keyboard = get_keyboard("location_keyboard")
    new_search = SearchHistory(telegram_id = user.id)
    await new_search.save()



    return SET_LOCATION


async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Second state of the search process, set the location and goes to the SET_DAY state
    """
    assert False, "ERROR: Not implemented yet"

    return SET_DAY


async def set_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Third state of the search process, set the day and goes to the SET_START_TIME state
    """
    assert False, "ERROR: Not implemented yet"

    return SET_START_TIME


async def set_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fourth state of the search process, set the start time and goes to the SET_END_AND_SEND state
    """
    assert False, "ERROR: Not implemented yet"

    return SET_END_AND_SEND


async def set_end_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fifth state of the search process, set the end time and send the results
    """
    assert False, "ERROR: Not implemented yet"

    return ConversationHandler.END

def create_conversation_handler() -> ConversationHandler:
    """Build the conversation handler for the search process

    Returns:
        ConversationHandler: The search process conversation handler
    """
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Filters.regex(get_keys("search")), search)],
        states= {
            SET_LOCATION: [],
            SET_DAY: [],
            SET_START_TIME: [],
            SET_END_AND_SEND: []
        },
        fallbacks=[],
    )

    return conv_handler