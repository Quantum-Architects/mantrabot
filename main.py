import logging
import mantrapy.querier
import requests
import json
import mantrapy
import users

from cosmospy import _wallet as wallet
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from mantrapy.querier.querier import API, RPC, Querier

querier = Querier(API, RPC)

DEFAULT_BECH32 = "mantra"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_wallet = wallet.generate_wallet(hrp=DEFAULT_BECH32)
    users.save_wallet(update.effective_user, user_wallet)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def query_block_by_height(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    height = int(context.args[0])
    try:
        req = querier.get_block_by_height(height)
        print(req.block)
        await update.message.reply_text(req.block)
    except Exception as e:
        print(e)
        await update.message.reply_text(
            "height -- Cant connect to the server. Please try again later"
        )

async def query_status(update: Update, context: ContextTypes) -> None:
      return  


async def query_block_by_hash(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    hash = context.args[0]
    try:
        print(hash)
        if hash == "latest":
            hash = querier.get_last_hash()
            print(hash)
        print(hash)
        req = querier.get_block_by_hash(hash)

        print(req.block)
        await update.message.reply_text(req.block)
    except Exception as e:
        print(e)
        await update.message.reply_text(
            "hash -- Cant connect to the server. Please try again later"
        )


async def query_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query a block either by hash, height or latest"""
    try:
        args = context.args[0]
    except:
        await update.message.reply_text("/block latest|BLOCK_NUMBER|BLOCK_HASH")
        return

    try:
        height = int(args)
        print(height)
        await query_block_by_height(update, context)
    except:
        await query_block_by_hash(update, context)


async def iam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Define who you are so you can use your"""
    return


async def query_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    address = users.get_address(update.effective_user)
    if address == "":
        await update.message.reply_text("You have no account registered under your user!")
        return
    
    balances_resp = querier.get_balances(address)
    if len(balances_resp.balances) == 0:
        await update.message.reply_text("You dont have any balance!")
        return
    print(balances_resp.balances)
    await update.message.reply_text(balances_resp.balances)

async def query_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    address = users.get_address(update.effective_user)
    if address == "":
        await update.message.reply_text("You have no account registered under your user!")
        return
    account_resp = querier.get_account(address)
    if account_resp.account is None:
        await update.message.reply_text("The account does not exist yet. Please send a transaction, in order for it to be created")
    print(account_resp)
    await update.message.reply_text(account_resp.account)


async def query_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    address = users.get_address(update.effective_user)
    if address == "":
         await update.message.reply_text("You have no account registered under your user!")
         return
    await update.message.reply_text(address)


# async def options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    # keyboard = [
    #     [
    #         InlineKeyboardButton("Option 1", callback_data="1"),
    #         InlineKeyboardButton("Option 2", callback_data="2"),
    #         InlineKeyboardButton("Option 3", callback_data="3"),
    #     ],
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)

    # await update.message.reply_text("Please choose:", reply_markup=reply_markup)


# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()

#     await query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token("7655436649:AAHgfubO5N4IfvvxNRT96Q5DTV7KS8b7CAA")
        .build()
    )

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rawblock", query_block))
    application.add_handler(CommandHandler("block", query_block))
    application.add_handler(CommandHandler("iam", iam))
    application.add_handler(CommandHandler("balance", query_balance))
    application.add_handler(CommandHandler("whoami", query_address))
    application.add_handler(CommandHandler("account", query_account))
    # application.add_handler(CallbackQueryHandler(button))
    # application.add_handler(CommandHandler("send", send_tx))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
