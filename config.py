import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
UPI_ID = os.getenv('UPI_ID', 'susilmadhesh@okaxis')
PAYEE_NAME = os.getenv('PAYEE_NAME', 'Susil Madhesh')
CURRENCY = os.getenv('CURRENCY', 'INR')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
