import logging
from dotenv import load_dotenv
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

"""
States for the conversation handler
"""
(
    INITIAL_STATE,
    SET_LOCATION,
    SET_DAY,
    SET_START_TIME,
    SET_END_AND_SEND,
    SETTINGS,
    SET_LANG,
    SET_CAMPUS,
    SET_TIME,
    NOW,
) = range(10)

"""
The Functions below are used for the various commands in the states, first three functions are
referred to the initial state, second three are referred to the settings state
"""


async def search(update: Update, context: CallbackContext, lang) -> int:
    """
    Send the keyboard for the location and return to set_location state ,
    this function is the initial state for the searching process
    """
    await update.message.reply_text(
        texts[lang]["texts"]["location"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS.location_keyboard(lang), one_time_keyboard=True
        ),
    )
    return SET_LOCATION

async def now(update: Update, context: CallbackContext, lang) -> int:
    """
    Thhis functions implements the quick search, after checking if the campus is in
    the preferences of the user call the end_state function, otherwise return to the initial_state
    """
    user = update.message.from_user
    logging.info("%d : %s in now state", user.id, user.username)
    loc, dur = user_data_handler.get_user_preferences(context)

    if loc is None:
        await update.message.reply_text(
            texts[lang]["texts"]["missing"],
            reply_markup=ReplyKeyboardMarkup(KEYBOARDS.initial_keyboard(lang)),
        )
        return INITIAL_STATE

    start_time = int(datetime.now(pytz.timezone("Europe/Rome")).strftime("%H"))
    if start_time >= MAX_TIME or start_time < MIN_TIME:
        await update.message.reply_text(texts[lang]["texts"]["ops"])
        start_time = MIN_TIME
    end_time = start_time + dur if start_time + dur < MAX_TIME else MAX_TIME

    context.user_data["location"] = loc
    context.user_data["date"] = datetime.now(pytz.timezone("Europe/Rome")).strftime(
        "%d/%m/%Y"
    )
    context.user_data["start_time"] = start_time
    update.message.text = end_time
    return end_state(update, context)


async def preferences(update: Update, context: CallbackContext, lang) -> int:
    """
    Send the keyboard for the preferences state and return to setting state
    """
    await update.message.reply_text(
        texts[lang]["texts"]["settings"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)),
    )
    return SETTINGS


async def language(update: Update, context: CallbackContext, lang) -> int:
    """
    Send the keyboard for the languages and return to set_lang state
    """
    await update.message.reply_text(
        texts[lang]["texts"]["language"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.language_keyboard(lang)),
    )
    return SET_LANG


async def duration(update: Update, context: CallbackContext, lang) -> int:
    """
    Send the keyboard for the duration and return to set_time state
    """
    await update.message.reply_text(
        texts[lang]["texts"]["time"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.time_keyboard(lang)),
    )
    return SET_TIME


async def campus(update: Update, context: CallbackContext, lang) -> int:
    """
    Send the keyboard for the campus and return to set_campus state
    """
    await update.message.reply_text(
        texts[lang]["texts"]["campus"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang)),
    )
    return SET_CAMPUS





async def initial_state(update: Update, context: CallbackContext) -> int:
    """
    Initial State of the ConversationHandler, through the function_map return to
    the right function based on the user input
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in  choose initial state", user.id, user.username)

    return function_map[message](update, context, lang)


async def settings(update: Update, context: CallbackContext):
    """
    Settings state of the Conversation Handler, from here based on the user input
    calls the right function using the function_map
    """
    user = update.message.from_user
    message = update.message.text
    logging.info("%d : %s in  settings", user.id, user.username)
    lang = user_data_handler.get_lang(context)

    return function_map[message](update, context, lang)


async def set_language(update: Update, context: CallbackContext):
    """
    In this state is stored in the user_data the preference for the language,
    if the input check goes well it returns to the settings, otherwise remain
    in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set language", user.id, user.username)

    if not input_check.language_check(message, texts):
        errorhandler.bonk(update, texts, lang)
        return SET_LANG
    lang = message
    user_data_handler.update_lang(lang, context)

    await update.message.reply_text(
        texts[lang]["texts"]["success"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)),
    )
    return SETTINGS


async def set_campus(update: Update, context: CallbackContext):
    """
    In this state is stored in the user_data the preference for the campus,
    if the input check goes well it returns to the settings, otherwise remain
    in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set campus", user.id, user.username)

    if not input_check.location_check(message, location_dict):
        errorhandler.bonk(update, texts, lang)
        return SET_CAMPUS

    user_data_handler.update_campus(message, context)
    await update.message.reply_text(
        texts[lang]["texts"]["success"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)),
    )
    return SETTINGS


async def set_time(update: Update, context: CallbackContext):
    """
    In this state is stored in the user_data the preference for the duration
    in terms of hours for the quick search, if the input check goes well it
    returns to the settings, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set time", user.id, user.username)

    if not input_check.time_check(message):
        errorhandler.bonk(update, texts, lang)
        return SET_TIME

    user_data_handler.update_time(message, context)
    await update.message.reply_text(
        texts[lang]["texts"]["success"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)),
    )
    return SETTINGS


