import json
import os

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config",
    "payment_settings.json"
)

DEFAULT_SETTINGS = {
    "provider": "Manual Payment",
    "merchant_name": "",
    "merchant_id": "",
    "terminal_id": "",
    "store_id": "",
    "upi_id": "",
    "api_key": "",
    "api_secret": "",
    "webhook": "",
    "environment": "Sandbox",
    "auto_connect": True,
    "auto_print": True,
    "auto_whatsapp": True,
    "save_reference": True,
    "split_payment": True,
    "auto_qr": True
}


def load_payment_settings():
    if not os.path.exists(CONFIG_FILE):
        save_payment_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_payment_settings(settings):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)