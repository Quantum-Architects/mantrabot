import users
import logging
import json
from mantrapy.wallet import wallet
from mantrapy.txbuilder.builder import TxBuilder
from mantrapy.client.client import Client
from mantrapy.constants.constants import Constants
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

c = Constants()
c.testnet()
querier = Client(c.api_endpoint, c.rpc_endpoint)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TEST_MNEMONIC = 'anger pencil awful note doctor like slide muffin hungry keen appear eight barrel stone quiz candy loud blush load three analyst buddy health member'  # noqa: E501


async def send_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, mnemonic, _, _ = users.get_wallet(update.effective_user.username)
    if not mnemonic:
        await context.bot.send_message(update.effective_user.id, "No account registered for your user.")
        return
    w = wallet.wallet_from_mnemonic(mnemonic)

    if not context.args:
        #TODO error handle
        return
    if len(context.args) != 2:
        return

    try:
        handle = context.args[0]
        _, mnemonic2, _, _ = users.get_wallet(handle)
        if not mnemonic:
            await context.bot.send_message(update.effective_user.id, "No account registered for your user.")
            return
        receiver = wallet.wallet_from_mnemonic(mnemonic2)
    except:
        return
    try:
        amount = int(context.args[1])
    except:
        return


    builder = TxBuilder(w, is_testnet=True)
    body, auth, sign_doc = builder.bank_send(receiver.address, amount, 'uom')
    #TODO add error handling
    resp = builder.broadcast_tx(body, auth, builder.sign_message(sign_doc))
    # {"tx_response": {"height": "0", "txhash": "AA910D53270C2C2B55C949CDEBC2C28475DAFECC82600C071A29D5C516C9E2E8", "codespace": "", "code": 0, "data": "", "raw_log": "", "logs": [], "info": "", "gas_wanted": "0", "gas_used": "0", "tx": null, "timestamp": "", "events": []}}
    #TODO humanize this
    await context.bot.send_message(update.effective_user.id, resp)
    return

async def fund_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, mnemonic, _, address = users.get_wallet(update.effective_user.username)
    if not mnemonic:
        await context.bot.send_message(update.effective_user.id, "No account registered for your user.")
        return
    try:
        w = wallet.wallet_from_mnemonic(TEST_MNEMONIC)
        builder = TxBuilder(w, is_testnet=True)
        body, auth, sign_doc = builder.bank_send(address, 3600, 'uom')
        resp = builder.broadcast_tx(body, auth, builder.sign_message(sign_doc))
        print(resp)

        html_message = f"""🤑Coins sent 🤑

💵 3600 uom

📩 TxHash: <a href="https://explorer.mantrachain.io/MANTRA-Dukong/tx/{resp['tx_response']['txhash']}">{resp['tx_response']['txhash']}</a>
"""
        await context.bot.send_message(update.effective_user.id, html_message, parse_mode="HTML")
    except Exception:
        await context.bot.send_message(update.effective_user.id, "❌ Error sending the transaction. ❌")
    return