async def set_location_state(update: Update, context: CallbackContext) -> int:
    """
    In this state is saved in the user_data the location for the search process,
    if the input check goes well it returns to the set_day, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in  set location state", user.id, user.username)

    if not input_check.location_check(message, location_dict):
        errorhandler.bonk(update, texts, lang)
        return SET_LOCATION

    context.user_data["location"] = message

    await update.message.reply_text(
        texts[lang]["texts"]["day"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS.day_keyboard(lang), one_time_keyboard=True
        ),
    )

    return SET_DAY


async def set_day_state(update: Update, context: CallbackContext) -> int:
    """
    In this state is saved in the user_data the chosen day for the search process,
    if the input check goes well it returns to the set_start_time, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set day state", user.id, user.username)

    ret, chosen_date = input_check.day_check(message, texts, lang)
    if not ret:
        errorhandler.bonk(update, texts, lang)
        return SET_DAY

    context.user_data["date"] = chosen_date
    await update.message.reply_text(
        texts[lang]["texts"]["starting_time"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS.start_time_keyboard(lang), one_time_keyboard=True
        ),
    )

    return SET_START_TIME


async def set_start_time_state(update: Update, context: CallbackContext) -> int:
    """
    In this state is saved in the user_data the starting time of the search process,
    if the input check goes well it returns to the end_state, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set start state", user.id, user.username)
    ret, start_time = input_check.start_time_check(message)

    if not ret:
        errorhandler.bonk(update, texts, lang)
        return SET_START_TIME

    context.user_data["start_time"] = start_time
    await update.message.reply_text(
        texts[lang]["texts"]["ending_time"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS.end_time_keyboard(lang, start_time), one_time_keyboard=True
        ),
    )

    return SET_END_AND_SEND


async def end_state(update: Update, context: CallbackContext) -> int:
    """
    Final state of the search process, check if the last input is valid and
    proceed to return to the user all the free classrooms, otherwise remains
    in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)

    start_time = context.user_data["start_time"]
    date = context.user_data["date"]
    location = context.user_data["location"]
    ret, end_time = input_check.end_time_check(message, start_time)

    if not ret:
        errorhandler.bonk(update, texts, lang)
        return SET_END_AND_SEND

    logging.info("%d : %s in the set end time state and search", user.id, user.username)

    day, month, year = date.split("/")
    try:
        available_rooms = find_free_room(
            float(start_time + TIME_SHIFT),
            float(end_time + TIME_SHIFT),
            location_dict[location],
            int(day),
            int(month),
            int(year),
        )
        await update.message.reply_text(
            "{}   {}   {}-{}".format(date, location, start_time, end_time)
        )
        for m in string_builder.room_builder_str(
            available_rooms, texts[lang]["texts"]["until"]
        ):
            await update.message.reply_chat_action(telegram.ChatAction.TYPING)
            await update.message.reply_text(
                m,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardMarkup(initial_keyboard),
            )

        logging.info(
            "%d : %s search was: %s %s %d %d",
            user.id,
            user.username,
            location,
            date,
            start_time,
            end_time,
        )
    except Exception as e:
        logging.info(
            "Exception occurred during find_free_room, search was: %s  %s  %d-%d ",
            date,
            location,
            start_time,
            end_time,
        )
        await update.message.reply_text(
            texts[lang]["texts"]["exception"],
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(initial_keyboard),
            disable_web_page_preview=True,
        )

    user_data_handler.reset_user_data(context)

    return INITIAL_STATE


"""FALLBACKS"""


async def terminate(update: Update, context: CallbackContext) -> int:
    """
    This function terminate the Conversation handler
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    context.user_data.clear()

    logging.info("%d : %s terminated the conversation.", user.id, user.username)
    await update.message.reply_text(
        texts[lang]["texts"]["terminate"], reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def info(update: Update, context: CallbackContext):
    """
    Return some info to the user
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    logging.info("%d : %s asked for more info.", user.id, user.username)
    await update.message.reply_text(
        texts[lang]["texts"]["info"],
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(initial_keyboard),
    )
    return


async def cancel(update: Update, context: CallbackContext):
    """
    Stop any process and return to the initial state
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    user_data_handler.reset_user_data(context)
    logging.info("%d : %s canceled.", user.id, user.username)
    await update.message.reply_text(
        texts[lang]["texts"]["cancel"],
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(initial_keyboard),
    )
    return INITIAL_STATE

def create_conversation_handler()
    pass