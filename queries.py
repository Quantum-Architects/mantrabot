import json
import logging

from mantrapy.client.client import Client
from mantrapy.constants.constants import Constants
from mantrapy.wallet import wallet
from telegram import Update
from telegram.ext import ContextTypes

import users

c = Constants()
c.testnet()
querier = Client(c.api_endpoint, c.rpc_endpoint)
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_wallet = wallet.random_wallet()
    print(user_wallet)
    users.save_wallet(update.effective_user.username, user_wallet)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo='https://pbs.twimg.com/profile_images/1790339778346618880/ihlLQAMC_400x400.jpg',
    )
    await update.message.reply_html(
        rf'Hi {user.mention_html()}! Welcome to the MantraPyBot',
    )


async def query_block_by_height(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Query a block by its height."""
    try:
        height = int(context.args[0])
    except (ValueError, IndexError):
        raise Exception('ValueError')

    try:
        req = querier.get_block_by_height(height)
        if req.status_code == 200:
            logger.error(req.error)
            return
        await context.bot.send_message(update.effective_user.id, req.data.block)
    except Exception as e:
        logger.error(f'Failed to retrieve block by height: {e}')
        await context.bot.send_message(
            update.effective_user.id,
                'Error: Unable to connect to the server. Try again later.',
        )


async def query_block_by_hash(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Query a block by its hash."""
    try:
        block_hash = context.args[0]
        if block_hash == 'latest':
            block_hash = querier.get_last_hash()

        req = querier.get_block_by_hash(block_hash)
        if req.status_code != 200:
            logger.error(req.error)
            await context.bot.send_message(
                update.effective_user.id,
                'Error: Unable to connect to the server. Try again later.',
            )
            return
        await context.bot.send_message(update.effective_user.id, req.data.block)
    except IndexError:
        await context.bot.send_message(update.effective_user.id, 'Please provide a block hash.')
    except Exception as e:
        logger.error(f'Failed to retrieve block by hash: {e}')
        await context.bot.send_message(
            update.effective_user.id,
                'Error: Unable to connect to the server. Try again later.',
        )


async def query_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query a block by either hash or height."""
    if not context.args:
        await context.bot.send_message(update.effective_user.id, '/block <latest|BLOCK_NUMBER|BLOCK_HASH>')
        return
    try:
        await query_block_by_height(update, context)
    except Exception:
        await query_block_by_hash(update, context)


async def query_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query the user's balance."""
    address = users.get_address(update.effective_user.username)
    if not address:
        await context.bot.send_message(update.effective_user.id, '❌ No account registered for your user, please type /start first ❌')
        return

    try:
        balances_resp = querier.get_balances(address)
        print(balances_resp)
        if balances_resp.status_code != 200:
            logger.error(balances_resp.error)
            return
    except Exception as e:
        logger.error(e)
        await context.bot.send_message(update.effective_user.id, '❌ Sorry, we couldnt reach the server right now. Please try again later. ❌')
        return
    if not balances_resp.data.balances:
        await context.bot.send_message(update.effective_user.id, 'You have no coins. 😞')
    else:
        balance = '💰 Your balance 💰 \n\n'
        for c in balances_resp.data.balances:
            balance += f'\t 💵 {c.amount} {c.denom}\n'
        await context.bot.send_message(update.effective_user.id, balance)


async def query_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query the user's account details."""
    address = users.get_address(update.effective_user.username)
    if not address:
        await context.bot.send_message(update.effective_user.id, '❌ No account registered for your user, please type /start first ❌')
        return
    try:
        account_resp = querier.get_account(address)
        if account_resp.status_code == 404:
            await context.bot.send_message(
                update.effective_user.id,
                '❌ Account not found. Send a transaction to create it. ❌',
            )
            return
        if account_resp.status_code != 200:
            logger.error(account_resp.error)
            print(account_resp)
            return
    except Exception as e:
        logger.error(e)
        await context.bot.send_message(update.effective_user.id, '❌ Sorry, we couldnt reach the server right now. Please try again later. ❌')
        return

    if not account_resp.data.account:
        await context.bot.send_message(
            update.effective_user.id,
                '❌ Account not found. Send a transaction to create it. ❌',
        )
    else:
        await context.bot.send_message(update.effective_user.id, json.dumps(account_resp.data.account, indent=2))


async def query_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query the user's address."""
    address = users.get_address(update.effective_user.username)
    if not address:
        await context.bot.send_message(update.effective_user.id, '❌ No account registered for your user ❌')
    else:
        html_message = f"""Your wallet address:
📪 <a href="https://explorer.mantrachain.io/MANTRA-Dukong/account/{address}">{address}</a> 📪
"""
        await context.bot.send_message(update.effective_user.id, html_message, parse_mode='HTML')
