import logging

from mantrapy.client.client import Client
from mantrapy.constants.constants import Constants
from mantrapy.txbuilder.builder import TxBuilder
from mantrapy.wallet import wallet
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

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

TEST_MNEMONIC = 'anger pencil awful note doctor like slide muffin hungry keen appear eight barrel stone quiz candy loud blush load three analyst buddy health member'  # noqa: E501


async def send_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, mnemonic, _, _ = users.get_wallet(update.effective_user.username)
    if not mnemonic:
        await context.bot.send_message(update.effective_user.id, '❌ No account registered for your user, please type /start first ❌')
        return
    w = wallet.wallet_from_mnemonic(mnemonic)

    if not context.args:
        await context.bot.send_message(update.effective_user.id, '❌ Arguments are missing ❌')
        return
    if len(context.args) != 2:
        return

    try:
        handle = context.args[0]
        _, mnemonic2, _, _ = users.get_wallet(handle)
        if not mnemonic:
            await context.bot.send_message(update.effective_user.id, '❌ The receiver is not registered. ❌')
            return
        receiver = wallet.wallet_from_mnemonic(mnemonic2)
    except Exception:
        return
    try:
        amount = int(context.args[1])
    except Exception:
        return

    try:
        builder = TxBuilder(w, is_testnet=True)
        body, auth, sign_doc = builder.bank_send(receiver.address, amount, 'uom')
        resp = builder.broadcast_tx(body, auth, builder.sign_message(sign_doc))
        html_message = f"""💸 {amount} uom sent to {handle} 🚀

📩 TxHash: <a href="https://explorer.mantrachain.io/MANTRA-Dukong/tx/{resp['tx_response']['txhash']}">{resp['tx_response']['txhash']}</a>
"""
        await context.bot.send_message(update.effective_user.id, html_message, parse_mode='HTML')
    except Exception:
        await context.bot.send_message(update.effective_user.id, '❌ Error sending the transaction. ❌')

    return


async def fund_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, mnemonic, _, address = users.get_wallet(update.effective_user.username)
    if not mnemonic:
        await context.bot.send_message(update.effective_user.id, '❌ No account registered for your user, please type /start first ❌')
        return
    try:
        w = wallet.wallet_from_mnemonic(TEST_MNEMONIC)
        builder = TxBuilder(w, is_testnet=True)
        body, auth, sign_doc = builder.bank_send(address, 3600, 'uom')
        resp = builder.broadcast_tx(body, auth, builder.sign_message(sign_doc))
        html_message = f"""🤑Coins sent 🤑

💵 3600 uom

📩 TxHash: <a href="https://explorer.mantrachain.io/MANTRA-Dukong/tx/{resp['tx_response']['txhash']}">{resp['tx_response']['txhash']}</a>
"""
        await context.bot.send_message(update.effective_user.id, html_message, parse_mode='HTML')
    except Exception:
        await context.bot.send_message(update.effective_user.id, '❌ Error sending the transaction. ❌')
    return
