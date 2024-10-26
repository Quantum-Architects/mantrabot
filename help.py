import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

import main
import queries
import txns


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    keyboard = [
        [InlineKeyboardButton('What is my address?', callback_data='address')],
        [InlineKeyboardButton('Notify me!', callback_data='follow')],
        [InlineKeyboardButton("What's my balance?", callback_data='balance')],
        [InlineKeyboardButton('I need some money!', callback_data='fundme')],
        [InlineKeyboardButton('How do I interact with other users?', callback_data='guide')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('What do you want to do?', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # await query.answer()
    print(query.data)
    # await query.edit_message_text(text=f"Selected option: {query.data}")
    if query.data == 'address':
        await queries.query_address(update, context)
    elif query.data == 'fundme':
        await txns.fund_user(update, context)
    elif  query.data == 'follow':
        await main.follow(update, context)
    elif  query.data == 'balance':
        await queries.query_balance(update, context)
    elif query.data == 'guide':
        await show_guide(update, context)

async def show_guide(update: Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    html_message =f"""🤖 Welcome to MantraBot! 🤖

    You can send a coin to a friend by using the command:
    <code>/send friend_handle 1</code>

    🙏 Make sure your friend has interacted with MantraBot first so we can recognize them! 🙏
    """
    await context.bot.send_message(update.effective_user.id, html_message, parse_mode='HTML')
