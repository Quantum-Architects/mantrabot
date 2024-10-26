import logging
import sys
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
import requests
import json
import mantrapy
import users
import asyncio
from dataclasses import dataclass

from cosmospy import _wallet as wallet
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    filters,
    TypeHandler,
    ExtBot
)

from mantrapy.querier.querier import API, RPC, Querier

querier = Querier(API, RPC)
WEBHOOKS = 'http://localhost:8000/webhooks'
DEFAULT_BECH32 = "mantra"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""
    events: str

class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_wallet = wallet.generate_wallet(hrp=DEFAULT_BECH32)
    users.save_wallet(update.effective_user.id, user_wallet)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://pbs.twimg.com/profile_images/1790339778346618880/ihlLQAMC_400x400.jpg",
    )
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Welcome to the MantraPyBot"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def query_block_by_height(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Query a block by its height."""
    try:
        height = int(context.args[0])
    except (ValueError, IndexError):
        raise Exception("ValueError")

    try:
        req = querier.get_block_by_height(height)
        await update.message.reply_text(req.block)
    except Exception as e:
        logger.error(f"Failed to retrieve block by height: {e}")
        await update.message.reply_text(
            "Error: Unable to connect to the server. Try again later."
        )


async def query_block_by_hash(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Query a block by its hash."""
    try:
        block_hash = context.args[0]
        if block_hash == "latest":
            block_hash = querier.get_last_hash()

        req = querier.get_block_by_hash(block_hash)
        await update.message.reply_text(req.block)
    except IndexError:
        await update.message.reply_text("Please provide a block hash.")
    except Exception as e:
        logger.error(f"Failed to retrieve block by hash: {e}")
        await update.message.reply_text(
            "Error: Unable to connect to the server. Try again later."
        )


async def query_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query a block by either hash or height."""
    if not context.args:
        await update.message.reply_text("/block <latest|BLOCK_NUMBER|BLOCK_HASH>")
        return
    try:
        await query_block_by_height(update, context)
    except Exception as e:
        await query_block_by_hash(update, context)


async def query_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query the user's balance."""
    address = users.get_address(update.effective_user.id)
    if not address:
        await update.message.reply_text("No account registered for your user.")
        return

    try:
        balances_resp = querier.get_balances(address)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, we couldnt reach the server right now. Please try again later.")
        return
    if not balances_resp.balances:
        await update.message.reply_text("You have no balance.")
    else:
        await update.message.reply_text(json.dumps(balances_resp.balances, indent=2))


async def query_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query the user's account details."""
    address = users.get_address(update.effective_user.id)
    if not address:
        await update.message.reply_text("No account registered for your user.")
        return
    try:
        account_resp = querier.get_account(address)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, we couldnt reach the server right now. Please try again later.")
        return
    
    if not account_resp.account:
        await update.message.reply_text(
            "Account not found. Send a transaction to create it."
        )
    else:
        await update.message.reply_text(json.dumps(account_resp.account, indent=2))


async def query_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query the user's address."""
    address = users.get_address(update.effective_user.id)
    if not address:
        await update.message.reply_text("No account registered for your user.")
    else:
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


async def subscribe_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
Supported queries:
- module (e.g. module=staking)
- event type (e.g. event.type=transfer)
- event value (e.g. event.value=mantra1...)
- addess (e.g. address=mantra1...)
- smart contract calls (e.g. contract=mantra1...)

    curl --location 'http://localhost:8000/webhooks' \
    --header 'Content-Type: application/json' \
    --data '{
        "url": "http://test.url",
        "query": "module=bank"
    }'
