# MantraBot

Mantrabot is a Telegram messaging bot that enables interaction with the Mantra blockchain.
With Mantrabot, users can create accounts, send transfers, and onboard new users effortlessly—all through simple, intuitive messages.

Requirements python > 3.10

To run `MantraBot` follow this steps:
   ```
   git clone https://github.com/Quantum-Architects/mantrabot
   cd mantrabot
   python venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   python main.py new
   ```
You will also need the `MantraPy` webhooks server to handle push notifications to the users:
   ```
   git clone https://github.com/Quantum-Architects/mantrapy
   cd mantrapy
   python venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   fastapi dev mantrapy/server/main.py
   ```
