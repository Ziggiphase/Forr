import httpx
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

async def send_telegram_message(token: str, chat_id: str, text: str):
    """Sends a message using the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        if res.status_code != 200:
            logger.error(f"Failed to send Telegram message: {res.text}")
        return res

async def send_whatsapp_message(sid: str, auth_token: str, from_number: str, to_number: str, text: str):
    """Sends a message using the Twilio REST API for WhatsApp."""
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    auth = (sid, auth_token)
    data = {
        "From": from_number,
        "To": to_number,
        "Body": text
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.post(url, data=data, auth=auth)
        if res.status_code not in (200, 201):
            logger.error(f"Failed to send WhatsApp message: {res.text}")
        return res