"""
    # address = users.get_address(update.effective_user.id)
    # if not address:
    #     await update.message.reply_text("No account registered for your user.")
    print("Subscribing to event")
    print(update.effective_user.first_name)
    data = '{"url":"http://127.0.0.1:8010", "query": "module=staking"}'
    msg = requests.post(WEBHOOKS, data=data)
    
    response = json.loads(msg.text)
    if msg.status_code == 200:
        users.register_webhook(response["hook_id"], update.effective_user.username, update.effective_chat.id)
    print(response)

"""{'events': [{'type': 'message', 'attributes': [{'key': 'action', 'value': '/cosmos.bank.v1beta1.MsgSend', 'index': True}, {'key': 'sender', 'value': 'mantra1nagtgts4y4s3d08ykqe0vsd68l53gnlujms9zj', 'index': True}, {'key': 'module', 'value': 'bank', 'index': True}, {'key': 'msg_index', 'value': '0', 'index': True}]}]}"""

def humanize_data(data):
    output = []

    # Extract and format general information
    output.append(f"Query: {data.get('query', 'N/A')}")
    
    # Process each event generically
    for event in data.get('events', []):
        event_type = event.get('type', 'Unknown')
        output.append(f"Event Type: {event_type.capitalize()}")
        
        # Process each attribute in the event
        for attr in event.get('attributes', []):
            key = attr.get('key', 'Unknown').replace('_', ' ').capitalize()
            value = attr.get('value', 'N/A')
            
            # Special case for action key to extract transaction type if present
            if key.lower() == 'action' and '.' in value:
                transaction_type = value.split('.')[-1]
                output.append(f" - Transaction Type: {transaction_type}")
            else:
                output.append(f" - {key}: {value}")
        output.append("")  # Add a line break between events

    return "\n".join(output)

async def webhook_update(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle custom updates."""
    print("webhook update")
    print(update.events)
    print()
    humanized = humanize_data(update.events)
    # events =  json.loads(update.events)
    user, id = users.get_user_by_hook(update.events["hook_id"])
    user = "@"+user
    print(user)
    print(id)
    # chat_member = await context.bot.get_chat(chat_id=int(id))
    # payloads = context.user_data.setdefault("payloads", [])
    # payloads.append(update.payload)
    # combined_payloads = "</code>\n• <code>".join(payloads)
    # text = (
    #     f"The user {chat_member.user.mention_html()} has sent a new payload. "
    #     f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    # )
    await context.bot.send_message(chat_id=int(id), text=humanized)

async def start_bot():
    """Initialize and start the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token("7655436649:AAHgfubO5N4IfvvxNRT96Q5DTV7KS8b7CAA")
        .build()
    )
    async def custom_update(req: Request) -> None:
        """Handle custom updates."""
    # chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    # payloads = context.user_data.setdefault("payloads", [])
    # payloads.append(update.payload)
    # combined_payloads = "</code>\n• <code>".join(payloads)
    # text = (
    #     f"The user {chat_member.user.mention_html()} has sent a new payload. "
    #     f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    # )
    # await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode=ParseMode.HTML)
        # print(req)
        # print(req.body)
        data = await req.json()
        # user_id = int(req.query_params["user_id"])
        # print("response!")
        await application.update_queue.put(WebhookUpdate(data))
        return PlainTextResponse("Thank you for the submission! It's being forwarded.")
        # await update.message.reply_text("Webhook response")

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("block", query_block))
    application.add_handler(CommandHandler("balance", query_balance))
    application.add_handler(CommandHandler("account", query_account))
    application.add_handler(CommandHandler("subscribe", subscribe_to))

    application.add_handler(TypeHandler(type=WebhookUpdate,callback=webhook_update))

    starlette_app = Starlette(
        routes=[
            # Route("/telegram", telegram, methods=["POST"]),
            Route("/", custom_update, methods=["POST"]),
            # Route("/submitpayload", custom_updates, methods=["POST", "GET"]),
        ]
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=8010,
            use_colors=False,
            host="127.0.0.1",
        )
    )
    # await application.run_polling(allowed_updates=Update.ALL_TYPES)
    async with application:
        await application.start()
        await application.updater.start_polling()
        await webserver.serve()
        await application.close()
    # Run application and webserver together

async def main() -> None:
    # Check if its necessary to create or reset the db
    args = sys.argv[1:]
    if args:
        if args[0] == "new":
            users.create_db()
        elif args[0] == "reset":
            users.force_create_db()
        else:
            print("Unknown option")
            return
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
