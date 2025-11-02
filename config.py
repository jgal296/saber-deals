# config.py

import os
from dotenv import load_dotenv

load_dotenv()

DISNEY_STORE_URL = "https://www.disneystore.com/collectibles/lightsabers-and-relics/"
EMAIL_ALERTS_ENABLED = os.getenv("EMAIL_ALERTS_ENABLED", "False").lower() == "true"
PUSH_NOTIFICATIONS_ENABLED = os.getenv("PUSH_NOTIFICATIONS_ENABLED", "False").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")