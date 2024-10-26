import sqlite3

from mantrapy.wallet.wallet import Wallet

# Initialize a global connection to the SQLite database
DATABASE = 'users.db'


# Function to save a wallet in the database
def save_wallet(user_id: str, wallet: Wallet) -> None:
    wallet_data = (
        user_id,
        wallet.mnemonic,
        wallet.privkey,
        wallet.address,
    )

    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(
                'INSERT INTO users (id, mnemonic , pk, address) VALUES (?, ?, ?, ?)',
                wallet_data,
            )
            con.commit()
            print(f'Wallet for user {user_id} saved successfully.')
    except sqlite3.Error as e:
        print(f'Failed to save wallet for user {user_id}: {e}')


# Function to retrieve a user's address from the database
def get_address(user_id: str) -> str:
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute('SELECT address FROM users WHERE id = ?', (user_id,))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                print(f'No address found for user {user_id}.')
                return ''
    except sqlite3.Error as e:
        print(f'Failed to retrieve address for user {user_id}: {e}')
        return ''


# Function to retrieve a user's address from the database
def get_wallet(user_id: str) -> str:
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            result = cur.fetchone()
            if result:
                return result
            else:
                print(f'No address found for user {user_id}.')
                return ''
    except sqlite3.Error as e:
        print(f'Failed to retrieve address for user {user_id}: {e}')
        return ''


# Function to forcefully create/reset the database
def force_create_db() -> None:
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute('DROP TABLE IF EXISTS users')
            cur.execute('DROP TABLE IF EXISTS subscriptions')
            cur.execute(
                'CREATE TABLE users (id TEXT PRIMARY KEY, mnemonic TEXT, pk TEXT, address TEXT)',
            )
            cur.execute(
                'CREATE TABLE subscriptions (id TEXT PRIMARY KEY, username TEXT, user_id TEXT)',
            )
            con.commit()
            print('Database reset successfully.')
    except sqlite3.Error as e:
        print(f'Failed to reset database: {e}')


# Function to create the database if it does not already exist
def create_db() -> None:
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(
                'CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, mnemonic TEXT, pk TEXT, address TEXT)',
            )
            cur.execute(
                'CREATE TABLE IF NOT EXISTS subscriptions (id TEXT PRIMARY KEY, username TEXT, user_id TEXT)',
            )
            con.commit()
            print('Database checked/created successfully.')
    except sqlite3.Error as e:
        print(f'Failed to create database: {e}')


def register_webhook(hook: str, username: str, user_id: str) -> None:
    # 036c4464-5273-4bdb-89d6-9e97325b69fe
    webhook_data = (
        hook,
        username,
        user_id,
    )

    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(
                'INSERT INTO subscriptions (id, username, user_id) VALUES (?, ?, ?)',
                webhook_data,
            )
            con.commit()
            print(f'User {user_id} registered to a new event.')
    except sqlite3.Error as e:
        print(f'Failed to register hook to user {user_id}: {e}')


def get_user_by_hook(hook: str) -> None:
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute('SELECT username, user_id FROM subscriptions WHERE id = ?', (hook,))
            result = cur.fetchone()
            print(result)
            if result:
                return result
            else:
                print(f'No user is listening to {hook}.')
                return ''
    except sqlite3.Error as e:
        print(f'Failed to retrieve user for hook {hook}: {e}')
        return ''

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
