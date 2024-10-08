import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')
