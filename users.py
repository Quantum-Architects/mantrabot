import json
import sqlite3
from cosmospy import privkey_to_pubkey, Transaction

db = {}

# {
#     "seed": "arch skill acquire abuse frown reject front second album pizza hill slogan guess random wonder benefit industry custom green ill moral daring glow elevator",
#     "derivation_path": "m/44'/118'/0'/0/0",
#     "private_key": b"\xbb\xec^\xf6\xdcg\xe6\xb5\x89\xed\x8cG\x05\x03\xdf0:\xc9\x8b \x85\x8a\x14\x12\xd7\xa6a\x01\xcd\xf8\x88\x93",
#     "public_key": b"\x03h\x1d\xae\xa7\x9eO\x8e\xc5\xff\xa3sAw\xe6\xdd\xc9\xb8b\x06\x0eo\xc5a%z\xe3\xff\x1e\xd2\x8e5\xe7",
#     "address": "cosmos1uuhna3psjqfxnw4msrfzsr0g08yuyfxeht0qfh",
# }

# privkey = bytes.fromhex(
#     "6dcd05d7ac71e09d3cf7da666709ebd59362486ff9e99db0e8bc663570515afa"
# )
# pubkey = privkey_to_pubkey(privkey)

def save_wallet(user : str, wallet:dict) -> None:
    db[user] = wallet
    return

def get_address(user : str) -> str:
    if user not in db:
        return ""
    
    return db[user]["address"]


# tx = Transaction(
#     privkey=bytes.fromhex(
#         "26d167d549a4b2b66f766b0d3f2bdbe1cd92708818c338ff453abde316a2bd59"
#     ),
#     account_num=11335,
#     sequence=0,
#     fee=1000,
#     gas=70000,
#     memo="",
#     chain_id="cosmoshub-3",
#     sync_mode="sync",
# )
# tx.add_transfer(
#     recipient="cosmos103l758ps7403sd9c0y8j6hrfw4xyl70j4mmwkf", amount=387000
# )
# tx.add_transfer(recipient="cosmos1lzumfk6xvwf9k9rk72mqtztv867xyem393um48", amount=123)
# pushable_tx = tx.get_pushable()