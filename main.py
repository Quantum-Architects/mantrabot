import asyncio
import json
import logging
import sys
from dataclasses import dataclass

import requests
import uvicorn
from mantrapy.client.client import Client
from mantrapy.constants.constants import Constants
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import ExtBot
from telegram.ext import TypeHandler

import help
import humanize
import queries
import txns
import users

c = Constants()
c.testnet()
querier = Client(c.api_endpoint, c.rpc_endpoint)
WEBHOOKS = 'http://localhost:8000/webhooks'
DEFAULT_BECH32 = 'mantra'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)
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
        application: 'Application',
    ) -> 'CustomContext':
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def subscribe_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # address = users.get_address(update.effective_user.id)
    # if not address:
    #     await context.bot.send_message(update.effective_user.id, "No account registered for your user.")
    data = '{"url":"http://127.0.0.1:8010", "query": "module=staking"}'
    msg = requests.post(WEBHOOKS, data=data)

    response = json.loads(msg.text)
    if msg.status_code == 200:
        users.register_webhook(response['hook_id'], update.effective_user.username, update.effective_chat.id)
    print(response)
    logger.info(rf"User {update.effective_user.username} subscribed to {response['hook_id']}")


async def follow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    address = users.get_address(update.effective_user.username)
    if not address:
        await context.bot.send_message(update.effective_user.id, 'No account registered for your user.')

    data = '{"url":"http://127.0.0.1:8010", "query": "type=transfer&value='+address+'"}'
    print(data)
    msg = requests.post(WEBHOOKS, data=data)

    response = json.loads(msg.text)
    if msg.status_code == 200:
        users.register_webhook(response['hook_id'], update.effective_user.username, update.effective_chat.id)
    print(response)
    logger.info(rf"User {update.effective_user.username} subscribed to {response['hook_id']}")
    await context.bot.send_message(update.effective_user.id, '🤖 I will notify you when someone interacts with your wallet! 🚀')


async def webhook_update(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle custom updates."""
    username, id = users.get_user_by_hook(update.events['hook_id'])
    # TODO: get wallet
    addr = users.get_address(username)
    humanized = humanize.event(update.events, addr)
    print(update.events)
    print(humanized)
    await context.bot.send_message(chat_id=int(id), text=humanized)


async def start_bot():
    """Initialize and start the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token('7655436649:AAHgfubO5N4IfvvxNRT96Q5DTV7KS8b7CAA')
        .build()
    )

    async def custom_update(req: Request) -> None:
        """Handle custom updates."""
        data = await req.json()
        await application.update_queue.put(WebhookUpdate(data))
        return PlainTextResponse("Thank you for the submission! It's being forwarded.")

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', queries.start))
    application.add_handler(CommandHandler('help', help.help_command))
    application.add_handler(CallbackQueryHandler(help.button))
    application.add_handler(CommandHandler('block', queries.query_block))
    application.add_handler(CommandHandler('balance', queries.query_balance))
    application.add_handler(CommandHandler('account', queries.query_account))
    application.add_handler(CommandHandler('address', queries.query_address))
    application.add_handler(CommandHandler('whoami', queries.query_address))

    application.add_handler(CommandHandler('subscribe', subscribe_to))
    application.add_handler(CommandHandler('follow', follow))
    # application.add_handler(CommandHandler("unsubscribe", subscribe_to))

    # TODO delegation
    # application.add_handler(CommandHandler("delegation", get_delegation_total_rewards))
    # application.add_handler(CommandHandler("delegator_delegation", get_delegator_delegations))

    application.add_handler(CommandHandler('send', txns.send_to))
    application.add_handler(CommandHandler('fundme', txns.fund_user))

    # Webhooks
    application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))

    # Run application and webserver together
    starlette_app = Starlette(
        routes=[
            Route('/', custom_update, methods=['POST']),
        ],
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=8010,
            use_colors=False,
            host='127.0.0.1',
        ),
    )
    async with application:
        await application.start()
        await application.updater.start_polling()
        await webserver.serve()
        await application.close()


async def main() -> None:
    # Check if its necessary to create or reset the db
    args = sys.argv[1:]
    if args:
        if args[0] == 'new':
            users.create_db()
        elif args[0] == 'reset':
            users.force_create_db()
        else:
            print('Unknown option')
            return
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main())
