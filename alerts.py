# alerts.py
import logging
import requests
from config import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logging.info("Telegram alert sent!")
        else:
            logging.error(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        logging.error(f"Exception when sending Telegram alert: {e}", exc_info=True)
