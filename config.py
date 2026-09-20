import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
UPI_ID = os.getenv('UPI_ID', 'susilmadhesh@okaxis')
PAYEE_NAME = os.getenv('PAYEE_NAME', 'Susil Madhesh')
CURRENCY = os.getenv('CURRENCY', 'INR')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Authorization configuration
# Role name or role ID that has permission to use the bot
AUTHORIZED_ROLE = os.getenv('AUTHORIZED_ROLE', 'Payment Authorized')
# Comma-separated Discord User IDs allowed to use the bot
AUTHORIZED_USERS = [u.strip() for u in os.getenv('AUTHORIZED_USERS', '').split(',') if u.strip()]
