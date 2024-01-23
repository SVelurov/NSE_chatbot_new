import os
from dotenv import load_dotenv
load_dotenv()

TG_BOT_TOKEN = os.getenv('token')
if TG_BOT_TOKEN is None:
    raise Exception('Please set TG_BOT_TOKEN env variable to your Telegram bot token')

login_url_et = os.getenv('login_url_et')
username_et = os.getenv('username_et')
password_et = os.getenv('password_et')